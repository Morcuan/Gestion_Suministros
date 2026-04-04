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

from datetime import date, datetime, timedelta


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


# -------------------------------------------------------------#
# Determinación del estado de un contrato                      #
# -------------------------------------------------------------#


def determinar_estado_contrato(
    efec_suple, fin_suple, fec_anulacion, lista_fechas_efecto, fecha_ref=None
):
    """
    Determina el estado de un contrato según el DRU de estados.
    Parámetros:
        efec_suple: fecha ISO yyyy-mm-dd
        fin_suple: fecha ISO yyyy-mm-dd
        fec_anulacion: fecha ISO yyyy-mm-dd o None
        lista_fechas_efecto: lista de fechas ISO de todos los suplementos
        fecha_ref: fecha ISO o None (por defecto hoy)
    """

    # Convertir a objetos date
    efec = datetime.strptime(efec_suple, "%Y-%m-%d").date()
    fin = datetime.strptime(fin_suple, "%Y-%m-%d").date()

    anul = None
    if fec_anulacion:
        anul = datetime.strptime(fec_anulacion, "%Y-%m-%d").date()

    if fecha_ref is None:
        fecha_ref = date.today()
    else:
        fecha_ref = datetime.strptime(fecha_ref, "%Y-%m-%d").date()

    # ---------------------------------------------------------
    # 1. CASOS CON ANULACIÓN
    # ---------------------------------------------------------
    if anul is not None:

        # 1.1 Posible "Sin efecto"
        if anul == efec:
            # Si todos los suplementos tienen la misma fecha de efecto
            if len(set(lista_fechas_efecto)) == 1:
                return "Sin efecto"
            # Si hay fechas distintas → no puede ser "Sin efecto"
            # Se evalúa como anulado normal

        # 1.2 Anulado (siempre válido porque ya validas que anul <= fin)
        return "Anulado"

    # ---------------------------------------------------------
    # 2. CASOS SIN ANULACIÓN
    # ---------------------------------------------------------

    # 2.1 Futuro
    if efec > fecha_ref:
        return "Futuro"

    # 2.2 Caducado
    if fin < fecha_ref:
        return "Caducado"

    # 2.3 En vigor
    if efec <= fecha_ref <= fin:
        return "En vigor"

    return "Indeterminado"
