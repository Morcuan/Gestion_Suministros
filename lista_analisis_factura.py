# ------------------------------------------------------------#
# Modulo: lista_analisis_factura.py                           #
# Descripción: Lista de contratos para Explorador de facturas #
# Autor: Antonio Morales                                      #
# Fecha: 2026-03-03                                           #
# ------------------------------------------------------------#

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

from lista_contratos import obtener_lista_contratos


class ListaAnalisisFactura(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # ------------------------------------------------------------
        # TÍTULO
        # ------------------------------------------------------------
        titulo = QLabel("Explorador de facturas – Seleccione un contrato")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(titulo)

        # ------------------------------------------------------------
        # TABLA DE CONTRATOS
        # ------------------------------------------------------------
        self.tabla = QTableWidget()
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)

        # Doble clic = abrir detalles
        self.tabla.itemDoubleClicked.connect(self.abrir_detalles)

        # Cambio de selección = habilitar botón
        self.tabla.itemSelectionChanged.connect(self.actualizar_estado_boton)

        layout.addWidget(self.tabla)

        # ------------------------------------------------------------
        # BOTONES (solo dos, según DRU)
        # ------------------------------------------------------------
        botones = QHBoxLayout()

        self.btn_detalles = QPushButton("Detalles")
        self.btn_cancelar = QPushButton("Cancelar")

        self.btn_detalles.setEnabled(False)

        self.btn_detalles.clicked.connect(self.abrir_detalles)
        self.btn_cancelar.clicked.connect(self.volver_menu)

        botones.addStretch()
        botones.addWidget(self.btn_detalles)
        botones.addWidget(self.btn_cancelar)

        layout.addLayout(botones)
        self.setLayout(layout)

        self.cargar_datos()

    # ------------------------------------------------------------
    # LOCALIZAR MAINWINDOW REAL
    # ------------------------------------------------------------
    def get_mainwindow(self):
        w = self.parent()
        while w is not None and not hasattr(w, "cargar_modulo"):
            w = w.parent()
        return w

    # ------------------------------------------------------------
    # CARGA DE DATOS
    # ------------------------------------------------------------
    def cargar_datos(self):
        main = self.get_mainwindow()
        conn = main.conn

        lista = obtener_lista_contratos(
            conn,
            solo_activos=False,
            solo_ultimo_suplemento=True,
            incluir_anulados=True,
        )

        # Mismos campos que en todas las listas
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(
            ["Nº contrato", "Supl.", "Compañía", "C.P.", "Inicio", "Efecto", "Estado"]
        )
        self.tabla.setRowCount(len(lista))

        for fila, row in enumerate(lista):
            (
                id_contrato,
                ncontrato,
                suplemento,
                estado,
                compania,
                codigo_postal,
                poblacion,
                fec_inicio,
                fec_final,
                efec_suple,
                fin_suple,
                fec_anulacion,
                *_,
            ) = row

            datos = [
                ncontrato,
                suplemento,
                compania,
                codigo_postal,
                fec_inicio,
                efec_suple,
                estado,
            ]

            for col, valor in enumerate(datos):
                item = QTableWidgetItem(str(valor))

                if col in (0, 1, 3, 6):
                    item.setTextAlignment(Qt.AlignCenter)

                self.tabla.setItem(fila, col, item)

        self.tabla.resizeColumnsToContents()
        header = self.tabla.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Stretch)

    # ------------------------------------------------------------
    # HABILITAR BOTÓN DETALLES
    # ------------------------------------------------------------
    def actualizar_estado_boton(self):
        self.btn_detalles.setEnabled(self.tabla.currentRow() >= 0)

    # ------------------------------------------------------------
    # ABRIR DETALLES DEL CONTRATO
    # ------------------------------------------------------------
    def abrir_detalles(self, item=None):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Sin selección", "Debe seleccionar un contrato.")
            return

        ncontrato = self.tabla.item(fila, 0).text()

        main = self.get_mainwindow()
        from detalles_contrato import DetallesContratoWidget

        widget = DetallesContratoWidget(main.conn, ncontrato=ncontrato, parent=main)
        main.cargar_modulo(widget, f"Detalles del contrato {ncontrato}")

    # ------------------------------------------------------------
    # VOLVER AL MENÚ PRINCIPAL
    # ------------------------------------------------------------
    def volver_menu(self):
        main = self.get_mainwindow()
        main.cargar_modulo(
            main.crear_placeholder("Seleccione una opción del menú"), "Inicio"
        )
