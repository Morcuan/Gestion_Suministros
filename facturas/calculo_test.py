# -------------------------------------------------#
# Módulo: calculo_test.py                          #
# Descripción: Cálculo de facturas de energía      #
# Autor: Antonio Morales                           #
# Versión motor: ver constante VERSION_MOTOR       #
# -------------------------------------------------#

import json
import math

VERSION_MOTOR = "2.0.0"


def registrar_version_motor(cursor) -> None:
    cursor.execute(
        "SELECT 1 FROM version_motor_test WHERE version = ?",
        (VERSION_MOTOR,),
    )
    if cursor.fetchone():
        return

    cursor.execute("""
        UPDATE version_motor_test
        SET fecha_fin = DATE('now', '-1 day')
        WHERE fecha_fin IS NULL
    """)

    cursor.execute(
        """
        INSERT INTO version_motor_test (version, fecha_inicio, fecha_fin)
        VALUES (?, DATE('now'), NULL)
        """,
        (VERSION_MOTOR,),
    )


# ---------------------------------------------------------
# BLOQUE 1: ENERGÍA
# ---------------------------------------------------------
class Energia:

    def __init__(self, datos: dict):
        self.datos = datos
        self.total_potencia = 0.0
        self.total_consumo = 0.0
        self.compensacion_excedentes = 0.0
        self.sobrante_excedentes = 0.0
        self.impuesto_electrico = 0.0
        self.total_energia = 0.0

    def calcular_potencia(self):
        dias = self.datos["dias_factura"]
        p_punta = self.datos["ppunta"] * dias * self.datos["pv_ppunta"]
        p_valle = self.datos["pvalle"] * dias * self.datos["pv_pvalle"]
        self.total_potencia = round(p_punta + p_valle, 2)

    def calcular_consumo(self):
        c_punta = self.datos["consumo_punta"] * self.datos["pv_conpunta"]
        c_llano = self.datos["consumo_llano"] * self.datos["pv_conllano"]
        c_valle = self.datos["consumo_valle"] * self.datos["pv_convalle"]
        self.total_consumo = round(c_punta + c_llano + c_valle, 2)

    def calcular_excedentes(self, limite_por_consumo=True):
        exced_kwh = self.datos["excedentes"]
        precio_exc = self.datos["pv_excedent"]
        importe_excedentes = round(exced_kwh * precio_exc, 2)
        compensacion = -importe_excedentes

        if limite_por_consumo:
            max_compensable = self.total_consumo
            if abs(compensacion) > max_compensable:
                compensacion = -max_compensable

        self.compensacion_excedentes = round(compensacion, 2)
        self.sobrante_excedentes = round(
            importe_excedentes - abs(self.compensacion_excedentes), 2
        )

        if self.sobrante_excedentes < 0:
            self.sobrante_excedentes = 0.0

    def calcular_impuesto_electrico(self, bono_social):
        base = (
            self.total_potencia
            + (self.total_consumo - abs(self.compensacion_excedentes))
            + bono_social
        )
        porcentaje = self.datos["i_electrico"] / 100
        self.impuesto_electrico = round(base * porcentaje, 2)

    def calcular_bloque(self):
        self.total_energia = round(
            self.total_potencia
            + self.total_consumo
            + self.compensacion_excedentes
            + self.impuesto_electrico,
            2,
        )

    def calcular(self, bono_social):
        self.calcular_potencia()
        self.calcular_consumo()
        self.calcular_excedentes()
        self.calcular_impuesto_electrico(bono_social)
        self.calcular_bloque()
        return self


# ---------------------------------------------------------
# BLOQUE 2: CARGOS NORMATIVOS
# ---------------------------------------------------------
class CargosNormativos:

    def __init__(self, datos: dict):
        self.datos = datos
        self.bono_social = 0.0
        self.total_cargos = 0.0

    def calcular_bono_social(self):
        dias = self.datos["dias_factura"]
        importe_diario = self.datos["bono_social"]
        self.bono_social = round(importe_diario * dias, 2)

    def calcular_bloque(self):
        self.total_cargos = round(self.bono_social, 2)

    def calcular(self):
        self.calcular_bono_social()
        self.calcular_bloque()
        return self


