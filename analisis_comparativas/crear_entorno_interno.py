# -------------------------------------------------------------#
# Módulo: crear_entorno_test.py                                #
# Descripción: Crea las tablas y vistas necesarias para el     #
#              entorno de pruebas (facturas_test, etc.)        #
# Autor: Antonio Morales                                       #
# Fecha: 2026-04                                               #
# -------------------------------------------------------------#

import sqlite3


def crear_entorno_test(ruta_bd):
    conn = sqlite3.connect(ruta_bd)
    cursor = conn.cursor()

    print("🧱 Creando entorno de pruebas...")

    # ---------------------------------------------------------
    # 1. Tablas duplicadas
    # ---------------------------------------------------------
    tablas = [
        ("facturas_test", "facturas"),
        ("factura_calculos_test", "factura_calculos"),
        ("saldo_cloud_test", "saldo_cloud"),
    ]

    for tabla_test, tabla_real in tablas:
        print(f"→ Creando tabla {tabla_test}...")
        cursor.execute(f"DROP TABLE IF EXISTS {tabla_test};")
        cursor.execute(f"CREATE TABLE {tabla_test} AS SELECT * FROM {tabla_real};")

    # ---------------------------------------------------------
    # 2. Vista v_datos_calculo_test
    # ---------------------------------------------------------
    print("→ Creando vista v_datos_calculo_test...")

    cursor.execute("DROP VIEW IF EXISTS v_datos_calculo_test;")

    cursor.execute(
        """
        CREATE VIEW v_datos_calculo_test AS
            SELECT
                -- Factura (TEST)
                fa.ncontrato,
                fa.suplemento,
                fa.nfactura,
                fa.inicio_factura,
                fa.fin_factura,
                fa.dias_factura,
                fa.consumo_punta,
                fa.consumo_llano,
                fa.consumo_valle,
                fa.excedentes,
                fa.servicios,
                fa.dcto_servicios,
                fa.saldos_pendientes,
                fa.bat_virtual,

                -- Suplemento correcto
                ci.id_contrato,
                ci.efec_suple,
                ci.fin_suple,

                -- Contratos energía
                ce.ppunta,
                ce.pv_ppunta,
                ce.pvalle,
                ce.pv_pvalle,
                ce.pv_conpunta,
                ce.pv_conllano,
                ce.pv_convalle,
                ce.pv_excedent,

                -- Contratos gastos
                cg.bono_social,
                cg.alq_contador,
                cg.otros_gastos,
                cg.i_electrico,
                cg.iva

            FROM facturas_test fa
            JOIN contratos_identificacion ci
                ON ci.ncontrato = fa.ncontrato
               AND fa.inicio_factura BETWEEN ci.efec_suple AND ci.fin_suple
            JOIN contratos_energia ce
                ON ce.id_contrato = ci.id_contrato
            JOIN contratos_gastos cg
                ON cg.id_contrato = ci.id_contrato;
    """
    )

    conn.commit()
    conn.close()

    print("✅ Entorno de pruebas creado correctamente.")


if __name__ == "__main__":
    # Ajusta la ruta a tu BD real
    crear_entorno_test("data/almacen.db")
