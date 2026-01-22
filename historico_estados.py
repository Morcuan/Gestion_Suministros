# ------------------------------------------------------#
# Modulo: historico_estados.py                          #
# Descripcion: Ventana para mostrar el histórico de     #
#   estados de un contrato.                             #
# Autor: Antonio Morales                                #
# Fecha: 2025-12-XX                                     #
# ------------------------------------------------------#

from datetime import datetime

from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
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

        # Ajuste de columnas para que se vea fecha + hora
        self.tabla.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

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
        mostrando la fecha en formato dd/mm/yyyy hh:mm:ss si existe.
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

            # Conversión robusta: acepta "YYYY-MM-DD" y "YYYY-MM-DD HH:MM:SS"
            try:
                dt = datetime.strptime(fecha_iso, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dt = datetime.strptime(fecha_iso, "%Y-%m-%d")

            # Mostrar fecha + hora si existe
            fecha_natural = dt.strftime("%d/%m/%Y %H:%M:%S")

            self.tabla.insertRow(fila)
            self.tabla.setItem(fila, 0, QTableWidgetItem(fecha_natural))
            self.tabla.setItem(fila, 1, QTableWidgetItem(estado))
