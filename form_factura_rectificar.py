# ---------------------------------------------------------
# Modulo: form_factura_rectificar.py
# Descripción: Rectificación de facturas
# ---------------------------------------------------------

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


def to_float(valor, etiqueta):
    """Convierte a float o lanza error con etiqueta amigable."""
    if valor.strip() == "":
        return 0.0
    try:
        return float(valor.replace(",", "."))
    except:
        raise ValueError(f"El campo '{etiqueta}' debe ser numérico.")


class FormFacturaRectificar(QWidget):

    def __init__(self, parent=None, ncontrato=None, nfactura=None):
        super().__init__(parent)

        self.ncontrato = ncontrato
        self.nfactura_original = nfactura

        self.setWindowTitle(f"Rectificar factura – {ncontrato}")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ---------------------------------------------------------
        # TÍTULO
        # ---------------------------------------------------------
        titulo = QLabel(f"Rectificación de factura {nfactura}")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        # ---------------------------------------------------------
        # BLOQUE 1: IDENTIFICACIÓN
        # ---------------------------------------------------------
        self.ncontrato_edit = QLineEdit()
        self.nfactura_edit = QLineEdit()
        self.suplemento = QLineEdit()

        self.fec_inicio = QLineEdit()
        self.fec_final = QLineEdit()
        self.dias = QLineEdit()
        self.fec_emision = QLineEdit()

        ident = QGridLayout()
        ident.addWidget(QLabel("Contrato:"), 0, 0)
        ident.addWidget(self.ncontrato_edit, 0, 1)

        ident.addWidget(QLabel("Factura original:"), 1, 0)
        ident.addWidget(self.nfactura_edit, 1, 1)

        ident.addWidget(QLabel("Suplemento:"), 2, 0)
        ident.addWidget(self.suplemento, 2, 1)

        ident.addWidget(QLabel("Inicio factura:"), 3, 0)
        ident.addWidget(self.fec_inicio, 3, 1)

        ident.addWidget(QLabel("Fin factura:"), 4, 0)
        ident.addWidget(self.fec_final, 4, 1)

        ident.addWidget(QLabel("Días facturados:"), 5, 0)
        ident.addWidget(self.dias, 5, 1)

        ident.addWidget(QLabel("Fecha emisión:"), 6, 0)
        ident.addWidget(self.fec_emision, 6, 1)

        grupo_ident = QGroupBox("Identificación")
        grupo_ident.setLayout(ident)
        layout.addWidget(grupo_ident)

        # ---------------------------------------------------------
        # BLOQUE 2: ENERGÍA
        # ---------------------------------------------------------
        self.con_punta = QLineEdit()
        self.con_llano = QLineEdit()
        self.con_valle = QLineEdit()
        self.excedentes = QLineEdit()
        self.importe_compensado = QLineEdit()

        energia = QGridLayout()
        energia.addWidget(QLabel("Consumo punta (kWh):"), 0, 0)
        energia.addWidget(self.con_punta, 0, 1)

        energia.addWidget(QLabel("Consumo llano (kWh):"), 1, 0)
        energia.addWidget(self.con_llano, 1, 1)

        energia.addWidget(QLabel("Consumo valle (kWh):"), 2, 0)
        energia.addWidget(self.con_valle, 2, 1)

        energia.addWidget(QLabel("Excedentes (kWh):"), 3, 0)
        energia.addWidget(self.excedentes, 3, 1)

        energia.addWidget(QLabel("Importe compensado (€):"), 4, 0)
        energia.addWidget(self.importe_compensado, 4, 1)

        grupo_energia = QGroupBox("Energía")
        grupo_energia.setLayout(energia)
        layout.addWidget(grupo_energia)

        # ---------------------------------------------------------
        # BLOQUE 3: GASTOS Y DESCUENTOS
        # ---------------------------------------------------------
        self.servicios = QLineEdit()
        self.dcto_servicios = QLineEdit()
        self.saldos = QLineEdit()
        self.bat = QLineEdit()

        gastos = QGridLayout()
        gastos.addWidget(QLabel("Servicios asociados (€):"), 0, 0)
        gastos.addWidget(self.servicios, 0, 1)

        gastos.addWidget(QLabel("Dctos. servicios (€):"), 1, 0)
        gastos.addWidget(self.dcto_servicios, 1, 1)

        gastos.addWidget(QLabel("Saldos pendientes (€):"), 2, 0)
        gastos.addWidget(self.saldos, 2, 1)

        gastos.addWidget(QLabel("Batería virtual (€):"), 3, 0)
        gastos.addWidget(self.bat, 3, 1)

        grupo_gastos = QGroupBox("Gastos y descuentos")
        grupo_gastos.setLayout(gastos)
        layout.addWidget(grupo_gastos)

        # ---------------------------------------------------------
        # BOTONES
        # ---------------------------------------------------------
        botones = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar rectificación")
        self.btn_cancelar = QPushButton("Cancelar")

        botones.addWidget(self.btn_guardar)
        botones.addStretch()
        botones.addWidget(self.btn_cancelar)

        layout.addLayout(botones)
        self.setLayout(layout)

        # Eventos
        self.btn_guardar.clicked.connect(self.guardar_rectificacion)
        self.btn_cancelar.clicked.connect(self.volver)

        # ---------------------------------------------------------
        # CARGA DE DATOS
        # ---------------------------------------------------------
        self.cargar_factura_original()

    # ---------------------------------------------------------
    # CARGA DE DATOS DESDE BD
    # ---------------------------------------------------------
    def cargar_factura_original(self):
        main = self.get_mainwindow()

        cursor = main.conn.cursor()

        cursor.execute(
            """
            SELECT id_contrato, nfactura, inicio_factura, fin_factura,
                   dias_factura, fec_emision, consumo_punta, consumo_llano,
                   consumo_valle, excedentes, importe_compensado,
                   servicios, dcto_servicios, saldos_pendientes, bat_virtual,
                   estado, rectifica_a, ncontrato, suplemento
            FROM facturas
            WHERE ncontrato = ? AND nfactura = ?
        """,
            (self.ncontrato, self.nfactura_original),
        )

        row = cursor.fetchone()
        if not row:
            QMessageBox.critical(self, "Error", "Factura no encontrada.")
            self.close()
            return

        (
            self.id_contrato,
            nfactura,
            inicio,
            fin,
            dias,
            fec_emision,
            con_punta,
            con_llano,
            con_valle,
            exced,
            imp_comp,
            servicios,
            dcto,
            saldos,
            bat,
            estado,
            rectifica_a,
            ncontrato,
            suplemento,
        ) = row

        # Rellenar campos
        self.ncontrato_edit.setText(ncontrato)
        self.nfactura_edit.setText(nfactura)
        self.suplemento.setText(str(suplemento))

        self.ncontrato_edit.setReadOnly(True)
        self.nfactura_edit.setReadOnly(True)
        self.suplemento.setReadOnly(True)

        # Fechas ISO → dd/mm/yyyy
        def ddmmyyyy(f):
            a, m, d = f.split("-")
            return f"{d}/{m}/{a}"

        self.fec_inicio.setText(ddmmyyyy(inicio))
        self.fec_final.setText(ddmmyyyy(fin))
        self.dias.setText(str(dias))
        self.fec_emision.setText(ddmmyyyy(fec_emision))

        # Energía
        self.con_punta.setText(str(con_punta))
        self.con_llano.setText(str(con_llano))
        self.con_valle.setText(str(con_valle))
        self.excedentes.setText(str(exced))
        self.importe_compensado.setText(str(imp_comp))

        # Gastos
        self.servicios.setText(str(servicios))
        self.dcto_servicios.setText(str(dcto))
        self.saldos.setText(str(saldos))
        self.bat.setText(str(bat))

    # ---------------------------------------------------------
    # GUARDAR RECTIFICACIÓN
    # ---------------------------------------------------------
    def guardar_rectificacion(self):
        # ---------------------------------------------------------
        # 1. VALIDACIONES DE FECHAS Y DÍAS
        # ---------------------------------------------------------
        if (
            not validar_fecha(self.fec_inicio.text())
            or not validar_fecha(self.fec_final.text())
            or not validar_fecha(self.fec_emision.text())
        ):
            QMessageBox.warning(self, "Error", "Formato de fecha incorrecto.")
            return

        # Validación de días
        try:
            dias_correctos = dias_entre_fechas(
                self.fec_inicio.text(), self.fec_final.text()
            )
            if int(self.dias.text()) != dias_correctos:
                QMessageBox.warning(
                    self, "Error", f"Los días correctos son {dias_correctos}."
                )
                return
        except:
            QMessageBox.warning(self, "Error", "Días facturados incorrectos.")
            return

        # Conversión dd/mm/yyyy → ISO
        def iso(f):
            d, m, a = f.split("/")
            return f"{a}-{m}-{d}"

        # ---------------------------------------------------------
        # 2. GENERAR NÚMERO RECTIFICATIVO (<original>-N)
        # ---------------------------------------------------------
        main = self.get_mainwindow()
        cursor = main.conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM facturas
            WHERE ncontrato = ? AND rectifica_a = ?
            """,
            (self.ncontrato, self.nfactura_original),
        )
        row = cursor.fetchone()
        existentes = row[0] if row else 0
        siguiente = existentes + 1
        nfactura_rect = f"{self.nfactura_original}-{siguiente}"

        # ---------------------------------------------------------
        # 3. INSERTAR FACTURA RECTIFICADORA
        # ---------------------------------------------------------
        try:
            cursor.execute(
                """
                INSERT INTO facturas (
                    id_contrato, nfactura, inicio_factura, fin_factura,
                    dias_factura, fec_emision,
                    consumo_punta, consumo_llano, consumo_valle,
                    excedentes, importe_compensado,
                    servicios, dcto_servicios, saldos_pendientes, bat_virtual,
                    estado, rectifica_a, ncontrato, suplemento, recalcular
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.id_contrato,
                    nfactura_rect,
                    iso(self.fec_inicio.text()),
                    iso(self.fec_final.text()),
                    int(self.dias.text()),
                    iso(self.fec_emision.text()),
                    to_float(self.con_punta.text(), "Consumo punta"),
                    to_float(self.con_llano.text(), "Consumo llano"),
                    to_float(self.con_valle.text(), "Consumo valle"),
                    to_float(self.excedentes.text(), "Excedentes"),
                    to_float(self.importe_compensado.text(), "Importe compensado"),
                    to_float(self.servicios.text(), "Servicios"),
                    to_float(self.dcto_servicios.text(), "Descuento servicios"),
                    to_float(self.saldos.text(), "Saldos pendientes"),
                    to_float(self.bat.text(), "Batería virtual"),
                    "Rectificadora",
                    self.nfactura_original,
                    self.ncontrato,
                    int(self.suplemento.text()),
                    1,  # marcar como pendiente de recálculo
                ),
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error al insertar rectificadora:\n{e}"
            )
            return

        # ---------------------------------------------------------
        # 4. MARCAR ORIGINAL COMO RECTIFICADA
        # ---------------------------------------------------------
        try:
            cursor.execute(
                """
                UPDATE facturas
                SET estado = 'Rectificada'
                WHERE ncontrato = ? AND nfactura = ?
                """,
                (self.ncontrato, self.nfactura_original),
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar original:\n{e}")
            return

        # ---------------------------------------------------------
        # 5. CONFIRMAR Y VOLVER AL MENÚ
        # ---------------------------------------------------------
        main.conn.commit()

        QMessageBox.information(
            self,
            "Rectificación completada",
            f"Factura rectificadora creada: {nfactura_rect}",
        )

    # ---------------------------------------------------------
    # VOLVER A PANTALLA B
    # ---------------------------------------------------------
    def volver(self):
        from lista_facturas_rectificar import ListaFacturasRectificar

        main = self.get_mainwindow()

        main.cargar_modulo(
            ListaFacturasRectificar(
                parent=main,
                ncontrato=self.ncontrato,
                conn=main.conn,
            ),
            "Seleccionar factura",
        )

    def get_mainwindow(self):
        w = self.parent()
        while w is not None and not hasattr(w, "cargar_modulo"):
            w = w.parent()
        return w
