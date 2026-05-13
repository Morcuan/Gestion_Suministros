#!/usr/bin/env python3
# -------------------------------------------------------------#
# Módulo: crear_entorno_interno.py (versión segura)            #
# Descripción: Prepara el entorno interno SIN destruir datos   #
# Autor: Antonio                                               #
# Fecha: 2026-05-13                                            #
# Versión: 2.2 (vista corregida)                               #
# -------------------------------------------------------------#

import logging

logger = logging.getLogger(__name__)

TABLAS_TEST = [
    "facturas_test",
    "factura_calculos_test",
    "saldo_cloud_test",
    "contratos_identificacion_test",
    "contratos_energia_test",
    "contratos_gastos_test",
]


def tabla_existe(cursor, nombre):
    cursor.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?;
    """,
        (nombre,),
    )
    return cursor.fetchone() is not None


def crear_entorno_interno(conn):
    cursor = conn.cursor()
    logger.info("Preparando entorno interno (modo seguro)")

    # ---------------------------------------------------------
    # 1. Verificar que TODAS las tablas test existen
    # ---------------------------------------------------------
    tablas_faltantes = []

    for tabla in TABLAS_TEST:
        if not tabla_existe(cursor, tabla):
            tablas_faltantes.append(tabla)

    if tablas_faltantes:
        logger.warning("⚠️ Las siguientes tablas test NO existen:")
        for t in tablas_faltantes:
            logger.warning(f"   - {t}")

        logger.warning("El entorno interno NO se recrea automáticamente.")
        logger.warning("Debes ejecutar un proceso de inicialización manual.")
        conn.commit()
        return "Entorno interno incompleto (faltan tablas test)"

    logger.info("✔️ Todas las tablas test existen. No se recrean.")

    # ---------------------------------------------------------
    # 2. Recrear la vista v_datos_calculo_test (seguro y necesario)
    # ---------------------------------------------------------
    logger.info("Recreando vista v_datos_calculo_test")

    cursor.execute("DROP VIEW IF EXISTS v_datos_calculo_test;")

    cursor.execute("""
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
            JOIN contratos_identificacion_test ci
                ON ci.ncontrato = fa.ncontrato
               AND fa.inicio_factura BETWEEN ci.efec_suple AND ci.fin_suple
            JOIN contratos_energia_test ce
                ON ce.id_contrato = ci.id_contrato
            JOIN contratos_gastos_test cg
                ON cg.id_contrato = ci.id_contrato;
        """)

    conn.commit()
    logger.info("✔️ Entorno interno preparado correctamente (modo seguro)")

    return "Entorno interno preparado (sin recrear tablas test)"
