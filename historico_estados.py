# ------------------------------------------------------#
# Modulo: historico_estados.py                          #
# Descripcion: Ventana para mostrar el histórico de     #
#   estados de un contrato.                             #
# Autor: Antonio Morales                                #
# Fecha: 2025-12-XX                                     #
# ------------------------------------------------------#

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from aux_database import obtener_historico_estados


class HistoricoEstadosWidget(QWidget):
    def __init__(self, numero_contrato, parent=None):
        super().__init__(parent)
        self.numero_contrato = numero_contrato

        self.setWindowTitle(f"Histórico de estados — Contrato {numero_contrato}")
        self.resize(450, 300)

        layout = QVBoxLayout(self)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(2)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Estado"])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.tabla)

        # Botón cerrar
        botones = QHBoxLayout()
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        botones.addStretch()
        botones.addWidget(btn_cerrar)
        layout.addLayout(botones)

        # Cargar datos
        self.cargar_historico()

    # --------------------------------------------------

    def cargar_historico(self):
        """
        Carga el histórico de estados del contrato en la tabla,
        mostrando la fecha en formato dd/mm/yyyy.
        """
        datos = obtener_historico_estados(self.numero_contrato)

        # Si no hay movimientos, avisamos y dejamos la ventana abierta
        if not datos:
            QMessageBox.information(
                self,
                "Sin movimientos",
                "Este contrato no tiene movimientos registrados.",
            )
            self.tabla.setRowCount(0)
            return

        self.tabla.setRowCount(0)

        for fila, (fecha_iso, estado) in enumerate(datos):
            fecha_natural = datetime.strptime(fecha_iso, "%Y-%m-%d").strftime(
                "%d/%m/%Y"
            )

            self.tabla.insertRow(fila)
            self.tabla.setItem(fila, 0, QTableWidgetItem(fecha_natural))
            self.tabla.setItem(fila, 1, QTableWidgetItem(estado))
