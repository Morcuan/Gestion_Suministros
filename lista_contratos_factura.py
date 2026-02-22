# ------------------------------------------            --#
# Modulo: lista_contratos_factura.py                    #
# Descripción: Ventana para seleccionar contrato para nueva factura #
# Autor: Antonio Morales                      #
# Fecha: 2026-02-09                           #
# --------------------------------------------#

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from form_factura import FormFactura


class ListaContratosFactura(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()

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
    #  LOCALIZAR MAINWINDOW REAL
    # ============================================================

    def get_mainwindow(self):
        w = self.parent()
        while w is not None and not hasattr(w, "cargar_modulo"):
            w = w.parent()
        return w

    # ============================================================
    #  CARGA DE DATOS
    # ============================================================

    def cargar_datos(self):
        main = self.get_mainwindow()
        cursor = main.cursor

        cursor.execute("""
            SELECT id_contrato, ncontrato, estado, compania, codigo_postal, poblacion
            FROM vista_contratos_facturacion
            ORDER BY ncontrato
            """)
        datos = cursor.fetchall()

        self.tabla.setRowCount(len(datos))
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Nº contrato", "Estado", "Compañía", "CP", "Población"]
        )

        for fila, reg in enumerate(datos):
            for col, valor in enumerate(reg):
                self.tabla.setItem(fila, col, QTableWidgetItem(str(valor)))

        self.tabla.resizeColumnsToContents()
        self.tabla.setColumnHidden(0, True)

    # ============================================================
    #  HABILITAR BOTÓN SEGÚN SELECCIÓN
    # ============================================================

    def actualizar_estado_boton(self):
        self.btn_seleccionar.setEnabled(self.tabla.currentRow() >= 0)

    # ============================================================
    #  ACEPTAR SELECCIÓN
    # ============================================================

    def aceptar(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return

        id_contrato = self.tabla.item(fila, 0).text()
        ncontrato = self.tabla.item(fila, 1).text()
        compania = self.tabla.item(fila, 3).text()

        main = self.get_mainwindow()

        form = FormFactura(
            parent=main, id_contrato=id_contrato, ncontrato=ncontrato, compania=compania
        )

        main.cargar_modulo(form, f"Nueva factura – {ncontrato} – {compania}")

    # ============================================================
    #  SALIR → VOLVER AL MENÚ PRINCIPAL
    # ============================================================

    def volver_menu(self):
        main = self.get_mainwindow()
        main.cargar_modulo(
            main.crear_placeholder("Seleccione una opción del menú"), "Inicio"
        )
