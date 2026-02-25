# --------------------------------------------------
# lista_contratos.py
# Función para obtener la lista de contratos desde
#  la base de datos
# Autor: Antonio Morales
# Fecha: 26/02/2026
# ---------//-----------------------------------------


def obtener_lista_contratos(
    conn,
    solo_activos=False,
    solo_ultimo_suplemento=True,
    excluir_anulados=False,
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

    if ncontrato is not None:
        query += " AND ncontrato = ?"
        params.append(ncontrato)

    if solo_activos:
        query += " AND estado = 'Activo'"

    if excluir_anulados:
        query += " AND fec_anulacion IS NULL"

    if not incluir_anulados:
        query += " AND fec_anulacion IS NULL"

    query += " ORDER BY ncontrato, suplemento"

    cursor.execute(query, params)
    registros = cursor.fetchall()

    if solo_ultimo_suplemento:
        ultimos = {}
        for r in registros:
            id_contrato = r[0]
            suplemento = r[2]
            if id_contrato not in ultimos or suplemento > ultimos[id_contrato][2]:
                ultimos[id_contrato] = r
        registros = list(ultimos.values())

    return registros
