# -------------------------------------------------------------#
# Módulo: lista_contratos_factura.py                           #
# Descripción: Selección de contrato para facturas             #
# Autor: Antonio Morales                                       #
# Fecha: 2026-02-10                                            #
# -------------------------------------------------------------#

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ListaContratosFactura(QWidget):
    """
    Módulo específico para facturas.
    Selecciona un contrato y abre:
      - Nueva factura
      - Seleccionar factura (rectificar/anular)
    según el modo recibido.
    """

    def __init__(self, parent=None, modo="nuevo"):
        super().__init__(parent)
        self.parent = parent
        self.modo = modo  # nuevo / rectificar / anular

        # Conexión a BD heredada del MainWindow
        self.conn = self.parent.conn
        self.cur = self.conn.cursor()

        self.crear_ui()
        self.cargar_datos()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def crear_ui(self):
        layout = QVBoxLayout(self)

        titulo = QLabel("Seleccionar contrato")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels(
            [
                "Contrato",
                "Suplemento",
                "Fec_inicio",
                "Compañía",
                "C.P.",
                "Inicio",
                "Final",
                "Anulación",
            ]
        )
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.tabla)

        # Botones
        botones = QHBoxLayout()

        btn_sel = QPushButton("Seleccionar contrato")
        btn_sel.clicked.connect(self.seleccionar_contrato)
        botones.addWidget(btn_sel)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.cancelar)
        botones.addWidget(btn_cancelar)

        layout.addLayout(botones)

    # ---------------------------------------------------------
    # Cargar datos desde vista_contratos
    # ---------------------------------------------------------
    def cargar_datos(self):
        query = """
            SELECT ncontrato, suplemento, compania, codigo_postal,
                    efec_suple, fin_suple, fec_anulacion, fec_inicio
                FROM vista_contratos
                WHERE
                    DATE('now') BETWEEN efec_suple AND fin_suple
                    OR
                    (suplemento = 0 AND DATE('now') < efec_suple)
                ORDER BY ncontrato ASC, suplemento ASC;
        """

        self.cur.execute(query)
        rows = self.cur.fetchall()

        self.tabla.setRowCount(len(rows))

        for r, row in enumerate(rows):
            (
                ncontrato,
                suplemento,
                compania,
                cp,
                efec,
                fin,
                anul,
                fec_inicio,
            ) = row

            valores = [
                ncontrato,
                suplemento,
                fec_inicio,
                compania,
                cp,
                efec,
                fin,
                anul,
            ]

            for c, value in enumerate(valores):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.tabla.setItem(r, c, item)

    # ---------------------------------------------------------
    # Selección de contrato
    # ---------------------------------------------------------
    def seleccionar_contrato(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Debe seleccionar un contrato.")
            return

        ncontrato = self.tabla.item(row, 0).text()
        suplemento = self.tabla.item(row, 1).text()

        mw = self.window()

        # --- NUEVA FACTURA ---
        if self.modo == "nuevo":
            from facturas.nueva_factura import NuevaFactura

            widget = NuevaFactura(
                parent=mw,
                conn=self.conn,
                ncontrato=ncontrato,
                suplemento=suplemento,
            )

            mw.cargar_modulo(widget, f"Nueva factura – Contrato {ncontrato}")
            return

        # --- RECTIFICAR / ANULAR FACTURA ---
        from facturas.seleccionar_factura import SeleccionarFactura

        widget = SeleccionarFactura(
            parent=mw,
            conn=self.conn,
            ncontrato=ncontrato,
            modo=self.modo,  # rectificar o anular
        )

        mw.cargar_modulo(widget, f"Seleccionar factura – Contrato {ncontrato}")

    # ---------------------------------------------------------
    # Cancelar
    # ---------------------------------------------------------
    def cancelar(self):
        mw = self.window()
        mw.volver_inicio()
