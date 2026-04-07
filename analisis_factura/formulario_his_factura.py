# -------------------------------------------------------------#
# Módulo: formulario_his_factura.py                            #
# Descripción: Detalle de factura en modo consulta (histórico) #
# Autor: Antonio Morales                                       #
# Fecha: 2026-04                                               #
# -------------------------------------------------------------#

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class FormularioHisFactura(QWidget):
    """
    Formulario de consulta para el histórico de facturas.
    - Muestra los datos tal como se capturan en el formulario original.
    - Tres bloques: Identificación, Consumos, Servicios y ajustes.
    - Todo en modo solo lectura.
    """

    def __init__(self, parent=None, conn=None, nfactura=None):
        super().__init__(parent)
        self.parent = parent
        self.conn = conn
        self.nfactura = nfactura

        self.crear_ui()
        self.cargar_datos()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def crear_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # -------------------------
        # BLOQUE IDENTIFICACIÓN
        # -------------------------
        self.gb_ident = QGroupBox("Identificación")
        f_ident = QFormLayout()

        self.txt_ncontrato = self._crear_campo()
        self.txt_suplemento = self._crear_campo()
        self.txt_nfactura = self._crear_campo()

        # Campo rectificativa
        self.txt_rectifica = self._crear_campo()
        self.lbl_rectifica = QLabel("Sustituye a:")

        self.txt_fec_emision = self._crear_campo()
        self.txt_inicio = self._crear_campo()
        self.txt_fin = self._crear_campo()
        self.txt_dias = self._crear_campo()

        f_ident.addRow("Contrato:", self.txt_ncontrato)
        f_ident.addRow("Suplemento:", self.txt_suplemento)
        f_ident.addRow("Nº factura:", self.txt_nfactura)
        f_ident.addRow(self.lbl_rectifica, self.txt_rectifica)  # ← CORRECTO
        f_ident.addRow("Fecha emisión:", self.txt_fec_emision)
        f_ident.addRow("Inicio periodo:", self.txt_inicio)
        f_ident.addRow("Fin periodo:", self.txt_fin)
        f_ident.addRow("Días facturados:", self.txt_dias)

        self.gb_ident.setLayout(f_ident)
        layout.addWidget(self.gb_ident)

        # -------------------------
        # BLOQUE CONSUMOS
        # -------------------------
        self.gb_con = QGroupBox("Consumos")
        f_con = QFormLayout()

        self.txt_punta = self._crear_campo()
        self.txt_llano = self._crear_campo()
        self.txt_valle = self._crear_campo()
        self.txt_exced = self._crear_campo()
        self.txt_comp = self._crear_campo()

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

        self.txt_serv = self._crear_campo()
        self.txt_dcto = self._crear_campo()
        self.txt_saldos = self._crear_campo()
        self.txt_bat = self._crear_campo()

        f_srv.addRow("Servicios (€):", self.txt_serv)
        f_srv.addRow("Dto. servicios (€):", self.txt_dcto)
        f_srv.addRow("Saldos pendientes (€):", self.txt_saldos)
        f_srv.addRow("Batería virtual (€):", self.txt_bat)

        self.gb_srv.setLayout(f_srv)
        layout.addWidget(self.gb_srv)

        # -------------------------
        # BOTONES
        # -------------------------
        botones = QHBoxLayout()

        btn_calculos = QPushButton("Mostrar cálculos")
        btn_calculos.clicked.connect(self.mostrar_calculos)
        botones.addWidget(btn_calculos)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.volver)
        botones.addWidget(btn_cancelar)

        layout.addLayout(botones)
        layout.addStretch()

    # ---------------------------------------------------------
    # Crear campo de solo lectura
    # ---------------------------------------------------------
    def _crear_campo(self):
        campo = QLineEdit()
        campo.setReadOnly(True)
        return campo

    # ---------------------------------------------------------
    # Cargar datos desde BD
    # ---------------------------------------------------------
    def cargar_datos(self):
        cur = self.conn.cursor()

        cur.execute(
            """
            SELECT ncontrato, suplemento, nfactura, fec_emision,
                   inicio_factura, fin_factura, dias_factura,
                   consumo_punta, consumo_llano, consumo_valle,
                   excedentes, importe_compensado,
                   servicios, dcto_servicios, saldos_pendientes, bat_virtual,
                   rectifica_a
            FROM facturas
            WHERE nfactura = ?
            """,
            (self.nfactura,),
        )

        row = cur.fetchone()
        if not row:
            return

        (
            ncontrato,
            suplemento,
            nfactura,
            fec_emision,
            inicio,
            fin,
            dias,
            punta,
            llano,
            valle,
            exced,
            comp,
            serv,
            dcto,
            saldos,
            bat,
            rectifica_a,
        ) = row

        # Identificación
        self.txt_ncontrato.setText(str(ncontrato))
        self.txt_suplemento.setText(str(suplemento))
        self.txt_nfactura.setText(str(nfactura))
        self.txt_fec_emision.setText(str(fec_emision))
        self.txt_inicio.setText(str(inicio))
        self.txt_fin.setText(str(fin))
        self.txt_dias.setText(str(dias))

        # Rectificación
        if rectifica_a:
            self.txt_rectifica.setText(str(rectifica_a))
        else:
            self.lbl_rectifica.setVisible(False)
            self.txt_rectifica.setVisible(False)

        # Consumos
        self.txt_punta.setText(str(punta))
        self.txt_llano.setText(str(llano))
        self.txt_valle.setText(str(valle))
        self.txt_exced.setText(str(exced))
        self.txt_comp.setText(str(comp))

        # Servicios
        self.txt_serv.setText(str(serv))
        self.txt_dcto.setText(str(dcto))
        self.txt_saldos.setText(str(saldos))
        self.txt_bat.setText(str(bat))

    # ---------------------------------------------------------
    # Navegación
    # ---------------------------------------------------------
    def mostrar_calculos(self):
        from analisis_factura.detalles_calculo_his_factura import (
            DetallesCalculoHisFactura,
        )

        mw = self.window()
        widget = DetallesCalculoHisFactura(
            parent=mw,
            conn=self.conn,
            nfactura=self.nfactura,
        )
        mw.cargar_modulo(widget, f"Cálculo factura {self.nfactura}")

    def volver(self):
        from analisis_factura.seleccionar_his_factura import SeleccionarHisFactura

        mw = self.window()
        widget = SeleccionarHisFactura(
            parent=mw,
            conn=self.conn,
            ncontrato=self.txt_ncontrato.text(),
        )
        mw.cargar_modulo(widget, f"Facturas del contrato {self.txt_ncontrato.text()}")
