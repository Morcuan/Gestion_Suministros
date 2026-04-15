# -------------------------------------------------------------#
# Módulo: recalculo_test.py                                    #
# Descripción: Recalculo completo de facturas_test usando      #
#              el contrato ficticio y escribiendo en tablas    #
#              de simulación (factura_calculos_test, saldo...) #
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
)


# -------------------------------------------------------------
# Leer datos de facturas_test
# -------------------------------------------------------------
def obtener_datos_factura_test(cursor, nfactura):
    cursor.execute(
        """
        SELECT nfactura, inicio_factura, fin_factura, dias_factura,
               fec_emision, consumo_punta, consumo_llano, consumo_valle,
               excedentes, importe_compensado, servicios, dcto_servicios,
               saldos_pendientes, bat_virtual, recalcular, estado,
               rectifica_a, ncontrato, suplemento
        FROM facturas_test
        WHERE nfactura = ?
    """,
        (nfactura,),
    )
    row = cursor.fetchone()

    if not row:
        return None

    cols = [
        "nfactura",
        "inicio_factura",
        "fin_factura",
        "dias_factura",
        "fec_emision",
        "consumo_punta",
        "consumo_llano",
        "consumo_valle",
        "excedentes",
        "importe_compensado",
        "servicios",
        "dcto_servicios",
        "saldos_pendientes",
        "bat_virtual",
        "recalcular",
        "estado",
        "rectifica_a",
        "ncontrato",
        "suplemento",
    ]

    return dict(zip(cols, row))


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
            servicios.total_servicios,
            iva.total_iva,
            aplicado_cloud,
            nuevo_saldo,
            iva.total_con_iva,
            detalles_json,
            datos_base["bono_social"],
            datos_base["alq_contador"],
            datos_base["otros_gastos"],
            datos_base["i_electrico"],
            datos_base["iva"],
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

    # 2) Obtener facturas_test
    cursor.execute("SELECT nfactura FROM facturas_test ORDER BY fec_emision ASC")
    pendientes = [row[0] for row in cursor.fetchall()]

    if not pendientes:
        return {"total": 0, "procesadas": 0, "errores": []}

    # 3) Limpiar solo el saldo, NO los cálculos históricos
    cursor.execute("DELETE FROM saldo_cloud_test")
    cursor.execute(
        "INSERT INTO saldo_cloud_test (ncontrato, saldo) VALUES (?, 0)",
        (ncontrato_test,),
    )

    errores = []
    procesadas = 0

    # 4) Recalcular TODAS las facturas_test
    for nfactura in pendientes:
        try:
            datos = obtener_datos_factura_test(cursor, nfactura)
            if not datos:
                errores.append(f"{nfactura}: datos no encontrados")
                continue

            # Forzar contrato ficticio
            datos["ncontrato"] = ncontrato_test

            # 1) Cargos
            cargos = calcular_cargos_para_factura(datos)

            # 2) Energía
            energia, datos_base = calcular_energia_para_factura(
                cursor,
                nfactura,
                cargos.bono_social,
            )

            # ---------------------------------------------------------
            # 🔥 DEBUG: VER QUÉ PASA CON LOS VALORES HISTÓRICOS
            # ---------------------------------------------------------
            print("\n--- DEBUG RECALCULO TEST ---")
            print("Buscando valores históricos para nfactura:", nfactura)

            cursor.execute("SELECT nfactura FROM factura_calculos_test")
            print("Facturas presentes en factura_calculos_test:", cursor.fetchall())

            # ---------------------------------------------------------
            # 🔥 LEER VALORES HISTÓRICOS DESDE factura_calculos REAL
            # ---------------------------------------------------------
            cursor.execute(
                """
                SELECT bono_social, alq_contador, otros_gastos, i_electrico, iva
                FROM factura_calculos
                WHERE nfactura = ?
                """,
                (nfactura,),
            )
            row = cursor.fetchone()

            print("Resultado SELECT valores históricos:", row)

            if row:
                datos_base["bono_social"] = row[0]
                datos_base["alq_contador"] = row[1]
                datos_base["otros_gastos"] = row[2]
                datos_base["i_electrico"] = row[3]
                datos_base["iva"] = row[4]
            else:
                errores.append(
                    f"{nfactura}: no hay datos históricos en factura_calculos"
                )
                continue

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

            # 6) Bono Solar Cloud (test)
            total_final, aplicado_cloud, nuevo_saldo = calcular_bono_solar_cloud(
                cursor,
                ncontrato_test,
                total_con_saldos,
                energia.sobrante_excedentes,
            )

            # 7) JSON
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