# ---------------------------------------------------------
# BLOQUE 3: SERVICIOS Y OTROS
# ---------------------------------------------------------
class ServiciosOtros:

    def __init__(self, datos: dict):
        self.datos = datos
        self.equipos = 0.0
        self.servicios = 0.0
        self.total_servicios_otros = 0.0

    def calcular_equipos(self):
        dias = self.datos["dias_factura"]
        precio_diario = self.datos["alq_contador"]
        self.equipos = round(dias * precio_diario, 2)

    def calcular_servicios(self):
        servicios = self.datos["servicios"]
        descuento = self.datos["dcto_servicios"]
        self.servicios = round(servicios + descuento, 2)

    def calcular_bloque(self):
        self.total_servicios_otros = round(
            self.equipos + self.servicios,
            2,
        )

    def calcular(self):
        self.calcular_equipos()
        self.calcular_servicios()
        self.calcular_bloque()
        return self


# ---------------------------------------------------------
# BLOQUE 4: IVA
# ---------------------------------------------------------
class IVA:

    def __init__(self, base_imponible: float, tipo_iva_porcentaje: float):
        self.base_imponible = round(base_imponible, 2)
        self.tipo_iva = float(tipo_iva_porcentaje) / 100
        self.cuota_iva = 0.0
        self.total_con_iva = 0.0

    def calcular_iva(self):
        self.cuota_iva = round(self.base_imponible * self.tipo_iva, 2)
        self.total_con_iva = round(self.base_imponible + self.cuota_iva, 2)

    def calcular(self):
        self.calcular_iva()
        return {
            "base_imponible": self.base_imponible,
            "tipo_iva": self.tipo_iva,
            "cuota_iva": self.cuota_iva,
            "total_con_iva": self.total_con_iva,
        }


# ---------------------------------------------------------
# BLOQUE 5: SALDOS PENDIENTES
# ---------------------------------------------------------
class SaldosPendientes:

    def __init__(self, datos: dict):
        self.datos = datos
        self.saldo_pendiente = 0.0
        self.total_con_saldos = 0.0

    def calcular_saldo(self):
        valor = self.datos.get("saldos_pendientes", 0.0)
        self.saldo_pendiente = float(valor) if valor is not None else 0.0

    def aplicar(self, total_con_iva: float):
        self.total_con_saldos = round(total_con_iva + self.saldo_pendiente, 2)
        return self.total_con_saldos

    def calcular(self, total_con_iva: float):
        self.calcular_saldo()
        return self.aplicar(total_con_iva)


# ---------------------------------------------------------
# BLOQUE 6: BONO SOLAR CLOUD
# ---------------------------------------------------------
def obtener_saldo_inicial(cursor, ncontrato):
    cursor.execute("SELECT saldo_inicial FROM saldo_cloud_inicial_test WHERE id = 1")
    row = cursor.fetchone()
    if not row:
        return 0.0
    valor = float(row[0])
    if math.isnan(valor) or math.isinf(valor):
        return 0.0
    return valor


def obtener_saldo_cloud(cursor, ncontrato):
    cursor.execute(
        "SELECT saldo FROM saldo_cloud_test WHERE ncontrato = ?",
        (ncontrato,),
    )
    row = cursor.fetchone()
    if row:
        valor = float(row[0])
        if math.isnan(valor) or math.isinf(valor):
            return 0.0
        return valor

    saldo_inicial = obtener_saldo_inicial(cursor, ncontrato)
    cursor.execute(
        "INSERT INTO saldo_cloud_test (ncontrato, saldo) VALUES (?, ?)",
        (ncontrato, saldo_inicial),
    )
    return saldo_inicial


