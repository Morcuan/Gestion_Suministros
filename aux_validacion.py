# -------------------------------------------------------------#
# Módulo: aux_validacion.py                                    #
# Descripción: Funciones comunes de validación numérica        #
# Autor: Antonio Morales                                       #
# Fecha: 2025-12-22                                            #
# -------------------------------------------------------------#

from decimal import Decimal, InvalidOperation


# -------------------------------------------------------------
# Normaliza texto numérico: convierte punto→coma y añade 0 si empieza por coma
# Ej: ".5" → "0,5", "3.2" → "3,2"
# -------------------------------------------------------------
def normalizar_decimal(texto: str) -> str:
    if not texto:
        return ""
    t = texto.strip().replace(".", ",")
    if t.startswith(","):
        t = "0" + t
    return t


# -------------------------------------------------------------
# Convierte texto a Decimal exacto, aceptando coma o punto
# Devuelve None si no es válido
# -------------------------------------------------------------
def a_decimal(texto: str) -> Decimal | None:
    if not texto:
        return None

    t = texto.strip().replace(",", ".")
    if t.startswith("."):
        t = "0" + t

    try:
        return Decimal(t)
    except InvalidOperation:
        return None


# -------------------------------------------------------------
# Valida que un número esté dentro de un rango [min, max]
# Devuelve True si es válido, False si no
# -------------------------------------------------------------
def validar_rango(valor, minimo, maximo) -> bool:
    """
    Valida que un valor numérico esté dentro del rango [minimo, maximo].
    Acepta texto, coma o punto, y usa Decimal para evitar errores silenciosos.
    """

    dec = a_decimal(str(valor))
    if dec is None:
        return False

    try:
        return Decimal(minimo) <= dec <= Decimal(maximo)
    except Exception:
        return False


# ------------------------------------------------------------
