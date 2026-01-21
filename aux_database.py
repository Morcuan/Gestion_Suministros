# --------------------------------------------------#
# Modulo: aux_database.py                           #
# Descripción: Funciones auxiliares para la BD      #
# Autor: Antonio Morales                             #
# Fecha: 2025-12-01                                  #
# --------------------------------------------------#

from datetime import date, datetime

from aux_fechas import a_iso, hoy_iso
from base_bd import BaseBD

# Instancia centralizada de la BD
bd = BaseBD("data/almacen.db")


# -------------------------------------------------------------#
# Funciones auxiliares (fechas, estado, etc.)                  #
# -------------------------------------------------------------#


def parse_fecha(fecha):
    """
    Convierte una fecha en str o date a datetime.date.
    Usa a_iso() para unificar formatos.
    """
    if isinstance(fecha, date):
        return fecha

    if isinstance(fecha, str):
        iso = a_iso(fecha)
        if iso:
            return datetime.strptime(iso, "%Y-%m-%d").date()

    raise ValueError(f"Formato de fecha no reconocido: {fecha}")


# -------------------------------------------------------------#
# Funciones de conexión y pruebas                              #
# -------------------------------------------------------------#


def test_conexion():
    try:
        bd.consultar("SELECT 1")
        return True
    except Exception:
        return False


def conectar():
    """Alias para compatibilidad con código antiguo."""
    return bd


# -------------------------------------------------------------#
# Consultas auxiliares                                          #
# -------------------------------------------------------------#


def listar_companias():
    sql = "SELECT id_compania, nombre FROM companias ORDER BY nombre"
    return bd.consultar(sql)


# -------------------------------------------------------------#
# Inserción y actualización de contratos                        #
# -------------------------------------------------------------#


