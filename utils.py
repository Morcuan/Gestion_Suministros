# --------------------------------------------#
# Modulo: utils.py                          #
# Descripción: Utilidades varias para el proyecto #
# Autor: Antonio Morales                      #
# Fecha: 2026-02-09                           #
# --------------------------------------------#
# Este módulo contiene funciones de utilidad para el manejo de fechas y otros aspectos comunes del proyecto.

from datetime import datetime


# Funciones de manejo de fechas
def convertir_fecha_a_iso(fecha_ddmmyyyy):
    """
    Convierte 'dd/mm/yyyy' → 'yyyy-mm-dd'.
    Lanza ValueError si el formato no es válido.
    """
    try:
        d = datetime.strptime(fecha_ddmmyyyy, "%d/%m/%Y")
        return d.strftime("%Y-%m-%d")
    except Exception:
        raise ValueError("Formato de fecha incorrecto")


# Devuelve el número de días entre dos fechas dd/mm/yyyy (incluyendo ambos).
def dias_entre_fechas(inicio_ddmmyyyy, fin_ddmmyyyy):
    """
    Devuelve el número de días entre dos fechas dd/mm/yyyy (incluyendo ambos).
    """
    d1 = datetime.strptime(inicio_ddmmyyyy, "%d/%m/%Y")
    d2 = datetime.strptime(fin_ddmmyyyy, "%d/%m/%Y")
    return (d2 - d1).days


# Valida que una fecha esté en formato dd/mm/yyyy y sea una fecha real.
def validar_fecha(fecha_ddmmyyyy):
    """
    Valida una fecha en formato dd/mm/yyyy.
    Devuelve True si es válida, False si no lo es.
    """
    try:
        datetime.strptime(fecha_ddmmyyyy, "%d/%m/%Y")
        return True
    except:
        return False


# Convierte 'yyyy-mm-dd' → 'dd/mm/yyyy'.
def a_ddmm(fecha_iso):
    """
    Convierte 'yyyy-mm-dd' → 'dd/mm/yyyy'.
    """
    if not fecha_iso:
        return ""
    try:
        y, m, d = fecha_iso.split("-")
        return f"{d}/{m}/{y}"
    except:
        return fecha_iso
