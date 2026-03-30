# -------------------------------------------------------------#
# Módulo: logica_negocio.py                                    #
# Descripción: Funciones comunes de lógica de negocio (stub)   #
# Autor: Antonio Morales                                       #
# Fecha: 2026-02-10                                            #
# -------------------------------------------------------------#

"""
Este módulo contiene funciones reutilizables de lógica de negocio.
Versión inicial: solo stubs para permitir que el proyecto arranque.
"""

from datetime import datetime, timedelta


def validar_fecha(fecha_str):
    """Valida formato dd/mm/yyyy."""
    try:
        datetime.strptime(fecha_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False


def convertir_a_iso(fecha_str):
    """Convierte dd/mm/yyyy → yyyy-mm-dd."""
    d = datetime.strptime(fecha_str, "%d/%m/%Y")
    return d.strftime("%Y-%m-%d")


def convertir_a_ddmmaaaa(fecha_iso):
    """Convierte yyyy-mm-dd → dd/mm/yyyy."""
    d = datetime.strptime(fecha_iso, "%Y-%m-%d")
    return d.strftime("%d/%m/%Y")


def sumar_10_anios(fecha_iso):
    """Suma 10 años a una fecha ISO y resta 1 día para obtener la fecha final."""
    d = datetime.strptime(fecha_iso, "%Y-%m-%d").date()

    # Intentamos sumar 10 años respetando día y mes
    try:
        d_fin = d.replace(year=d.year + 10)
    except ValueError:
        # Caso raro: 29/02 → ajustamos a 28/02 del año destino
        d_fin = d.replace(year=d.year + 10, day=28)

    # Restamos 1 día para obtener la fecha final real
    d_fin = d_fin - timedelta(days=1)

    return d_fin.strftime("%Y-%m-%d")


def dias_entre_fechas(inicio_ddmmyyyy, fin_ddmmyyyy):
    """
    Devuelve el número de días entre dos fechas dd/mm/yyyy (incluyendo ambos).
    """
    d1 = datetime.strptime(inicio_ddmmyyyy, "%d/%m/%Y")
    d2 = datetime.strptime(fin_ddmmyyyy, "%d/%m/%Y")
    return (d2 - d1).days + 1


def calcular_estado_contrato(fec_inicio, fec_final):
    """Stub: devuelve un estado ficticio."""
    return "activo"
