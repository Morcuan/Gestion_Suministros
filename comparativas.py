# -----------------------------------------------------------------#
# Módulo: comparativas.py                                         #
# Descripción: Contiene la clase ComparativasWidget que           #
#              define el widget para la sección de comparativas   #
# El modulo comparativas se encargará de gestionar la comparativa #
# de diferentes contratos y facturas de electricidad contra otros #
# disponibles en el mercado, permitiendo al usuario evaluar si su #
# contrato actual es competitivo o si existen mejores opciones.   #
# Autor: Antonio Morales                                          #
# Fecha: 2025-12-20                                               #
# -----------------------------------------------------------------#

# Importaciones necesarias
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


# Clase ComparativasWidget -inicio-
class ComparativasWidget(QWidget):
    def __init__(self):
        super().__init__()
        fuente = QFont("Noto Sans", 12)
        self.setFont(fuente)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Aquí irá el formulario de Comparativas"))
        self.setLayout(layout)


# Clase ComparativasWidget -fin-
# -----------------------------------------------------------------#
