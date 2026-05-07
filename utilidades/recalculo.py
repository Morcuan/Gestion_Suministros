# -------------------------------------------------------------#
# Módulo: recalculo.py                                         #
# Descripción: Recalculo masivo de facturas con flag pendiente #
# Autor: Antonio Morales                                       #
# Fecha: 2026-04                                               #
# Notas:
#   - Alineado con el motor oficial facturas.calculo (v2.0.0)
#   - Sin motor paralelo en utilidades                         #
# -------------------------------------------------------------#

from facturas.calculo import (
    VERSION_MOTOR,
    calcular_bono_solar_cloud,
    calcular_cargos_para_factura,
    calcular_energia_para_factura,
    calcular_iva_para_factura,
    calcular_saldos_pendientes,
    calcular_servicios_para_factura,
    generar_json_calculo,
    guardar_calculo_factura,
    obtener_datos_factura,
)


def obtener_facturas_pendientes(cursor):
    cursor.execute("""
        SELECT nfactura
        FROM facturas
        WHERE recalcular = 1
        ORDER BY fec_emision ASC
        """)
    return [row[0] for row in cursor.fetchall()]


def marcar_factura_recalculada(cursor, nfactura):
    cursor.execute(
        "UPDATE facturas SET recalcular = 0 WHERE nfactura = ?",
        (nfactura,),
    )


def recalcular_facturas(conn):
    """
    Proceso completo de recálculo masivo de facturas con flag 'recalcular = 1'.

    Utiliza el mismo motor y los mismos bloques que el cálculo individual:
    - facturas.calculo (VERSION_MOTOR 2.0.0)
    """

    cursor = conn.cursor()

    pendientes = obtener_facturas_pendientes(cursor)

    if not pendientes:
        return {
            "total": 0,
            "procesadas": 0,
            "errores": [],
            "mensaje": "No hay facturas pendientes de recálculo.",
        }

    errores = []
    procesadas = 0

    for nfactura in pendientes:
        try:
            # -------------------------------------------------
            # 1) Datos base de la factura
            # -------------------------------------------------
            datos = obtener_datos_factura(cursor, nfactura)
            if not datos:
                errores.append(f"{nfactura}: datos no encontrados")
                continue

            id_contrato = datos["ncontrato"]

            # -------------------------------------------------
            # 2) Cargos normativos
            # -------------------------------------------------
            cargos = calcular_cargos_para_factura(datos)

            # -------------------------------------------------
            # 3) Energía (usa datos de la vista y bono_social)
            #    Devuelve objeto Energia y (de nuevo) datos_base
            # -------------------------------------------------
            energia, datos_base = calcular_energia_para_factura(
                cursor,
                nfactura,
                cargos.bono_social,
            )

            # -------------------------------------------------
            # 4) Servicios y otros conceptos
            # -------------------------------------------------
            servicios = calcular_servicios_para_factura(datos_base)

            # -------------------------------------------------
            # 5) IVA
            # -------------------------------------------------
            iva = calcular_iva_para_factura(
                energia,
                cargos,
                servicios,
                datos_base,
            )

            # -------------------------------------------------
            # 6) Saldos pendientes
            # -------------------------------------------------
            saldos, total_con_saldos = calcular_saldos_pendientes(
                datos_base,
                iva.total_con_iva,
            )

            # -------------------------------------------------
            # 7) Bono Solar Cloud
            #    (lee y guarda saldo_cloud internamente)
            # -------------------------------------------------
            total_final, aplicado_cloud, nuevo_saldo = calcular_bono_solar_cloud(
                cursor,
                id_contrato,
                total_con_saldos,
                energia.sobrante_excedentes,
            )

            # -------------------------------------------------
            # 8) JSON ampliado del cálculo
            # -------------------------------------------------
            detalles_json = generar_json_calculo(
                energia,
                cargos,
                servicios,
                iva,
                saldos,
                aplicado_cloud,
                nuevo_saldo,
                datos_base,
            )

            # -------------------------------------------------
            # 9) Guardado final en factura_calculos
            # -------------------------------------------------
            guardar_calculo_factura(
                cursor,
                nfactura,
                VERSION_MOTOR,
                energia,
                cargos,
                servicios,
                iva,
                saldos,
                aplicado_cloud,
                nuevo_saldo,
                detalles_json,
                datos_base,
            )

            # -------------------------------------------------
            # 10) Marcar factura como recalculada
            # -------------------------------------------------
            marcar_factura_recalculada(cursor, nfactura)

            procesadas += 1

        except Exception as e:
            errores.append(f"{nfactura}: {str(e)}")

    conn.commit()

    return {
        "total": len(pendientes),
        "procesadas": procesadas,
        "errores": errores,
        "mensaje": "Proceso de recálculo finalizado.",
    }
