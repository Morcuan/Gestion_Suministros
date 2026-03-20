# -------------------------------------------------------------#
# Modulo: nuevo_contrato.py                                    #
# Descripción: Controlador inicial del proceso Nuevo Contrato  #
# Autor: Antonio Morales                                       #
# Fecha: 2026-02-10                                            #
# -------------------------------------------------------------#

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QWidget

from contratos.formulario_contrato import FormularioContrato
from utilidades.utilidades_bd import obtener_companias


class NuevoContrato(QWidget):
    """
    Controlador del proceso de alta de contrato.
    Versión inicial: solo muestra el formulario incrustado.
    """

    cerrado = Signal()  # Señal para volver al inicio

    def __init__(self, parent=None):
        super().__init__(parent)

        # ---------------------------------------------------------
        # ACCESO A BD (heredado de MainWindow)
        # ---------------------------------------------------------
        self.conn = parent.conn
        self.cursor = parent.cursor

        # ---------------------------------------------------------
        # LAYOUT PRINCIPAL
        # ---------------------------------------------------------
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # ---------------------------------------------------------
        # FORMULARIO
        # ---------------------------------------------------------
        self.formulario = FormularioContrato(parent=self)
        self.formulario.set_modo("nuevo")  # ← MODO NUEVO ACTIVADO
        layout.addWidget(self.formulario)

        # ---------------------------------------------------------
        # CARGA DE COMPAÑÍAS DESDE BD
        # ---------------------------------------------------------
        lista = obtener_companias(self.cursor)  # ← OBTENEMOS LISTA
        self.formulario.cargar_companias(lista)  # ← CARGAMOS EN EL FORMULARIO

        # ---------------------------------------------------------
        # CONEXIONES BÁSICAS (sin lógica aún)
        # ---------------------------------------------------------
        self.formulario.btn_guardar.clicked.connect(self.guardar)
        self.formulario.btn_cancelar.clicked.connect(self.cancelar)

    # ---------------------------------------------------------
    # ACCIONES BÁSICAS
    # ---------------------------------------------------------
    def guardar(self):
        """
        Acción temporal para el botón Guardar.
        Más adelante se implementará la lógica real.
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("Guardar contrato")
        msg.setText("Funcionalidad pendiente de implementar.")
        msg.exec()

    def cancelar(self):
        """Cierra el módulo y vuelve al inicio."""
        self.cerrado.emit()
