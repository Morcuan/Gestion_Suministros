# ------------------------------------------------------#
# Modulo: contrato_main.py                             #
# Descripcion: Clase principal para gestionar los      #
#   contratos. Abre los módulos: nuevo, consulta,      #
#   modificación y baja.                               #
# Autor: Antonio Morales                               #
# Fecha: 2025-12-01                                    #
# ------------------------------------------------------#

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Import correcto para edición
from aux_database import obtener_contrato_para_edicion
from contrato_baja import ContratoBaja
from contrato_consulta import ConsultaContratoWidget
from contrato_nuevo import NuevoContratoWidget


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
    # def abrir_consulta(self):
    #    self.consulta = ConsultaContratoWidget(contrato_main=self)

    #    self.consulta.show()

    def abrir_consulta(self):
        self.consulta = ConsultaContratoWidget(contrato_main=self)
        self.consulta.show()

    # -----------------------------------------------------
    def abrir_modificacion(self):
        self.seleccion = SeleccionContratoWindow()
        self.seleccion.contrato_seleccionado.connect(self._abrir_edicion)
        self.seleccion.show()

    # -----------------------------------------------------
    def _abrir_edicion(self, numero_contrato):
        # Recuperar datos en el formato correcto para edición
        datos = obtener_contrato_para_edicion(numero_contrato)

        if not datos:
            QMessageBox.warning(
                None,
                "Contrato no encontrado",
                f"No existe el contrato {numero_contrato}.",
            )
            return

        # Abrir ventana moderna en modo edición
        self.modificacion = NuevoContratoWidget(modo="edicion", datos=datos, bd=self.bd)
        self.modificacion.abrir()

    # -----------------------------------------------------
    def abrir_baja(self):
        self.seleccion = SeleccionContratoWindow()
        self.seleccion.contrato_seleccionado.connect(self._abrir_baja_real)
        self.seleccion.show()

    def _abrir_baja_real(self, numero_contrato):
        self.baja.parent = None  # o self.consulta si quieres refrescar lista
        self.baja.abrir(numero_contrato)
