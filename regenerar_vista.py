# ------------------------------------------------------#
# Modulo: regenerar_vista.py                            #
# Descripción: Regenera únicamente la vista_contratos   #
# Autor: Antonio Morales                                #
# Fecha: 2026-01-11                                     #
# ------------------------------------------------------#

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "almacen.db")

VISTA_SQL = """
DROP VIEW IF EXISTS vista_contratos;

CREATE VIEW vista_contratos AS
SELECT
    c.numero_contrato,
    co.nombre AS comercializadora,
    printf('%05d', c.codigo_postal) AS codigo_postal,
    cp.poblacion,
    strftime('%d/%m/%Y', c.fecha_inicio) AS fecha_inicio,
    strftime('%d/%m/%Y', c.fecha_final) AS fecha_final,

    CASE
        WHEN ult.estado = 'ANULADO' THEN 'ANULADO'
        WHEN date(c.fecha_inicio) > date('now') THEN 'PENDIENTE'
        WHEN date(c.fecha_final) < date('now') THEN 'CADUCADO'
        ELSE 'ACTIVO'
    END AS estado_actual,

    c.potencia_punta,
    c.importe_potencia_punta,
    c.potencia_valle,
    c.importe_potencia_valle,
    c.importe_consumo_punta,
    c.importe_consumo_llano,
    c.importe_consumo_valle,
    CASE c.vertido WHEN 1 THEN 'SI' ELSE 'NO' END AS vertido,
    c.importe_excedentes,
    c.importe_bono_social,
    c.importe_alquiler_contador,
    c.importe_asistente_smart,
    c.impuesto_electricidad,
    c.iva

FROM contratos c
LEFT JOIN companias co ON co.id_compania = c.id_compania
LEFT JOIN cpostales cp ON cp.codigo_postal = c.codigo_postal

LEFT JOIN (
    SELECT numero_contrato, estado
    FROM contratos_estados
    WHERE fecha_modificacion = (
        SELECT MAX(fecha_modificacion)
        FROM contratos_estados ce2
        WHERE ce2.numero_contrato = contratos_estados.numero_contrato
    )
) AS ult ON ult.numero_contrato = c.numero_contrato;
"""


def main():
    print("Regenerando vista_contratos...")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.executescript(VISTA_SQL)
        conn.commit()
        print("Vista regenerada correctamente.")
    except Exception as e:
        print(f"Error regenerando la vista: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
