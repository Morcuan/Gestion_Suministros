# -------------------------------------------------------------#
# Módulo: lista_contratos_precios.py
# Descripción: Selección de contrato para análisis histórico
#              de precios
# Autor: Antonio Morales
# Fecha: 2026-10
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


class ListaContratosPrecios(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.conn = self.parent.conn
        self.cur = self.conn.cursor()

        self.crear_ui()
        self.cargar_datos()

    def crear_ui(self):

        layout = QVBoxLayout(self)

        titulo = QLabel(
            "Seleccione un contrato para analizar su evolución histórica de precios"
        )

        titulo.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        self.tabla = QTableWidget()

        self.tabla.setColumnCount(8)

        self.tabla.setHorizontalHeaderLabels(
            [
                "Contrato",
                "Fec_inicio",
                "Compañía",
                "C.P.",
                "Inicio",
                "Final",
                "Anulación",
                "Estado",
            ]
        )

        self.tabla.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.tabla.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.tabla)

        botones = QHBoxLayout()

        btn_sel = QPushButton("Analizar contrato")
        btn_sel.clicked.connect(self.seleccionar_contrato)
        botones.addWidget(btn_sel)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.cancelar)
        botones.addWidget(btn_cancelar)

        layout.addLayout(botones)

    def cargar_datos(self):

        query = """
            SELECT vc.ncontrato,
                   vc.compania,
                   vc.codigo_postal,
                   vc.efec_suple,
                   vc.fin_suple,
                   vc.fec_anulacion,
                   vc.fec_inicio
            FROM vista_contratos vc
            WHERE vc.suplemento = (
                    SELECT MAX(v2.suplemento)
                    FROM vista_contratos v2
                    WHERE v2.ncontrato = vc.ncontrato
                  )
              AND (
                    DATE('now') BETWEEN vc.efec_suple AND vc.fin_suple
                    OR DATE('now') < vc.efec_suple
                  )
            ORDER BY vc.ncontrato ASC;
        """

        self.cur.execute(query)

        rows = self.cur.fetchall()

        self.tabla.setRowCount(0)

        fila_visual = 0

        for row in rows:

            ncontrato, compania, cp, efec, fin, anul, fec_inicio = row

            self.cur.execute(
                """
                SELECT efec_suple
                FROM contratos_identificacion
                WHERE ncontrato = ?
                """,
                (ncontrato,),
            )

            fechas = [f[0] for f in self.cur.fetchall()]

            estado = determinar_estado_contrato(
                efec_suple=efec,
                fin_suple=fin,
                fec_anulacion=anul,
                lista_fechas_efecto=fechas,
            )

            if estado in ("Anulado", "Sin efecto"):
                continue

            self.tabla.insertRow(fila_visual)

            valores = [
                ncontrato,
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
                self.tabla.setItem(
                    fila_visual,
                    c,
                    item,
                )

            fila_visual += 1

    def seleccionar_contrato(self):

        row = self.tabla.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Aviso",
                "Debe seleccionar un contrato.",
            )
            return

        ncontrato = self.tabla.item(
            row,
            0,
        ).text()

        from analisis_contrato.historico_precios import HistoricoPrecios

        mw = self.window()

        widget = HistoricoPrecios(
            parent=mw,
            conn=self.conn,
            ncontrato=ncontrato,
        )

        mw.cargar_modulo(
            widget,
            f"Histórico de precios - {ncontrato}",
        )

    def cancelar(self):

        mw = self.window()
        mw.volver_inicio()