def guardar_saldo_cloud(cursor, ncontrato, nuevo_saldo):
    if nuevo_saldo < 0:
        nuevo_saldo = 0.0
    cursor.execute(
        """
        INSERT INTO saldo_cloud_test (ncontrato, saldo)
        VALUES (?, ?)
        ON CONFLICT(ncontrato) DO UPDATE SET saldo = excluded.saldo
        """,
        (ncontrato, nuevo_saldo),
    )


def calcular_bono_solar_cloud(cursor, ncontrato, total_con_saldos, sobrante_excedentes):
    saldo_anterior = obtener_saldo_cloud(cursor, ncontrato)
    aplicado = min(saldo_anterior, total_con_saldos)
    total_final = round(total_con_saldos - aplicado, 2)
    nuevo_saldo = round((saldo_anterior - aplicado) + sobrante_excedentes, 2)
    if nuevo_saldo < 0:
        nuevo_saldo = 0.0
    guardar_saldo_cloud(cursor, ncontrato, nuevo_saldo)
    return total_final, aplicado, nuevo_saldo


# ---------------------------------------------------------
# FUNCIONES EXTERNAS
# ---------------------------------------------------------
def obtener_datos_factura(cursor, nfactura: str) -> dict:
    cursor.execute(
        """
        SELECT *
        FROM v_datos_calculo_test
        WHERE nfactura = ?
        """,
        (nfactura,),
    )
    row = cursor.fetchone()
    columnas = [d[0] for d in cursor.description]
    return dict(zip(columnas, row))


# ---------------------------------------------------------
# ORQUESTADORES DE BLOQUES
# ---------------------------------------------------------
def calcular_energia_para_factura(cursor, nfactura: str, bono_social: float):
    datos = obtener_datos_factura(cursor, nfactura)
    energia = Energia(datos)
    energia.calcular(bono_social)
    return energia, datos


def calcular_cargos_para_factura(datos: dict):
    cargos = CargosNormativos(datos)
    cargos.calcular()
    return cargos


def calcular_servicios_para_factura(datos: dict):
    serv = ServiciosOtros(datos)
    serv.calcular()
    return serv


def calcular_iva_para_factura(energia_obj, cargos_obj, servicios_obj, datos_base):
    base = round(
        energia_obj.total_energia
        + cargos_obj.total_cargos
        + servicios_obj.total_servicios_otros,
        2,
    )
    tipo_iva = datos_base["iva"]
    iva = IVA(base, tipo_iva)
    iva.calcular()
    return iva


def calcular_saldos_pendientes(datos: dict, total_con_iva: float):
    saldos = SaldosPendientes(datos)
    total_con_saldos = saldos.calcular(total_con_iva)
    return saldos, total_con_saldos


