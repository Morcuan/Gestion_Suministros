# --------------------------------------------#
# Modulo: calculo.py                          #
# Descripción: Calculo de facturas de energía #
# Autor: Antonio Morales                      #
# Fecha: 2026-02-09                           #
# --------------------------------------------#
# Este módulo contiene la lógica de cálculo de las facturas de energía, organizada
# en clases para cada bloque de la factura (energía, cargos normativos, servicios y
# otros conceptos, IVA) y funciones para orquestar el cálculo completo de la factura,
# incluyendo el Bono Solar Cloud. Cada bloque tiene su propia clase con métodos específicos
# para calcular los conceptos dentro del bloque, y un método orquestador para realizar el
# cálculo completo del bloque de energía. Las funciones externas permiten calcular cada
# bloque de la factura a partir de los datos obtenidos de la base de datos, y generar el JSON
# con los detalles del cálculo para su almacenamiento y visualización.

# ------------------------------------------------------------
# IMPORTACIONES
# ------------------------------------------------------------
import json

# ---------------------------------------------------------
# BLOQUE 1: ENERGIA
# ---------------------------------------------------------
# Bloque 1.- ENERGÍA
# Incluye:
# - Potencia (kW × días × precio)
# - Energía consumida (kWh × precio)
# - Compensación por excedentes (kWh × precio, con límite por consumo)
# - Impuesto eléctrico (aplica sobre la suma de los anteriores, con posible
# bonificación por bono social)


