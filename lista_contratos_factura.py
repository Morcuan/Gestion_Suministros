# ------------------------------------------------------------#
# Modulo: lista_contratos_factura.py                          #
# Descripción: Selección de contrato para crear nueva factura #
# Autor: Antonio Morales                                      #
# Fecha: 2026-02-27                                           #
# ------------------------------------------------------------#
# Este módulo muestra una tabla con los contratos disponibles para facturar.
# El usuario puede seleccionar un contrato y abrir el formulario de factura.

# ------------------------------------------------------------
# IMPORTACIONES
# ------------------------------------------------------------
from PySide6.QtCore import Qt
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

from form_factura import FormFactura
from lista_contratos import obtener_lista_contratos


# ------------------------------------------------------------
# CLASE PRINCIPAL
# ------------------------------------------------------------
class ListaContratosFactura(QWidget):

    # ============================================================
    # INICIALIZACIÓN
    # ============================================================
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # ------------------------------------------------------------
        # TÍTULO
        # ------------------------------------------------------------
        titulo = QLabel("Seleccionar contrato para nueva factura")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(titulo)

        # ------------------------------------------------------------
        # TABLA
        # ------------------------------------------------------------
        self.tabla = QTableWidget()
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)

        # Doble clic = aceptar
        self.tabla.itemDoubleClicked.connect(self.aceptar)

        # Cambio de selección = habilitar botón
        self.tabla.itemSelectionChanged.connect(self.actualizar_estado_boton)

        layout.addWidget(self.tabla)

        # ------------------------------------------------------------
        # BOTONES
        # ------------------------------------------------------------
        botones = QHBoxLayout()
        self.btn_seleccionar = QPushButton("Seleccionar contrato")
        self.btn_salir = QPushButton("Salir")

        self.btn_seleccionar.setEnabled(False)

        self.btn_seleccionar.clicked.connect(self.aceptar)
        self.btn_salir.clicked.connect(self.volver_menu)

        botones.addStretch()
        botones.addWidget(self.btn_seleccionar)
        botones.addWidget(self.btn_salir)

        layout.addLayout(botones)
        self.setLayout(layout)

        self.cargar_datos()

    # ============================================================
    # LOCALIZAR MAINWINDOW REAL
    # ============================================================
    def get_mainwindow(self):
        w = self.parent()
        while w is not None and not hasattr(w, "cargar_modulo"):
            w = w.parent()
        return w

    # ============================================================
    # CARGA DE DATOS
    # ============================================================
    def cargar_datos(self):

        main = self.get_mainwindow()
        conn = main.conn

        lista = obtener_lista_contratos(
            conn,
            solo_activos=False,
            solo_ultimo_suplemento=True,
            incluir_anulados=True,
        )

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

            for col, valor in enumerate(datos):
                item = QTableWidgetItem(str(valor))

                if col in (0, 1, 3, 6):
                    item.setTextAlignment(Qt.AlignCenter)

                self.tabla.setItem(fila, col, item)

        self.tabla.resizeColumnsToContents()

    # ============================================================
    # HABILITAR BOTÓN SEGÚN SELECCIÓN
    # ============================================================
    def actualizar_estado_boton(self):
        self.btn_seleccionar.setEnabled(self.tabla.currentRow() >= 0)

    # ============================================================
    # ACEPTAR SELECCIÓN
    # ============================================================
    def aceptar(self, item=None):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Sin selección", "Debe seleccionar un contrato.")
            return

        id_contrato = self.tabla.item(fila, 0).text()
        ncontrato = self.tabla.item(fila, 1).text()
        compania = self.tabla.item(fila, 2).text()

        main = self.get_mainwindow()

        form = FormFactura(
            parent=main,
            id_contrato=id_contrato,
            ncontrato=ncontrato,
            compania=compania,
        )

        titulo = f"Factura nueva para contrato {ncontrato}"
        main.cargar_modulo(form, titulo)

    # ============================================================
    # SALIR → VOLVER AL MENÚ PRINCIPAL
    # ============================================================
    def volver_menu(self):
        main = self.get_mainwindow()
        main.cargar_modulo(
            main.crear_placeholder("Seleccione una opción del menú"), "Inicio"
        )
        )
        )