# ---------------------------------------------------------
# JSON AMPLIADO
# ---------------------------------------------------------
def generar_json_calculo(
    energia_obj,
    cargos_obj,
    servicios_obj,
    iva_obj,
    saldos_obj,
    aplicado_cloud,
    nuevo_saldo,
    datos_base,
):

    detalles = {
        "dias_factura": datos_base["dias_factura"],
        "potencia": {
            "punta": {
                "kw": datos_base["ppunta"],
                "precio": datos_base["pv_ppunta"],
                "dias": datos_base["dias_factura"],
                "importe": round(
                    datos_base["ppunta"]
                    * datos_base["pv_ppunta"]
                    * datos_base["dias_factura"],
                    2,
                ),
            },
            "valle": {
                "kw": datos_base["pvalle"],
                "precio": datos_base["pv_pvalle"],
                "dias": datos_base["dias_factura"],
                "importe": round(
                    datos_base["pvalle"]
                    * datos_base["pv_pvalle"]
                    * datos_base["dias_factura"],
                    2,
                ),
            },
            "total": energia_obj.total_potencia,
        },
        "consumo": {
            "punta": {
                "kwh": datos_base["consumo_punta"],
                "precio": datos_base["pv_conpunta"],
                "importe": round(
                    datos_base["consumo_punta"] * datos_base["pv_conpunta"], 2
                ),
            },
            "llano": {
                "kwh": datos_base["consumo_llano"],
                "precio": datos_base["pv_conllano"],
                "importe": round(
                    datos_base["consumo_llano"] * datos_base["pv_conllano"], 2
                ),
            },
            "valle": {
                "kwh": datos_base["consumo_valle"],
                "precio": datos_base["pv_convalle"],
                "importe": round(
                    datos_base["consumo_valle"] * datos_base["pv_convalle"], 2
                ),
            },
            "total": energia_obj.total_consumo,
        },
        "excedentes": {
            "generados_kwh": datos_base["excedentes"],
            "precio_unitario": datos_base["pv_excedent"],
            "compensados": energia_obj.compensacion_excedentes,
            "sobrante": energia_obj.sobrante_excedentes,
        },
        "cargos": {
            "bono_social": {
                "dias": datos_base["dias_factura"],
                "importe_diario": datos_base["bono_social"],
                "importe": cargos_obj.bono_social,
            },
            "iee": {
                "base": (
                    energia_obj.total_potencia
                    + (
                        energia_obj.total_consumo
                        - abs(energia_obj.compensacion_excedentes)
                    )
                    + cargos_obj.bono_social
                ),
                "porcentaje": datos_base["i_electrico"] / 100,
                "importe": energia_obj.impuesto_electrico,
            },
        },
        "servicios": {
            "equipos": servicios_obj.equipos,
            "servicios": servicios_obj.servicios,
            "total": servicios_obj.total_servicios_otros,
        },
        "iva": {
            "base": iva_obj.base_imponible,
            "tipo": iva_obj.tipo_iva,
            "importe": iva_obj.cuota_iva,
        },
        "saldos_pendientes": {
            "importe": saldos_obj.saldo_pendiente,
            "total_tras_saldos": saldos_obj.total_con_saldos,
        },
        "cloud": {
            "aplicado": aplicado_cloud,
            "sobrante_excedentes": energia_obj.sobrante_excedentes,
            "saldo_final": nuevo_saldo,
        },
    }

    detalles["total_final"] = round(saldos_obj.total_con_saldos - aplicado_cloud, 2)

    return json.dumps(detalles, ensure_ascii=False, indent=2)


# ---------------------------------------------------------
# GUARDADO FINAL EN BD
# ---------------------------------------------------------
def guardar_calculo_factura(
    cursor,
    nfactura: str,
    version_motor: str,
    energia_obj,
    cargos_obj,
    servicios_obj,
    iva_obj,
    saldos_obj,
    aplicado_cloud: float,
    nuevo_saldo: float,
    detalles_json: str,
    datos_base: dict,
):

    cursor.execute("DELETE FROM factura_calculos_test WHERE nfactura = ?", (nfactura,))
    registrar_version_motor(cursor)

    cursor.execute(
        """
        INSERT INTO factura_calculos_test (
            nfactura, fecha_calculo, version_motor, total_energia,
            total_cargos, total_servicios, total_iva, cloud_aplicado,
            cloud_sobrante, total_final, detalles_json, bono_social,
            alq_contador, otros_gastos, i_electrico, iva
        )
        VALUES (?, date('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            nfactura,
            version_motor,
            energia_obj.total_energia,
            cargos_obj.total_cargos,
            servicios_obj.total_servicios_otros,
            iva_obj.cuota_iva,
            aplicado_cloud,
            energia_obj.sobrante_excedentes,
            round(saldos_obj.total_con_saldos - aplicado_cloud, 2),
            detalles_json,
            datos_base["bono_social"],
            datos_base["alq_contador"],
            datos_base["otros_gastos"],
            datos_base["i_electrico"],
            datos_base["iva"],
        ),
    )
