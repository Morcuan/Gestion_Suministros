# ------------------------------------------------------------
# lista_facturas_rectificar.py
# Ventana para listar facturas de un contrato y rectificarlas
# ------------------------------------------------------------

import sqlite3
from typing import Any, Dict, List

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

# ============================================================
#  CONSTANTES DE ESTADO
# ============================================================
ESTADO_EMITIDA = "Emitida"
ESTADO_RECTIFICADA = "Rectificada"
ESTADO_RECTIFICADORA = "Rectificadora"


# ============================================================
#  FUNCIÓN: OBTENER FACTURAS POR ncontrato (NO por id_contrato)
# ============================================================
def obtener_facturas_para_rectificar(conn: sqlite3.Connection, ncontrato: str):
    """
    Devuelve las facturas asociadas al contrato real (ncontrato),
    independientemente del suplemento al que pertenecen.
    """

    sql = """
        SELECT
            f.id_contrato,
            f.nfactura,
            f.fec_emision,
            f.estado,
            f.rectifica_a
        FROM facturas f
        WHERE f.ncontrato = ?
        ORDER BY f.fec_emision, f.nfactura
    """

    cur = conn.cursor()
    cur.execute(sql, (ncontrato,))
    rows = cur.fetchall()

    facturas = []
    for row in rows:
        facturas.append(
            {
                "id_contrato": row[0],  # suplemento al que pertenecía en su momento
                "nfactura": row[1],
                "fecha": row[2],
                "importe_total": 0.0,  # placeholder
                "estado": row[3],
                "rectifica_a": row[4],
            }
        )
    return facturas


# ============================================================
#  CONTROLADOR LÓGICO
# ============================================================
class ListaFacturasRectificarController:
    def __init__(self, conn: sqlite3.Connection, ncontrato: str, ui):
        self.conn = conn
        self.ncontrato = ncontrato
        self.ui = ui
        self.facturas: List[Dict[str, Any]] = []

        print("DEBUG → Controller recibe ncontrato =", ncontrato)

        self._configurar_signals()
        self.cargar_facturas()

    def _configurar_signals(self):
        self.ui.botonRectificar.clicked.connect(self.on_rectificar_clicked)
        self.ui.botonCancelar.clicked.connect(self.on_cancelar_clicked)

    def cargar_facturas(self):
        self.facturas = obtener_facturas_para_rectificar(self.conn, self.ncontrato)
        print("DEBUG → Cargando facturas para ncontrato =", self.ncontrato)

        self._poblar_tabla()

    def _poblar_tabla(self):
        tabla = self.ui.tablaFacturas
        tabla.setRowCount(len(self.facturas))

        for row_idx, f in enumerate(self.facturas):
            tabla.setItem(row_idx, 0, QTableWidgetItem(f["nfactura"]))
            tabla.setItem(row_idx, 1, QTableWidgetItem(str(f["fecha"])))
            tabla.setItem(row_idx, 2, QTableWidgetItem(f"{f['importe_total']:.2f}"))
            tabla.setItem(row_idx, 3, QTableWidgetItem(f["estado"]))
            tabla.setItem(row_idx, 4, QTableWidgetItem(f["rectifica_a"] or ""))

        tabla.resizeColumnsToContents()

    def _obtener_factura_seleccionada(self):
        tabla = self.ui.tablaFacturas
        row = tabla.currentRow()
        if row < 0:
            return None
        return self.facturas[row]

    def on_rectificar_clicked(self):
        factura = self._obtener_factura_seleccionada()
        if not factura:
            QMessageBox.warning(
                self.ui, "Rectificar factura", "Debe seleccionar una factura."
            )
            return

        estado = factura["estado"]

        if estado == ESTADO_RECTIFICADA:
            QMessageBox.information(
                self.ui,
                "Rectificar factura",
                "Esta factura ya está rectificada y no puede rectificarse de nuevo.",
            )
            return

        if estado not in (ESTADO_EMITIDA, ESTADO_RECTIFICADORA):
            QMessageBox.information(
                self.ui,
                "Rectificar factura",
                "Solo se pueden rectificar facturas Emitidas o Rectificadoras.",
            )
            return

        # Abrir formulario de rectificación
        from form_factura_rectificar import abrir_form_factura_rectificar

        abrir_form_factura_rectificar(
            self.conn,
            factura["id_contrato"],  # suplemento original
            factura["nfactura"],
            self._on_rectificacion_guardada,
        )

    def _on_rectificacion_guardada(self):
        self.cargar_facturas()

    def on_cancelar_clicked(self):
        self.ui.close()


# ============================================================
#  CLASE VISUAL (QWidget)
# ============================================================
class ListaFacturasRectificar(QWidget):
    def __init__(self, parent=None, conn=None, ncontrato=None):
        super().__init__(parent)

        self.conn = conn
        self.ncontrato = ncontrato

        self.setWindowTitle(f"Facturas del contrato {ncontrato}")

        # --- Layout principal ---
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"Facturas del contrato {ncontrato}:"))

        # --- Tabla ---
        self.tablaFacturas = QTableWidget()
        self.tablaFacturas.setColumnCount(5)
        self.tablaFacturas.setHorizontalHeaderLabels(
            ["Factura", "Fecha", "Importe", "Estado", "Rectifica a"]
        )
        layout.addWidget(self.tablaFacturas)

        # --- Botones ---
        botones = QHBoxLayout()
        self.botonRectificar = QPushButton("Rectificar factura")
        self.botonCancelar = QPushButton("Cerrar")

        botones.addWidget(self.botonRectificar)
        botones.addStretch()
        botones.addWidget(self.botonCancelar)

        layout.addLayout(botones)

        # --- Crear controlador ---
        self.controller = ListaFacturasRectificarController(
            conn=self.conn, ncontrato=self.ncontrato, ui=self
        )