# El bloque de energía se calcula en una clase dedicada, que recibe el diccionario
# completo de datos para facilitar el acceso a los datos necesarios para cada cálculo,
# y tiene métodos específicos para calcular cada concepto dentro del bloque, así como
# un método orquestador para realizar el cálculo completo del bloque de energía.
class Energia:
    # init recibe el diccionario completo de datos para facilitar cálculos posteriores
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
    # El cálculo de potencia se hace directamente con los datos de días y precios,
    # sin necesidad de variables intermedias para kW, ya que el resultado final
    # es el importe total por potencia.
    def calcular_potencia(self):
        dias = self.datos["dias_factura"]

        ppunta = self.datos["ppunta"] * dias * self.datos["pv_ppunta"]
        pvalle = self.datos["pvalle"] * dias * self.datos["pv_pvalle"]

        self.total_potencia = round(ppunta + pvalle, 2)

    # ---------------------------------------------------------
    # ENERGÍA CONSUMIDA
    # ---------------------------------------------------------
    # Similar al caso de potencia, el cálculo se hace directamente con los datos
    # de consumo y precios, sin necesidad de variables intermedias para kWh,
    # ya que el resultado final es el importe total por consumo.
    def calcular_consumo(self):
        c_punta = self.datos["consumo_punta"] * self.datos["pv_conpunta"]
        c_llano = self.datos["consumo_llano"] * self.datos["pv_conllano"]
        c_valle = self.datos["consumo_valle"] * self.datos["pv_convalle"]

        self.total_consumo = round(c_punta + c_llano + c_valle, 2)

    # ---------------------------------------------------------
    # EXCEDENTES
    # ---------------------------------------------------------
    # El cálculo de excedentes se hace en varios pasos:
    # 1) Calcular el importe total generado por los excedentes (kWh × precio)
    # 2) Calcular la compensación aplicable (siempre negativa, con límite por consumo)
    # 3) Calcular el sobrante de excedentes que no se compensan,
    # para acumularlo en el Bono Solar Cloud
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

        # Cálculo del sobrante de excedentes para el Bono Solar Cloud
        self.sobrante_excedentes = round(
            importe_excedentes - abs(self.compensacion_excedentes), 2
        )

        if self.sobrante_excedentes < 0:
            self.sobrante_excedentes = 0.0

    # ---------------------------------------------------------
    # IMPUESTO ELÉCTRICO (IEE)
    # ---------------------------------------------------------
    # El impuesto eléctrico se calcula aplicando el porcentaje sobre la suma de
    # potencia, consumo, compensación por excedentes y bono social (si aplica).
    def calcular_impuesto_electrico(self, bono_social):
        base = (
            self.total_potencia
            + self.total_consumo
            + self.compensacion_excedentes
            + bono_social
        )

        porcentaje = self.datos["i_electrico"] / 100
        self.impuesto_electrico = round(base * porcentaje, 2)

    # ---------------------------------------------------------
    # TOTAL BLOQUE
    # ---------------------------------------------------------
    # El total del bloque de energía es la suma de potencia, consumo, compensación
    # por excedentes e impuesto eléctrico.
    def calcular_bloque(self):
        self.total_energia = round(
            self.total_potencia
            + self.total_consumo
            + self.compensacion_excedentes
            + self.impuesto_electrico,
            2,
        )

    # ---------------------------------------------------------
    # ORQUESTADOR
    # ---------------------------------------------------------
    # El método calcular orquesta el cálculo completo del bloque de energía, recibiendo
    # el bono social como parámetro para incluirlo en el cálculo del impuesto eléctrico.
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
# Bloque 2.- CARGOS NORMATIVOS
# Incluye:
# - Bono social (importe diario × días)
class CargosNormativos:
    """
    Bloque 2.- CARGOS NORMATIVOS
    Incluye:
    - Bono social (importe diario × días)
    """

    # El init recibe el diccionario completo de datos para facilitar cálculos posteriores
    def __init__(self, datos: dict):
        self.datos = datos
        self.bono_social = 0.0
        self.total_cargos = 0.0

    # ---------------------------------------------------------
    # BONO SOCIAL (importe fijo diario)
    # ---------------------------------------------------------
    # El cálculo del bono social se hace directamente con los datos de días y el
    # importe diario, sin necesidad de variables intermedias, ya que el resultado
    # final es el importe total por bono social.
    def calcular_bono_social(self):
        dias = self.datos["dias_factura"]
        importe_diario = self.datos["bono_social"]

        self.bono_social = round(importe_diario * dias, 2)

    # ---------------------------------------------------------
    # TOTAL BLOQUE
    # ---------------------------------------------------------
    # El total del bloque de cargos normativos es el importe del bono social, ya que
    # no hay otros cargos normativos en este bloque.
    def calcular_bloque(self):
        self.total_cargos = round(self.bono_social, 2)

    # ---------------------------------------------------------
    # ORQUESTADOR
    # ---------------------------------------------------------
    # El método calcular orquesta el cálculo completo del bloque de cargos normativos,
    # que en este caso se reduce al cálculo del bono social y su asignación al
    # total de cargos.
    def calcular(self):

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

    # El init recibe el diccionario completo de datos para facilitar cálculos posteriores
    def __init__(self, datos: dict):
        self.datos = datos

        self.equipos = 0.0
        self.servicios = 0.0
        self.total_servicios_otros = 0.0

    # ---------------------------------------------------------
    # ALQUILER DE EQUIPOS
    # ---------------------------------------------------------
    # El cálculo del alquiler de equipos se hace directamente con los datos de días y el
    # precio diario, sin necesidad de variables intermedias, ya que el resultado final
    # es el importe total por alquiler de equipos.
    def calcular_equipos(self):
        dias = self.datos["dias_factura"]
        precio = self.datos["alq_contador"]

        self.equipos = round(dias * precio, 2)

    # ---------------------------------------------------------
    # SERVICIOS ASOCIADOS
    # ---------------------------------------------------------
    # El cálculo de servicios asociados se hace directamente con los datos de importe total
    # de servicios y el descuento aplicado, sin necesidad de variables intermedias, ya que
    # el resultado final es el importe total por servicios asociados después de
    # aplicar el descuento.
    def calcular_servicios(self):
        servicios = self.datos["servicios"]
        dcto = self.datos["dcto_servicios"]  # viene en negativo

        self.servicios = round(servicios + dcto, 2)

    # ---------------------------------------------------------
    # TOTAL BLOQUE
    # ---------------------------------------------------------
    def calcular_bloque(self):
        self.total_servicios_otros = round(self.equipos + self.servicios, 2)

    # ---------------------------------------------------------
    # ORQUESTADOR
    # ---------------------------------------------------------
    # El método calcular orquesta el cálculo completo del bloque de servicios y
    # otros conceptos, que incluye
    def calcular(self):

        self.calcular_equipos()
        self.calcular_servicios()
        self.calcular_bloque()
        return self


