# -------------------------------------------------------------#
# Módulo: motor_calculo.py                                     #
# Descripción: Motor puro de cálculo, sin BD ni efectos laterales
# Autor: Antonio Morales                                       #
# Fecha: 2026-04                                               #
# -------------------------------------------------------------#

import json


class Energia:
    def __init__(self, datos: dict):
        self.datos = datos

        # Totales
        self.total_potencia = 0.0
        self.total_consumo = 0.0
        self.compensacion_excedentes = 0.0
        self.impuesto_electrico = 0.0
        self.total_energia = 0.0
        self.sobrante_excedentes = 0.0

        # Detalle potencia (kW)
        self.pot_punta_kw = 0.0
        self.pot_punta_precio = 0.0
        self.pot_punta_importe = 0.0

        self.pot_llano_kw = 0.0
        self.pot_llano_precio = 0.0
        self.pot_llano_importe = 0.0  # en tu esquema actual será 0

        self.pot_valle_kw = 0.0
        self.pot_valle_precio = 0.0
        self.pot_valle_importe = 0.0

        # Detalle consumo (kWh)
        self.con_punta_kwh = 0.0
        self.con_punta_precio = 0.0
        self.con_punta_importe = 0.0

        self.con_llano_kwh = 0.0
        self.con_llano_precio = 0.0
        self.con_llano_importe = 0.0

        self.con_valle_kwh = 0.0
        self.con_valle_precio = 0.0
        self.con_valle_importe = 0.0

    def calcular_potencia(self):
        dias = self.datos["dias_factura"]

        # Punta
        self.pot_punta_kw = self.datos["ppunta"]
        self.pot_punta_precio = self.datos["pv_ppunta"]
        self.pot_punta_importe = round(
            self.pot_punta_kw * dias * self.pot_punta_precio, 2
        )

        # Llano (si no existe en tu tarifa, lo dejamos a 0)
        self.pot_llano_kw = 0.0
        self.pot_llano_precio = 0.0
        self.pot_llano_importe = 0.0

        # Valle
        self.pot_valle_kw = self.datos["pvalle"]
        self.pot_valle_precio = self.datos["pv_pvalle"]
        self.pot_valle_importe = round(
            self.pot_valle_kw * dias * self.pot_valle_precio, 2
        )

        self.total_potencia = round(
            self.pot_punta_importe + self.pot_llano_importe + self.pot_valle_importe, 2
        )

    def calcular_consumo(self):
        # Punta
        self.con_punta_kwh = self.datos["consumo_punta"]
        self.con_punta_precio = self.datos["pv_conpunta"]
        self.con_punta_importe = round(self.con_punta_kwh * self.con_punta_precio, 2)

        # Llano
        self.con_llano_kwh = self.datos["consumo_llano"]
        self.con_llano_precio = self.datos["pv_conllano"]
        self.con_llano_importe = round(self.con_llano_kwh * self.con_llano_precio, 2)

        # Valle
        self.con_valle_kwh = self.datos["consumo_valle"]
        self.con_valle_precio = self.datos["pv_convalle"]
        self.con_valle_importe = round(self.con_valle_kwh * self.con_valle_precio, 2)

        self.total_consumo = round(
            self.con_punta_importe + self.con_llano_importe + self.con_valle_importe,
            2,
        )

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
            + self.total_consumo
            + self.compensacion_excedentes
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


class ServiciosOtros:
    def __init__(self, datos: dict):
        self.datos = datos
        self.equipos = 0.0
        self.servicios = 0.0
        self.total_servicios_otros = 0.0

    def calcular_equipos(self):
        dias = self.datos["dias_factura"]
        precio = self.datos["alq_contador"]
        self.equipos = round(dias * precio, 2)

    def calcular_servicios(self):
        servicios = self.datos["servicios"]
        dcto = self.datos["dcto_servicios"]
        self.servicios = round(servicios + dcto, 2)

    def calcular_bloque(self):
        self.total_servicios_otros = round(self.equipos + self.servicios, 2)

    def calcular(self):
        self.calcular_equipos()
        self.calcular_servicios()
        self.calcular_bloque()
        return self


