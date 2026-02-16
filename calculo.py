# ---------------------------------------------------------
# BLOQUE 1: ENERGIA
# ---------------------------------------------------------
class Energia:
    """
    Bloque 1.- ENERGIA
    Incluye:
    - Potencia facturada
    - Energía consumida
    - Excedentes
    - Impuesto eléctrico (IEE)
    """

    def __init__(self, datos: dict):
        self.datos = datos

        self.total_potencia = 0.0
        self.total_consumo = 0.0
        self.compensacion_excedentes = 0.0
        self.impuesto_electrico = 0.0
        self.total_energia = 0.0

    # ---------------------------------------------------------
    # POTENCIA
    # ---------------------------------------------------------
    def calcular_potencia(self):
        dias = self.datos["dias_factura"]

        ppunta = self.datos["ppunta"] * dias * self.datos["pv_ppunta"]
        pvalle = self.datos["pvalle"] * dias * self.datos["pv_pvalle"]

        self.total_potencia = round(ppunta + pvalle, 2)

        print(f"[ENERGIA] Potencia total: {self.total_potencia:.2f} €")

    # ---------------------------------------------------------
    # ENERGÍA CONSUMIDA
    # ---------------------------------------------------------
    def calcular_consumo(self):
        c_punta = self.datos["consumo_punta"] * self.datos["pv_conpunta"]
        c_llano = self.datos["consumo_llano"] * self.datos["pv_conllano"]
        c_valle = self.datos["consumo_valle"] * self.datos["pv_convalle"]

        self.total_consumo = round(c_punta + c_llano + c_valle, 2)

        print(f"[ENERGIA] Consumo total: {self.total_consumo:.2f} €")

    # ---------------------------------------------------------
    # EXCEDENTES
    # ---------------------------------------------------------
    def calcular_excedentes(self, limite_por_consumo=True):
        exced_kwh = self.datos["excedentes"]
        precio_exc = self.datos["pv_excedent"]

        importe_excedentes = round(exced_kwh * precio_exc, 2)
        compensacion = -importe_excedentes  # siempre negativo

        if limite_por_consumo:
            max_compensable = self.total_consumo
            if abs(compensacion) > max_compensable:
                compensacion = -max_compensable

        self.compensacion_excedentes = round(compensacion, 2)

        print(f"[ENERGIA] Excedentes compensados: {self.compensacion_excedentes:.2f} €")

    # ---------------------------------------------------------
    # IMPUESTO ELÉCTRICO (IEE)
    # ---------------------------------------------------------
    def calcular_impuesto_electrico(self, bono_social):
        base = (
            self.total_potencia
            + self.total_consumo
            + self.compensacion_excedentes
            + bono_social
        )

        porcentaje = self.datos["i_electrico"] / 100
        self.impuesto_electrico = round(base * porcentaje, 2)

        print(
            f"[ENERGIA] Impuesto eléctrico ({porcentaje * 100:.7f}% sobre {base:.2f} €): "
            f"{self.impuesto_electrico:.2f} €"
        )

    # ---------------------------------------------------------
    # TOTAL BLOQUE
    # ---------------------------------------------------------
    def calcular_bloque(self):
        self.total_energia = round(
            self.total_potencia
            + self.total_consumo
            + self.compensacion_excedentes
            + self.impuesto_electrico,
            2,
        )

        print(f"[ENERGIA] TOTAL BLOQUE ENERGÍA: {self.total_energia:.2f} €")

    # ---------------------------------------------------------
    # ORQUESTADOR
    # ---------------------------------------------------------
    def calcular(self, bono_social):
        print("\n===== BLOQUE 1: ENERGÍA =====")
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
    """
    Bloque 2.- CARGOS NORMATIVOS
    Incluye:
    - Bono social (importe diario × días)
    """

    def __init__(self, datos: dict):
        self.datos = datos
        self.bono_social = 0.0
        self.total_cargos = 0.0

    # ---------------------------------------------------------
    # BONO SOCIAL (importe fijo diario)
    # ---------------------------------------------------------
    def calcular_bono_social(self):
        dias = self.datos["dias_factura"]
        importe_diario = self.datos["bono_social"]

        self.bono_social = round(importe_diario * dias, 2)

        print(
            f"[CARGOS] Bono social ({importe_diario} €/día × {dias} días): "
            f"{self.bono_social:.2f} €"
        )

    # ---------------------------------------------------------
    # TOTAL BLOQUE
    # ---------------------------------------------------------
    def calcular_bloque(self):
        self.total_cargos = round(self.bono_social, 2)
        print(f"[CARGOS] TOTAL BLOQUE CARGOS NORMATIVOS: {self.total_cargos:.2f} €")

    # ---------------------------------------------------------
    # ORQUESTADOR
    # ---------------------------------------------------------
    def calcular(self):
        print("\n===== BLOQUE 2: CARGOS NORMATIVOS =====")
        self.calcular_bono_social()
        self.calcular_bloque()
        return self


# ---------------------------------------------------------
# FUNCIONES EXTERNAS PARA LLAMAR DESDE LA VENTANA
# ---------------------------------------------------------


def obtener_datos_factura(cursor, nfactura: str) -> dict:
    cursor.execute(
        """
        SELECT *
        FROM v_datos_calculo
        WHERE nfactura = ?
    """,
        (nfactura,),
    )
    row = cursor.fetchone()
    columnas = [d[0] for d in cursor.description]
    return dict(zip(columnas, row))


def calcular_cargos_para_factura(datos: dict):
    cargos = CargosNormativos(datos)
    cargos.calcular()
    return cargos


def calcular_energia_para_factura(cursor, nfactura: str, bono_social: float):
    datos = obtener_datos_factura(cursor, nfactura)
    energia = Energia(datos)
    energia.calcular(bono_social)
    return energia, datos
