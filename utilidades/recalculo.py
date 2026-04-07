# -------------------------------------------------------------#
# Módulo: recalculo.py                                         #
# Descripción: Recalculo masivo de facturas con flag pendiente #
# Autor: Antonio Morales                                       #
# Fecha: 2026-04                                               #
# -------------------------------------------------------------#

from facturas.calculo import VERSION_MOTOR, registrar_version_motor
from utilidades.motor_calculo import motor_calculo


def obtener_facturas_pendientes(cursor):
    cursor.execute(
        """
        SELECT nfactura
        FROM facturas
        WHERE recalcular = 1
        ORDER BY fec_emision ASC
        """
    )
    return [row[0] for row in cursor.fetchall()]


def obtener_datos_para_factura(cursor, nfactura):
    cursor.execute(
        """
        SELECT *
        FROM v_datos_calculo
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
        "SELECT saldo FROM saldo_cloud WHERE id_contrato = ?", (id_contrato,)
    )
    row = cursor.fetchone()
    return row[0] if row else 0.0


def guardar_saldo_cloud(cursor, id_contrato, nuevo_saldo):
    cursor.execute(
        """
        INSERT INTO saldo_cloud (id_contrato, saldo)
        VALUES (?, ?)
        ON CONFLICT(id_contrato) DO UPDATE SET saldo = excluded.saldo
        """,
        (id_contrato, nuevo_saldo),
    )


def guardar_calculo(cursor, nfactura, resultado, version_motor):
    """
    Inserta el cálculo en factura_calculos.
    """

    cursor.execute("DELETE FROM factura_calculos WHERE nfactura = ?", (nfactura,))

    cursor.execute(
        """
        INSERT INTO factura_calculos (
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
    cursor.execute("UPDATE facturas SET recalcular = 0 WHERE nfactura = ?", (nfactura,))


def recalcular_facturas(conn):
    """
    Proceso completo de recálculo masivo.
    """

    cursor = conn.cursor()

    # Registrar versión del motor si no existe
    registrar_version_motor(cursor)

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
            datos = obtener_datos_para_factura(cursor, nfactura)
            if not datos:
                errores.append(f"{nfactura}: datos no encontrados")
                continue

            id_contrato = datos["ncontrato"]
            saldo_actual = obtener_saldo_cloud(cursor, id_contrato)

            # Motor puro
            resultado = motor_calculo(datos, saldo_actual)

            # Guardar saldo cloud
            guardar_saldo_cloud(cursor, id_contrato, resultado["nuevo_saldo"])

            # Guardar cálculo
            guardar_calculo(cursor, nfactura, resultado, VERSION_MOTOR)

            # Marcar como recalculada
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
