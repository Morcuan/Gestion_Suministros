# -------------------------------------------------------------#
# Módulo: lista_contratos_historico.py                         #
# Descripción: Selección de contratos (Histórico)              #
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

from analisis_contrato.lista_suplementos_historico import ListaSuplementosHistorico
from utilidades.logica_negocio import determinar_estado_contrato


class ListaContratosHistorico(QWidget):
    def __init__(self, parent=None, conn=None):
        super().__init__(parent)

        self.main_window = parent
        self.conn = conn
        self.cur = conn.cursor()

        self.crear_ui()
        self.cargar_datos()

    # ---------------------------------------------------------
    # INTERFAZ
    # ---------------------------------------------------------
    def crear_ui(self):
        layout = QVBoxLayout(self)

        titulo = QLabel("Listado de contratos (Histórico)")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["Contrato", "Compañía", "C.P.", "Población", "Fecha inicio", "Estado"]
        )
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)

        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

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
    # CARGA DE DATOS
    # ---------------------------------------------------------
    def cargar_datos(self):
        """
        Carga todos los contratos (suplemento 0).
        """

        query = """
            SELECT ncontrato, compania, codigo_postal, poblacion,
                   fec_inicio, efec_suple, fin_suple, fec_anulacion
            FROM vista_contratos
            WHERE suplemento = 0
            ORDER BY ncontrato ASC;
        """

        self.cur.execute(query)
        rows = self.cur.fetchall()

        self.tabla.setRowCount(0)

        for fila, row in enumerate(rows):
            (
                ncontrato,
                compania,
                cp,
                poblacion,
                fec_inicio,
                efec_suple,
                fin_suple,
                fec_anulacion,
            ) = row

            # Obtener todas las fechas de efecto del contrato
            self.cur.execute(
                "SELECT efec_suple FROM contratos_identificacion WHERE ncontrato = ?",
                (ncontrato,),
            )
            fechas = [f[0] for f in self.cur.fetchall()]

            estado = determinar_estado_contrato(
                efec_suple=efec_suple,
                fin_suple=fin_suple,
                fec_anulacion=fec_anulacion,
                lista_fechas_efecto=fechas,
            )

            valores = [
                ncontrato,
                compania,
                cp,
                poblacion,
                fec_inicio,
                estado,
            ]

            self.tabla.insertRow(fila)

            for col, value in enumerate(valores):
                item = QTableWidgetItem("" if value is None else str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.tabla.setItem(fila, col, item)

    # ---------------------------------------------------------
    # ACCIONES
    # ---------------------------------------------------------
    def seleccionar_contrato(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Debe seleccionar un contrato.")
            return

        ncontrato = self.tabla.item(row, 0).text()

        widget = ListaSuplementosHistorico(
            parent=self.main_window,
            conn=self.conn,
            ncontrato=ncontrato,
        )

        self.main_window.cargar_modulo(widget, f"Suplementos {ncontrato}")

    def cancelar(self):
        self.main_window.volver_inicio()
