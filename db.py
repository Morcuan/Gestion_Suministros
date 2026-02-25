# --------------------------------------------#
# Modulo: db.py                               #
# Descripción: Acceso a datos para contratos   #
# Autor: Antonio Morales + Copilot            #
# Fecha: 2026-02-24                           #
# --------------------------------------------#

import sqlite3
from datetime import datetime, timedelta

DB_PATH = "data/almacen.db"


# ============================================================
#  CONEXIÓN
# ============================================================
def get_conn():
    return sqlite3.connect(DB_PATH)


# ============================================================
#  LECTURA DEL SUPLEMENTO VIGENTE
# ============================================================
def obtener_suplemento_vigente(ncontrato: str) -> dict:
    """
    Devuelve un diccionario con TODOS los datos del suplemento vigente
    usando la vista vista_contratos.
    """

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM vista_contratos
        WHERE ncontrato = ?
        ORDER BY suplemento DESC
        LIMIT 1
        """,
        (ncontrato,),
    )

    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    columnas = [d[0] for d in cur.description]
    datos = dict(zip(columnas, row))

    # Necesitamos id_contrato real del suplemento vigente
    cur.execute(
        """
        SELECT id_contrato
        FROM contratos_identificacion
        WHERE ncontrato = ? AND suplemento = ?
        """,
        (ncontrato, datos["suplemento"]),
    )
    datos["id_contrato"] = cur.fetchone()[0]

    conn.close()
    return datos


# ============================================================
#  DUPLICADO DE REGISTROS PARA SUPLEMENTO NUEVO
# ============================================================
def duplicar_registro(cur, tabla: str, id_contrato: int, nuevo_id: int):
    """
    Duplica un registro completo de una tabla (energia o gastos)
    cambiando solo el id_contrato.
    """

    cur.execute(f"PRAGMA table_info({tabla})")
    columnas = [c[1] for c in cur.fetchall()]

    columnas_sin_id = [c for c in columnas if c != "id_contrato"]

    cur.execute(
        f"""
        SELECT {",".join(columnas_sin_id)}
        FROM {tabla}
        WHERE id_contrato = ?
        """,
        (id_contrato,),
    )
    valores = list(cur.fetchone())

    placeholders = ",".join(["?"] * len(columnas_sin_id))
    columnas_sql = ",".join(columnas_sin_id)

    cur.execute(
        f"""
        INSERT INTO {tabla} (id_contrato, {columnas_sql})
        VALUES (?, {placeholders})
        """,
        (nuevo_id, *valores),
    )


# ============================================================
#  CREACIÓN DE SUPLEMENTO NUEVO
# ============================================================
def crear_suplemento_nuevo(datos_actualizados: dict):
    """
    Crea un suplemento nuevo:
    - Inserta en contratos_identificacion
    - Duplica energia y gastos
    - Actualiza suplemento anterior
    - Marca facturas afectadas
    """

    conn = get_conn()
    cur = conn.cursor()

    id_ant = datos_actualizados["id_contrato"]
    ncontrato = datos_actualizados["ncontrato"]

    # Obtener suplemento anterior
    cur.execute(
        """
        SELECT suplemento, efec_suple, fin_suple, fec_final
        FROM contratos_identificacion
        WHERE id_contrato = ?
        """,
        (id_ant,),
    )
    sup_ant, efec_ant, fin_ant, fec_final_contrato = cur.fetchone()

    sup_nuevo = sup_ant + 1

    # ------------------------------------------------------------
    # 1. Crear nuevo registro en contratos_identificacion
    # ------------------------------------------------------------
    cur.execute(
        """
        INSERT INTO contratos_identificacion (
            ncontrato, suplemento, compania, codigo_postal,
            fec_inicio, fec_final, efec_suple, fin_suple,
            fec_anulacion, estado
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datos_actualizados["ncontrato"],
            sup_nuevo,
            datos_actualizados["compania"],
            datos_actualizados["codigo_postal"],
            datos_actualizados["fec_inicio"],
            datos_actualizados["fec_final"],
            datos_actualizados["efec_suple"],
            fec_final_contrato,  # fin_suple del nuevo suplemento
            datos_actualizados["fec_anulacion"],
            "Activo",
        ),
    )

    nuevo_id = cur.lastrowid

    # 2. Insertar energía con los valores nuevos
    cur.execute(
        """
        INSERT INTO contratos_energia (
            id_contrato, ppunta, pvalle,
            pv_ppunta, pv_pvalle,
            pv_conpunta, pv_conllano, pv_convalle,
            vertido, pv_excedent
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            nuevo_id,
            datos_actualizados["ppunta"],
            datos_actualizados["pvalle"],
            datos_actualizados["pv_ppunta"],
            datos_actualizados["pv_pvalle"],
            datos_actualizados["pv_conpunta"],
            datos_actualizados["pv_conllano"],
            datos_actualizados["pv_convalle"],
            datos_actualizados["vertido"],
            datos_actualizados["pv_excedent"],
        ),
    )

    # 3. Insertar gastos con los valores nuevos
    cur.execute(
        """
        INSERT INTO contratos_gastos (
            id_contrato, bono_social, alq_contador,
            otros_gastos, i_electrico, iva
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            nuevo_id,
            datos_actualizados["bono_social"],
            datos_actualizados["alq_contador"],
            datos_actualizados["otros_gastos"],
            datos_actualizados["i_electrico"],
            datos_actualizados["iva"],
        ),
    )

    # ------------------------------------------------------------
    # 3. Actualizar suplemento anterior
    # ------------------------------------------------------------
    fecha_fin_ant = (
        datetime.strptime(datos_actualizados["efec_suple"], "%Y-%m-%d")
        - timedelta(days=1)
    ).strftime("%Y-%m-%d")

    cur.execute(
        """
        UPDATE contratos_identificacion
        SET fin_suple = ?, estado = 'Modificado'
        WHERE id_contrato = ?
        """,
        (fecha_fin_ant, id_ant),
    )

    # ------------------------------------------------------------
    # 4. Marcar facturas afectadas
    # ------------------------------------------------------------
    marcar_facturas_para_recalculo(
        cur,
        ncontrato,
        datos_actualizados["efec_suple"],
        fec_final_contrato,
    )

    conn.commit()

    return nuevo_id


# ============================================================
#  ACTUALIZAR SUPLEMENTO VIGENTE (solo cambios administrativos)
# ============================================================
def actualizar_suplemento_vigente(datos_actualizados: dict):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE contratos_identificacion
        SET compania = ?, codigo_postal = ?
        WHERE id_contrato = ?
        """,
        (
            datos_actualizados["compania"],
            datos_actualizados["codigo_postal"],
            datos_actualizados["id_contrato"],
        ),
    )

    conn.commit()


# ============================================================
#  MARCAR FACTURAS PARA RECÁLCULO
# ============================================================
def marcar_facturas_para_recalculo(
    cur, ncontrato, efec_suple_nuevo, fec_final_contrato
):
    """
    Marca facturas cuyo inicio_factura está dentro del rango del nuevo suplemento
    y que ya tengan cálculo previo.
    """

    cur.execute(
        """
        UPDATE facturas
        SET recalcular = 1
        WHERE id_contrato IN (
            SELECT id_contrato
            FROM contratos_identificacion
            WHERE ncontrato = ?
        )
        AND inicio_factura >= ?
        AND inicio_factura <= ?
        AND nfactura IN (
            SELECT id_factura
            FROM factura_calculos
        )
        """,
        (ncontrato, efec_suple_nuevo, fec_final_contrato),
    )
