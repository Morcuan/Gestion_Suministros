# ------------------------------------------------------------#
# FormularioContrato.py                                       #
# Formulario unificado para ALTA y MODIFICACIÓN de contratos  #
# ------------------------------------------------------------#
import sys

print(">>> CARGANDO formulario_contrato DESDE:", __name__)
print(">>> sys.modules contiene:")
for m in sys.modules:
    if "formulario_contrato" in m:
        print("   -", m, "=>", sys.modules[m])

import copy
import re
from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from estilo import aplicar_estilo_campo


class FormularioContrato(QWidget):

    guardado_alta = Signal(dict)
    guardado_modificacion = Signal(dict)
    cancelado = Signal()

    def __init__(self, modo="alta", datos=None, parent=None):
        """
        modo = "alta" o "modificacion"
        datos = diccionario con datos del contrato (solo en modificación)
        """
        super().__init__(parent)

        self.modo = modo
        self.datos_originales = copy.deepcopy(datos) if datos else {}
        self.setWindowTitle(
            "Nuevo contrato" if modo == "alta" else "Modificación de contrato"
        )

        # ------------------------------------------------------------
        #  BLOQUES
        # ------------------------------------------------------------
        self.bloque_ident = self.crear_bloque_identificacion()
        self.bloque_energia = self.crear_bloque_energia()
        self.bloque_gastos = self.crear_bloque_gastos()

        # ------------------------------------------------------------
        #  ESTILO DE CAMPOS (igual que en Nuevo contrato)
        # ------------------------------------------------------------
        for w in self.findChildren(QLineEdit):
            aplicar_estilo_campo(w)
        for w in self.findChildren(QComboBox):
            aplicar_estilo_campo(w)

        # ------------------------------------------------------------
        #  TÍTULO
        # ------------------------------------------------------------
        titulo = QLabel(
            "Nuevo contrato" if modo == "alta" else "Modificación de contrato"
        )
        fuente = QFont()
        fuente.setBold(True)
        fuente.setPointSize(12)
        titulo.setFont(fuente)

        # ------------------------------------------------------------
        #  BOTONES
        # ------------------------------------------------------------
        self.btn_guardar = QPushButton(
            "Guardar contrato" if modo == "alta" else "Guardar modificación"
        )
        self.btn_cancelar = QPushButton("Cancelar")

        self.btn_guardar.clicked.connect(self.pre_guardado)
        self.btn_cancelar.clicked.connect(lambda: self.cancelado.emit())

        # ------------------------------------------------------------
        #  LAYOUT GENERAL
        # ------------------------------------------------------------
        layout = QVBoxLayout()
        layout.addWidget(titulo)
        layout.addWidget(self.bloque_ident)
        layout.addWidget(self.bloque_energia)
        layout.addWidget(self.bloque_gastos)

        botones = QHBoxLayout()
        botones.addWidget(self.btn_guardar)
        botones.addStretch()
        botones.addWidget(self.btn_cancelar)

        layout.addLayout(botones)
        self.setLayout(layout)

        # Ajuste de anchos (igual que en Nuevo contrato)
        self.ajustar_anchos()

        # Cargar datos si estamos en modificación
        if self.modo == "modificacion":
            self.cargar_datos(self.datos_originales)
            self.bloquear_campos_modificacion()

        # Validaciones
        self.conectar_validaciones()

    # ============================================================
    #  BLOQUE IDENTIFICACIÓN
    # ============================================================
    def crear_bloque_identificacion(self):
        box = QGroupBox("Identificación")
        layout = QFormLayout()
        layout.setHorizontalSpacing(20)
        layout.setVerticalSpacing(6)

        self.ncontrato = QLineEdit()
        self.suplemento = QLineEdit()
        self.compania = QComboBox()
        self.codigo_postal = QLineEdit()

        self.fec_inicio = QLineEdit()
        self.fec_final = QLineEdit()
        self.fec_anulacion = QLineEdit()
        self.estado = QLineEdit()

        self.efec_suple = QLineEdit()
        self.fin_suple = QLineEdit()

        layout.addRow("Nº contrato:", self.ncontrato)
        layout.addRow("Suplemento:", self.suplemento)
        layout.addRow("Compañía:", self.compania)
        layout.addRow("Código postal:", self.codigo_postal)
        layout.addRow("Fecha inicio (dd/mm/yyyy):", self.fec_inicio)
        layout.addRow("Fecha final (dd/mm/yyyy):", self.fec_final)
        layout.addRow("Fecha anulación (dd/mm/yyyy):", self.fec_anulacion)
        layout.addRow("Estado:", self.estado)
        layout.addRow("Efecto suplemento:", self.efec_suple)
        layout.addRow("Fin suplemento:", self.fin_suple)

        box.setLayout(layout)
        box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        return box

    # ============================================================
    #  BLOQUE ENERGÍA
    # ============================================================
    def crear_bloque_energia(self):
        box = QGroupBox("Energía")
        layout = QFormLayout()
        layout.setHorizontalSpacing(20)
        layout.setVerticalSpacing(6)

        self.ppunta = QLineEdit()
        self.pvalle = QLineEdit()

        self.pv_ppunta = QLineEdit()
        self.pv_pvalle = QLineEdit()

        self.pv_conpunta = QLineEdit()
        self.pv_conllano = QLineEdit()
        self.pv_convalle = QLineEdit()

        self.vertido = QComboBox()
        self.vertido.addItems(["Sí", "No"])

        self.pv_excedent = QLineEdit()

        layout.addRow("Potencia punta (kW):", self.ppunta)
        layout.addRow("Potencia valle (kW):", self.pvalle)
        layout.addRow("Potencia punta (€/kW·día):", self.pv_ppunta)
        layout.addRow("Potencia valle (€/kW·día):", self.pv_pvalle)
        layout.addRow("Consumo punta (€/kWh):", self.pv_conpunta)
        layout.addRow("Consumo llano (€/kWh):", self.pv_conllano)
        layout.addRow("Consumo valle (€/kWh):", self.pv_convalle)
        layout.addRow("Vertido:", self.vertido)
        layout.addRow("Excedente (€/kWh):", self.pv_excedent)

        box.setLayout(layout)
        box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        return box

    # ============================================================
    #  BLOQUE GASTOS
    # ============================================================
    def crear_bloque_gastos(self):
        box = QGroupBox("Gastos")
        layout = QFormLayout()
        layout.setHorizontalSpacing(20)
        layout.setVerticalSpacing(6)

        self.bono_social = QLineEdit()
        self.alq_contador = QLineEdit()
        self.otros_gastos = QLineEdit()
        self.i_electrico = QLineEdit()
        self.iva = QLineEdit()

        layout.addRow("Bono social (€/día):", self.bono_social)
        layout.addRow("Alquiler contador (€/día):", self.alq_contador)
        layout.addRow("Otros gastos:", self.otros_gastos)
        layout.addRow("Impuesto eléctrico (%):", self.i_electrico)
        layout.addRow("IVA (%):", self.iva)

        box.setLayout(layout)
        box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        return box

    # ============================================================
    #  CARGA DE DATOS (solo en modificación)
    # ============================================================
    def cargar_datos(self, d):
        self.ncontrato.setText(str(d.get("ncontrato", "")))
        self.suplemento.setText(str(d.get("suplemento", "")))

        self.compania.addItem(d.get("compania", ""))
        self.compania.setCurrentText(d.get("compania", ""))

        self.codigo_postal.setText(str(d.get("codigo_postal", "")))

        self.fec_inicio.setText(self.from_iso(d.get("fec_inicio")))
        self.fec_final.setText(self.from_iso(d.get("fec_final")))
        self.fec_anulacion.setText(self.from_iso(d.get("fec_anulacion")))
        self.estado.setText(str(d.get("estado", "")))

        self.efec_suple.setText(self.from_iso(d.get("efec_suple")))
        self.fin_suple.setText(self.from_iso(d.get("fin_suple")))

        self.ppunta.setText(self.to_str(d.get("ppunta")))
        self.pvalle.setText(self.to_str(d.get("pvalle")))
        self.pv_ppunta.setText(self.to_str(d.get("pv_ppunta")))
        self.pv_pvalle.setText(self.to_str(d.get("pv_pvalle")))
        self.pv_conpunta.setText(self.to_str(d.get("pv_conpunta")))
        self.pv_conllano.setText(self.to_str(d.get("pv_conllano")))
        self.pv_convalle.setText(self.to_str(d.get("pv_convalle")))

        self.vertido.setCurrentText("Sí" if d.get("vertido") else "No")
        self.pv_excedent.setText(self.to_str(d.get("pv_excedent")))

        self.bono_social.setText(self.to_str(d.get("bono_social")))
        self.alq_contador.setText(self.to_str(d.get("alq_contador")))
        self.otros_gastos.setText(self.to_str(d.get("otros_gastos")))
        self.i_electrico.setText(self.to_str(d.get("i_electrico")))
        self.iva.setText(self.to_str(d.get("iva")))

    # ============================================================
    #  BLOQUEAR CAMPOS EN MODO MODIFICACIÓN
    # ============================================================
    def bloquear_campos_modificacion(self):
        self.ncontrato.setReadOnly(True)
        self.suplemento.setReadOnly(True)
        self.fec_inicio.setReadOnly(True)
        self.fec_final.setReadOnly(True)
        self.fec_anulacion.setReadOnly(True)
        self.estado.setReadOnly(True)
        self.fin_suple.setReadOnly(True)

    # ============================================================
    #  VALIDACIONES
    # ============================================================
    def conectar_validaciones(self):
        widgets = [
            self.codigo_postal,
            self.efec_suple,
            self.ppunta,
            self.pvalle,
            self.pv_ppunta,
            self.pv_pvalle,
            self.pv_conpunta,
            self.pv_conllano,
            self.pv_convalle,
            self.pv_excedent,
            self.bono_social,
            self.alq_contador,
            self.otros_gastos,
            self.i_electrico,
            self.iva,
        ]

        for w in widgets:
            w.textChanged.connect(self.validar_formulario)

        self.vertido.currentIndexChanged.connect(self.validar_formulario)
        self.validar_formulario()

    def validar_formulario(self):
        # Validación de fecha
        if not self.validar_fecha(self.efec_suple.text()):
            self.btn_guardar.setEnabled(False)
            return

        # Validación numérica
        for campo in [
            self.ppunta,
            self.pvalle,
            self.pv_ppunta,
            self.pv_pvalle,
            self.pv_conpunta,
            self.pv_conllano,
            self.pv_convalle,
            self.pv_excedent,
            self.bono_social,
            self.alq_contador,
            self.otros_gastos,
            self.i_electrico,
            self.iva,
        ]:
            t = campo.text().strip()
            if t in ("", "-", ",", ".", "0,", "0.", ",0"):
                continue
            try:
                float(t.replace(",", "."))
            except ValueError:
                self.btn_guardar.setEnabled(False)
                return

        self.btn_guardar.setEnabled(True)

    # ============================================================
    #  PRE-GUARDADO
    # ============================================================
    def pre_guardado(self):
        if not self.btn_guardar.isEnabled():
            QMessageBox.warning(self, "Atención", "Hay errores en el formulario.")
            return

        datos = self.recoger_datos()

        if self.modo == "alta":
            self.guardado_alta.emit(datos)
        else:
            self.guardado_modificacion.emit(datos)

        self.close()

    # ============================================================
    #  RECOGER DATOS
    # ============================================================
    def recoger_datos(self):
        d = {}

        d["ncontrato"] = self.ncontrato.text().strip()
        d["suplemento"] = self.suplemento.text().strip()
        d["compania"] = self.compania.currentText()
        d["codigo_postal"] = self.codigo_postal.text().strip()

        d["fec_inicio"] = self.to_iso(self.fec_inicio.text())
        d["fec_final"] = self.to_iso(self.fec_final.text())
        d["fec_anulacion"] = (
            self.to_iso(self.fec_anulacion.text())
            if self.fec_anulacion.text().strip()
            else None
        )
        d["estado"] = self.estado.text().strip()

        d["efec_suple"] = self.to_iso(self.efec_suple.text())
        d["fin_suple"] = self.fin_suple.text().strip()

        d["ppunta"] = self.to_float(self.ppunta.text())
        d["pvalle"] = self.to_float(self.pvalle.text())
        d["pv_ppunta"] = self.to_float(self.pv_ppunta.text())
        d["pv_pvalle"] = self.to_float(self.pv_pvalle.text())
        d["pv_conpunta"] = self.to_float(self.pv_conpunta.text())
        d["pv_conllano"] = self.to_float(self.pv_conllano.text())
        d["pv_convalle"] = self.to_float(self.pv_convalle.text())

        d["vertido"] = 1 if self.vertido.currentText() == "Sí" else 0
        d["pv_excedent"] = self.to_float(self.pv_excedent.text())

        d["bono_social"] = self.to_float(self.bono_social.text())
        d["alq_contador"] = self.to_float(self.alq_contador.text())
        d["otros_gastos"] = self.to_float(self.otros_gastos.text())
        d["i_electrico"] = self.to_float(self.i_electrico.text())
        d["iva"] = self.to_float(self.iva.text())

        return d

    # ============================================================
    #  AUXILIARES
    # ============================================================
    def ajustar_anchos(self):
        for w in self.findChildren(QLineEdit):
            w.setMinimumWidth(260)
            w.setFixedHeight(28)
        for w in self.findChildren(QComboBox):
            w.setMinimumWidth(260)
            w.setFixedHeight(28)

    @staticmethod
    def validar_fecha(f):
        return bool(re.fullmatch(r"\d{2}/\d{2}/\d{4}", f.strip()))

    @staticmethod
    def to_iso(f):
        d = datetime.strptime(f.strip(), "%d/%m/%Y")
        return d.strftime("%Y-%m-%d")

    @staticmethod
    def from_iso(f):
        if not f:
            return ""
        d = datetime.strptime(f, "%Y-%m-%d")
        return d.strftime("%d/%m/%Y")

    @staticmethod
    def to_float(t):
        if not t.strip():
            return 0.0
        return float(t.replace(",", "."))

    @staticmethod
    def to_str(v):
        if v is None:
            return ""
        if isinstance(v, float):
            return str(v).replace(".", ",")
        return str(v)