# ---------------------------------------------------------
# BLOQUE 4: IVA
# ---------------------------------------------------------
# Bloque 4.- IVA
# Incluye:
# - Base imponible (suma de bloques 1, 2 y 3)
# - Tipo de IVA aplicado
# - Cuota resultante
class IVA:
    """
    Bloque 4.- IVA
    Incluye:
    - Base imponible (suma de bloques 1, 2 y 3)
    - Tipo de IVA aplicado
    - Cuota resultante
    """

    # El init recibe la base imponible calculada a partir de la suma de los bloques
    # anteriores, y el tipo de IVA a aplicar, que por defecto es el 21%.
    # No es necesario recibir el total de los bloques anteriores,
    # ya que la base imponible se pasa directamente desde el cálculo de los bloques anteriores.
    def __init__(self, base_imponible: float, tipo_iva: float = 0.21):
        self.base_imponible = round(base_imponible, 2)
        self.tipo_iva = tipo_iva
        self.cuota_iva = 0.0
        self.total_con_iva = 0.0

    # ---------------------------------------------------------
    # CÁLCULO DEL IVA
    # ---------------------------------------------------------
    # El cálculo del IVA se hace aplicando el tipo de IVA sobre la base imponible,
    # y luego sumando la cuota de IVA a la base para obtener el total con IVA.
    def calcular_iva(self):
        self.cuota_iva = round(self.base_imponible * self.tipo_iva, 2)
        self.total_con_iva = round(self.base_imponible + self.cuota_iva, 2)

    # ---------------------------------------------------------
    # ORQUESTADOR
    # ---------------------------------------------------------
    # El método calcular orquesta el cálculo completo del bloque de IVA, que incluye
    # el cálculo de la cuota de IVA y el total con IVA a partir de la base
    # imponible y el tipo de IVA.
    def calcular(self):

        self.calcular_iva()
        return self


# ---------------------------------------------------------
# BONO SOLAR CLOUD
# ---------------------------------------------------------


# El cálculo del Bono Solar Cloud se hace en una función externa, ya que requiere
# acceder a la base de datos para leer el saldo acumulado, aplicar ese saldo a
# la factura actual
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

    return total_final, aplicado, nuevo_saldo


# ---------------------------------------------------------
# FUNCIONES EXTERNAS PARA LLAMAR DESDE LA VENTANA
# ---------------------------------------------------------


# Función para obtener los datos de la factura desde la base de datos, a partir
# del número de factura.
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
    return dict(zip(columnas, row))  # noqa: B905


# Funciones para calcular cada bloque, recibiendo los datos necesarios y devolviendo
# el objeto con los resultados calculados.
def calcular_cargos_para_factura(datos: dict):
    cargos = CargosNormativos(datos)
    cargos.calcular()
    return cargos


# Función para calcular el bloque de energía, recibiendo el bono social calculado
# para incluirlo en el cálculo del impuesto eléctrico.
def calcular_energia_para_factura(cursor, nfactura: str, bono_social: float):
    datos = obtener_datos_factura(cursor, nfactura)
    energia = Energia(datos)
    energia.calcular(bono_social)
    return energia, datos


# Función para calcular el bloque de servicios y otros conceptos, recibiendo los
# datos necesarios para el cálculo.
def calcular_servicios_para_factura(datos: dict):
    serv = ServiciosOtros(datos)
    serv.calcular()
    return serv


# Función para calcular el bloque de IVA, recibiendo la base imponible calculada a
# partir de la suma de los bloques anteriores.
# No es necesario recibir el total de los bloques anteriores, ya que la base
# imponible se pasa directamente desde el cálculo de los bloques anteriores.
def calcular_iva_para_factura(
    total_energia: float, total_cargos: float, total_servicios: float
):
    base = round(total_energia + total_cargos + total_servicios, 2)
    iva = IVA(base)
    iva.calcular()
    return iva


