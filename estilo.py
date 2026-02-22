# --------------------------------------------#
# Modulo: estilo_contratos.py                 #
# Descripción: Estilo para ventana contratos  #
# Autor: Antonio Morales                      #
# Fecha: 2026-02-09                           #
# --------------------------------------------#

# estilo.py
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QComboBox, QLineEdit, QPushButton

# ---------------------------------------------------------
# PALETA BASE (DRU)
# ---------------------------------------------------------

COLOR_PRIMARIO = "#4A90E2"  # azul suave
COLOR_SECUNDARIO = "#F0F0F0"  # gris claro
COLOR_ACENTO = "#F5A623"  # naranja suave
COLOR_ERROR = "#D0021B"  # rojo suave
COLOR_TEXTO = "#333333"  # gris oscuro

# ---------------------------------------------------------
# TIPOGRAFÍAS
# ---------------------------------------------------------

FUENTE_TITULO = QFont("DejaVu Sans", 16)
FUENTE_NORMAL = QFont("DejaVu Sans", 13)
FUENTE_BOTON = QFont("DejaVu Sans", 12)

# ---------------------------------------------------------
# ESTILO PANEL LATERAL
# ---------------------------------------------------------


def aplicar_estilo_panel_lateral(widget):
    widget.setStyleSheet("""
        background-color: #F7F7F7;
        border-right: 1px solid #CCCCCC;
        """)


# ---------------------------------------------------------
# ESTILO BOTONES
# ---------------------------------------------------------


def aplicar_estilo_boton(boton: QPushButton, principal=False):
    boton.setFont(FUENTE_BOTON)
    boton.setStyleSheet(f"""
        QPushButton {{
            background-color: {"{0}".format(COLOR_PRIMARIO) if principal else COLOR_SECUNDARIO};
            color: {COLOR_TEXTO};
            border-radius: 6px;
            padding: 6px 10px;
            text-align: left;
        }}
        QPushButton:hover {{
            background-color: {COLOR_ACENTO};
        }}
        """)


# ---------------------------------------------------------
# ESTILO UNIVERSAL PARA CAMPOS (QLineEdit y QComboBox)
# ---------------------------------------------------------
# Este es el bloque que soluciona el problema de alturas
# y evita que el texto quede cortado por arriba o por abajo.


def aplicar_estilo_campo(widget):
    """
    Aplica estilo coherente a QLineEdit y QComboBox:
    - Fuente uniforme
    - Altura mínima suficiente
    - Padding interno
    - Coherencia visual en todo el formulario
    """
    widget.setFont(FUENTE_NORMAL)
    widget.setMinimumHeight(30)  # altura perfecta para evitar cortes
    widget.setContentsMargins(4, 4, 4, 4)

    # Para QLineEdit añadimos un pequeño padding interno
    if isinstance(widget, QLineEdit):
        widget.setStyleSheet("""
            QLineEdit {
                padding: 4px;
            }
            """)

    # Para QComboBox ajustamos padding y altura del desplegable
    if isinstance(widget, QComboBox):
        widget.setStyleSheet("""
            QComboBox {
                padding: 4px;
            }
            QComboBox QAbstractItemView {
                min-height: 28px;
            }
            """)


# ---------------------------------------------------------
# PALETAS DE COLORES
# ---------------------------------------------------------

PALETA_CLARA = {
    "fondo": "#FFFFFF",
    "panel": "#F7F7F7",
    "texto": COLOR_TEXTO,
    "boton": COLOR_SECUNDARIO,
    "boton_principal": COLOR_PRIMARIO,
    "acento": COLOR_ACENTO,
}

PALETA_OSCURA = {
    "fondo": "#1E1E1E",
    "panel": "#2C2C2C",
    "texto": "#E0E0E0",
    "boton": "#3A3A3A",
    "boton_principal": "#4A90E2",
    "acento": "#F5A623",
}

PALETA_SOLARIZADA = {
    "fondo": "#FDF6E3",
    "panel": "#EEE8D5",
    "texto": "#657B83",
    "boton": "#EEE8D5",
    "boton_principal": "#268BD2",
    "acento": "#B58900",
}

PALETAS = {
    "Clara": PALETA_CLARA,
    "Oscura": PALETA_OSCURA,
    "Solarizada": PALETA_SOLARIZADA,
}

# ---------------------------------------------------------
# GENERADOR DE STYLESHEET GLOBAL
# ---------------------------------------------------------


def generar_stylesheet(paleta):
    return f"""
        QWidget {{
            background-color: {paleta["fondo"]};
            color: {paleta["texto"]};
        }}

        QScrollArea {{
            background-color: {paleta["panel"]};
        }}

        QPushButton {{
            background-color: {paleta["boton"]};
            color: {paleta["texto"]};
            border-radius: 6px;
            padding: 6px 10px;
            text-align: left;
        }}

        QPushButton:hover {{
            background-color: {paleta["acento"]};
        }}
    """


def color_estado(estado):
    estado = estado.upper().strip()
    if estado == "ACTIVO":
        return QColor("green")
    if estado == "ANULADO":
        return QColor("red")
    return QColor(COLOR_TEXTO)


def color_fila_estado(estado):
    estado = estado.upper().strip()
    if estado == "ACTIVO":
        return QColor("darkgreen")
    if estado == "ANULADO":
        return QColor("darkred")
    return QColor(COLOR_TEXTO)
