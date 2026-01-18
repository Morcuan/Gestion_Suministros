# -----------------------------------#
# Modulo: consumos.py               #
# Descripcion: Widget para Consumos #
# Autor: Antonio Morales            #
# Fecha: 2025-12-01                 #
# -----------------------------------#

# Importaciones necesarias de PySide6
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


# Definicion del widget ConsumosWidget
class ConsumosWidget(QWidget):
    # Constructor del widget
    def __init__(self):
        super().__init__()
        fuente = QFont("Noto Sans", 12)
        self.setFont(fuente)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Aquí irá el formulario de Consumos"))
        self.setLayout(layout)
