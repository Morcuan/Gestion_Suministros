#!/usr/bin/env python3
# -------------------------------------------------------------#
# Módulo: comparador_interno.py                                #
# Descripción: Compara facturación real vs facturación interna #
# -------------------------------------------------------------#

from tabulate import tabulate

SQL_DIFERENCIAS = """
SELECT
    r.nfactura,
    r.total_final AS total_real,
    t.total_final AS total_test,
    ROUND(t.total_final - r.total_final, 2) AS diferencia
FROM factura_calculos r
JOIN factura_calculos_test t USING (nfactura)
ORDER BY ABS(diferencia) DESC;
"""


SQL_DETALLE = """
SELECT
    r.nfactura,
    r.total_energia AS energia_real,
    t.total_energia AS energia_test,
    ROUND(t.total_energia - r.total_energia, 2) AS dif_energia,
    r.total_cargos AS cargos_real,
    t.total_cargos AS cargos_test,
    ROUND(t.total_cargos - r.total_cargos, 2) AS dif_cargos,
    r.total_servicios AS servicios_real,
    t.total_servicios AS servicios_test,
    ROUND(t.total_servicios - r.total_servicios, 2) AS dif_servicios,
    r.total_iva AS iva_real,
    t.total_iva AS iva_test,
    ROUND(t.total_iva - r.total_iva, 2) AS dif_iva,
    r.cloud_aplicado AS cloud_real,
    t.cloud_aplicado AS cloud_test,
    ROUND(t.cloud_aplicado - r.cloud_aplicado, 2) AS dif_cloud,
    r.total_final AS total_real,
    t.total_final AS total_test,
    ROUND(t.total_final - r.total_final, 2) AS dif_total
FROM factura_calculos r
JOIN factura_calculos_test t USING (nfactura)
ORDER BY ABS(dif_total) DESC;
"""


SQL_DIVERGENCIAS = """
SELECT
    nfactura,
    total_real,
    total_test,
    diferencia
FROM (
    SELECT
        r.nfactura,
        r.total_final AS total_real,
        t.total_final AS total_test,
        ROUND(t.total_final - r.total_final, 2) AS diferencia
    FROM factura_calculos r
    JOIN factura_calculos_test t USING (nfactura)
)
WHERE ABS(diferencia) >= 0.01
ORDER BY ABS(diferencia) DESC;
"""


def comparar_facturacion_interna(conn):
    cursor = conn.cursor()

    print("\n📊 Comparando facturación REAL vs INTERNA...\n")

    cursor.execute(SQL_DIFERENCIAS)
    difs = cursor.fetchall()

    if not difs:
        print("No hay datos para comparar.")
        return

    print("=== DIFERENCIAS (ordenadas por impacto) ===")
    print(
        tabulate(
            difs,
            headers=["Factura", "Real (€)", "Test (€)", "Dif (€)"],
            tablefmt="github",
        )
    )

    cursor.execute(SQL_DIVERGENCIAS)
    divergencias = cursor.fetchall()

    print("\n=== DIVERGENCIAS SIGNIFICATIVAS (>= 0.01 €) ===")
    if divergencias:
        print(
            tabulate(
                divergencias,
                headers=["Factura", "Real (€)", "Test (€)", "Dif (€)"],
                tablefmt="github",
            )
        )
    else:
        print("✔️ No hay divergencias significativas. El motor nuevo es estable.")

    print("\n=== DETALLE POR BLOQUES ===")
    cursor.execute(SQL_DETALLE)
    detalle = cursor.fetchall()

    print(
        tabulate(
            detalle,
            headers=[
                "Factura",
                "Energia R",
                "Energia T",
                "Dif E",
                "Cargos R",
                "Cargos T",
                "Dif C",
                "Serv R",
                "Serv T",
                "Dif S",
                "IVA R",
                "IVA T",
                "Dif IVA",
                "Cloud R",
                "Cloud T",
                "Dif Cloud",
                "Total R",
                "Total T",
                "Dif Total",
            ],
            tablefmt="github",
        )
    )

    print("\n🏁 Comparación finalizada.\n")
