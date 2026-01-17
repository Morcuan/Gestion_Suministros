# -------------------------------------------------------------#
# Módulo: aux_fechas.py                                        #
# Descripción: Funciones centralizadas para manejo de fechas   #
# Autor: Antonio Morales                                       #
# Fecha: 2025-12-22                                            #
# -------------------------------------------------------------#

from datetime import datetime, date


# -------------------------------------------------------------
# Convierte dd/mm/yyyy, dd-mm-yyyy o yyyy/mm/dd → yyyy-mm-dd (ISO)
# Devuelve None si no es válida
# -------------------------------------------------------------
def a_iso(texto: str) -> str | None:
    if not texto:
        return None

    texto = texto.strip()

    formatos = (
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",  # NUEVO: formato adicional aceptado
    )

    for fmt in formatos:
        try:
            fecha = datetime.strptime(texto, fmt).date()
            return fecha.isoformat()
        except ValueError:
            continue

    return None


# -------------------------------------------------------------
# Convierte yyyy-mm-dd → dd/mm/yyyy
# Devuelve el texto original si no es válida
# -------------------------------------------------------------
def a_ddmm(texto_iso: str) -> str:
    if not texto_iso:
        return ""

    try:
        fecha = datetime.strptime(texto_iso.strip(), "%Y-%m-%d").date()
        return fecha.strftime("%d/%m/%Y")
    except ValueError:
        return texto_iso


# -------------------------------------------------------------
# Valida si un texto es una fecha dd/mm/yyyy o dd-mm-yyyy
# -------------------------------------------------------------
def es_fecha_valida(texto: str) -> bool:
    return a_iso(texto) is not None


# -------------------------------------------------------------
# NUEVO: devuelve la fecha actual en formato ISO (yyyy-mm-dd)
# -------------------------------------------------------------
def hoy_iso() -> str:
    return date.today().isoformat()