def insertar_contrato(tupla):
    sql = """
        INSERT INTO contratos (
            id_compania, id_postal, numero_contrato,
            fecha_inicio, fecha_final,
            potencia_punta, importe_potencia_punta, potencia_valle,
            importe_potencia_valle, importe_consumo_punta,
            importe_consumo_llano, importe_consumo_valle, vertido,
            importe_excedentes, importe_bono_social,
            importe_alquiler_contador, importe_asistente_smart,
            impuesto_electricidad, iva
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    bd.ejecutar(sql, tupla)


def actualizar_contrato(datos):
    sql = """
        UPDATE contratos
        SET id_compania = ?,
            id_postal = ?,
            numero_contrato = ?,
            fecha_inicio = ?,
            fecha_final = ?,
            potencia_punta = ?,
            importe_potencia_punta = ?,
            potencia_valle = ?,
            importe_potencia_valle = ?,
            importe_consumo_punta = ?,
            importe_consumo_llano = ?,
            importe_consumo_valle = ?,
            vertido = ?,
            importe_excedentes = ?,
            importe_bono_social = ?,
            importe_alquiler_contador = ?,
            importe_asistente_smart = ?,
            impuesto_electricidad = ?,
            iva = ?
        WHERE numero_contrato = ?
    """
    bd.ejecutar(sql, datos)


# -------------------------------------------------------------#
# Consultas de contratos                                        #
# -------------------------------------------------------------#


def listar_contratos():
    sql = "SELECT * FROM vista_contratos ORDER BY fecha_inicio DESC"
    return bd.consultar(sql)


def listar_contratos_activos():
    sql = "SELECT * FROM vista_contratos WHERE estado_actual = 'ACTIVO'"
    return bd.consultar(sql)


def listar_contratos_por_compania(id_compania):
    sql = "SELECT * FROM vista_contratos WHERE id_compania = ?"
    return bd.consultar(sql, (id_compania,))


def obtener_contrato_por_numero(numero):
    sql = """
        SELECT
            numero_contrato,
            comercializadora,
            codigo_postal,
            poblacion,
            fecha_inicio,
            fecha_final,
            estado_actual,
            potencia_punta,
            importe_potencia_punta,
            potencia_valle,
            importe_potencia_valle,
            importe_consumo_punta,
            importe_consumo_llano,
            importe_consumo_valle,
            vertido,
            importe_excedentes,
            importe_bono_social,
            importe_alquiler_contador,
            importe_asistente_smart,
            impuesto_electricidad,
            iva
        FROM vista_contratos
        WHERE numero_contrato = ?
    """
    filas = bd.consultar(sql, (numero,))
    return filas[0] if filas else None


def obtener_contrato_para_edicion(numero_contrato):
    """
    Devuelve datos listos para cargar en NuevoContratoWidget (modo edición).
    Fechas en dd/mm/yyyy.
    """
    sql = """
        SELECT co.id_compania,
               printf('%05d', c.id_postal) AS codigo_postal,
               cp.poblacion,
               c.numero_contrato,
               strftime('%d/%m/%Y', c.fecha_inicio) AS fecha_inicio,
               strftime('%d/%m/%Y', c.fecha_final) AS fecha_final,
               c.potencia_punta,
               c.importe_potencia_punta,
               c.potencia_valle,
               c.importe_potencia_valle,
               c.importe_consumo_punta,
               c.importe_consumo_llano,
               c.importe_consumo_valle,
               c.vertido,
               c.importe_excedentes,
               c.importe_bono_social,
               c.importe_alquiler_contador,
               c.importe_asistente_smart,
               c.impuesto_electricidad,
               c.iva
        FROM contratos c
        JOIN companias co ON c.id_compania = co.id_compania
        JOIN cpostales cp ON c.id_postal = cp.codigo_postal
        WHERE c.numero_contrato = ?
    """
    filas = bd.consultar(sql, (numero_contrato,))
    return filas[0] if filas else None


# -------------------------------------------------------------#
# Consultas auxiliares                                          #
# -------------------------------------------------------------#


def obtener_poblaciones_por_cp(codigo_postal: str):
    sql = "SELECT poblacion FROM cpostales WHERE codigo_postal = ? LIMIT 1"
    filas = bd.consultar(sql, (codigo_postal,))
    return [filas[0][0]] if filas else []


# -------------------------------------------------------------#
# Registro de estados                                           #
# -------------------------------------------------------------#


def registrar_estado_contrato(numero_contrato, estado):
    """
    Inserta un nuevo registro en contratos_estados.
    """
    sql = """
        INSERT INTO contratos_estados (
            numero_contrato, estado, fecha_baja, fecha_modificacion
        ) VALUES (?, ?, ?, ?)
    """
    fecha_iso = hoy_iso()
    bd.ejecutar(sql, (numero_contrato, estado, fecha_iso, fecha_iso))


def anulacion_contrato(numero_contrato):
    registrar_estado_contrato(numero_contrato, "ANULADO")


def rehabilitacion_contrato(numero_contrato):
    registrar_estado_contrato(numero_contrato, "REHABILITADO")


def modificacion_contrato(numero_contrato):
    registrar_estado_contrato(numero_contrato, "MODIFICADO")


# -------------------------------------------------------------#
# Construcción de tuplas                                        #
# -------------------------------------------------------------#


def construir_tupla_contrato(datos: dict) -> tuple:
    return (
        datos.get("id_compania"),
        datos.get("id_postal"),
        datos.get("numero"),
        datos.get("fecha_inicio"),
        datos.get("fecha_final"),
        datos.get("potencia_punta"),
        datos.get("importe_potencia_punta"),
        datos.get("potencia_valle"),
        datos.get("importe_potencia_valle"),
        datos.get("importe_consumo_punta"),
        datos.get("importe_consumo_llano"),
        datos.get("importe_consumo_valle"),
        datos.get("vertido"),
        datos.get("importe_excedentes"),
        datos.get("importe_bono_social"),
        datos.get("importe_alquiler_contador"),
        datos.get("importe_asistente_smart"),
        datos.get("impuesto_electricidad"),
        datos.get("iva"),
    )


def existe_contrato(bd, numero):
    sql = "SELECT 1 FROM contratos WHERE numero_contrato = ? LIMIT 1"
    filas = bd.consultar(sql, (numero,))
    return bool(filas)


def construir_tupla_contrato_edicion(datos: dict, numero_contrato: str) -> tuple:
    return construir_tupla_contrato(datos) + (numero_contrato,)


def obtener_historico_estados(numero_contrato):
    conn = conectar()
    cursor = conn.conn.cursor()

    cursor.execute(
        """
        SELECT fecha_modificacion, estado
        FROM contratos_estados
        WHERE numero_contrato = ?
        ORDER BY fecha_modificacion ASC
        """,
        (numero_contrato,),
    )

    datos = cursor.fetchall()
    return datos


# -------------------------------------------------------------#
# Gestión de instancia BD                                       #
# -------------------------------------------------------------#


def set_bd(instancia):
    global bd
    bd = instancia
