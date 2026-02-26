# --------------------------------------------#
# Modulo: form_contrato.py                    #
# Descripción: Formulario de contrato         #
# Autor: Antonio Morales                      #
# Fecha: 2026-02-09                           #
# --------------------------------------------#
# Este módulo define el formulario de contrato, dividido en tres bloques: Identificación, Energía y Gastos.
# Incluye validaciones progresivas, un flujo de pre-guardado para códigos postales inexistentes,
# y una ventana auxiliar para dar de alta nuevos códigos postales.

# Importaciones necesarias
import re
from datetime import date, datetime

# PySide6 para la interfaz gráfica
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

# Import del estilo
from estilo import aplicar_estilo_campo

# ============================================================
#  Ventana auxiliar para alta de códigos postales
# ============================================================


# Esta ventana se muestra cuando el usuario introduce un código postal que no
# existe en la base de datos.
class AltaCodigoPostal(QDialog):
    codigo_postal_creado = Signal(str, str)

    # El signal emite el código postal y la población introducida por el usuario,
    # para que el formulario principal pueda actualizarse y la base de datos pueda insertarlo.
    def __init__(self, codigo_postal, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Alta de código postal")

        self.cp = QLineEdit()
        self.cp.setText(codigo_postal)
        self.cp.setReadOnly(True)

        self.poblacion = QLineEdit()

        btn_guardar = QPushButton("Guardar")
        btn_cancelar = QPushButton("Cancelar")

        btn_guardar.clicked.connect(self.guardar)
        btn_cancelar.clicked.connect(self.reject)

        layout = QFormLayout()
        layout.addRow("Código postal:", self.cp)
        layout.addRow("Población:", self.poblacion)

        botones = QHBoxLayout()
        botones.addWidget(btn_guardar)
        botones.addWidget(btn_cancelar)

        v = QVBoxLayout()
        v.addLayout(layout)
        v.addLayout(botones)

        self.setLayout(v)

    # El método guardar valida que se haya introducido una población y luego emite el
    #   signal con el nuevo código postal y la población.
    def guardar(self):
        if not self.poblacion.text().strip():
            QMessageBox.warning(self, "Atención", "Debe introducir la población.")
            return

        self.codigo_postal_creado.emit(self.cp.text(), self.poblacion.text())

        self.accept()


# ============================================================
#  Formulario principal de contrato
# ============================================================


# El formulario de contrato se divide en tres bloques: Identificación, Energía y Gastos.
class FormContrato(QWidget):
    contrato_guardado = Signal(dict)
    cancelado = Signal()

    def __init__(self, modo="nuevo", datos=None, parent=None):
        super().__init__(parent)

        self.modo = modo
        self.datos = datos or {}

        self.setWindowTitle("Formulario de contrato")

        # ============================================================
        #  CREACIÓN DE BLOQUES
        # ============================================================

        self.bloque_ident = self.crear_bloque_identificacion()
        self.bloque_energia = self.crear_bloque_energia()
        self.bloque_gastos = self.crear_bloque_gastos()

        # ------------------------------------------------------------
        # APLICAR ESTILO A TODOS LOS CAMPOS
        # ------------------------------------------------------------
        for w in self.findChildren(QLineEdit):
            aplicar_estilo_campo(w)

        for w in self.findChildren(QComboBox):
            aplicar_estilo_campo(w)

        # 🔧 Ajustes de tamaño del formulario
        self.setMinimumWidth(650)
        self.setMaximumWidth(750)

        # ------------------------------------------------------------
        # BOTONES
        # ------------------------------------------------------------
        self.btn_guardar = QPushButton("Guardar contrato")
        self.btn_cancelar = QPushButton("Cancelar")

        self.btn_guardar.setEnabled(False)
        self.btn_guardar.clicked.connect(self.pre_guardado)
        self.btn_cancelar.clicked.connect(self.cancelado.emit)

        if self.modo == "consulta":
            self.btn_guardar.hide()

        # ------------------------------------------------------------
        # LAYOUT GENERAL
        # ------------------------------------------------------------
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

        # 🔧 Ajuste de anchos
        self.ajustar_anchos()

        # ------------------------------------------------------------
        # PRECARGA SI PROCEDE
        # ------------------------------------------------------------
        if self.modo in ("modificar", "consulta"):
            self.cargar_datos()

        # ------------------------------------------------------------
        # VALIDACIONES
        # ------------------------------------------------------------
        self.conectar_validaciones()

    # ============================================================
    #  BLOQUE IDENTIFICACIÓN
    # ============================================================
    # El bloque de identificación contiene los datos básicos del contrato,
    # como número de contrato,
    def crear_bloque_identificacion(self):
        box = QGroupBox("Identificación")
        layout = QFormLayout()

        layout.setHorizontalSpacing(20)
        layout.setVerticalSpacing(6)

        self.ncontrato = QLineEdit()
        self.suplemento = QLineEdit("0")
        self.suplemento.setReadOnly(True)

        self.compania = QComboBox()

        self.codigo_postal = QLineEdit()
        self.fec_inicio = QLineEdit()
        self.fec_final = QLineEdit()
        self.fec_anulacion = QLineEdit()
        if self.modo == "nuevo":
            self.fec_anulacion.setReadOnly(True)

        self.estado = QLineEdit()
        self.estado.setReadOnly(True)

        self.efec_suple = QLineEdit()
        self.efec_suple.setReadOnly(True)

        self.fin_suple = QLineEdit()
        self.fin_suple.setReadOnly(True)

        layout.addRow("Nº contrato:", self.ncontrato)
        layout.addRow("Suplemento:", self.suplemento)
        layout.addRow("Compañía:", self.compania)
        layout.addRow("Código postal:", self.codigo_postal)
        layout.addRow("Fecha inicio (dd/mm/yyyy):", self.fec_inicio)
        layout.addRow("Fecha final (dd/mm/yyyy):", self.fec_final)
        layout.addRow("Fecha anulación (dd/mm/yyyy):", self.fec_anulacion)
        layout.addRow("Estado:", self.estado)
        layout.addRow("Efecto suplemento (dd/mm/yyyy):", self.efec_suple)
        layout.addRow("Fin suplemento (dd/mm/yyyy):", self.fin_suple)

        box.setLayout(layout)
        box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        return box

    # ============================================================
    #  BLOQUE ENERGÍA
    # ============================================================
    # El bloque de energía contiene los datos relacionados con la potencia contratada,
    def crear_bloque_energia(self):
        box = QGroupBox("Energía")
        layout = QFormLayout()

        layout.setHorizontalSpacing(20)
        layout.setVerticalSpacing(6)

        # Potencias contratadas (kWh)
        self.ppunta = QLineEdit()
        self.pvalle = QLineEdit()

        # Precios (€/kWh)
        self.pv_ppunta = QLineEdit()
        self.pv_pvalle = QLineEdit()

        self.pv_conpunta = QLineEdit()
        self.pv_conllano = QLineEdit()
        self.pv_convalle = QLineEdit()

        self.vertido = QComboBox()
        self.vertido.addItems(["Sí", "No"])

        # Eliminado: self.excedentes
        self.pv_excedent = QLineEdit()

        # Etiquetas corregidas
        layout.addRow("Potencia punta (kWh):", self.ppunta)
        layout.addRow("Potencia valle (kWh):", self.pvalle)

        layout.addRow("Potencia punta (€/kWh):", self.pv_ppunta)
        layout.addRow("Potencia valle (€/kWh):", self.pv_pvalle)

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
    # El bloque de gastos contiene los datos relacionados con los gastos
    # adicionales del contrato,
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

        layout.addRow("Bono social:", self.bono_social)
        layout.addRow("Alquiler contador:", self.alq_contador)
        layout.addRow("Otros gastos:", self.otros_gastos)
        layout.addRow("Impuesto eléctrico (%):", self.i_electrico)
        layout.addRow("IVA (%):", self.iva)

        box.setLayout(layout)
        box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        return box

    # ============================================================
    #  VALIDACIONES PROGRESIVAS
    # ============================================================
    # Las validaciones progresivas se activan cada vez que el usuario modifica un
    # campo relevante,
    def conectar_validaciones(self):
        widgets = [
            self.ncontrato,
            self.codigo_postal,
            self.fec_inicio,
            self.fec_final,
            self.ppunta,
            self.pvalle,
            self.pv_ppunta,
            self.pv_pvalle,
            self.pv_conpunta,
            self.pv_conllano,
            self.pv_convalle,
            self.pv_excedent,  # Excedente precio
            self.bono_social,
            self.alq_contador,
            self.otros_gastos,
            self.i_electrico,
            self.iva,
        ]

        for w in widgets:
            w.textChanged.connect(self.validar_formulario)

        self.vertido.currentIndexChanged.connect(self.validar_formulario)

    # ============================================================
    #  VALIDACIÓN PRINCIPAL
    # ============================================================
    # La validación principal comprueba que los campos obligatorios estén completos
    # y tengan el formato correcto.
    def validar_formulario(self):
        nc = self.ncontrato.text().strip().upper().replace(" ", "")
        self.ncontrato.setText(nc)

        if not self.validar_fecha(self.fec_inicio.text()):
            self.btn_guardar.setEnabled(False)
            return

        if not self.validar_fecha(self.fec_final.text()):
            self.btn_guardar.setEnabled(False)
            return

        try:
            fi = self.to_iso(self.fec_inicio.text())
            ff = self.to_iso(self.fec_final.text())
            if fi >= ff:
                self.btn_guardar.setEnabled(False)
                return
        except:
            self.btn_guardar.setEnabled(False)
            return

        if not re.fullmatch(r"\d{5}", self.codigo_postal.text()):
            self.btn_guardar.setEnabled(False)
            return

        try:
            p1 = float(self.ppunta.text().replace(",", "."))
            p2 = float(self.pvalle.text().replace(",", "."))
            if not (0 < p1 < 10 or 0 < p2 < 10):
                self.btn_guardar.setEnabled(False)
                return
        except:
            self.btn_guardar.setEnabled(False)
            return

        self.btn_guardar.setEnabled(True)

    # ============================================================
    #  FLUJO DE PRE-GUARDADO (CP inexistente)
    # ============================================================
    # Antes de guardar, se comprueba si el código postal existe en la base de datos.
    def pre_guardado(self):
        cp = self.codigo_postal.text()

        if hasattr(self.parent(), "existe_cp"):
            if not self.parent().existe_cp(cp):
                r = QMessageBox.question(
                    self,
                    "Código postal no encontrado",
                    f"El código postal {cp} no existe.\n¿Desea añadirlo ahora?",
                    QMessageBox.Yes | QMessageBox.No,
                )

                if r == QMessageBox.No:
                    self.codigo_postal.setStyleSheet("color: red;")
                    self.codigo_postal.setFocus()
                    return

                dlg = AltaCodigoPostal(cp, self)
                dlg.codigo_postal_creado.connect(
                    self.parent().insertar_cp
                )  # Inserta en BD
                dlg.codigo_postal_creado.connect(
                    self.recibir_cp
                )  # Actualiza formulario
                dlg.exec()

        self.guardar()

    # ============================================================
    #  GUARDADO FINAL
    # ============================================================
    # Si el código postal es correcto o ya se ha dado de alta, se recopilan todos los datos
    # del formulario en un diccionario y se emite el signal contrato_guardado con esos datos.
    def guardar(self):
        datos = {
            "identificacion": {
                "ncontrato": self.ncontrato.text(),
                "suplemento": 0,
                "compania": self.compania.currentText(),
                "codigo_postal": self.codigo_postal.text(),
                "fec_inicio": self.to_iso(self.fec_inicio.text()),
                "fec_final": self.to_iso(self.fec_final.text()),
                "fec_anulacion": None,
                "estado": self.calcular_estado(),
                "efec_suple": self.to_iso(self.fec_inicio.text()),
                "fin_suple": self.to_iso(self.fec_final.text()),
            },
            "energia": {
                "ppunta": self.to_float(self.ppunta.text()),
                "pvalle": self.to_float(self.pvalle.text()),
                "pv_ppunta": self.to_float(self.pv_ppunta.text()),
                "pv_pvalle": self.to_float(self.pv_pvalle.text()),
                "pv_conpunta": self.to_float(self.pv_conpunta.text()),
                "pv_conllano": self.to_float(self.pv_conllano.text()),
                "pv_convalle": self.to_float(self.pv_convalle.text()),
                "vertido": self.vertido.currentText() == "Sí",
                "pv_excedent": self.to_float(self.pv_excedent.text()),
            },
            "gastos": {
                "bono_social": self.to_float(self.bono_social.text()),
                "alq_contador": self.to_float(self.alq_contador.text()),
                "otros_gastos": self.to_float(self.otros_gastos.text()),
                "i_electrico": self.to_float(self.i_electrico.text()),
                "iva": self.to_float(self.iva.text()),
            },
        }

        self.contrato_guardado.emit(datos)

    # ============================================================
    #  FUNCIONES AUXILIARES
    # ============================================================
    # Funciones auxiliares para convertir formatos, calcular estado del contrato, etc.
    def recibir_cp(self, cp, poblacion):
        self.codigo_postal.setText(cp)
        self.codigo_postal.setStyleSheet("")
        self.codigo_postal.setFocus()
        self.validar_formulario()

    def ajustar_anchos(self):
        for w in self.findChildren(QLineEdit):
            w.setMinimumWidth(260)
            w.setMaximumWidth(320)

        for w in self.findChildren(QComboBox):
            w.setMinimumWidth(260)
            w.setMaximumWidth(320)

    def validar_fecha(self, f):
        return bool(re.fullmatch(r"\d{2}/\d{2}/\d{4}", f))

    def to_iso(self, f):
        d = datetime.strptime(f, "%d/%m/%Y")
        return d.strftime("%Y-%m-%d")

    def to_float(self, t):
        if not t.strip():
            return 0.0
        return float(t.replace(",", "."))

    # El estado del contrato se calcula en función de las fechas de inicio y finalización,
    # comparándolas con la fecha actual.
    def calcular_estado(self):
        hoy = date.today()
        fi = datetime.strptime(self.to_iso(self.fec_inicio.text()), "%Y-%m-%d").date()
        ff = datetime.strptime(self.to_iso(self.fec_final.text()), "%Y-%m-%d").date()

        if fi <= hoy <= ff:
            return "Activo"
        elif hoy < fi:
            return "Futuro"
        elif hoy > ff:
            return "Caducado"
        return "Activo"

    def cargar_datos(self):
        pass

    # ============================================================
    #  AJUSTE DE TABULACIÓN
    # ============================================================
    # El orden de tabulación se ajusta para que siga un flujo lógico de entrada de datos,
    # con saltos
    def showEvent(self, event):
        super().showEvent(event)

        # ORDEN COMPLETO DE TABULACIÓN (de arriba a abajo)
        self.setTabOrder(self.ncontrato, self.compania)
        self.setTabOrder(self.compania, self.codigo_postal)
        self.setTabOrder(self.codigo_postal, self.fec_inicio)
        self.setTabOrder(self.fec_inicio, self.fec_final)

        # SALTO: desde Fecha final → Potencia punta (kWh)
        self.setTabOrder(self.fec_final, self.ppunta)

        # Continúa el orden natural en bloque Energía
        self.setTabOrder(self.ppunta, self.pvalle)
        self.setTabOrder(self.pvalle, self.pv_ppunta)
        self.setTabOrder(self.pv_ppunta, self.pv_pvalle)
        self.setTabOrder(self.pv_pvalle, self.pv_conpunta)
        self.setTabOrder(self.pv_conpunta, self.pv_conllano)
        self.setTabOrder(self.pv_conllano, self.pv_convalle)
        self.setTabOrder(self.pv_convalle, self.vertido)
        self.setTabOrder(self.vertido, self.pv_excedent)

        # Bloque Gastos
        self.setTabOrder(self.pv_excedent, self.bono_social)
        self.setTabOrder(self.bono_social, self.alq_contador)
        self.setTabOrder(self.alq_contador, self.otros_gastos)
        self.setTabOrder(self.otros_gastos, self.i_electrico)
        self.setTabOrder(self.i_electrico, self.iva)

        # Botones finales
        self.setTabOrder(self.iva, self.btn_guardar)
        self.setTabOrder(self.btn_guardar, self.btn_cancelar)
