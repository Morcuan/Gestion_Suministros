# ---------------------------------------------------------
# BLOQUE 1: ENERGIA
# ---------------------------------------------------------
class Energia:
    def __init__(self, datos: dict):
        self.datos = datos

        self.total_potencia = 0.0
        self.total_consumo = 0.0
        self.compensacion_excedentes = 0.0
        self.impuesto_electrico = 0.0
        self.total_energia = 0.0

        # NUEVO: sobrante de excedentes para el Bono Solar Cloud
        self.sobrante_excedentes = 0.0

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

        # Cálculo del sobrante de excedentes para el Bono Solar Cloud
        self.sobrante_excedentes = round(
            importe_excedentes - abs(self.compensacion_excedentes), 2
        )

        if self.sobrante_excedentes < 0:
            self.sobrante_excedentes = 0.0

        print(f"[ENERGIA] Sobrante excedentes: {self.sobrante_excedentes:.2f} €")

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
# BLOQUE 3: SERVICIOS Y OTROS CONCEPTOS
# ---------------------------------------------------------
class ServiciosOtros:
    """
    Bloque 3.- SERVICIOS Y OTROS CONCEPTOS
    Incluye:
    - Alquiler de equipos de medida
    - Servicios asociados (incluye descuentos)
    """

    def __init__(self, datos: dict):
        self.datos = datos

        self.equipos = 0.0
        self.servicios = 0.0
        self.total_servicios_otros = 0.0

    # ---------------------------------------------------------
    # ALQUILER DE EQUIPOS
    # ---------------------------------------------------------
    def calcular_equipos(self):
        dias = self.datos["dias_factura"]
        precio = self.datos["alq_contador"]

        self.equipos = round(dias * precio, 2)

        print(f"[SERVICIOS] Equipos (alq contador): {self.equipos:.2f} €")

    # ---------------------------------------------------------
    # SERVICIOS ASOCIADOS
    # ---------------------------------------------------------
    def calcular_servicios(self):
        servicios = self.datos["servicios"]
        dcto = self.datos["dcto_servicios"]  # viene en negativo

        self.servicios = round(servicios + dcto, 2)

        print(f"[SERVICIOS] Servicios asociados: {self.servicios:.2f} €")

    # ---------------------------------------------------------
    # TOTAL BLOQUE
    # ---------------------------------------------------------
    def calcular_bloque(self):
        self.total_servicios_otros = round(self.equipos + self.servicios, 2)

        print(
            f"[SERVICIOS] TOTAL BLOQUE SERVICIOS Y OTROS: "
            f"{self.total_servicios_otros:.2f} €"
        )

    # ---------------------------------------------------------
    # ORQUESTADOR
    # ---------------------------------------------------------
    def calcular(self):
        print("\n===== BLOQUE 3: SERVICIOS Y OTROS CONCEPTOS =====")
        self.calcular_equipos()
        self.calcular_servicios()
        self.calcular_bloque()
        return self


# ---------------------------------------------------------
# BLOQUE 4: IVA
# ---------------------------------------------------------
class IVA:
    """
    Bloque 4.- IVA
    Incluye:
    - Base imponible (suma de bloques 1, 2 y 3)
    - Tipo de IVA aplicado
    - Cuota resultante
    """

    def __init__(self, base_imponible: float, tipo_iva: float = 0.21):
        self.base_imponible = round(base_imponible, 2)
        self.tipo_iva = tipo_iva
        self.cuota_iva = 0.0
        self.total_con_iva = 0.0

    # ---------------------------------------------------------
    # CÁLCULO DEL IVA
    # ---------------------------------------------------------
    def calcular_iva(self):
        self.cuota_iva = round(self.base_imponible * self.tipo_iva, 2)
        self.total_con_iva = round(self.base_imponible + self.cuota_iva, 2)

        print(f"[IVA] Base imponible: {self.base_imponible:.2f} €")
        print(f"[IVA] Tipo aplicado: {int(self.tipo_iva * 100)} %")
        print(f"[IVA] Cuota IVA: {self.cuota_iva:.2f} €")
        print(f"[IVA] TOTAL BLOQUE IVA: {self.cuota_iva:.2f} €")

    # ---------------------------------------------------------
    # ORQUESTADOR
    # ---------------------------------------------------------
    def calcular(self):
        print("\n===== BLOQUE 4: IVA =====")
        self.calcular_iva()
        return self


# ---------------------------------------------------------
# BONO SOLAR CLOUD
# ---------------------------------------------------------


def calcular_bono_solar_cloud(cursor, id_contrato, total_con_iva, sobrante_excedentes):
    # 1) Leer saldo acumulado
    saldo_tabla = obtener_saldo_cloud(cursor, id_contrato)

    # 2) Aplicar saldo acumulado a la factura actual
    aplicado = min(saldo_tabla, total_con_iva)
    total_final = round(total_con_iva - aplicado, 2)

    # 3) Calcular nuevo saldo acumulado
    nuevo_saldo = round((saldo_tabla - aplicado) + sobrante_excedentes, 2)

    # 4) Guardar nuevo saldo
    guardar_saldo_cloud(cursor, id_contrato, nuevo_saldo)

    # 5) Mostrar resultados en consola
    print(f">>> SALDO CLOUD ANTERIOR: {saldo_tabla:.2f} €")
    print(f">>> SALDO CLOUD APLICADO: {aplicado:.2f} €")
    print(f">>> SOBRANTE EXCEDENTES MES: {sobrante_excedentes:.2f} €")
    print(f">>> SALDO CLOUD NUEVO: {nuevo_saldo:.2f} €")

    return total_final, aplicado, nuevo_saldo


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


def calcular_servicios_para_factura(datos: dict):
    serv = ServiciosOtros(datos)
    serv.calcular()
    return serv


def calcular_iva_para_factura(
    total_energia: float, total_cargos: float, total_servicios: float
):
    base = round(total_energia + total_cargos + total_servicios, 2)
    iva = IVA(base)
    iva.calcular()
    return iva


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