class IVA:
    def __init__(self, base_imponible: float, tipo_iva: float = 0.21):
        self.base_imponible = round(base_imponible, 2)
        self.tipo_iva = tipo_iva
        self.cuota_iva = 0.0
        self.total_con_iva = 0.0

    def calcular_iva(self):
        self.cuota_iva = round(self.base_imponible * self.tipo_iva, 2)
        self.total_con_iva = round(self.base_imponible + self.cuota_iva, 2)

    def calcular(self):
        self.calcular_iva()
        return self


def generar_json_calculo(
    energia_obj,
    cargos_obj,
    servicios_obj,
    iva_obj,
    aplicado_cloud,
    nuevo_saldo,
    datos_base,
):
    detalles = {
        "dias_factura": datos_base["dias_factura"],
        "potencia": {
            "periodos": {
                "punta": {
                    "kW": energia_obj.pot_punta_kw,
                    "precio_unitario": energia_obj.pot_punta_precio,
                    "importe": energia_obj.pot_punta_importe,
                },
                "llano": {
                    "kW": energia_obj.pot_llano_kw,
                    "precio_unitario": energia_obj.pot_llano_precio,
                    "importe": energia_obj.pot_llano_importe,
                },
                "valle": {
                    "kW": energia_obj.pot_valle_kw,
                    "precio_unitario": energia_obj.pot_valle_precio,
                    "importe": energia_obj.pot_valle_importe,
                },
            },
            "total": energia_obj.total_potencia,
        },
        "consumo": {
            "periodos": {
                "punta": {
                    "kWh": energia_obj.con_punta_kwh,
                    "precio_unitario": energia_obj.con_punta_precio,
                    "importe": energia_obj.con_punta_importe,
                },
                "llano": {
                    "kWh": energia_obj.con_llano_kwh,
                    "precio_unitario": energia_obj.con_llano_precio,
                    "importe": energia_obj.con_llano_importe,
                },
                "valle": {
                    "kWh": energia_obj.con_valle_kwh,
                    "precio_unitario": energia_obj.con_valle_precio,
                    "importe": energia_obj.con_valle_importe,
                },
            },
            "total": energia_obj.total_consumo,
        },
        "excedentes": {
            "generados_kWh": datos_base["excedentes"],
            "precio_unitario": datos_base["pv_excedent"],
            "compensados": energia_obj.compensacion_excedentes,
            "sobrante": energia_obj.sobrante_excedentes,
        },
        "cargos": {
            "bono_social": cargos_obj.bono_social,
            "total": cargos_obj.total_cargos,
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
        "cloud": {
            "aplicado": aplicado_cloud,
            "sobrante_excedentes": energia_obj.sobrante_excedentes,
            "saldo_final": nuevo_saldo,
        },
        "total_final": iva_obj.total_con_iva - aplicado_cloud,
    }

    return json.dumps(detalles, ensure_ascii=False, indent=2)


def motor_calculo(datos: dict, saldo_cloud_actual: float):
    """
    Motor puro: recibe datos de cálculo y saldo cloud actual.
    Devuelve totales + JSON sin tocar BD.
    """

    # 1. Cargos normativos
    cargos = CargosNormativos(datos).calcular()

    # 2. Energía
    energia = Energia(datos).calcular(cargos.bono_social)

    # 3. Servicios
    servicios = ServiciosOtros(datos).calcular()

    # 4. IVA
    base = energia.total_energia + cargos.total_cargos + servicios.total_servicios_otros
    iva = IVA(base).calcular()

    # 5. Cloud (solo cálculo matemático)
    aplicado = min(saldo_cloud_actual, iva.total_con_iva)
    nuevo_saldo = round(
        (saldo_cloud_actual - aplicado) + energia.sobrante_excedentes, 2
    )

    # 6. JSON
    detalles_json = generar_json_calculo(
        energia,
        cargos,
        servicios,
        iva,
        aplicado,
        nuevo_saldo,
        datos,
    )

    return {
        "energia": energia,
        "cargos": cargos,
        "servicios": servicios,
        "iva": iva,
        "cloud_aplicado": aplicado,
        "cloud_sobrante": energia.sobrante_excedentes,
        "nuevo_saldo": nuevo_saldo,
        "total_final": iva.total_con_iva - aplicado,
        "json": detalles_json,
    }
