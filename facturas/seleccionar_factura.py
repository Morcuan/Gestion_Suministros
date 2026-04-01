# -------------------------------------------------------------#
# Módulo: seleccionar_factura.py                               #
# Descripción: Selección de facturas de un contrato            #
# Autor: Antonio Morales                                       #
# Fecha: 2026-03-31                                            #
# -------------------------------------------------------------#

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class SeleccionarFactura(QWidget):
    def __init__(self, parent=None, conn=None, ncontrato=None, modo="rectificar"):
        super().__init__(parent)
        self.parent = parent
        self.conn = conn
        self.ncontrato = ncontrato
        self.modo = modo

        self.init_ui()
        self.cargar_facturas()

    # ---------------------------------------------------------
    def init_ui(self):
        layout = QVBoxLayout(self)

        titulo = QLabel(f"Facturas del contrato {self.ncontrato}")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            [
                "Nº Factura",
                "Fecha emisión",
                "Inicio periodo",
                "Fin periodo",
                "Importe total",
            ]
        )

        # Mejoras visuales
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStretchLastSection(True)

        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.tabla)

        botones = QHBoxLayout()
        self.btn_seleccionar = QPushButton("Seleccionar factura")
        self.btn_seleccionar.clicked.connect(self.on_seleccionar_factura)
        botones.addWidget(self.btn_seleccionar)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.parent.volver_menu_principal)
        botones.addWidget(self.btn_cancelar)

        layout.addLayout(botones)

    # ---------------------------------------------------------
    def cargar_facturas(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT f.nfactura,
                   f.fec_emision,
                   f.inicio_factura,
                   f.fin_factura,
                   COALESCE(fc.total_final, 0)
            FROM facturas f
            LEFT JOIN factura_calculos fc USING(nfactura)
            WHERE f.ncontrato = ?
            ORDER BY f.fec_emision DESC
        """,
            (self.ncontrato,),
        )

        filas = cursor.fetchall()
        self.tabla.setRowCount(len(filas))

        for i, fila in enumerate(filas):
            for j, valor in enumerate(fila):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(i, j, item)

    # ---------------------------------------------------------
    def obtener_factura_seleccionada(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return None
        return self.tabla.item(fila, 0).text()

    # ---------------------------------------------------------
    def on_seleccionar_factura(self):
        nfactura = self.obtener_factura_seleccionada()
        if not nfactura:
            QMessageBox.warning(self, "Aviso", "Debe seleccionar una factura.")
            return

        from facturas.control_rectif_anular import ControlRectifAnular

        widget = ControlRectifAnular(
            parent=self.parent,
            conn=self.conn,
            modo="edicion" if self.modo == "rectificar" else "anulacion",
            nfactura=nfactura,
        )

        self.parent.cargar_modulo(
            widget,
            "Rectificar factura" if self.modo == "rectificar" else "Anular factura",
        )
