# -------------------------------------------------------------#
# Módulo: recalculo_test.py                                    #
# Descripción: Recalculo completo de facturas_test usando      #
#              el motor calculo_test.py y escribiendo en       #
#              factura_calculos_test y saldo_cloud_test.       #
# -------------------------------------------------------------#

import json

from facturas.calculo_test import (
    VERSION_MOTOR,
    calcular_bono_solar_cloud,
    calcular_cargos_para_factura,
    calcular_energia_para_factura,
    calcular_iva_para_factura,
    calcular_saldos_pendientes,
    calcular_servicios_para_factura,
    generar_json_calculo,
    guardar_saldo_cloud,
    obtener_saldo_cloud,
    registrar_version_motor,
)


# -------------------------------------------------------------
# Obtener datos desde la vista v_datos_calculo_test
# -------------------------------------------------------------
def obtener_datos_factura_test(cursor, nfactura):
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


# -------------------------------------------------------------
# Guardar cálculo en factura_calculos_test
# -------------------------------------------------------------
def guardar_calculo_factura_test(
    cursor,
    nfactura,
    version_motor,
    energia,
    cargos,
    servicios,
    iva,
    saldos,
    aplicado_cloud,
    nuevo_saldo,
    detalles_json,
    datos_base,
):

    # Borrar cálculo previo
    cursor.execute("DELETE FROM factura_calculos_test WHERE nfactura = ?", (nfactura,))

    # Registrar versión del motor TEST
    registrar_version_motor(cursor)

    # Insertar nuevo cálculo
    cursor.execute(
        """
        INSERT INTO factura_calculos_test (
            nfactura,
            fecha_calculo,
            version_motor,
            total_energia,
            total_cargos,
            total_servicios,
            total_iva,
            cloud_aplicado,
            cloud_sobrante,
            total_final,
            detalles_json,
            bono_social,
            alq_contador,
            otros_gastos,
            i_electrico,
            iva
        ) VALUES (?, date('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            nfactura,
            version_motor,
            energia.total_energia,
            cargos.total_cargos,
            servicios.total_servicios_otros,
            iva.cuota_iva,
            aplicado_cloud,
            energia.sobrante_excedentes,
            round(saldos.total_con_saldos - aplicado_cloud, 2),
            detalles_json,
            float(datos_base["bono_social"]),
            float(datos_base["alq_contador"]),
            float(datos_base["otros_gastos"]),
            float(datos_base["i_electrico"]),
            float(datos_base["iva"]),
        ),
    )


# -------------------------------------------------------------
# Recalculo completo de facturas_test
# -------------------------------------------------------------
def recalcular_facturas_test(conn):
    cursor = conn.cursor()

    # 1) Obtener contrato ficticio
    cursor.execute("SELECT ncontrato FROM contratos_identificacion_test LIMIT 1")
    row = cursor.fetchone()
    if not row:
        return {
            "total": 0,
            "procesadas": 0,
            "errores": ["No existe contrato ficticio."],
        }

    ncontrato_test = row[0]

    # 2) Obtener facturas_test en orden cronológico REAL
    cursor.execute("""
        SELECT nfactura
        FROM facturas_test
        ORDER BY inicio_factura ASC
        """)
    pendientes = [row[0] for row in cursor.fetchall()]

    if not pendientes:
        return {"total": 0, "procesadas": 0, "errores": []}

    errores = []
    procesadas = 0

    # 3) Recalcular TODAS las facturas_test
    for nfactura in pendientes:
        try:
            datos = obtener_datos_factura_test(cursor, nfactura)
            if not datos:
                errores.append(f"{nfactura}: datos no encontrados en la vista")
                continue

            # 1) Cargos
            cargos = calcular_cargos_para_factura(datos)

            # 2) Energía
            energia, datos_base = calcular_energia_para_factura(
                cursor,
                nfactura,
                cargos.bono_social,
            )

            # 3) Servicios
            servicios = calcular_servicios_para_factura(datos_base)

            # 4) IVA
            iva = calcular_iva_para_factura(
                energia,
                cargos,
                servicios,
                datos_base,
            )

            # 5) Saldos pendientes
            saldos, total_con_saldos = calcular_saldos_pendientes(
                datos_base,
                iva.total_con_iva,
            )

            # 6) Bono Solar Cloud (motor test)
            total_final, aplicado_cloud, nuevo_saldo = calcular_bono_solar_cloud(
                cursor,
                ncontrato_test,
                total_con_saldos,
                energia.sobrante_excedentes,
            )

            # 7) JSON (motor test)
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

            # 8) Guardar en factura_calculos_test
            guardar_calculo_factura_test(
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

            procesadas += 1

        except Exception as e:
            errores.append(f"{nfactura}: {str(e)}")

    conn.commit()

    return {
        "total": len(pendientes),
        "procesadas": procesadas,
        "errores": errores,
        "mensaje": "Recalculo TEST finalizado.",
    }
