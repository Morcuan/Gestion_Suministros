# -------------------------------------------------------------#
# Módulo: formulario_factura.py                                #
# Descripción: Formulario reutilizable para captura de factura #
# Autor: Antonio Morales                                       #
# Fecha: 2026-02-10                                            #
# -------------------------------------------------------------#

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from utilidades.logica_negocio import dias_entre_fechas, validar_fecha


class FormularioFactura(QWidget):
    """
    Formulario reutilizable para:
    - Nueva factura
    - Modificar factura
    - Rectificar factura
    - Anular factura (bloques ocultables desde el controlador)

    No contiene lógica de BD ni motor.
    Solo UI + lectura/escritura de datos.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.crear_ui()
        self.conectar_eventos()

    # ---------------------------------------------------------
    # UI COMPLETA
    # ---------------------------------------------------------
    def crear_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # -----------------------------------------------------
        # MENSAJE DE AVISO (solo visible en modo anulación)
        # -----------------------------------------------------
        self.lbl_aviso = QLabel()
        self.lbl_aviso.setStyleSheet("color: red; font-weight: bold;")
        self.lbl_aviso.setVisible(False)
        layout.addWidget(self.lbl_aviso)

        # -------------------------
        # BLOQUE IDENTIFICACIÓN
        # -------------------------
        self.gb_ident = QGroupBox("Identificación")
        f_ident = QFormLayout()

        self.txt_ncontrato = QLineEdit()
        self.txt_ncontrato.setReadOnly(True)

        self.txt_suplemento = QLineEdit()
        self.txt_suplemento.setReadOnly(True)

        self.txt_nfactura = QLineEdit()
        self.txt_fec_emision = QLineEdit()
        self.txt_inicio = QLineEdit()
        self.txt_fin = QLineEdit()

        # AHORA editable (antes estaba readOnly)
        self.txt_dias = QLineEdit()

        f_ident.addRow("Contrato:", self.txt_ncontrato)
        f_ident.addRow("Suplemento:", self.txt_suplemento)
        f_ident.addRow("Nº factura:", self.txt_nfactura)
        f_ident.addRow("Fecha emisión (dd/mm/yyyy):", self.txt_fec_emision)
        f_ident.addRow("Inicio periodo (dd/mm/yyyy):", self.txt_inicio)
        f_ident.addRow("Fin periodo (dd/mm/yyyy):", self.txt_fin)
        f_ident.addRow("Días facturados:", self.txt_dias)

        self.gb_ident.setLayout(f_ident)
        layout.addWidget(self.gb_ident)

        # -------------------------
        # BLOQUE CONSUMOS
        # -------------------------
        self.gb_con = QGroupBox("Consumos")
        f_con = QFormLayout()

        self.txt_punta = QLineEdit()
        self.txt_llano = QLineEdit()
        self.txt_valle = QLineEdit()
        self.txt_exced = QLineEdit()
        self.txt_comp = QLineEdit()

        f_con.addRow("Consumo punta (kWh):", self.txt_punta)
        f_con.addRow("Consumo llano (kWh):", self.txt_llano)
        f_con.addRow("Consumo valle (kWh):", self.txt_valle)
        f_con.addRow("Excedentes (kWh):", self.txt_exced)
        f_con.addRow("Importe compensado (€):", self.txt_comp)

        self.gb_con.setLayout(f_con)
        layout.addWidget(self.gb_con)

        # -------------------------
        # BLOQUE SERVICIOS
        # -------------------------
        self.gb_srv = QGroupBox("Servicios y ajustes")
        f_srv = QFormLayout()

        self.txt_serv = QLineEdit()
        self.txt_dcto = QLineEdit()
        self.txt_saldos = QLineEdit()
        self.txt_bat = QLineEdit()

        f_srv.addRow("Servicios (€):", self.txt_serv)
        f_srv.addRow("Dto. servicios (€):", self.txt_dcto)
        f_srv.addRow("Saldos pendientes (€):", self.txt_saldos)
        f_srv.addRow("Batería virtual (€):", self.txt_bat)

        self.gb_srv.setLayout(f_srv)
        layout.addWidget(self.gb_srv)

        layout.addStretch()

    # ---------------------------------------------------------
    # EVENTOS
    # ---------------------------------------------------------
    def conectar_eventos(self):
        self.txt_inicio.editingFinished.connect(self.recalcular_dias)
        self.txt_fin.editingFinished.connect(self.recalcular_dias)
        self.txt_dias.editingFinished.connect(self.validar_dias_usuario)

    # ---------------------------------------------------------
    # LÓGICA DE DÍAS FACTURADOS
    # ---------------------------------------------------------
    def recalcular_dias(self):
        ini = self.txt_inicio.text().strip()
        fin = self.txt_fin.text().strip()

        if not validar_fecha(ini) or not validar_fecha(fin):
            return

        dias_calc = dias_entre_fechas(ini, fin)
        self.txt_dias.setText(str(dias_calc))

    def validar_dias_usuario(self):
        ini = self.txt_inicio.text().strip()
        fin = self.txt_fin.text().strip()
        dias_usuario = self.txt_dias.text().strip()

        if not dias_usuario.isdigit():
            QMessageBox.warning(
                self, "Valor inválido", "El campo días debe ser numérico."
            )
            self.recalcular_dias()
            return

        if validar_fecha(ini) and validar_fecha(fin):
            dias_calc = dias_entre_fechas(ini, fin)
            if int(dias_usuario) != dias_calc:
                QMessageBox.information(
                    self,
                    "Corrección automática",
                    f"Los días facturados deben ser {dias_calc}. Se corrige automáticamente.",
                )
                self.txt_dias.setText(str(dias_calc))

    # ---------------------------------------------------------
    # MÉTODOS PÚBLICOS
    # ---------------------------------------------------------
    def set_identificacion(self, ncontrato, suplemento):
        self.txt_ncontrato.setText(str(ncontrato))
        self.txt_suplemento.setText(str(suplemento))

    def get_datos(self):
        return {
            "ncontrato": self.txt_ncontrato.text().strip(),
            "suplemento": self.txt_suplemento.text().strip(),
            "nfactura": self.txt_nfactura.text().strip(),
            "fec_emision": self.txt_fec_emision.text().strip(),
            "inicio_factura": self.txt_inicio.text().strip(),
            "fin_factura": self.txt_fin.text().strip(),
            "dias_factura": self.txt_dias.text().strip(),
            "consumo_punta": self.txt_punta.text().strip(),
            "consumo_llano": self.txt_llano.text().strip(),
            "consumo_valle": self.txt_valle.text().strip(),
            "excedentes": self.txt_exced.text().strip(),
            "importe_compensado": self.txt_comp.text().strip(),
            "servicios": self.txt_serv.text().strip(),
            "dcto_servicios": self.txt_dcto.text().strip(),
            "saldos_pendientes": self.txt_saldos.text().strip(),
            "bat_virtual": self.txt_bat.text().strip(),
        }

    def set_datos(self, datos):
        for clave, valor in datos.items():
            attr = f"txt_{clave}"
            if hasattr(self, attr):
                getattr(self, attr).setText(str(valor))

    def limpiar(self):
        for attr in dir(self):
            if attr.startswith("txt_"):
                widget = getattr(self, attr)
                if isinstance(widget, QLineEdit) and not widget.isReadOnly():
                    widget.clear()
