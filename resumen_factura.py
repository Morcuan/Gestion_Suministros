# -------------------------         -----------------#
# Modulo: resumen_factura.py                         #
# Descripción: Resumen de factura de energía         #
# Autor: Antonio Morales                             #
# Fecha: 2026-02-09                                  #
# ---------------------------------------------------#

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)


# ResumenFactura: Ventana que muestra un resumen de la factura y
# permite acceder a detalles específicos
class ResumenFactura(QWidget):
    # init: recibe conexión, número de factura y contrato para cargar datos
    def __init__(self, conn, nfactura, id_contrato, parent=None):
        super().__init__(parent)

        self.conn = conn
        self.nfactura = nfactura
        self.id_contrato = id_contrato

        # Cargar datos del resumen + JSON
        self.datos, self.detalles_json = self.cargar_resumen()

        # Construir interfaz integrada
        self.init_ui()

    # ---------------------------------------------------------
    # CARGA DE DATOS
    # ---------------------------------------------------------
    # cargar_resumen: consulta la base de datos para obtener los totales y el JSON de detalles
    def cargar_resumen(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT
                total_energia,     -- 0
                total_cargos,      -- 1
                total_servicios,   -- 2
                total_iva,         -- 3
                cloud_aplicado,    -- 4
                cloud_sobrante,    -- 5
                total_final,       -- 6
                detalles_json      -- 7
            FROM factura_calculos
            WHERE id_factura = ?
        """,
            (self.nfactura,),
        )

        row = cursor.fetchone()

        if not row:
            raise Exception(f"No existe cálculo para la factura {self.nfactura}")

        detalles_json = json.loads(row[7])
        return row, detalles_json

    # ---------------------------------------------------------
    # INTERFAZ INTEGRADA
    # ---------------------------------------------------------
    # init_ui: construye la interfaz con un splitter que divide el resumen (izq)
    # y el detalle (der)
    def init_ui(self):
        self.setWindowTitle(f"Resumen de factura {self.nfactura}")

        # Splitter maestro: resumen (izq) + detalle (der)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(2)

        # Panel izquierdo: resumen
        self.panel_resumen = QWidget()
        self.layout_resumen = QVBoxLayout(self.panel_resumen)
        self.layout_resumen.setContentsMargins(20, 20, 20, 20)
        self.layout_resumen.setSpacing(15)

        self.layout_resumen.addWidget(self.bloque_resumen())

        # Botón VOLVER
        btn_volver = QPushButton("Volver")
        btn_volver.setStyleSheet("font-size: 16px; padding: 6px 12px;")
        btn_volver.clicked.connect(self.volver_a_lista)
        self.layout_resumen.addWidget(btn_volver)

        # Panel derecho: detalle (SIEMPRE con layout)
        self.panel_detalle = QWidget()
        self.layout_detalle = QVBoxLayout(self.panel_detalle)
        self.layout_detalle.setContentsMargins(20, 20, 20, 20)
        self.layout_detalle.setSpacing(15)

        # Añadir ambos paneles al splitter
        self.splitter.addWidget(self.panel_resumen)
        self.splitter.addWidget(self.panel_detalle)

        # Stretch factors
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.addWidget(self.splitter)

    # ---------------------------------------------------------
    # MÉTODO PARA CARGAR SUBFORMULARIOS
    # ---------------------------------------------------------
    # cargar_detalle: recibe un widget (subformulario) y lo
    # inserta en el panel derecho, limpiando antes cualquier contenido previo
    def cargar_detalle(self, widget):
        # 1) Limpiar el panel derecho
        self.limpiar_detalle()

        # 2) Insertar el subformulario en el layout del panel derecho
        self.layout_detalle.addWidget(widget)

    # ---------------------------------------------------------
    # VOLVER A LISTA DE FACTURAS
    # ---------------------------------------------------------
    # volver_a_lista: carga la vista de consulta de facturas del contrato,
    # pasando el ID del contrato
    def volver_a_lista(self):
        marco = self.window()

        from consulta_facturas import ConsultaFacturasWidget

        id_contrato = self.id_contrato

        vista = ConsultaFacturasWidget(self.conn, id_contrato, parent=marco)
        marco.cargar_modulo(vista, "Facturas del contrato")

    # ---------------------------------------------------------
    # BLOQUE PRINCIPAL DE RESUMEN
    # ---------------------------------------------------------
    # bloque_resumen: construye un bloque con los totales de la factura
    # y un boton para acceder a los detalles de cada sección
    def bloque_resumen(self):
        grupo = QGroupBox(f"Resumen de factura {self.nfactura}")
        form = QFormLayout()

        t = self.datos

        form.addRow("Energía:", self._fila_con_boton(t[0], "energia"))
        form.addRow("Cargos normativos:", self._fila_con_boton(t[1], "cargos"))
        form.addRow("Servicios y otros:", self._fila_con_boton(t[2], "servicios"))
        form.addRow("IVA:", self._fila_con_boton(t[3], "iva"))
        form.addRow("Cloud aplicado:", self._fila_con_boton(t[4], "cloud"))

        form.addRow("TOTAL FINAL:", QLabel(f"{t[6]:.2f} €"))

        grupo.setLayout(form)
        return grupo

    # ---------------------------------------------------------
    # FILA CON BOTÓN "DETALLES"
    # ---------------------------------------------------------
    # _fila_con_boton: construye una fila con el importe y un botón que llama
    # a mostrar_detalles
    def _fila_con_boton(self, importe, clave):
        cont = QHBoxLayout()
        cont.addWidget(QLabel(f"{importe:.2f} €"))

        btn = QPushButton("Detalles del cálculo")
        btn.setStyleSheet("font-size: 16px; padding: 6px 12px;")
        btn.clicked.connect(lambda: self.mostrar_detalles(clave))
        cont.addWidget(btn)

        w = QWidget()
        w.setLayout(cont)
        return w

    # ---------------------------------------------------------
    # CARGAR SUBFORMULARIO EN PANEL DERECHO
    # ---------------------------------------------------------
    # mostrar_detalles: recibe una clave que indica qué bloque de detalles cargar
    # y construye el widget correspondiente, pasándole el bloque de datos del JSON
    # y el número de días de la factura
    def mostrar_detalles(self, clave):
        from ventana_detalle_json import VentanaDetalleJSON

        dias = self.detalles_json.get("dias_factura", 1)

        # --- RECONSTRUIR BLOQUE ENERGÍA ---
        if clave == "energia":
            bloque = {
                "potencia": self.detalles_json.get("potencia", {}),
                "consumo": self.detalles_json.get("consumo", {}),
                "excedentes": self.detalles_json.get("excedentes", {}),
            }
        else:
            bloque = self.detalles_json.get(clave, {})

        widget = VentanaDetalleJSON(bloque, clave, dias, parent=self)
        self.cargar_detalle(widget)

    # ---------------------------------------------------------
    # LIMPIAR PANEL DERECHO
    # ---------------------------------------------------------
    # limpiar_detalle: elimina cualquier widget que esté actualmente en el panel derecho
    def limpiar_detalle(self):
        layout = self.layout_detalle

        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.setParent(None)
