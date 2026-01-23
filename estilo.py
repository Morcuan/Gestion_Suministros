# estilo.py
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QPushButton

# Paleta base (DRU)
COLOR_PRIMARIO = "#4A90E2"  # azul suave
COLOR_SECUNDARIO = "#F0F0F0"  # gris claro
COLOR_ACENTO = "#F5A623"  # naranja suave
COLOR_ERROR = "#D0021B"  # rojo suave
COLOR_TEXTO = "#333333"  # gris oscuro

# Tipografías
FUENTE_TITULO = QFont("DejaVu Sans", 16)
FUENTE_NORMAL = QFont("DejaVu Sans", 13)
FUENTE_BOTON = QFont("DejaVu Sans", 12)


def aplicar_estilo_panel_lateral(widget):
    widget.setStyleSheet(
        """
        background-color: #F7F7F7;
        border-right: 1px solid #CCCCCC;
    """
    )


def aplicar_estilo_boton(boton: QPushButton, principal=False):
    boton.setFont(FUENTE_BOTON)
    boton.setStyleSheet(
        f"""
        QPushButton {{
            background-color: {'{0}'.format(COLOR_PRIMARIO) if principal else COLOR_SECUNDARIO};
            color: {COLOR_TEXTO};
            border-radius: 6px;
            padding: 6px 10px;
            text-align: left;
        }}
        QPushButton:hover {{
            background-color: {COLOR_ACENTO};
        }}
    """
    )
