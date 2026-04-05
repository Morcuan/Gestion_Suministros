# -------------------------------------------------------------#
# Módulo: lista_suplementos_historico.py                       #
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

from analisis_contrato.formulario_contrato_historico import FormularioContratoHistorico


class ListaSuplementosHistorico(QWidget):
    def __init__(self, parent=None, conn=None, ncontrato=None):
        super().__init__(parent)

        self.main_window = parent
        self.conn = conn
        self.cur = conn.cursor()
        self.ncontrato = ncontrato

        self.crear_ui()
        self.cargar_datos()

    def crear_ui(self):
        layout = QVBoxLayout(self)

        titulo = QLabel(f"Suplementos del contrato: {self.ncontrato}")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["Suplemento", "Efecto", "Fin", "Compañía", "C.P.", "Anulación"]
        )
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)

        header = self.tabla.horizontalHeader()

        # Ajustes de ancho
        self.tabla.setColumnWidth(0, 240)  # Suplemento (más grande)
        self.tabla.setColumnWidth(1, 110)  # Efecto
        self.tabla.setColumnWidth(2, 110)  # Fin
        self.tabla.setColumnWidth(3, 160)  # Compañía
        self.tabla.setColumnWidth(4, 80)  # CP
        self.tabla.setColumnWidth(5, 120)  # Anulación

        # Suplemento absorbe el espacio sobrante
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        layout.addWidget(self.tabla)

        botones = QHBoxLayout()

        btn_sel = QPushButton("Seleccionar suplemento")
        btn_sel.clicked.connect(self.seleccionar_suplemento)
        botones.addWidget(btn_sel)

        btn_volver = QPushButton("Volver a contratos")
        btn_volver.clicked.connect(self.volver_contratos)
        botones.addWidget(btn_volver)

        layout.addLayout(botones)

    def cargar_datos(self):
        query = """
            SELECT suplemento, efec_suple, fin_suple,
                   compania, codigo_postal, fec_anulacion
            FROM vista_contratos
            WHERE ncontrato = ?
            ORDER BY suplemento ASC;
        """

        self.cur.execute(query, (self.ncontrato,))
        rows = self.cur.fetchall()

        self.tabla.setRowCount(0)

        for fila, row in enumerate(rows):
            suplemento, efec, fin, comp, cp, anul = row

            self.tabla.insertRow(fila)

            sup_texto = "Contrato original" if suplemento == 0 else str(suplemento)

            valores = [sup_texto, efec, fin, comp, cp, anul]

            for col, value in enumerate(valores):
                item = QTableWidgetItem("" if value is None else str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)

                if suplemento == 0:
                    item.setForeground(Qt.blue)
                elif anul:
                    item.setForeground(Qt.gray)

                self.tabla.setItem(fila, col, item)

    def seleccionar_suplemento(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Debe seleccionar un suplemento.")
            return

        sup_texto = self.tabla.item(row, 0).text()
        suplemento = 0 if sup_texto == "Contrato original" else int(sup_texto)

        widget = FormularioContratoHistorico(
            parent=self.main_window,
            conn=self.conn,
            ncontrato=self.ncontrato,
            suplemento=suplemento,
        )

        self.main_window.cargar_modulo(
            widget,
            f"Histórico contrato {self.ncontrato} — Suplemento {suplemento}",
        )

    def volver_contratos(self):
        from analisis_contrato.lista_contratos_historico import ListaContratosHistorico

        widget = ListaContratosHistorico(
            parent=self.main_window,
            conn=self.conn,
        )
        self.main_window.cargar_modulo(widget, "Histórico — Contratos")
