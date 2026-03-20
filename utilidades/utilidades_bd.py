# -------------------------------------------------------------#
# Módulo: utilidades_bd.py                                     #
# Descripción: Funciones generales de acceso a BD              #
# Autor: Antonio Morales                                       #
# Fecha: 2026-02-10                                            #
# -------------------------------------------------------------#

"""
Este módulo contiene funciones generales de acceso a la base de datos.
Todas las funciones reciben la conexión y el cursor desde main.py.
Ninguna función abre ni cierra la conexión.
"""


# -------------------------------------------------------------
# INSERTAR CONTRATO - IDENTIFICACIÓN
# -------------------------------------------------------------
def insertar_contrato_identificacion(cursor, datos):
    """
    Inserta datos en la tabla contratos_identificacion.
    Devuelve el id_contrato generado.
    """
    sql = """
        INSERT INTO contratos_identificacion
        (ncontrato, suplemento, compania, codigo_postal,
         fec_inicio, fec_final, efec_suple, fin_suple, fec_anulacion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(
        sql,
        (
            datos["ncontrato"],
            datos["suplemento"],
            datos["compania"],
            datos["codigo_postal"],
            datos["fec_inicio"],
            datos["fec_final"],
            datos["efec_suple"],
            datos["fin_suple"],
            datos["fec_anulacion"],
        ),
    )

    return cursor.lastrowid


# -------------------------------------------------------------
# INSERTAR CONTRATO - ENERGÍA
# -------------------------------------------------------------
def insertar_contrato_energia(cursor, id_contrato, datos):
    """
    Inserta datos en la tabla contratos_energia.
    """
    sql = """
        INSERT INTO contratos_energia
        (id_contrato, ppunta, pvalle, pv_ppunta, pv_pvalle,
         pv_conpunta, pv_conllano, pv_convalle, vertido, pv_excedentes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(
        sql,
        (
            id_contrato,
            datos["ppunta"],
            datos["pvalle"],
            datos["pv_ppunta"],
            datos["pv_pvalle"],
            datos["pv_conpunta"],
            datos["pv_conllano"],
            datos["pv_convalle"],
            datos["vertido"],
            datos["pv_excedentes"],
        ),
    )

    return True


# -------------------------------------------------------------
# INSERTAR CONTRATO - GASTOS
# -------------------------------------------------------------
def insertar_contrato_gastos(cursor, id_contrato, datos):
    """
    Inserta datos en la tabla contratos_gastos.
    """
    sql = """
        INSERT INTO contratos_gastos
        (id_contrato, bono_social, i_electrico, alq_contador,
         otros_gastos, iva)
        VALUES (?, ?, ?, ?, ?, ?)
    """

    cursor.execute(
        sql,
        (
            id_contrato,
            datos["bono_social"],
            datos["i_electrico"],
            datos["alq_contador"],
            datos["otros_gastos"],
            datos["iva"],
        ),
    )

    return True


# -------------------------------------------------------------
# ORQUESTA LA INSERCIÓN COMPLETA DEL CONTRATO
# -------------------------------------------------------------
def insertar_contrato(conn, cursor, datos_ident, datos_energia, datos_gastos):
    """
    Inserta un contrato completo en las tres tablas.
    """
    id_contrato = insertar_contrato_identificacion(cursor, datos_ident)
    insertar_contrato_energia(cursor, id_contrato, datos_energia)
    insertar_contrato_gastos(cursor, id_contrato, datos_gastos)

    conn.commit()
    return id_contrato


# -------------------------------------------------------------
# OBTENER LISTA DE COMPAÑÍAS
# -------------------------------------------------------------
def obtener_companias(cursor):
    """
    Devuelve una lista de nombres de compañías desde la tabla 'companias'.
    """
    cursor.execute("SELECT nombre FROM companias ORDER BY nombre")
    filas = cursor.fetchall()
    return [f[0] for f in filas]


# -------------------------------------------------------------
# VALIDAR CÓDIGO POSTAL
# -------------------------------------------------------------
def validar_codigo_postal(cursor, codigo_postal):
    """
    Comprueba si el código postal existe en la tabla cpostales.
    Devuelve (True, poblacion) si existe.
    Devuelve (False, None) si no existe.
    """
    cursor.execute("SELECT poblacion FROM cpostales WHERE codigo = ?", (codigo_postal,))
    fila = cursor.fetchone()

    if fila:
        return True, fila[0]
    else:
        return False, None


# -------------------------------------------------------------
# INSERTAR NUEVO CÓDIGO POSTAL
# -------------------------------------------------------------
def insertar_codigo_postal(conn, cursor, codigo_postal, poblacion):
    """
    Inserta un nuevo código postal en la tabla cpostales.
    """
    cursor.execute(
        "INSERT INTO cpostales (codigo, poblacion) VALUES (?, ?)",
        (codigo_postal, poblacion),
    )
    conn.commit()
    return True
