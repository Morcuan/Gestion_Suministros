#!/usr/bin/env python3
# -------------------------------------------------------------#
# Módulo: recalculo_interno.py                                 #
# Descripción: Recalcula facturas internas usando el motor     #
#              nuevo y guarda resultados en tablas *_test.     #
# Autor: Antonio (Gestion_Suministros)                         #
# Fecha: 2026-04-13                                            #
# Versión: 2.0                                                 #
# Notas:                                                       #
#   - Sustituye todos los prints por logger para evitar ruido  #
#     en terminal o en ejecución desde menú.                   #
#   - Solo el mensaje final se imprime para el usuario.        #
# -------------------------------------------------------------#

import logging

from facturas.calculo import VERSION_MOTOR, registrar_version_motor
from utilidades.motor_calculo import motor_calculo

logger = logging.getLogger(__name__)


def obtener_facturas_pendientes(cursor):
    cursor.execute(
        """
        SELECT nfactura
        FROM facturas_test
        WHERE recalcular = 1
        ORDER BY fec_emision ASC
        """
    )
    return [row[0] for row in cursor.fetchall()]


def obtener_datos_para_factura(cursor, nfactura):
    cursor.execute(
        """
        SELECT *
        FROM v_datos_calculo_test
        WHERE nfactura = ?
        """,
        (nfactura,),
    )
    row = cursor.fetchone()
    if not row:
        return None

    columnas = [d[0] for d in cursor.description]
    return dict(zip(columnas, row))


def obtener_saldo_cloud(cursor, id_contrato):
    cursor.execute(
        """
        SELECT saldo
        FROM saldo_cloud_test
        WHERE id_contrato = ?
        """,
        (id_contrato,),
    )
    row = cursor.fetchone()
    return row[0] if row else 0.0


def guardar_saldo_cloud(cursor, id_contrato, nuevo_saldo):
    cursor.execute(
        """
        INSERT INTO saldo_cloud_test (id_contrato, saldo)
        VALUES (?, ?)
        ON CONFLICT(id_contrato)
        DO UPDATE SET saldo = excluded.saldo
        """,
        (id_contrato, nuevo_saldo),
    )


def guardar_calculo(cursor, nfactura, resultado, version_motor):
    cursor.execute("DELETE FROM factura_calculos_test WHERE nfactura = ?", (nfactura,))
    cursor.execute(
        """
        INSERT INTO factura_calculos_test (
            nfactura, fecha_calculo, version_motor,
            total_energia, total_cargos, total_servicios,
            total_iva, cloud_aplicado, cloud_sobrante,
            total_final, detalles_json
        )
        VALUES (?, DATE('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            nfactura,
            version_motor,
            resultado["energia"].total_energia,
            resultado["cargos"].total_cargos,
            resultado["servicios"].total_servicios_otros,
            resultado["iva"].cuota_iva,
            resultado["cloud_aplicado"],
            resultado["cloud_sobrante"],
            resultado["total_final"],
            resultado["json"],
        ),
    )


def marcar_factura_recalculada(cursor, nfactura):
    cursor.execute(
        """
        UPDATE facturas_test
        SET recalcular = 0
        WHERE nfactura = ?
        """,
        (nfactura,),
    )


def recalcular_facturas_interno(conn):
    cursor = conn.cursor()

    # Registrar versión del motor
    registrar_version_motor(cursor)
    logger.info(f"Versión del motor registrada: {VERSION_MOTOR}")

    pendientes = obtener_facturas_pendientes(cursor)
    logger.info(f"Facturas pendientes de recálculo: {len(pendientes)}")

    if not pendientes:
        logger.info("No hay facturas pendientes de recálculo interno.")
        return {
            "total": 0,
            "procesadas": 0,
            "errores": [],
            "mensaje": "No hay facturas pendientes de recálculo (INTERNO).",
        }

    errores = []
    procesadas = 0

    for nfactura in pendientes:
        try:
            datos = obtener_datos_para_factura(cursor, nfactura)
            if not datos:
                errores.append(f"{nfactura}: datos no encontrados")
                logger.warning(f"Factura {nfactura}: datos no encontrados")
                continue

            id_contrato = datos["ncontrato"]
            saldo_actual = obtener_saldo_cloud(cursor, id_contrato)

            resultado = motor_calculo(datos, saldo_actual)

            guardar_saldo_cloud(cursor, id_contrato, resultado["nuevo_saldo"])
            guardar_calculo(cursor, nfactura, resultado, VERSION_MOTOR)
            marcar_factura_recalculada(cursor, nfactura)

            procesadas += 1
            logger.debug(f"Factura {nfactura} recalculada correctamente")

        except Exception as e:
            errores.append(f"{nfactura}: {str(e)}")
            logger.error(f"Error recalculando {nfactura}: {str(e)}")

    conn.commit()

    logger.info("Recalculo interno finalizado")

    return {
        "total": len(pendientes),
        "procesadas": procesadas,
        "errores": errores,
        "mensaje": "Recalculo INTERNO finalizado.",
    }
