# -------------------------------------------------------------#
# Módulo: lista_con_his_factura.py                             #
# Descripción: Selección de contrato para hist. facturas       #
# Autor: Antonio Morales                                       #
# Fecha: 2026-03                                               #
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


class ListaConHisFactura(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

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

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(
            [
                "Contrato",
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

        # Ajuste de columnas
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Contrato
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Compañía
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # C.P.
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Inicio
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Final
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Anulación
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Estado

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
    # Cargar datos
    # ---------------------------------------------------------
    def cargar_datos(self):
        # Obtener SOLO el último suplemento de cada contrato
        query = """
            SELECT ncontrato, compania, codigo_postal,
                   efec_suple, fin_suple, fec_anulacion
            FROM vista_contratos
            WHERE (ncontrato, suplemento) IN (
                SELECT ncontrato, MAX(suplemento)
                FROM vista_contratos
                GROUP BY ncontrato
            )
            ORDER BY ncontrato ASC;
        """

        self.cur.execute(query)
        rows = self.cur.fetchall()

        self.tabla.setRowCount(len(rows))

        for r, row in enumerate(rows):
            (
                ncontrato,
                compania,
                cp,
                efec,
                fin,
                anul,
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

    # ---------------------------------------------------------
    # Selección
    # ---------------------------------------------------------
    def seleccionar_contrato(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Debe seleccionar un contrato.")
            return

        ncontrato = self.tabla.item(row, 0).text()

        mw = self.window()

        from analisis_factura.seleccionar_his_factura import SeleccionarHisFactura

        widget = SeleccionarHisFactura(
            parent=mw,
            conn=self.conn,
            ncontrato=ncontrato,
        )
        mw.cargar_modulo(widget, f"Seleccionar factura – Contrato {ncontrato}")

    # ---------------------------------------------------------
    # Cancelar
    # ---------------------------------------------------------
    def cancelar(self):
        mw = self.window()
        mw.volver_inicio()
