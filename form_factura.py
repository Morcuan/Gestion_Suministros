# -----------------------------------------     ---#
# Modulo: form_factura.py                          #
# Descripción: Formulario de factura de energía    #
# Autor: Antonio Morales                           #
# Fecha: 2026-02-09                                #
# -------------------------------------------     -#
# Este módulo define la clase FormFactura, que es un formulario para introducir los datos de una factura de energía.
# El formulario se divide en tres bloques: identificación, energía y gastos/descuentos.
# El bloque de identificación incluye campos para el número de factura, fechas de inicio y fin,
# días facturados y fecha de emisión. El bloque de energía incluye campos para el consumo en punta,
# llano y valle, excedentes e importe compensado. El bloque de gastos/descuentos incluye
# campos para servicios asociados, descuentos, saldos pendientes y batería virtual.
# El formulario tiene validaciones para asegurar que los datos introducidos son correctos,
# como el formato de fechas y la coherencia entre los días facturados y las fechas.
# Al guardar la factura, se insera un nuevo registro en la base de datos con los datos
# introducidos. También hay opciones para limpiar el formulario para introducir
# otra factura o para volver a la lista de contratos.

# Importaciones necesarias para la interfaz gráfica y manejo de datos
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from utils import dias_entre_fechas, validar_fecha


# conversión de texto a float con manejo de errores y etiquetas amigables
def to_float(valor, etiqueta):
    """Convierte a float o lanza error con etiqueta amigable."""
    if valor.strip() == "":
        return 0.0
    try:
        return float(valor.replace(",", "."))
    except:
        raise ValueError(f"El campo '{etiqueta}' debe ser numérico.")


