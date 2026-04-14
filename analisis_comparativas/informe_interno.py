#!/usr/bin/env python3
# -------------------------------------------------------------#
# Módulo: informe_interno.py                                   #
# Descripción: Genera HTML para la comparativa interna         #
# Autor: Antonio                                               #
# Fecha: 2026-04-13                                            #
# Versión: 2.0                                                 #
# -------------------------------------------------------------#

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


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


def _tabla_html(headers, filas):
    th = "".join(f"<th>{h}</th>" for h in headers)
    trs = []
    for fila in filas:
        tds = "".join(f"<td>{v}</td>" for v in fila)
        trs.append(f"<tr>{tds}</tr>")
    return f"""
    <table>
      <thead><tr>{th}</tr></thead>
      <tbody>
        {''.join(trs)}
      </tbody>
    </table>
    """


def generar_html_comparativa_interna(conn):
    cursor = conn.cursor()

    cursor.execute(SQL_DIFERENCIAS)
    difs = cursor.fetchall()

    cursor.execute(SQL_DIVERGENCIAS)
    divergencias = cursor.fetchall()

    cursor.execute(SQL_DETALLE)
    detalle = cursor.fetchall()

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = f"""
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: Arial, sans-serif; font-size: 10pt; }}
        h1, h2 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 16px; }}
        th, td {{ border: 1px solid #ccc; padding: 4px 6px; text-align: right; }}
        th:first-child, td:first-child {{ text-align: left; }}
        thead {{ background-color: #f0f0f0; }}
      </style>
    </head>
    <body>
      <h1>Informe comparativa interna</h1>
      <p>Generado: {ahora}</p>
    """

    if difs:
        html += "<h2>Diferencias (ordenadas por impacto)</h2>"
        html += _tabla_html(
            ["Factura", "Real (€)", "Test (€)", "Dif (€)"],
            difs,
        )
    else:
        html += "<p>No hay datos para comparar.</p>"

    html += "<h2>Divergencias significativas (≥ 0,01 €)</h2>"
    if divergencias:
        html += _tabla_html(
            ["Factura", "Real (€)", "Test (€)", "Dif (€)"],
            divergencias,
        )
    else:
        html += "<p>No hay divergencias significativas. El motor nuevo es estable.</p>"

    html += "<h2>Detalle por bloques</h2>"
    html += _tabla_html(
        [
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
        detalle,
    )

    html += "</body></html>"
    return html
