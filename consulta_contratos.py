# --------------------------------------------#
# Modulo: consultas_contratos.py              #
# Descripción: Lista de contratos (consulta)  #
# Autor: Antonio Morales                      #
# Fecha: 2026-02-09                           #
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
from detalles_contrato import DetallesContratoWidget


# =========================================================
#   VENTANA PRINCIPAL: LISTA DE CONTRATOS
# =========================================================
class ConsultaContratosWidget(BaseConsulta):
    def __init__(self, conn, parent=None):
        super().__init__(parent)

        self.conn = conn
        self.setWindowTitle("Consulta de contratos")
        self.resize(800, 500)

        layout = QVBoxLayout(self)

        # -------------------------------------------------
        # TÍTULO
        # -------------------------------------------------
        titulo = QLabel("Listado de contratos")
        titulo.setFont(QFont("DejaVu Sans", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # -------------------------------------------------
        # TABLA
        # -------------------------------------------------
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(
            ["Nº contrato", "Compañía", "Código Postal", "Población"]
        )

        # Sin zebra, como pediste
        self.tabla.setAlternatingRowColors(False)

        # Ajuste automático de columnas
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setStretchLastSection(True)

        # Sin ordenar por clic
        self.tabla.setSortingEnabled(False)

        layout.addWidget(self.tabla)

        # -------------------------------------------------
        # BOTONES
        # -------------------------------------------------
        botones = QHBoxLayout()
        self.btn_detalles = QPushButton("Detalles")
        self.btn_cerrar = QPushButton("Cerrar")

        botones.addWidget(self.btn_detalles)
        botones.addStretch()
        botones.addWidget(self.btn_cerrar)

        layout.addLayout(botones)

        # Eventos
        self.btn_cerrar.clicked.connect(self.close)
        self.btn_detalles.clicked.connect(self.abrir_detalles)

        # Cargar datos
        self.cargar_contratos()

    # =====================================================
    #   CARGAR LISTA DE CONTRATOS
    # =====================================================
    def cargar_contratos(self):
        """
        Lista de contratos SIN suplementos.
        Una fila por contrato.
        Igual que en la captura de facturas.
        """

        cur = self.conn.cursor()

        cur.execute("""
            SELECT DISTINCT
                ci.ncontrato,
                ci.compania,
                ci.codigo_postal,
                cp.poblacion
            FROM contratos_identificacion ci
            JOIN cpostales cp ON ci.codigo_postal = cp.codigo_postal
            ORDER BY ci.ncontrato;
            """)

        datos = cur.fetchall()

        self.tabla.setRowCount(len(datos))

        for fila, (ncontrato, compania, cp, poblacion) in enumerate(datos):
            self.tabla.setItem(fila, 0, QTableWidgetItem(str(ncontrato)))
            self.tabla.setItem(fila, 1, QTableWidgetItem(str(compania)))
            self.tabla.setItem(fila, 2, QTableWidgetItem(str(cp)))
            self.tabla.setItem(fila, 3, QTableWidgetItem(str(poblacion)))

        self.tabla.resizeColumnsToContents()
        self.tabla.resizeRowsToContents()

    # =====================================================
    #   ABRIR DETALLES DEL CONTRATO
    # =====================================================
    def abrir_detalles(self):
        items = self.tabla.selectedItems()
        if not items:
            self.mostrar_aviso("Aviso", "Debe seleccionar un contrato.")
            return

        fila = items[0].row()
        ncontrato = self.tabla.item(fila, 0).text().strip()

        # Obtener el MainWindow real
        marco = self.window()

        # Crear la vista de detalles
        detalles = DetallesContratoWidget(self.conn, ncontrato, parent=marco)

        # Cargarla en la zona de contenido
        marco.cargar_modulo(detalles, "")
