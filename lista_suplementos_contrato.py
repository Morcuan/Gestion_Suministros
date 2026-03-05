# --------------------------------------------#
# Modulo: lista_suplementos_contrato.py
# Descripción: Lista de suplementos de un contrato
#              para acceder al detalle histórico.
# Autor: Antonio Morales + Copilot
# Fecha: 2026-03-05
# --------------------------------------------#

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from db import get_conn
from detalles_movimiento import DetallesMovimiento


class ListaSuplementosContrato(QWidget):
    """
    Lista de suplementos del contrato seleccionado.
    """

    def __init__(self, parent=None, ncontrato=None):
        super().__init__(parent)

        self.setWindowTitle(f"Suplementos del contrato {ncontrato}")
        self.conn = get_conn()
        self.ncontrato = ncontrato

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Supl.", "Inicio", "Efecto", "Estado"])

        # Botones
        self.btn_detalles = QPushButton("Detalles")
        self.btn_cerrar = QPushButton("Cancelar")

        self.btn_detalles.clicked.connect(self.abrir_detalles)
        self.btn_cerrar.clicked.connect(self.volver_lista_contratos)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Suplementos del contrato {ncontrato}:"))
        layout.addWidget(self.tabla)

        botones = QHBoxLayout()
        botones.addWidget(self.btn_detalles)
        botones.addStretch()
        botones.addWidget(self.btn_cerrar)

        layout.addLayout(botones)
        self.setLayout(layout)

        self.cargar_suplementos()

    # ------------------------------------------------------------
    # Cargar suplementos del contrato
    # ------------------------------------------------------------
    def cargar_suplementos(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT suplemento, fec_inicio, efec_suple, estado
            FROM vista_contratos
            WHERE ncontrato = ?
            ORDER BY suplemento ASC
            """,
            (self.ncontrato,),
        )

        lista = cursor.fetchall()
        self.tabla.setRowCount(len(lista))

        for i, row in enumerate(lista):
            suplemento, fec_inicio, efec_suple, estado = row

            datos = [
                suplemento,
                fec_inicio,
                efec_suple,
                estado,
            ]

            for j, value in enumerate(datos):
                self.tabla.setItem(i, j, QTableWidgetItem(str(value)))

        self.tabla.resizeColumnsToContents()
        self.tabla.horizontalHeader().setStretchLastSection(True)

    # ------------------------------------------------------------
    # Obtener MainWindow real
    # ------------------------------------------------------------
    def get_mainwindow(self):
        w = self.parent()
        while w is not None and not hasattr(w, "cargar_modulo"):
            w = w.parent()
        return w

    # ------------------------------------------------------------
    # Abrir detalles del suplemento (ventana C)
    # ------------------------------------------------------------
    def abrir_detalles(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Atención", "Debe seleccionar un suplemento.")
            return

        suplemento = self.tabla.item(fila, 0).text()

        main = self.get_mainwindow()
        widget = DetallesMovimiento(
            parent=main,
            conn=self.conn,  # ← AÑADIDO
            ncontrato=self.ncontrato,
            suplemento=suplemento,
        )
        main.cargar_modulo(
            widget, f"Suplemento {suplemento} del contrato {self.ncontrato}"
        )

    # ------------------------------------------------------------
    # Volver a la lista de contratos (ventana A)
    # ------------------------------------------------------------
    def volver_lista_contratos(self):
        from lista_contratos_historia import ListaContratosHistoria

        main = self.get_mainwindow()
        widget = ListaContratosHistoria(parent=main)
        main.cargar_modulo(widget, "Histórico contratos")
