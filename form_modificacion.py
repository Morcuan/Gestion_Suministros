# --------------------------------------------#
# Modulo: form_modificacion.py                #
# Descripción: Modificación de contrato       #
# Autor: Antonio Morales + Copilot            #
# Fecha: 2026-02-24                           #
# --------------------------------------------#
# Este módulo define el formulario de modificación de contrato/suplemento.
# Permite detectar cambios económicos vs administrativos, validar fechas
# y emitir señales diferenciadas según el tipo de cambio.


# IMPORTACIONES
import copy
import re
from datetime import date, datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from estilo import aplicar_estilo_campo


# ------------------------------------------------------------
# CLASE PRINCIPAL
# ------------------------------------------------------------
class FormModificacionContrato(QWidget):
    """
    Formulario de modificación de contrato / suplemento.

    Recibe un diccionario con los datos del suplemento vigente
    (normalmente procedente de vista_contratos + id_contrato)
    y permite:

    - Detectar cambios económicos vs administrativos
    - Validar fechas de efecto del nuevo suplemento
    - Emitir señales diferenciadas según el tipo de cambio
    """

    # Si solo hay cambios administrativos → actualizar suplemento vigente
    actualizar_vigente = Signal(dict)

    # Si hay cambios económicos → crear suplemento nuevo
    crear_suplemento = Signal(dict)

    cancelado = Signal()

    def __init__(self, datos_contrato: dict, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Modificación de contrato / suplemento")

        # Datos originales del suplemento vigente
        # Se espera algo del estilo:
        # {
        #   "id_contrato": ...,
        #   "ncontrato": ...,
        #   "suplemento": ...,
        #   "compania": ...,
        #   "codigo_postal": ...,
        #   "fec_inicio": "YYYY-MM-DD",
        #   "fec_final": "YYYY-MM-DD",
        #   "efec_suple": "YYYY-MM-DD",
        #   "fin_suple": "YYYY-MM-DD",
        #   "estado": ...,
        #   "ppunta": ...,
        #   "pv_ppunta": ...,
        #   "pvalle": ...,
        #   "pv_pvalle": ...,
        #   "pv_conpunta": ...,
        #   "pv_conllano": ...,
        #   "pv_convalle": ...,
        #   "vertido": 0/1,
        #   "pv_excedent": ...,
        #   "bono_social": ...,
        #   "alq_contador": ...,
        #   "otros_gastos": ...,
        #   "i_electrico": ...,
        #   "iva": ...
        # }
        self.datos_originales = copy.deepcopy(datos_contrato)
        self.datos = copy.deepcopy(datos_contrato)

        # Listas de campos económicos y administrativos
        self.campos_economicos = [
            "efec_suple",
            "ppunta",
            "pv_ppunta",
            "pvalle",
            "pv_pvalle",
            "pv_conpunta",
            "pv_conllano",
            "pv_convalle",
            "pv_excedent",
            "bono_social",
            "alq_contador",
            "otros_gastos",
            "i_electrico",
            "iva",
        ]

        # Administrativos (ejemplo: compañía, código postal, etc.)
        self.campos_administrativos = [
            "compania",
            "codigo_postal",
            # aquí se podrían añadir más campos no económicos
        ]

        # ------------------------------------------------------------
        #  CREACIÓN DE BLOQUES
        # ------------------------------------------------------------
        self.bloque_ident = self.crear_bloque_identificacion()
        self.bloque_energia = self.crear_bloque_energia()
        self.bloque_gastos = self.crear_bloque_gastos()

        for w in self.findChildren(QLineEdit):
            aplicar_estilo_campo(w)
        for w in self.findChildren(QComboBox):
            aplicar_estilo_campo(w)

        self.setMinimumWidth(650)
        self.setMaximumWidth(750)

        # ------------------------------------------------------------
        # BOTONES
        # ------------------------------------------------------------
        self.btn_guardar = QPushButton("Guardar modificación")
        self.btn_cancelar = QPushButton("Cancelar")

        self.btn_guardar.clicked.connect(self.pre_guardado)
        self.btn_cancelar.clicked.connect(lambda: self.cancelado.emit())

        print("BOTÓN CANCELAR REAL:", self.btn_cancelar)
        self.btn_cancelar.clicked.connect(lambda: print("CANCELAR PULSADO EN:", self))

        layout = QVBoxLayout()
        layout.addWidget(self.bloque_ident)
        layout.addWidget(self.bloque_energia)
        layout.addWidget(self.bloque_gastos)

        botones = QHBoxLayout()
        botones.addStretch()
        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_cancelar)

        layout.addLayout(botones)
        self.setLayout(layout)

        self.ajustar_anchos()
        self.cargar_datos()
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
        self.ncontrato.setReadOnly(True)

        self.suplemento = QLineEdit()
        self.suplemento.setReadOnly(True)

        self.compania = QComboBox()

        self.codigo_postal = QLineEdit()

        self.fec_inicio = QLineEdit()
        self.fec_inicio.setReadOnly(True)

        self.fec_final = QLineEdit()
        self.fec_final.setReadOnly(True)

        self.fec_anulacion = QLineEdit()
        self.fec_anulacion.setReadOnly(True)

        self.estado = QLineEdit()
        self.estado.setReadOnly(True)

        # En modificación, efec_suple SÍ es editable
        self.efec_suple = QLineEdit()

        self.fin_suple = QLineEdit()
        self.fin_suple.setReadOnly(True)

        layout.addRow("Nº contrato:", self.ncontrato)
        layout.addRow("Suplemento vigente:", self.suplemento)
        layout.addRow("Compañía:", self.compania)
        layout.addRow("Código postal:", self.codigo_postal)
        layout.addRow("Fecha inicio contrato:", self.fec_inicio)
        layout.addRow("Fecha final contrato:", self.fec_final)
        layout.addRow("Fecha anulación:", self.fec_anulacion)
        layout.addRow("Estado suplemento:", self.estado)
        layout.addRow("Efecto suplemento (dd/mm/yyyy):", self.efec_suple)
        layout.addRow("Fin suplemento (dd/mm/yyyy):", self.fin_suple)

        box.setLayout(layout)
        box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
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
        box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
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
        box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        return box

    # ============================================================
    #  CARGA DE DATOS
    # ============================================================
    def cargar_datos(self):
        d = self.datos_originales

        self.ncontrato.setText(str(d.get("ncontrato", "")))
        self.suplemento.setText(str(d.get("suplemento", "")))

        # Compañía: aquí asumimos que el combo se rellenará desde fuera
        # y que d["compania"] coincide con uno de los textos
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

        # Validación básica de formato de fecha
        if not self.validar_fecha(self.efec_suple.text()):
            self.btn_guardar.setEnabled(False)
            return

        try:
            # Convertir fechas a ISO
            fi_iso = self.to_iso(self.fec_inicio.text())
            ff_iso = self.to_iso(self.fec_final.text())
            fe_iso = self.to_iso(self.efec_suple.text())

            # Convertir a date
            fi = datetime.strptime(fi_iso, "%Y-%m-%d").date()
            ff = datetime.strptime(ff_iso, "%Y-%m-%d").date()
            fe = datetime.strptime(fe_iso, "%Y-%m-%d").date()

            # Validar rango dentro del contrato
            if not (fi <= fe <= ff):
                self.btn_guardar.setEnabled(False)
                return

            # Validar que el nuevo suplemento empieza después del vigente
            fe_vigente_iso = self.datos_originales.get("efec_suple")
            if fe_vigente_iso:
                fe_v = datetime.strptime(fe_vigente_iso, "%Y-%m-%d").date()
                if fe <= fe_v:
                    self.btn_guardar.setEnabled(False)
                    return

        except Exception:
            self.btn_guardar.setEnabled(False)
            return

        # Validaciones numéricas tolerantes
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
            texto = campo.text().strip()

            # Permitir valores intermedios mientras el usuario escribe
            if texto in ("", "-", ",", ".", "0,", "0.", ",0"):
                continue

            try:
                float(texto.replace(",", "."))
            except ValueError:
                self.btn_guardar.setEnabled(False)
                return

        # Si todo es válido → habilitar botón
        self.btn_guardar.setEnabled(True)

    # ============================================================
    #  PRE-GUARDADO
    # ============================================================
    def pre_guardado(self):
        if not self.btn_guardar.isEnabled():
            QMessageBox.warning(self, "Atención", "Hay errores en el formulario.")
            return

        # Construir diccionario actual
        actual = self.recoger_datos_actuales()

        # Detectar cambios
        cambios_econ, cambios_admin = self.detectar_cambios(actual)

        if not cambios_econ and not cambios_admin:
            QMessageBox.information(
                self, "Sin cambios", "No se ha modificado ningún dato."
            )
            return

        if not cambios_econ and cambios_admin:
            # Solo cambios administrativos → actualizar suplemento vigente
            self.actualizar_vigente.emit(actual)
            return

        # Hay cambios económicos → crear suplemento nuevo
        self.crear_suplemento.emit(actual)
        self.close()

    # ============================================================
    #  RECOGER DATOS ACTUALES
    # ============================================================
    def recoger_datos_actuales(self) -> dict:
        d = {}

        d["id_contrato"] = self.datos_originales.get("id_contrato")
        d["ncontrato"] = self.ncontrato.text().strip()
        d["suplemento"] = self.datos_originales.get("suplemento")  # el vigente
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
        d["fin_suple"] = self.datos_originales.get("fin_suple")

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
    #  DETECCIÓN DE CAMBIOS
    # ============================================================
    def detectar_cambios(self, actual: dict):
        cambios_econ = False
        cambios_admin = False

        for campo in self.campos_economicos:
            if self.normalizar_valor(
                self.datos_originales.get(campo)
            ) != self.normalizar_valor(actual.get(campo)):
                cambios_econ = True
                break

        for campo in self.campos_administrativos:
            if self.normalizar_valor(
                self.datos_originales.get(campo)
            ) != self.normalizar_valor(actual.get(campo)):
                cambios_admin = True
                break

        return cambios_econ, cambios_admin

    @staticmethod
    def normalizar_valor(v):
        if isinstance(v, float):
            return round(v, 6)
        return v

    # ============================================================
    #  AUXILIARES
    # ============================================================
    def ajustar_anchos(self):
        for w in self.findChildren(QLineEdit):
            w.setMinimumWidth(260)
            w.setMaximumWidth(320)
        for w in self.findChildren(QComboBox):
            w.setMinimumWidth(260)
            w.setMaximumWidth(320)

    @staticmethod
    def validar_fecha(f: str) -> bool:
        return bool(re.fullmatch(r"\d{2}/\d{2}/\d{4}", f.strip()))

    @staticmethod
    def to_iso(f: str) -> str:
        d = datetime.strptime(f.strip(), "%d/%m/%Y")
        return d.strftime("%Y-%m-%d")

    @staticmethod
    def from_iso(f: str | None) -> str:
        if not f:
            return ""
        d = datetime.strptime(f, "%Y-%m-%d")
        return d.strftime("%d/%m/%Y")

    @staticmethod
    def to_float(t: str) -> float:
        if not t.strip():
            return 0.0
        return float(t.replace(",", "."))

    @staticmethod
    def to_str(v) -> str:
        if v is None:
            return ""
        if isinstance(v, float):
            return str(v).replace(".", ",")
        return str(v)

    # ============================================================
    #  AJUSTE DE TABULACIÓN
    # ============================================================
    def showEvent(self, event):
        super().showEvent(event)

        self.setTabOrder(self.ncontrato, self.compania)
        self.setTabOrder(self.compania, self.codigo_postal)
        self.setTabOrder(self.codigo_postal, self.efec_suple)

        self.setTabOrder(self.efec_suple, self.ppunta)
        self.setTabOrder(self.ppunta, self.pvalle)
        self.setTabOrder(self.pvalle, self.pv_ppunta)
        self.setTabOrder(self.pv_ppunta, self.pv_pvalle)
        self.setTabOrder(self.pv_pvalle, self.pv_conpunta)
        self.setTabOrder(self.pv_conpunta, self.pv_conllano)
        self.setTabOrder(self.pv_conllano, self.pv_convalle)
        self.setTabOrder(self.pv_convalle, self.vertido)
        self.setTabOrder(self.vertido, self.pv_excedent)

        self.setTabOrder(self.pv_excedent, self.bono_social)
        self.setTabOrder(self.bono_social, self.alq_contador)
        self.setTabOrder(self.alq_contador, self.otros_gastos)
        self.setTabOrder(self.otros_gastos, self.i_electrico)
        self.setTabOrder(self.i_electrico, self.iva)

        self.setTabOrder(self.iva, self.btn_guardar)
        self.setTabOrder(self.btn_guardar, self.btn_cancelar)
        self.setTabOrder(self.btn_guardar, self.btn_cancelar)
        self.setTabOrder(self.btn_guardar, self.btn_cancelar)
