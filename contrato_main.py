# ------------------------------------------------------#
# Modulo: contrato_main.py                             #
# Descripcion: Clase principal para gestionar los      #
#   contratos. Abre los módulos: nuevo, consulta,      #
#   modificación y baja.                               #
# Autor: Antonio Morales                               #
# Fecha: 2025-12-01                                    #
# ------------------------------------------------------#

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)
from PySide6.QtCore import Signal

from contrato_consulta import ConsultaContratoWidget
from contrato_nuevo import NuevoContratoWidget
from contrato_modificacion import ContratoModificacion
from contrato_baja import ContratoBaja


# ---------------------------------------------------------
# Ventana para seleccionar un contrato por número
# ---------------------------------------------------------
class SeleccionContratoWindow(QWidget):
    contrato_seleccionado = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar contrato")
        self.resize(300, 150)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Número de contrato")
        layout.addWidget(self.input)

        botones = QHBoxLayout()
        btn_aceptar = QPushButton("Aceptar")
        btn_salir = QPushButton("Salir")

        botones.addWidget(btn_aceptar)
        botones.addWidget(btn_salir)
        layout.addLayout(botones)

        btn_aceptar.clicked.connect(self._on_aceptar)
        btn_salir.clicked.connect(self.close)

    def _on_aceptar(self):
        numero = self.input.text().strip()
        if numero:
            self.contrato_seleccionado.emit(numero)
            self.close()


# ---------------------------------------------------------
# Clase principal para gestionar los contratos
# ---------------------------------------------------------
class ContratoMain:
    def __init__(self, bd):
        self.bd = bd

        # Widgets principales
        self.nuevo = NuevoContratoWidget(bd=self.bd)
        self.consulta = ConsultaContratoWidget()
        self.baja = ContratoBaja(self.bd)

    # -----------------------------------------------------
    def abrir_nuevo(self):
        self.nuevo.abrir()

    # -----------------------------------------------------
    def abrir_consulta(self):
        self.consulta = ConsultaContratoWidget()
        self.consulta.show()

    # -----------------------------------------------------
    def abrir_modificacion(self):
        self.seleccion = SeleccionContratoWindow()
        self.seleccion.contrato_seleccionado.connect(self._abrir_edicion)
        self.seleccion.show()

    # -----------------------------------------------------
    def _abrir_edicion(self, numero_contrato):
        # ContratoModificacion(numero_contrato, parent)
        self.modificacion = ContratoModificacion(numero_contrato, None)
        self.modificacion.show()

    # -----------------------------------------------------
    def abrir_baja(self):
        self.baja.abrir()
