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
                "id_contrato": row[0],
                "nfactura": row[1],
                "fecha": row[2],
                "importe_total": 0.0,
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

        self._configurar_signals()
        self.cargar_facturas()

    # --------------------------------------------------------
    # LOCALIZAR MAINWINDOW REAL (versión correcta para controladores)
    # --------------------------------------------------------
    def get_mainwindow(self):
        w = self.ui.parent()
        while w is not None and not hasattr(w, "cargar_modulo"):
            w = w.parent()
        return w

    def _configurar_signals(self):
        self.ui.botonRectificar.clicked.connect(self.on_rectificar_clicked)
        self.ui.botonCancelar.clicked.connect(self.on_cancelar_clicked)

    def cargar_facturas(self):
        self.facturas = obtener_facturas_para_rectificar(self.conn, self.ncontrato)
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

        # ---------------------------------------------------------
        # ABRIR FORMULARIO DE RECTIFICACIÓN (Pantalla C)
        # ---------------------------------------------------------
        from form_factura_rectificar import FormFacturaRectificar

        main = self.get_mainwindow()

        main.cargar_modulo(
            FormFacturaRectificar(
                parent=main, ncontrato=self.ncontrato, nfactura=factura["nfactura"]
            ),
            "Rectificar factura",
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

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"Facturas del contrato {ncontrato}:"))

        self.tablaFacturas = QTableWidget()
        self.tablaFacturas.setColumnCount(5)
        self.tablaFacturas.setHorizontalHeaderLabels(
            ["Factura", "Fecha", "Importe", "Estado", "Rectifica a"]
        )
        layout.addWidget(self.tablaFacturas)

        botones = QHBoxLayout()
        self.botonRectificar = QPushButton("Rectificar factura")
        self.botonCancelar = QPushButton("Cerrar")

        botones.addWidget(self.botonRectificar)
        botones.addStretch()
        botones.addWidget(self.botonCancelar)

        layout.addLayout(botones)

        # Crear controlador
        self.controller = ListaFacturasRectificarController(
            conn=self.conn, ncontrato=self.ncontrato, ui=self
        )
