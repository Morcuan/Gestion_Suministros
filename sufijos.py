# ----------------------------------------------#
# Modulo: sufijos.py                           #
# Descripción: Sufijos para los campos         #
# de contratos, facturas y consumos.           #
# Autor: Antonio Morales                       #
# Fecha: 2025-12-01                            #
# ----------------------------------------------#

# Campos de contratos
SUFIJOS_CONTRATOS = {
    "Compañía": "",
    "Código postal": "",
    "Número de contrato": "",
    "Fecha inicio": "",
    "Fecha final": "",
    "Potencia punta": " kWh",
    "Potencia valle": " kWh",
    "Importe potencia punta": " €",
    "Importe potencia valle": " €",
    "Importe consumo punta": " €",
    "Importe consumo valle": " €",
    "Importe consumo llano": " €",
    "Importe excedentes": " €",
    "Importe bono social": " €",
    "Importe alquiler contador": " €",
    "Importe asistente smart": " €",
    "Impuesto electricidad": " %",
    "IVA": " %",
}
# Fin de SUFIJOS_CONTRATOS

# Campos de facturas
SUFIJOS_FACTURAS = {
    "factura": "",
    "dias_factura": " días",
    "fecha_emision": "",
    "importe_energia": " €",
    "cargos_normativos": " €",
    "servicios_y_otros": " €",
    "iva": " €",
    "bateria_virtual": " €",
    "total_factura": " €",
}
# Fin de SUFIJOS_FACTURAS

# Lista de tuplas (campo, etiqueta) para las facturas
CAMPOS_FACTURAS = [
    ("factura", "Factura"),
    ("dias_factura", "Días factura"),
    ("fecha_emision", "Fecha emisión"),
    ("importe_energia", "Importe energía"),
    ("cargos_normativos", "Cargos normativos"),
    ("servicios_y_otros", "Servicios y otros"),
    ("iva", "I.V.A."),
    ("bateria_virtual", "Batería virtual"),
    ("total_factura", "Total factura"),
]
# Fin de CAMPOS_FACTURAS

# Campos de consumos
SUFIJOS_CONSUMOS = {
    "Consumo punta": " kWh",
    "Consumo valle": " kWh",
    "Consumo llano": " kWh",
    "Excedentes vertidos": " kWh",
}
# Fin de SUFIJOS_CONSUMOS

# -- Diccionario global ---
SUFIJOS = {**SUFIJOS_CONTRATOS, **SUFIJOS_FACTURAS, **SUFIJOS_CONSUMOS}

# Fin de SUFIJOS
