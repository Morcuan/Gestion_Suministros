# --------------------------------------------------
# lista_contratos.py
# Función para obtener la lista de contratos desde
#  la base de datos
# Autor: Antonio Morales
# Fecha: 26/02/2026
# ---------//-----------------------------------------
# Función para obtener la lista de contratos desde la base de datos
# Parámetros:
# - conn: conexión a la base de datos
# - solo_activos: si True, solo devuelve contratos activos
# - solo_ultimo_suplemento: si True, solo devuelve el último suplemento de cada contrato
# - incluir_anulados: si False, excluye contratos anulados
# - ncontrato: si se proporciona, filtra por número de contrato específico

# Devuelve una lista de tuplas con los datos de los contratos
def obtener_lista_contratos(
    conn,
    solo_activos=False,
    solo_ultimo_suplemento=True,
    incluir_anulados=True,
    ncontrato=None,
):
    cursor = conn.cursor()

    query = """
        SELECT
            id_contrato,
            ncontrato,
            suplemento,
            estado,
            compania,
            codigo_postal,
            poblacion,
            fec_inicio,
            fec_final,
            efec_suple,
            fin_suple,
            fec_anulacion,
            ppunta, pv_ppunta, pvalle, pv_pvalle,
            pv_conpunta, pv_conllano, pv_convalle,
            vertido, pv_excedent,
            bono_social, alq_contador, otros_gastos,
            i_electrico, iva
        FROM vista_contratos
        WHERE 1=1
    """

    params = []

    # Filtrar por número de contrato si se proporciona
    if ncontrato is not None:
        query += " AND ncontrato = ?"
        params.append(ncontrato)
    # Filtrar por estado si solo_activos es True
    if solo_activos:
        query += " AND estado = 'Activo'"
    # Excluir contratos anulados si incluir_anulados es False
    if not incluir_anulados:
        query += " AND fec_anulacion IS NULL"

    # Orden correcto: suplemento DESC para que el primero sea el último
    query += " ORDER BY ncontrato, suplemento DESC"
    # Ejecutar la consulta
    cursor.execute(query, params)
    registros = cursor.fetchall()

    # Si solo queremos el último suplemento, filtramos los resultados
    if solo_ultimo_suplemento:
        ultimos = {}
        for r in registros:
            ncontrato = r[1]  # ESTA es la clave correcta
            if ncontrato not in ultimos:
                ultimos[ncontrato] = r
        registros = list(ultimos.values())
    # Devolvemos la lista de contratos
    return registros
