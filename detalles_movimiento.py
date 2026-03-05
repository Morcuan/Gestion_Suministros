# --------------------------------------------#
# Modulo: detalles_movimiento.py
# Descripción: Detalle de un suplemento concreto
#              usando DetallesContratoWidget.
# Autor: Antonio Morales + Copilot
# Fecha: 2026-03-05
# --------------------------------------------#

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from detalles_contrato import DetallesContratoWidget


class DetallesMovimiento(QWidget):
    """
    Muestra los detalles de un suplemento concreto (ncontrato + suplemento)
    reutilizando DetallesContratoWidget.
    """

    def __init__(self, parent=None, conn=None, ncontrato=None, suplemento=None):

        super().__init__(parent)

        self.setWindowTitle(f"Suplemento {suplemento} del contrato {ncontrato}")
        self.conn = conn

        self.ncontrato = ncontrato
        self.suplemento = suplemento

        layout = QVBoxLayout()
        layout.addWidget(
            QLabel(f"Detalles del suplemento {suplemento} del contrato {ncontrato}:")
        )

        # Widget reutilizado SIN botones internos
        self.detalles = DetallesContratoWidget(
            self.conn,
            ncontrato,
            suplemento,
            parent=self,
            mostrar_botones=False,  # ← CLAVE
        )

        layout.addWidget(self.detalles)

        # Botón cancelar centrado
        botonera = QHBoxLayout()
        botonera.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.volver_suplementos)
        botonera.addWidget(btn_cancelar)
        botonera.addStretch()

        layout.addLayout(botonera)

        self.setLayout(layout)

    # ------------------------------------------------------------
    # Volver a la lista de suplementos (ventana B)
    # ------------------------------------------------------------
    def volver_suplementos(self):
        from lista_suplementos_contrato import ListaSuplementosContrato

        main = self.get_mainwindow()
        widget = ListaSuplementosContrato(parent=main, ncontrato=self.ncontrato)
        main.cargar_modulo(widget, f"Movimientos del contrato {self.ncontrato}")

    # ------------------------------------------------------------
    # Obtener MainWindow real
    # ------------------------------------------------------------
    def get_mainwindow(self):
        w = self.parent()
        while w is not None and not hasattr(w, "cargar_modulo"):
            w = w.parent()
        return w
