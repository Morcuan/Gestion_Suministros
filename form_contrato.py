import re
from datetime import date, datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
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

# ============================================================
#  Ventana auxiliar para alta de códigos postales
# ============================================================

class AltaCodigoPostal(QDialog):
    codigo_postal_creado = Signal(str)

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

    def guardar(self):
        if not self.poblacion.text().strip():
            QMessageBox.warning(self, "Atención", "Debe introducir la población.")
            return

        self.codigo_postal_creado.emit(self.cp.text())
        self.accept()



# ============================================================
#  Formulario principal de contrato
# ============================================================

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

    def crear_bloque_identificacion(self):
        box = QGroupBox("Identificación")
        layout = QFormLayout()

        layout.setHorizontalSpacing(20)
        layout.setVerticalSpacing(6)

        self.ncontrato = QLineEdit()
        self.suplemento = QLineEdit("0")
        self.suplemento.setReadOnly(True)

        self.compania = QComboBox()

        self.cod_postal = QLineEdit()
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
        layout.addRow("Código postal:", self.cod_postal)
        layout.addRow("Fecha inicio:", self.fec_inicio)
        layout.addRow("Fecha final:", self.fec_final)
        layout.addRow("Fecha anulación:", self.fec_anulacion)
        layout.addRow("Estado:", self.estado)
        layout.addRow("Efecto suplemento:", self.efec_suple)
        layout.addRow("Fin suplemento:", self.fin_suple)

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

        self.excedentes = QLineEdit()
        self.pv_excedent = QLineEdit()

        layout.addRow("Potencia punta:", self.ppunta)
        layout.addRow("Potencia valle:", self.pvalle)
        layout.addRow("PV potencia punta:", self.pv_ppunta)
        layout.addRow("PV potencia valle:", self.pv_pvalle)
        layout.addRow("PV consumo punta:", self.pv_conpunta)
        layout.addRow("PV consumo llano:", self.pv_conllano)
        layout.addRow("PV consumo valle:", self.pv_convalle)
        layout.addRow("Vertido:", self.vertido)
        layout.addRow("Excedentes:", self.excedentes)
        layout.addRow("PV excedente:", self.pv_excedent)

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

        layout.addRow("Bono social:", self.bono_social)
        layout.addRow("Alquiler contador:", self.alq_contador)
        layout.addRow("Otros gastos:", self.otros_gastos)
        layout.addRow("Impuesto eléctrico (%):", self.i_electrico)
        layout.addRow("IVA (%):", self.iva)

        box.setLayout(layout)
        box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        return box



    # ============================================================
    #  VALIDACIONES PROGRESIVAS
    # ============================================================

    def conectar_validaciones(self):
        widgets = [
            self.ncontrato, self.cod_postal, self.fec_inicio, self.fec_final,
            self.ppunta, self.pvalle, self.pv_ppunta, self.pv_pvalle,
            self.pv_conpunta, self.pv_conllano, self.pv_convalle,
            self.excedentes, self.pv_excedent,
            self.bono_social, self.alq_contador, self.otros_gastos,
            self.i_electrico, self.iva
        ]

        for w in widgets:
            w.textChanged.connect(self.validar_formulario)

        self.vertido.currentIndexChanged.connect(self.validar_formulario)



    # ============================================================
    #  VALIDACIÓN PRINCIPAL
    # ============================================================

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

        if not re.fullmatch(r"\d{5}", self.cod_postal.text()):
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

    def pre_guardado(self):
        cp = self.cod_postal.text()

        if hasattr(self.parent(), "existe_cp"):
            if not self.parent().existe_cp(cp):
                r = QMessageBox.question(
                    self,
                    "Código postal no encontrado",
                    f"El código postal {cp} no existe.\n¿Desea añadirlo ahora?",
                    QMessageBox.Yes | QMessageBox.No
                )

                if r == QMessageBox.No:
                    self.cod_postal.setStyleSheet("color: red;")
                    self.cod_postal.setFocus()
                    return

                dlg = AltaCodigoPostal(cp, self)
                dlg.codigo_postal_creado.connect(self.parent().insertar_cp)
                dlg.exec()

        self.guardar()



    # ============================================================
    #  GUARDADO FINAL
    # ============================================================

    def guardar(self):
        datos = {
            "identificacion": {
                "ncontrato": self.ncontrato.text(),
                "suplemento": 0,
                "compania": self.compania.currentText(),
                "cod_postal": self.cod_postal.text(),
                "fec_inicio": self.to_iso(self.fec_inicio.text()),
                "fec_final": self.to_iso(self.fec_final.text()),
                "fec_anulacion": None,
                "estado": self.calcular_estado(),
                "efec_suple": self.to_iso(self.fec_inicio.text()),
                "fin_suple": self.to_iso(self.fec_final.text())
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
                "excedentes": self.to_float(self.excedentes.text()),
                "pv_excedent": self.to_float(self.pv_excedent.text())
            },
            "gastos": {
                "bono_social": self.to_float(self.bono_social.text()),
                "alq_contador": self.to_float(self.alq_contador.text()),
                "otros_gastos": self.to_float(self.otros_gastos.text()),
                "i_electrico": self.to_float(self.i_electrico.text()),
                "iva": self.to_float(self.iva.text())
            }
        }

        self.contrato_guardado.emit(datos)



    # ============================================================
    #  FUNCIONES AUXILIARES
    # ============================================================

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
