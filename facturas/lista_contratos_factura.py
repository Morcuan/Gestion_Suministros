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
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from utilidades.logica_negocio import determinar_estado_contrato


class ListaContratosFactura(QWidget):
    def __init__(self, parent=None, modo="nuevo"):
        super().__init__(parent)
        self.parent = parent
        self.modo = modo

        self.conn = self.parent.conn
        self.cur = self.conn.cursor()

        self.crear_ui()
        self.cargar_datos()

    def crear_ui(self):
        layout = QVBoxLayout(self)

        titulo = QLabel("Seleccionar contrato")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(9)
        self.tabla.setHorizontalHeaderLabels(
            [
                "Contrato",
                "Sup.",  # <<< Ajustado
                "Fec_inicio",
                "Compañía",
                "C.P.",
                "Inicio",
                "Final",
                "Anulación",
                "Estado",
            ]
        )
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)

        # --- Ajuste fino por columnas ---
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Contrato
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Sup.
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Fec_inicio
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Compañía
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # C.P.
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Inicio
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Final
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Anulación
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Estado

        layout.addWidget(self.tabla)

        botones = QHBoxLayout()

        btn_sel = QPushButton("Seleccionar contrato")
        btn_sel.clicked.connect(self.seleccionar_contrato)
        botones.addWidget(btn_sel)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.cancelar)
        botones.addWidget(btn_cancelar)

        layout.addLayout(botones)

    def cargar_datos(self):
        query = """
            SELECT ncontrato, suplemento, compania, codigo_postal,
                   efec_suple, fin_suple, fec_anulacion, fec_inicio
            FROM vista_contratos
            WHERE DATE('now') BETWEEN efec_suple AND fin_suple
               OR (suplemento = 0 AND DATE('now') < efec_suple)
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

            # Obtener todas las fechas de efecto del contrato
            self.cur.execute(
                "SELECT efec_suple FROM contratos_identificacion WHERE ncontrato = ?",
                (ncontrato,),
            )
            fechas = [f[0] for f in self.cur.fetchall()]

            estado = determinar_estado_contrato(
                efec_suple=efec,
                fin_suple=fin,
                fec_anulacion=anul,
                lista_fechas_efecto=fechas,
            )

            valores = [
                ncontrato,
                suplemento,
                fec_inicio,
                compania,
                cp,
                efec,
                fin,
                anul,
                estado,
            ]

            for c, value in enumerate(valores):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.tabla.setItem(r, c, item)

    def seleccionar_contrato(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Debe seleccionar un contrato.")
            return

        ncontrato = self.tabla.item(row, 0).text()
        suplemento = self.tabla.item(row, 1).text()

        mw = self.window()

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

        from facturas.seleccionar_factura import SeleccionarFactura

        widget = SeleccionarFactura(
            parent=mw,
            conn=self.conn,
            ncontrato=ncontrato,
            modo=self.modo,
        )
        mw.cargar_modulo(widget, f"Seleccionar factura – Contrato {ncontrato}")

    def cancelar(self):
        mw = self.window()
        mw.volver_inicio()
