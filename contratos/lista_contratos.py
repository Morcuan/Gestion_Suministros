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


class ListaContratos(QWidget):
    def __init__(self, parent=None, modo="modificacion"):
        super().__init__(parent)
        self.parent = parent
        self.modo = modo  # modificacion / anulacion

        # Heredar conexión desde MainWindow
        self.conn = self.parent.conn
        self.cur = self.conn.cursor()

        self.crear_ui()
        self.cargar_datos()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def crear_ui(self):
        layout = QVBoxLayout(self)

        titulo = QLabel("Listado de contratos")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["Contrato", "Compañía", "C.P.", "Inicio", "Final", "Anulación"]
        )
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.tabla)

        botones = QHBoxLayout()
        btn_sel = QPushButton("Seleccionar contrato")
        btn_sel.clicked.connect(self.seleccionar_contrato)
        botones.addWidget(btn_sel)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.cancelar)
        botones.addWidget(btn_cancelar)

        layout.addLayout(botones)

    # ---------------------------------------------------------
    # CARGA DE DATOS (solo suplemento vigente)
    # ---------------------------------------------------------
    def cargar_datos(self):
        query = """
            SELECT ncontrato, compania, codigo_postal,
                   efec_suple, fin_suple, fec_anulacion
            FROM vista_contratos
            WHERE DATE('now') BETWEEN efec_suple AND fin_suple
                OR DATE('now') < efec_suple
            ORDER BY ncontrato ASC;
        """

        self.cur.execute(query)
        rows = self.cur.fetchall()

        self.tabla.setRowCount(len(rows))

        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.tabla.setItem(r, c, item)

    # ---------------------------------------------------------
    # SELECCIONAR CONTRATO
    # ---------------------------------------------------------
    def seleccionar_contrato(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Debe seleccionar un contrato.")
            return

        ncontrato = self.tabla.item(row, 0).text()
        mw = self.window()  # MainWindow real

        if self.modo == "modificacion":
            from contratos.modificar_contrato import ModificarContrato

            widget = ModificarContrato(parent=mw, conn=self.conn, ncontrato=ncontrato)
            mw.cargar_modulo(widget, f"Modificación contrato {ncontrato}")
            return

        if self.modo == "anulacion":
            from contratos.anular_rehabilitar import AnularRehabilitar

            widget = AnularRehabilitar(parent=mw, conn=self.conn, ncontrato=ncontrato)
            mw.cargar_modulo(widget, f"Anulación contrato {ncontrato}")
            return

        QMessageBox.critical(self, "Error", f"Modo desconocido: {self.modo}")

    # ---------------------------------------------------------
    # CANCELAR
    # ---------------------------------------------------------
    def cancelar(self):
        mw = self.window()
        mw.volver_inicio()
