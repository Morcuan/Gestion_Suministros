# --------------------------------------------#
# Modulo: consulta_facturas.py                #
# Descripción: Lista de facturas (consulta)   #
# Autor: Antonio Morales                      #
# Fecha: 2026-02-13 (adaptado al DRU)         #
# --------------------------------------------#

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from base_consulta import BaseConsulta


# =========================================================
#   LISTA DE FACTURAS DE UN CONTRATO
# =========================================================
class ConsultaFacturasWidget(BaseConsulta):
    # init recibe la conexión a la base de datos y el id_contrato para mostrar sus facturas
    def __init__(self, conn, id_contrato, parent=None):
        super().__init__(parent)

        self.conn = conn
        self.id_contrato = id_contrato

        self.resize(900, 520)

        layout = QVBoxLayout(self)

        # -------------------------------------------------
        # TÍTULO LOCAL
        # -------------------------------------------------
        cur = self.conn.cursor()
        cur.execute(
            "SELECT ncontrato FROM contratos_identificacion WHERE id_contrato = ? LIMIT 1;",
            (self.id_contrato,),
        )
        fila = cur.fetchone()
        ncontrato = fila[0] if fila else "?"

        titulo = QLabel(f"Facturas del contrato {ncontrato}")
        titulo.setFont(QFont("DejaVu Sans", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # -------------------------------------------------
        # TABLA
        # -------------------------------------------------
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            [
                "Nº factura",
                "Fecha emisión",
                "Periodo desde",
                "Periodo hasta",
                "Excdtes (kWh)",
            ]
        )

        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setSortingEnabled(False)

        layout.addWidget(self.tabla)

        # -------------------------------------------------
        # BOTONES
        # -------------------------------------------------
        botones = QHBoxLayout()
        self.btn_detalles = QPushButton("Detalles factura")
        self.btn_cerrar = QPushButton("Cerrar")

        botones.addWidget(self.btn_detalles)
        botones.addStretch()
        botones.addWidget(self.btn_cerrar)

        layout.addLayout(botones)

        # Eventos
        self.btn_cerrar.clicked.connect(self.volver)
        self.btn_detalles.clicked.connect(self.abrir_detalles)

        # Cargar datos
        self.cargar_facturas()

    # =====================================================
    #   CARGAR LISTA DE FACTURAS
    # =====================================================
    # Consulta las facturas del contrato y las muestra en la tabla
    def cargar_facturas(self):
        cur = self.conn.cursor()

        cur.execute(
            """
            SELECT
                nfactura,
                fec_emision,
                inicio_factura,
                fin_factura,
                excedentes
            FROM facturas
            WHERE id_contrato = ?
            ORDER BY fec_emision ASC;
            """,
            (self.id_contrato,),
        )

        datos = cur.fetchall()
        self.tabla.setRowCount(len(datos))

        for fila, (nfactura, fec, ini, fin, exc) in enumerate(datos):
            item_nfac = QTableWidgetItem(str(nfactura))
            item_nfac.setData(Qt.UserRole, nfactura)

            self.tabla.setItem(fila, 0, item_nfac)
            self.tabla.setItem(fila, 1, QTableWidgetItem(str(fec)))
            self.tabla.setItem(fila, 2, QTableWidgetItem(str(ini)))
            self.tabla.setItem(fila, 3, QTableWidgetItem(str(fin)))
            self.tabla.setItem(fila, 4, QTableWidgetItem(str(exc)))

        self.tabla.resizeColumnsToContents()
        self.tabla.resizeRowsToContents()

    # =====================================================
    #   ABRIR DETALLES DE LA FACTURA
    # =====================================================
    # Al hacer clic en "Detalles factura", se abre el módulo de detalles para la
    # factura seleccionada
    def abrir_detalles(self):
        items = self.tabla.selectedItems()
        if not items:
            self.mostrar_aviso("Aviso", "Debe seleccionar una factura.")
            return

        fila = items[0].row()
        nfactura = self.tabla.item(fila, 0).data(Qt.UserRole)

        marco = self.window()

        from detalles_factura import DetallesFactura

        detalles = DetallesFactura(self.conn, self.id_contrato, nfactura, parent=marco)

        marco.cargar_modulo(detalles, "Detalles de la factura")

    # =====================================================
    #   VOLVER A DETALLES DEL CONTRATO
    # =====================================================
    def volver(self):
        from detalles_contrato import DetallesContratoWidget

        cur = self.conn.cursor()
        cur.execute(
            "SELECT ncontrato FROM contratos_identificacion WHERE id_contrato = ? LIMIT 1;",
            (self.id_contrato,),
        )
        fila = cur.fetchone()
        if not fila:
            self.mostrar_aviso("Error", "No se pudo recuperar el número de contrato.")
            return

        ncontrato = fila[0]

        marco = self.window()
        vista = DetallesContratoWidget(self.conn, ncontrato, parent=marco)
        marco.cargar_modulo(vista, "Detalles del contrato")
