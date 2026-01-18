# -------------------------------------------------------------#
# Módulo: aux_presentacion.py                                  #
# Descripción: Funciones comunes de presentación visual        #
# Autor: Antonio Morales                                       #
# Fecha: 2025-12-22                                            #
# -------------------------------------------------------------#

from PySide6.QtGui import QColor

# -------------------------------------------------------------
# Mapa centralizado de colores por estado
# -------------------------------------------------------------
_COLORES_ESTADO = {
    "ACTIVO": QColor("green"),
    "CADUCADO": QColor("orange"),
    "ANULADO": QColor("red"),
    "PENDIENTE": QColor("blue"),
}


# -------------------------------------------------------------
# Devuelve el color asociado a un estado
# -------------------------------------------------------------
def color_estado(estado: str) -> QColor:
    estado = estado.upper().strip()
    return _COLORES_ESTADO.get(estado, QColor("black"))


# -------------------------------------------------------------
# Color para filas en la tabla de contratos
# (usa la misma lógica que color_estado)
# -------------------------------------------------------------
def color_fila_estado(estado: str) -> QColor:
    return color_estado(estado)


# -------------------------------------------------------------
# Estilo CSS para botones estándar
# -------------------------------------------------------------
def estilo_boton(tipo: str) -> str:
    tipo = tipo.lower().strip()

    estilos = {
        "guardar": (
            "QPushButton { background-color: #41b883; color: white; "
            "font-weight: bold; padding: 6px 12px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #369a6e; }"
        ),
        "cancelar": (
            "QPushButton { background-color: #e76f51; color: white; "
            "font-weight: bold; padding: 6px 12px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #c75b43; }"
        ),
        "salir": (
            "QPushButton { background-color: #e76f51; color: white; "
            "font-weight: bold; padding: 6px 12px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #c75b43; }"
        ),
    }

    return estilos.get(tipo, "")


# -------------------------------------------------------------