# clase principal del formulario de factura
class FormFactura(QWidget):
    # inicialización del formulario con parámetros de contrato y compañía
    def __init__(self, parent=None, id_contrato=None, ncontrato=None, compania=None):
        super().__init__(parent)

        self.id_contrato = id_contrato
        self.ncontrato = ncontrato
        self.compania = compania

        self.setWindowTitle(f"Nueva factura – {ncontrato} – {compania}")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ============================================================
        #  TÍTULO SUPERIOR
        # ============================================================

        titulo = QLabel(f"Contrato nº: {self.ncontrato}")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        # ============================================================
        #  BLOQUE 1: IDENTIFICACIÓN
        # ============================================================

        self.nfactura = QLineEdit()
        self.fec_inicio = QLineEdit()
        self.fec_final = QLineEdit()
        self.dias = QLineEdit()
        self.fec_emision = QLineEdit()

        ident_layout = QGridLayout()
        ident_layout.addWidget(QLabel("Nº de factura:"), 0, 0)
        ident_layout.addWidget(self.nfactura, 0, 1)

        ident_layout.addWidget(QLabel("Inicio factura (dd/mm/yyyy):"), 1, 0)
        ident_layout.addWidget(self.fec_inicio, 1, 1)

        ident_layout.addWidget(QLabel("Fin factura (dd/mm/yyyy):"), 2, 0)
        ident_layout.addWidget(self.fec_final, 2, 1)

        ident_layout.addWidget(QLabel("Días facturados:"), 3, 0)
        ident_layout.addWidget(self.dias, 3, 1)

        ident_layout.addWidget(QLabel("Fec. emisión (dd/mm/yyyy):"), 4, 0)
        ident_layout.addWidget(self.fec_emision, 4, 1)

        grupo_ident = QGroupBox("Identificación")
        grupo_ident.setLayout(ident_layout)
        layout.addWidget(grupo_ident)

        self.fec_final.textChanged.connect(self.autocalcular_dias)

        # ============================================================
        #  BLOQUE 2: ENERGÍA
        # ============================================================

        self.con_punta = QLineEdit()
        self.con_llano = QLineEdit()
        self.con_valle = QLineEdit()
        self.excedentes = QLineEdit()
        self.importe_compensado = QLineEdit()  # NUEVO CAMPO

        ene_layout = QGridLayout()
        ene_layout.addWidget(QLabel("Consumo punta (kWh):"), 0, 0)
        ene_layout.addWidget(self.con_punta, 0, 1)

        ene_layout.addWidget(QLabel("Consumo llano (kWh):"), 1, 0)
        ene_layout.addWidget(self.con_llano, 1, 1)

        ene_layout.addWidget(QLabel("Consumo valle (kWh):"), 2, 0)
        ene_layout.addWidget(self.con_valle, 2, 1)

        ene_layout.addWidget(QLabel("Excedentes (kWh):"), 3, 0)
        ene_layout.addWidget(self.excedentes, 3, 1)

        ene_layout.addWidget(QLabel("Importe compensado (€):"), 4, 0)
        ene_layout.addWidget(self.importe_compensado, 4, 1)

        grupo_energia = QGroupBox("Energía")
        grupo_energia.setLayout(ene_layout)
        layout.addWidget(grupo_energia)

        # ============================================================
        #  BLOQUE 3: GASTOS Y DESCUENTOS
        # ============================================================

        self.servicios = QLineEdit()
        self.dcto_servicios = QLineEdit()
        self.saldos = QLineEdit()
        self.bat = QLineEdit()

        gas_layout = QGridLayout()
        gas_layout.addWidget(QLabel("Servicios asociados (€):"), 0, 0)
        gas_layout.addWidget(self.servicios, 0, 1)

        gas_layout.addWidget(QLabel("Dctos. servicios (€):"), 1, 0)
        gas_layout.addWidget(self.dcto_servicios, 1, 1)

        gas_layout.addWidget(QLabel("Saldos pendientes (€):"), 2, 0)
        gas_layout.addWidget(self.saldos, 2, 1)

        gas_layout.addWidget(QLabel("Batería virtual (€):"), 3, 0)
        gas_layout.addWidget(self.bat, 3, 1)

        grupo_gastos = QGroupBox("Gastos y descuentos")
        grupo_gastos.setLayout(gas_layout)
        layout.addWidget(grupo_gastos)

        # ============================================================
        #  BOTONES
        # ============================================================

        botones = QHBoxLayout()
        self.btn_guardar = QPushButton("Grabar factura")
        self.btn_otra = QPushButton("Otra factura")
        self.btn_salir = QPushButton("Salir")

        self.btn_otra.setEnabled(False)

        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_otra)
        botones.addStretch()
        botones.addWidget(self.btn_salir)

        layout.addLayout(botones)
        self.setLayout(layout)

        self.btn_guardar.clicked.connect(self.guardar_factura)
        self.btn_otra.clicked.connect(self.limpiar_formulario)
        self.btn_salir.clicked.connect(self.volver_lista)

    # ============================================================
    #  LOCALIZAR MAINWINDOW REAL
    # ============================================================
    # Este método sube por la jerarquía de widgets hasta encontrar el mainwindow real
    def get_mainwindow(self):
        w = self.parent()
        while w is not None and not hasattr(w, "cargar_modulo"):
            w = w.parent()
        return w

    # ============================================================
    #  AUTOCÁLCULO DE DÍAS
    # ============================================================
    # Cada vez que se cambia la fecha final, se recalculan los días entre inicio y fin
    def autocalcular_dias(self):
        inicio = self.fec_inicio.text()
        fin = self.fec_final.text()

        if validar_fecha(inicio) and validar_fecha(fin):
            try:
                d = dias_entre_fechas(inicio, fin)
                self.dias.setText(str(d))
                self.dias.setStyleSheet("")
            except:
                pass

    # ============================================================
    #  VALIDACIÓN DE DÍAS
    # ============================================================
    # Antes de guardar, se comprueba que los días introducidos coinciden con los
    # días entre las fechas
    def validar_dias(self):
        inicio = self.fec_inicio.text()
        fin = self.fec_final.text()

        if not validar_fecha(inicio) or not validar_fecha(fin):
            return False

        dias_correctos = dias_entre_fechas(inicio, fin)

        try:
            dias_usuario = int(self.dias.text())
        except:
            return False

        if dias_correctos != dias_usuario:
            self.dias.setStyleSheet("background-color: #ffcccc;")
            QMessageBox.warning(
                self,
                "Error en días",
                f"Los días correctos son {dias_correctos}. Corrija el valor.",
            )
            self.dias.setFocus()
            return False

        self.dias.setStyleSheet("")
        return True

    # ============================================================
    #  GUARDADO REAL
    # ============================================================
    # Al hacer clic en guardar, se validan los datos y se inserta la factura en la
    # base de datos
    def guardar_factura(self):
        if not self.validar_dias():
            return

        main = self.get_mainwindow()
        conn = main.conn
        cursor = conn.cursor()

        for campo in [self.fec_inicio, self.fec_final, self.fec_emision]:
            if not validar_fecha(campo.text()):
                QMessageBox.warning(self, "Error", "Formato de fecha incorrecto.")
                return

        def iso(f):
            d, m, a = f.split("/")
            return f"{a}-{m}-{d}"

        try:
            servicios = to_float(self.servicios.text(), "Servicios asociados")
            dcto = -abs(to_float(self.dcto_servicios.text(), "Dctos. servicios"))
            saldos = -abs(to_float(self.saldos.text(), "Saldos pendientes"))
            bat = -abs(to_float(self.bat.text(), "Batería virtual"))
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            return

        try:
            cursor.execute(
                """
                INSERT INTO facturas (
                    id_contrato, nfactura, inicio_factura, fin_factura,
                    dias_factura, fec_emision,
                    consumo_punta, consumo_llano, consumo_valle,
                    excedentes, importe_compensado,
                    servicios, dcto_servicios, saldos_pendientes, bat_virtual
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.id_contrato,
                    self.nfactura.text(),
                    iso(self.fec_inicio.text()),
                    iso(self.fec_final.text()),
                    int(self.dias.text()),
                    iso(self.fec_emision.text()),
                    to_float(self.con_punta.text(), "Consumo punta"),
                    to_float(self.con_llano.text(), "Consumo llano"),
                    to_float(self.con_valle.text(), "Consumo valle"),
                    to_float(self.excedentes.text(), "Excedentes"),
                    to_float(self.importe_compensado.text(), "Importe compensado"),
                    servicios,
                    dcto,
                    saldos,
                    bat,
                ),
            )

            conn.commit()

            QMessageBox.information(self, "OK", "Factura guardada correctamente.")
            self.btn_guardar.setEnabled(False)
            self.btn_otra.setEnabled(True)

        except Exception as e:
            conn.rollback()

            if "UNIQUE constraint failed" in str(e):
                QMessageBox.warning(
                    self,
                    "Número de factura duplicado",
                    "El número de factura ya existe. Introduzca uno diferente.",
                )
                self.nfactura.setStyleSheet("background-color: #ffcccc;")
                self.nfactura.setFocus()
                return

            QMessageBox.critical(self, "Error", str(e))

    # ============================================================
    #  LIMPIAR FORMULARIO
    # ============================================================
    # Al hacer clic en "Otra factura", se limpian los campos para introducir
    # una nueva factura
    def limpiar_formulario(self):
        for widget in self.findChildren(QLineEdit):
            widget.clear()
            widget.setStyleSheet("")

        self.btn_guardar.setEnabled(True)
        self.btn_otra.setEnabled(False)
        self.nfactura.setFocus()

    # ============================================================
    #  VOLVER A LA LISTA
    # ============================================================
    # Al hacer clic en "Salir", se vuelve al módulo de lista de contratos
    def volver_lista(self):
        from lista_contratos_factura import ListaContratosFactura

        main = self.get_mainwindow()
        main.cargar_modulo(ListaContratosFactura(parent=main), "Seleccionar contrato")
        main.cargar_modulo(ListaContratosFactura(parent=main), "Seleccionar contrato")
