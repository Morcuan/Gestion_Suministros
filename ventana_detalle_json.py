# --------------------------------------------#
# Modulo: ventana_detalle_json.py                          #
# Descripción: Ventana de detalle de JSON de factura #
# Autor: Antonio Morales                      #
# Fecha: 2026-02-09                           #
# --------------------------------------------#

# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


# Ventana de detalle para mostrar el JSON de cada bloque (energía, cargos, servicios, IVA)
class VentanaDetalleJSON(QWidget):
    # init con datos del bloque, clave para identificar
    # el bloque y días para mostrar en el título
    def __init__(self, datos_bloque, clave, dias, parent=None):
        super().__init__(parent)

        # Tamaño de letra para TODO el subformulario
        self.setStyleSheet("font-size: 16px;")

        self.datos = datos_bloque
        self.clave = clave
        self.dias = dias

        # --- CONTENEDOR INTERNO PARA EVITAR QUE EL PANEL DERECHO SE ESTIRE ---
        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)

        # --- TU CÓDIGO TAL CUAL ---
        if clave == "energia":
            layout.addWidget(self.bloque_energia(self.datos))
        elif clave == "cargos":
            layout.addWidget(self.bloque_generico("CARGOS NORMATIVOS", self.datos))
        elif clave == "servicios":
            layout.addWidget(self.bloque_generico("SERVICIOS Y OTROS", self.datos))
        elif clave == "iva":
            layout.addWidget(self.bloque_generico("IVA", self.datos))

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.cerrar_subformulario)
        layout.addWidget(btn_cerrar, alignment=Qt.AlignRight)

        # --- SCROLL PARA QUE EL SUBFORMULARIO NO SE DESCUELGUE ---
        scroll = QScrollArea()
        scroll.setWidget(contenedor)
        scroll.setWidgetResizable(True)

        # --- LAYOUT FINAL ---
        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(scroll)
        self.setLayout(layout_principal)

    # ---------------------------------------------------------
    # BLOQUES
    # ---------------------------------------------------------
    # Bloque específico para energía, con estructura de periodos y totales
    def bloque_energia(self, energia):
        grupo = QGroupBox("DETALLE DE ENERGÍA")
        form = QFormLayout()

        # --- POTENCIA ---
        pot = energia.get("potencia", {})
        if pot:
            form.addRow(QLabel("<b>POTENCIA</b>"))
            periodos = pot.get("periodos", {})
            for periodo, datos in periodos.items():
                form.addRow(f"  {periodo}:", QLabel(""))
                for k, v in datos.items():
                    form.addRow(f"    {k}:", QLabel(str(v)))
            form.addRow("Total potencia:", QLabel(str(pot.get("total", ""))))

        # --- CONSUMO ---
        con = energia.get("consumo", {})
        if con:
            form.addRow(QLabel("<b>CONSUMO</b>"))
            periodos = con.get("periodos", {})
            for periodo, datos in periodos.items():
                form.addRow(f"  {periodo}:", QLabel(""))
                for k, v in datos.items():
                    form.addRow(f"    {k}:", QLabel(str(v)))
            form.addRow("Total consumo:", QLabel(str(con.get("total", ""))))

        # --- EXCEDENTES ---
        exc = energia.get("excedentes", {})
        if exc:
            form.addRow(QLabel("<b>EXCEDENTES</b>"))
            for k, v in exc.items():
                form.addRow(f"{k}:", QLabel(str(v)))

        grupo.setLayout(form)
        return grupo

    # Bloque genérico para cargos, servicios e IVA, con estructura simple de clave-valor
    def bloque_generico(self, titulo, datos):
        grupo = QGroupBox(titulo)
        form = QFormLayout()

        for clave, valor in datos.items():
            form.addRow(f"{clave}:", QLabel(str(valor)))

        grupo.setLayout(form)
        return grupo

    # ---------------------------------------------------------
    # BOTÓN CERRAR
    # ---------------------------------------------------------
    # def cerrar_subformulario(self):
    #    parent = self.parent()
    #    if hasattr(parent, "cargar_detalle"):
    #       parent.cargar_detalle(parent.panel_detalle)

    # def cerrar_subformulario(self):
    #    self.setParent(None)
    #    self.deleteLater()

    def cerrar_subformulario(self):
        parent = self.parent().parent()  # subimos hasta ResumenFactura
        if hasattr(parent, "limpiar_detalle"):
            parent.limpiar_detalle()
            parent.limpiar_detalle()
