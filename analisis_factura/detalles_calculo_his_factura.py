# -------------------------------------------------------------#
# Módulo: detalles_calculo_his_factura.py                      #
# Descripción: Detalle del cálculo de una factura (histórico)  #
# Autor: Antonio Morales                                       #
# Fecha: 2026-04                                               #
# -------------------------------------------------------------#

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,  ### CAMBIO
    QVBoxLayout,
    QWidget,
)


class DetallesCalculoHisFactura(QWidget):
    """
    Pantalla 4 del histórico.
    Muestra el cálculo completo de una factura usando los datos
    precalculados en factura_calculos.
    """

    def __init__(self, parent=None, conn=None, nfactura=None):
        super().__init__(parent)
        self.parent = parent
        self.conn = conn
        self.nfactura = nfactura

        self.datos_factura = self.cargar_datos_factura()
        self.datos_calculo = self.cargar_calculo()

        self.crear_ui()

    # ---------------------------------------------------------
    # CARGA DE DATOS
    # ---------------------------------------------------------
    def cargar_datos_factura(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT nfactura, inicio_factura, fin_factura,
                   dias_factura, fec_emision
            FROM facturas
            WHERE nfactura = ?
            """,
            (self.nfactura,),
        )
        row = cur.fetchone()
        if not row:
            return None

        return {
            "nfactura": row[0],
            "inicio": row[1],
            "fin": row[2],
            "dias": row[3],
            "emision": row[4],
        }

    def cargar_calculo(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT total_energia, total_cargos, total_servicios,
                   total_iva, cloud_aplicado, cloud_sobrante,
                   total_final, detalles_json,
                   version_motor, fecha_calculo
            FROM factura_calculos
            WHERE nfactura = ?
            """,
            (self.nfactura,),
        )
        row = cur.fetchone()
        if not row:
            return None

        return {
            "total_energia": row[0],
            "total_cargos": row[1],
            "total_servicios": row[2],
            "total_iva": row[3],
            "cloud_aplicado": row[4],
            "cloud_sobrante": row[5],
            "total_final": row[6],
            "json": json.loads(row[7]),
            "version_motor": row[8],
            "fecha_calculo": row[9],
        }

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def crear_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        layout.addWidget(self.bloque_identificacion())
        layout.addWidget(self.bloque_totales())

        ### CAMBIO — El bloque de detalles va dentro de un scroll vertical
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        contenedor_detalles = QWidget()
        vbox_detalles = QVBoxLayout(contenedor_detalles)
        vbox_detalles.addWidget(self.bloque_detalles())
        scroll.setWidget(contenedor_detalles)

        layout.addWidget(scroll)

        layout.addWidget(self.bloque_motor())

        # Botón volver SIEMPRE visible (fuera del scroll)
        botones = QHBoxLayout()
        btn_volver = QPushButton("Volver")
        btn_volver.clicked.connect(self.volver)
        botones.addStretch()
        botones.addWidget(btn_volver)

        layout.addLayout(botones)

    # ---------------------------------------------------------
    # BLOQUES
    # ---------------------------------------------------------
    def bloque_identificacion(self):
        d = self.datos_factura

        grupo = QGroupBox("Identificación")
        form = QFormLayout()

        form.addRow("Número factura:", QLabel(str(d["nfactura"])))
        form.addRow("Inicio periodo:", QLabel(str(d["inicio"])))
        form.addRow("Fin periodo:", QLabel(str(d["fin"])))
        form.addRow("Días facturados:", QLabel(str(d["dias"])))
        form.addRow("Fecha emisión:", QLabel(str(d["emision"])))

        grupo.setLayout(form)
        return grupo

    def bloque_totales(self):
        d = self.datos_calculo

        grupo = QGroupBox("Totales factura")
        form = QFormLayout()

        form.addRow("Total energía (€):", QLabel(str(d["total_energia"])))
        form.addRow("Total cargos (€):", QLabel(str(d["total_cargos"])))
        form.addRow("Total servicios (€):", QLabel(str(d["total_servicios"])))
        form.addRow("IVA (€):", QLabel(str(d["total_iva"])))
        form.addRow("Cloud aplicado (€):", QLabel(str(d["cloud_aplicado"])))
        form.addRow("Sobrante excedentes (€):", QLabel(str(d["cloud_sobrante"])))
        form.addRow("TOTAL FINAL (€):", QLabel(str(d["total_final"])))

        grupo.setLayout(form)
        return grupo

    def bloque_detalles(self):
        j = self.datos_calculo["json"]

        grupo = QGroupBox("Desglose del cálculo")
        layout = QVBoxLayout()

        layout.addWidget(self.subbloque("Potencia", j["potencia"]))
        layout.addWidget(self.subbloque("Consumo", j["consumo"]))
        layout.addWidget(self.subbloque("Excedentes", j["excedentes"]))
        layout.addWidget(self.subbloque("Cargos normativos", j["cargos"]))
        layout.addWidget(self.subbloque("Servicios", j["servicios"]))
        layout.addWidget(self.subbloque("IVA", j["iva"]))
        layout.addWidget(self.subbloque("Cloud", j["cloud"]))

        grupo.setLayout(layout)
        return grupo

    ### CAMBIO — subbloque recursivo
    def subbloque(self, titulo, datos_dict):
        grupo = QGroupBox(titulo)
        layout = QVBoxLayout()

        for clave, valor in datos_dict.items():
            if isinstance(valor, dict):
                # Sub-sub-bloque
                layout.addWidget(self.subbloque(clave, valor))
            else:
                fila = QFormLayout()
                fila.addRow(f"{clave}:", QLabel(str(valor)))
                layout.addLayout(fila)

        grupo.setLayout(layout)
        return grupo

    def bloque_motor(self):
        d = self.datos_calculo

        grupo = QGroupBox("Información del motor")
        form = QFormLayout()

        form.addRow("Versión motor:", QLabel(str(d["version_motor"])))
        form.addRow("Fecha cálculo:", QLabel(str(d["fecha_calculo"])))

        grupo.setLayout(form)
        return grupo

    # ---------------------------------------------------------
    # NAVEGACIÓN
    # ---------------------------------------------------------
    def volver(self):
        from analisis_factura.formulario_his_factura import FormularioHisFactura

        mw = self.window()
        widget = FormularioHisFactura(
            parent=mw,
            conn=self.conn,
            nfactura=self.nfactura,
        )
        mw.cargar_modulo(widget, "Detalles de la factura")