# Función para calcular el Bono Solar Cloud, recibiendo el cursor de la base de datos,
# el id del contrato, el total con IVA de la factura actual y el sobrante de excedentes
# para acumular en el bono. Devuelve el total final después de aplicar el bono, el
# importe aplicado del bono
def obtener_saldo_cloud(cursor, id_contrato):
    cursor.execute(
        "SELECT saldo FROM saldo_cloud WHERE id_contrato = ?", (id_contrato,)
    )
    row = cursor.fetchone()
    return row[0] if row else 0.0


# Función para guardar el nuevo saldo acumulado del Bono Solar Cloud en la base de datos,
# utilizando una sentencia INSERT para insertar o actualizar el saldo según corresponda.
def guardar_saldo_cloud(cursor, id_contrato, nuevo_saldo):
    cursor.execute(
        """
        INSERT INTO saldo_cloud (id_contrato, saldo)
        VALUES (?, ?)
        ON CONFLICT(id_contrato) DO UPDATE SET saldo = excluded.saldo
    """,
        (id_contrato, nuevo_saldo),
    )


# Función para generar el JSON con los detalles del cálculo de la factura, recibiendo
# los objetos de cada bloque con los resultados calculados, el importe aplicado del
# Bono Solar Cloud, el nuevo saldo acumulado, y los datos base para incluir en el JSON.
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
                    "kW": datos_base["ppunta"],
                    "precio_unitario": datos_base["pv_ppunta"],
                    "importe": round(
                        datos_base["ppunta"]
                        * datos_base["dias_factura"]
                        * datos_base["pv_ppunta"],
                        2,
                    ),
                },
                "llano": {
                    "kW": 0,
                    "precio_unitario": 0,
                    "importe": 0,
                },
                "valle": {
                    "kW": datos_base["pvalle"],
                    "precio_unitario": datos_base["pv_pvalle"],
                    "importe": round(
                        datos_base["pvalle"]
                        * datos_base["dias_factura"]
                        * datos_base["pv_pvalle"],
                        2,
                    ),
                },
            },
            "total": energia_obj.total_potencia,
        },
        "consumo": {
            "periodos": {
                "punta": {
                    "kWh": datos_base["consumo_punta"],
                    "precio_unitario": datos_base["pv_conpunta"],
                    "importe": round(
                        datos_base["consumo_punta"] * datos_base["pv_conpunta"], 2
                    ),
                },
                "llano": {
                    "kWh": datos_base["consumo_llano"],
                    "precio_unitario": datos_base["pv_conllano"],
                    "importe": round(
                        datos_base["consumo_llano"] * datos_base["pv_conllano"], 2
                    ),
                },
                "valle": {
                    "kWh": datos_base["consumo_valle"],
                    "precio_unitario": datos_base["pv_convalle"],
                    "importe": round(
                        datos_base["consumo_valle"] * datos_base["pv_convalle"], 2
                    ),
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
    }

    # 👉 AÑADIDO AQUÍ, EN EL SITIO CORRECTO
    detalles["total_final"] = iva_obj.total_con_iva - aplicado_cloud

    return json.dumps(detalles, ensure_ascii=False, indent=2)


# Función para guardar el cálculo de la factura en la base de datos, recibiendo el cursor,
# el número de factura (nfactura), la versión del motor de cálculo, los objetos de cada bloque
# con los resultados calculados, el importe aplicado del Bono Solar Cloud, el nuevo
# saldo acumulado y el JSON de detalles.
def guardar_calculo_factura(
    cursor,
    nfactura: str,
    version_motor: str,
    energia_obj,
    cargos_obj,
    servicios_obj,
    iva_obj,
    aplicado_cloud: float,
    nuevo_saldo: float,
    detalles_json: str,
):

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
            energia_obj.total_energia,
            cargos_obj.total_cargos,
            servicios_obj.total_servicios_otros,
            iva_obj.cuota_iva,
            aplicado_cloud,
            energia_obj.sobrante_excedentes,
            iva_obj.total_con_iva - aplicado_cloud,
            detalles_json,
        ),
    )
