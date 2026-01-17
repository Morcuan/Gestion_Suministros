# -----------------------------------------------#
# Modulo: facturas.py                           #
# Descripcion: Contiene la clase FacturasWidget #
# Autor: Antonio Morales                        #
# Fecha: 2024-06-20                             #
# -----------------------------------------------#

# Importaciones librerias necesarias PySide6
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QFont


# Clase FacturasWidget
class FacturasWidget(QWidget):
    def __init__(self):
        super().__init__()
        fuente = QFont("Noto Sans", 12)
        self.setFont(fuente)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Aquí irá el formulario de Facturas/Consumos"))
        self.setLayout(layout)


# Fin de la clase FacturasWidget
