# -------------------------------------------------------------#
# Módulo: seleccionar_his_factura.py                           #
# Descripción: Selección de facturas de un contrato (histórico)#
# Autor: Antonio Morales                                       #
# Fecha: 2026-03-31                                            #
# -------------------------------------------------------------#

from PySide6.QtCore import Qt
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


class SeleccionarHisFactura(QWidget):
    def __init__(self, parent=None, conn=None, ncontrato=None):
        super().__init__(parent)
        self.parent = parent
        self.conn = conn
        self.ncontrato = ncontrato

        self.init_ui()
        self.cargar_facturas()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def init_ui(self):
        layout = QVBoxLayout(self)

        # *** TÍTULO ELIMINADO ***
        # La MainWindow ya pone el título centrado

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

        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Nº Factura
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Fecha emisión
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Inicio periodo
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Fin periodo
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Importe total

        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.tabla)

        # -----------------------------------------------------
        # BOTONES
        # -----------------------------------------------------
        botones = QHBoxLayout()

        self.btn_seleccionar = QPushButton("Seleccionar factura")
        self.btn_seleccionar.clicked.connect(self.on_seleccionar_factura)
        botones.addWidget(self.btn_seleccionar)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.on_cancelar)
        botones.addWidget(self.btn_cancelar)

        layout.addLayout(botones)

    # ---------------------------------------------------------
    # Cargar facturas
    # ---------------------------------------------------------
    def cargar_facturas(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT f.nfactura,
                f.fec_emision,
                f.inicio_factura,
                f.fin_factura,
                ROUND(COALESCE(fc.total_final, 0), 2) AS total
            FROM facturas f
            LEFT JOIN factura_calculos fc USING(nfactura)
            WHERE f.ncontrato = ?
            ORDER BY f.inicio_factura ASC
            """,
            (self.ncontrato,),
        )

        filas = cursor.fetchall()
        self.tabla.setRowCount(len(filas))

        for i, fila in enumerate(filas):
            for j, valor in enumerate(fila):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.tabla.setItem(i, j, item)

    # ---------------------------------------------------------
    # Utilidades selección
    # ---------------------------------------------------------
    def obtener_factura_seleccionada(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return None
        return self.tabla.item(fila, 0).text()

    # ---------------------------------------------------------
    # Eventos
    # ---------------------------------------------------------
    def on_seleccionar_factura(self):
        nfactura = self.obtener_factura_seleccionada()
        if not nfactura:
            QMessageBox.warning(self, "Aviso", "Debe seleccionar una factura.")
            return

        from analisis_factura.formulario_his_factura import FormularioHisFactura

        mw = self.window()
        widget = FormularioHisFactura(
            parent=mw,
            conn=self.conn,
            nfactura=nfactura,
        )
        mw.cargar_modulo(widget, f"Detalle factura {nfactura}")

    def on_cancelar(self):
        # Volver a la lista de contratos (Pantalla 1)
        from analisis_factura.lista_con_his_factura import ListaConHisFactura

        mw = self.window()
        widget = ListaConHisFactura(parent=mw)
        mw.cargar_modulo(widget, "Seleccionar contrato")
