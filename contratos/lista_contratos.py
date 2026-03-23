# --------------------------------------------------
# lista_contratos.py
# Función para obtener la lista de contratos desde
#  la base de datos
# Autor: Antonio Morales
# Fecha: 23/03/2026
# ---------//-----------------------------------------

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from utilidades.logica_negocio import convertir_a_ddmmaaaa


class ListaContratos(QWidget):
    """
    Lista de contratos incrustada en la zona de contenido.
    Muestra solo el último suplemento de cada contrato.
    """

    def __init__(self, parent, conn, callback):
        super().__init__(parent)

        self.main_window = parent  # referencia explícita al MainWindow
        self.conn = conn
        self.callback = callback

        self._crear_ui()
        self._cargar_datos()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def _crear_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # --- Tabla ---
        self.tabla = QTableView()
        self.modelo = QStandardItemModel(self)
        self.tabla.setModel(self.modelo)
        self.tabla.setSelectionBehavior(QTableView.SelectRows)
        self.tabla.setSelectionMode(QTableView.SingleSelection)
        self.tabla.setEditTriggers(QTableView.NoEditTriggers)

        cabeceras = ["Contrato", "Compañía", "CP", "Efecto", "Fin", "Anulación"]
        self.modelo.setColumnCount(len(cabeceras))
        self.modelo.setHorizontalHeaderLabels(cabeceras)

        layout.addWidget(self.tabla)

        # --- Botones inferiores ---
        botones = QHBoxLayout()

        self.btn_elegir = QPushButton("Elegir contrato")
        self.btn_cancelar = QPushButton("Cancelar")

        self.btn_elegir.setMinimumHeight(40)
        self.btn_cancelar.setMinimumHeight(40)

        botones.addWidget(self.btn_elegir, 1)
        botones.addWidget(self.btn_cancelar, 1)

        layout.addLayout(botones)

        # Señales
        self.btn_elegir.clicked.connect(self._elegir)
        self.btn_cancelar.clicked.connect(self._cancelar)

    # ---------------------------------------------------------
    # Cargar datos
    # ---------------------------------------------------------
    def _cargar_datos(self):
        self.modelo.removeRows(0, self.modelo.rowCount())

        cursor = self.conn.cursor()

        sql = """
            SELECT v.ncontrato, v.compania, v.codigo_postal,
                   v.efec_suple, v.fin_suple, v.fec_anulacion
            FROM vista_contratos v
            WHERE v.suplemento = (
                SELECT MAX(v2.suplemento)
                FROM vista_contratos v2
                WHERE v2.ncontrato = v.ncontrato
            )
            ORDER BY v.ncontrato ASC
        """

        cursor.execute(sql)
        filas = cursor.fetchall()

        for fila in filas:
            ncontrato, compania, cp, efec, fin, anul = fila

            efec_fmt = convertir_a_ddmmaaaa(efec) if efec else ""
            fin_fmt = convertir_a_ddmmaaaa(fin) if fin else ""
            anul_fmt = convertir_a_ddmmaaaa(anul) if anul else ""

            datos = [
                str(ncontrato),
                compania or "",
                cp or "",
                efec_fmt,
                fin_fmt,
                anul_fmt,
            ]

            items = [QStandardItem(str(v)) for v in datos]
            for item in items:
                item.setEditable(False)

            self.modelo.appendRow(items)

        # Ajuste visual
        self.tabla.resizeColumnsToContents()
        self.tabla.horizontalHeader().setStretchLastSection(True)

    # ---------------------------------------------------------
    # Selección
    # ---------------------------------------------------------
    def _elegir(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            return

        fila = index.row()
        ncontrato = self.modelo.item(fila, 0).text()

        self.callback(ncontrato)

    def _cancelar(self):
        # Volver a la pantalla de inicio
        self.main_window.cargar_modulo(self.main_window.crear_pantalla_inicio(), None)
