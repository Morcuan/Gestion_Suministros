# --------------------------------------------#
# Modulo: lista_contratos_historia.py
# Descripción: Lista de contratos (solo último suplemento)
#              para acceder al histórico de movimientos.
# Autor: Antonio Morales + Copilot
# Fecha: 2026-03-05
# --------------------------------------------#

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from db import get_conn
from lista_contratos import obtener_lista_contratos
from lista_suplementos_contrato import ListaSuplementosContrato


class ListaContratosHistoria(QWidget):
    """
    Lista de contratos (solo un registro por contrato)
    para acceder al histórico de suplementos.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Histórico de contratos")
        self.conn = get_conn()

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(
            ["Nº contrato", "Supl.", "Compañía", "C.P.", "Inicio", "Efecto", "Estado"]
        )

        # Botones
        self.btn_movimientos = QPushButton("Movimientos")
        self.btn_cerrar = QPushButton("Cancelar")

        self.btn_movimientos.clicked.connect(self.abrir_movimientos)
        self.btn_cerrar.clicked.connect(self.volver_menu)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Seleccione un contrato para ver sus movimientos:"))
        layout.addWidget(self.tabla)

        botones = QHBoxLayout()
        botones.addWidget(self.btn_movimientos)
        botones.addStretch()
        botones.addWidget(self.btn_cerrar)

        layout.addLayout(botones)
        self.setLayout(layout)

        self.cargar_contratos()

    # ------------------------------------------------------------
    # Cargar contratos (solo último suplemento)
    # ------------------------------------------------------------
    def cargar_contratos(self):
        lista = obtener_lista_contratos(
            self.conn,
            solo_activos=False,
            solo_ultimo_suplemento=True,
            incluir_anulados=True,
        )

        self.tabla.setRowCount(len(lista))

        for i, row in enumerate(lista):
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
                ppunta,
                pv_ppunta,
                pvalle,
                pv_pvalle,
                pv_conpunta,
                pv_conllano,
                pv_convalle,
                vertido,
                pv_excedent,
                bono_social,
                alq_contador,
                otros_gastos,
                i_electrico,
                iva,
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

            for j, value in enumerate(datos):
                self.tabla.setItem(i, j, QTableWidgetItem(str(value)))

        self.tabla.resizeColumnsToContents()
        self.tabla.horizontalHeader().setStretchLastSection(True)

    # ------------------------------------------------------------
    # Obtener MainWindow real
    # ------------------------------------------------------------
    def get_mainwindow(self):
        w = self.parent()
        while w is not None and not hasattr(w, "cargar_modulo"):
            w = w.parent()
        return w

    # ------------------------------------------------------------
    # Abrir lista de suplementos (ventana B)
    # ------------------------------------------------------------
    def abrir_movimientos(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Atención", "Debe seleccionar un contrato.")
            return

        ncontrato = self.tabla.item(fila, 0).text()

        main = self.get_mainwindow()
        widget = ListaSuplementosContrato(parent=main, ncontrato=ncontrato)
        main.cargar_modulo(widget, f"Movimientos del contrato {ncontrato}")

    # ------------------------------------------------------------
    # Volver al menú principal
    # ------------------------------------------------------------
    def volver_menu(self):
        main = self.get_mainwindow()
        main.volver_inicio()
