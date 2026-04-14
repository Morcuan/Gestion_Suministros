#!/usr/bin/env python3
# -------------------------------------------------------------#
# Módulo: crear_entorno_interno.py                             #
# Descripción: Genera tablas y vistas internas para pruebas    #
# Autor: Antonio                                               #
# Fecha: 2026-04-13                                            #
# Versión: 2.0                                                 #
# -------------------------------------------------------------#

import logging

logger = logging.getLogger(__name__)


def crear_entorno_interno(conn):
    cursor = conn.cursor()

    logger.info("Creando entorno interno")

    tablas = [
        ("facturas_test", "facturas"),
        ("factura_calculos_test", "factura_calculos"),
        ("saldo_cloud_test", "saldo_cloud"),
    ]

    for tabla_test, tabla_real in tablas:
        logger.debug(f"Creando tabla {tabla_test}")
        cursor.execute(f"DROP TABLE IF EXISTS {tabla_test};")
        cursor.execute(f"CREATE TABLE {tabla_test} AS SELECT * FROM {tabla_real};")

    logger.debug("Creando vista v_datos_calculo_test")

    cursor.execute("DROP VIEW IF EXISTS v_datos_calculo_test;")

    cursor.execute(
        """
        CREATE VIEW v_datos_calculo_test AS
            SELECT
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
                ci.id_contrato,
                ci.efec_suple,
                ci.fin_suple,
                ce.ppunta,
                ce.pv_ppunta,
                ce.pvalle,
                ce.pv_pvalle,
                ce.pv_conpunta,
                ce.pv_conllano,
                ce.pv_convalle,
                ce.pv_excedent,
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
    logger.info("Entorno interno creado correctamente")
