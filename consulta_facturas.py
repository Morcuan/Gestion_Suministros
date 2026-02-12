# --------------------------------------------#
# Modulo: consulta_facturas.py                #
# Descripción: Lista de facturas (consulta)   #
# Autor: Antonio Morales                      #
# Fecha: 2026-02-11                           #
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
    QWidget,
)

from base_consulta import BaseConsulta


# =========================================================
#   LISTA DE FACTURAS DE UN CONTRATO
# =========================================================
class ConsultaFacturasWidget(BaseConsulta):
    def __init__(self, conn, id_contrato, parent=None):
        super().__init__(parent)

        self.conn = conn
        self.id_contrato = id_contrato

        # Ya no usamos título de ventana global
        # self.setWindowTitle("Facturas del contrato")
        self.resize(800, 500)

        layout = QVBoxLayout(self)

        # -------------------------------------------------
        # TÍTULO "LOCAL" DE LA VENTANA
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
                "Nº de factura",
                "Fecha de emisión",
                "Periodo desde",
                "Periodo hasta",
                "Importe",
            ]
        )

        self.tabla.setAlternatingRowColors(False)
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
    def cargar_facturas(self):
        cur = self.conn.cursor()

        cur.execute(
            """
            SELECT
                fi.id_factura,
                fi.nfactura,
                fi.fec_emision,
                fi.inicio_factura,
                fi.fin_factura,
                fa.total_factura
            FROM factura_identificacion fi
            JOIN factura_asociados fa ON fi.id_factura = fa.id_factura
            WHERE fi.id_contrato = ?
            ORDER BY fi.fec_emision ASC;
            """,
            (self.id_contrato,),
        )

        datos = cur.fetchall()
        self.tabla.setRowCount(len(datos))

        for fila, (id_factura, nfac, fec, ini, fin, total) in enumerate(datos):
            item_nfac = QTableWidgetItem(str(nfac))
            item_nfac.setData(Qt.UserRole, id_factura)

            self.tabla.setItem(fila, 0, item_nfac)
            self.tabla.setItem(fila, 1, QTableWidgetItem(str(fec)))
            self.tabla.setItem(fila, 2, QTableWidgetItem(str(ini)))
            self.tabla.setItem(fila, 3, QTableWidgetItem(str(fin)))
            self.tabla.setItem(fila, 4, QTableWidgetItem(f"{total:.2f}"))

        self.tabla.resizeColumnsToContents()
        self.tabla.resizeRowsToContents()

    # =====================================================
    #   ABRIR DETALLES DE LA FACTURA
    # =====================================================
    def abrir_detalles(self):
        items = self.tabla.selectedItems()
        if not items:
            self.mostrar_aviso("Aviso", "Debe seleccionar una factura.")
            return

        fila = items[0].row()
        id_factura = self.tabla.item(fila, 0).data(Qt.UserRole)

        # Obtener el MainWindow real
        marco = self.window()

        from detalles_factura import DetallesFactura

        detalles = DetallesFactura(self.conn, id_factura, parent=marco)

        marco.cargar_modulo(detalles, "Detalles de la factura")

    def volver(self):
        from detalles_contrato import DetallesContratoWidget

        # Recuperar ncontrato a partir del id_contrato
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
