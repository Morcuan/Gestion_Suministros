#!/usr/bin/env python3
# -------------------------------------------------------------#
# Módulo: recalculo_interno.py                                 #
# Descripción: Recalcula facturas internas usando el motor     #
#              oficial y guarda resultados en tablas *_test.   #
# Autor: Antonio (Gestion_Suministros)                         #
# Fecha: 2026-05-13                                            #
# Versión: 2.2 (motor oficial + vista test)                    #
# -------------------------------------------------------------#

import logging

from facturas.calculo import (
    VERSION_MOTOR,
    calcular_bono_solar_cloud,
    calcular_cargos_para_factura,
    calcular_energia_para_factura,
    calcular_iva_para_factura,
    calcular_saldos_pendientes,
    calcular_servicios_para_factura,
    generar_json_calculo,
    registrar_version_motor,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# WRAPPER DEL MOTOR OFICIAL (CORREGIDO)
# ---------------------------------------------------------
def motor_calculo_interno(cursor, nfactura, saldo_actual):
    """
    Ejecuta el motor oficial de cálculo usando la vista TEST
    y devuelve un diccionario con la misma estructura que el motor externo.
    """

    # 1) Obtener datos base desde la vista test
    cursor.execute("SELECT * FROM v_datos_calculo_test WHERE nfactura = ?", (nfactura,))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"No hay datos en vista test para factura {nfactura}")

    columnas = [d[0] for d in cursor.description]
    datos = dict(zip(columnas, row))

    # 2) ENERGÍA
    energia, datos = calcular_energia_para_factura(
        cursor,
        nfactura,
        datos["bono_social"],
    )

    # 3) CARGOS
    cargos = calcular_cargos_para_factura(datos)

    # 4) SERVICIOS
    servicios = calcular_servicios_para_factura(datos)

    # 5) IVA
    iva = calcular_iva_para_factura(energia, cargos, servicios, datos)

    # 6) SALDOS PENDIENTES
    saldos, total_con_saldos = calcular_saldos_pendientes(
        datos,
        iva.total_con_iva,
    )

    # 7) CLOUD
    total_final, aplicado_cloud, nuevo_saldo = calcular_bono_solar_cloud(
        cursor,
        datos["id_contrato"],
        total_con_saldos,
        energia.sobrante_excedentes,
    )

    # 8) JSON
    json_detalles = generar_json_calculo(
        energia,
        cargos,
        servicios,
        iva,
        saldos,
        aplicado_cloud,
        nuevo_saldo,
        datos,
    )

    return {
        "energia": energia,
        "cargos": cargos,
        "servicios": servicios,
        "iva": iva,
        "cloud_aplicado": aplicado_cloud,
        "cloud_sobrante": energia.sobrante_excedentes,
        "nuevo_saldo": nuevo_saldo,
        "total_final": total_final,
        "json": json_detalles,
    }


# ---------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------
def obtener_facturas_pendientes(cursor):
    cursor.execute("""
        SELECT nfactura
        FROM facturas_test
        WHERE recalcular = 1
        ORDER BY fec_emision ASC
        """)
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


# ---------------------------------------------------------
# PROCESO PRINCIPAL
# ---------------------------------------------------------
def recalcular_facturas_interno(conn):
    cursor = conn.cursor()

    registrar_version_motor(cursor)
    logger.info(f"Versión del motor registrada: {VERSION_MOTOR}")

    pendientes = obtener_facturas_pendientes(cursor)
    logger.info(f"Facturas pendientes de recálculo: {len(pendientes)}")

    if not pendientes:
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
                continue

            saldo_actual = obtener_saldo_cloud(cursor, datos["id_contrato"])

            resultado = motor_calculo_interno(cursor, nfactura, saldo_actual)

            guardar_saldo_cloud(cursor, datos["id_contrato"], resultado["nuevo_saldo"])
            guardar_calculo(cursor, nfactura, resultado, VERSION_MOTOR)
            marcar_factura_recalculada(cursor, nfactura)

            procesadas += 1

        except Exception as e:
            errores.append(f"{nfactura}: {str(e)}")

    conn.commit()

    return {
        "total": len(pendientes),
        "procesadas": procesadas,
        "errores": errores,
        "mensaje": "Recalculo INTERNO finalizado.",
    }
