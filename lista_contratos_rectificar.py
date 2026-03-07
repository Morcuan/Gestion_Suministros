# --------------------------------------------#
# Modulo: lista_contratos_rectificar.py
# Selección de contrato para rectificar facturas
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

from lista_contratos import obtener_lista_contratos
from lista_facturas_rectificar import ListaFacturasRectificar


class ListaContratosRectificar(QWidget):
    def __init__(self, parent=None, conn=None):
        super().__init__(parent)

        self.setWindowTitle("Rectificar facturas de contrato")
        self.conn = conn

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(
            ["Nº contrato", "Supl.", "Compañía", "C.P.", "Inicio", "Efecto", "Estado"]
        )

        self.btn_seleccionar = QPushButton("Seleccionar contrato")
        self.btn_cerrar = QPushButton("Cerrar")

        self.btn_seleccionar.clicked.connect(self.abrir_rectificacion)
        self.btn_cerrar.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Seleccione un contrato para rectificar sus facturas:"))
        layout.addWidget(self.tabla)

        botones = QHBoxLayout()
        botones.addWidget(self.btn_seleccionar)
        botones.addStretch()
        botones.addWidget(self.btn_cerrar)

        layout.addLayout(botones)
        self.setLayout(layout)

        self.lista_contratos = []
        self.cargar_contratos()

    def cargar_contratos(self):
        self.lista_contratos = obtener_lista_contratos(
            self.conn,
            solo_activos=False,
            solo_ultimo_suplemento=True,
            incluir_anulados=True,
        )

        lista = self.lista_contratos
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

    def get_mainwindow(self):
        w = self.parent()
        while w is not None and not hasattr(w, "cargar_modulo"):
            w = w.parent()
        return w

    def abrir_rectificacion(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Atención", "Debe seleccionar un contrato.")
            return

        row = self.lista_contratos[fila]
        ncontrato = row[1]  # este es el identificador real del contrato

        main = self.get_mainwindow()
        if main is None:
            QMessageBox.critical(self, "Error", "No se encontró la ventana principal.")
            return

        form = ListaFacturasRectificar(
            parent=main,
            conn=self.conn,
            ncontrato=ncontrato,
        )

        main.cargar_modulo(form, f"Rectificar facturas del contrato {ncontrato}")
