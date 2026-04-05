# -------------------------------------------------------------#
# Módulo: formulario_contrato_historico.py                     #
# -------------------------------------------------------------#

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from utilidades.logica_negocio import convertir_a_ddmmaaaa


class FormularioContratoHistorico(QWidget):
    def __init__(self, parent=None, conn=None, ncontrato=None, suplemento=None):
        super().__init__(parent)

        self.main_window = parent
        self.conn = conn
        self.cur = conn.cursor()

        self.ncontrato = ncontrato
        self.suplemento = suplemento

        self.crear_ui()
        self.cargar_datos()

    # ---------------------------------------------------------
    # INTERFAZ
    # ---------------------------------------------------------
    def crear_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setSpacing(12)
        layout_principal.setContentsMargins(12, 12, 12, 12)

        # Estilo global
        self.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
            }
            QLineEdit {
                font-size: 16px;
                padding: 3px;
            }
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                margin-top: 14px;
            }
            """
        )

        banner = QLabel("🔍 Consulta histórica — Datos en modo solo lectura")
        banner.setStyleSheet("font-size: 18px; font-weight: bold; color: #004080;")
        layout_principal.addWidget(banner)

        # =====================================================
        # IDENTIFICACIÓN
        # =====================================================
        gb_ident = QGroupBox("Identificación del contrato")
        layout_ident = QFormLayout()
        layout_ident.setSpacing(8)
        gb_ident.setLayout(layout_ident)

        self.txt_ncontrato = QLineEdit()
        self.txt_suplemento = QLineEdit()
        self.cmb_compania = QComboBox()
        self.txt_codigo_postal = QLineEdit()
        self.txt_poblacion = QLineEdit()
        self.txt_fec_inicio = QLineEdit()
        self.txt_fec_final = QLineEdit()
        self.txt_efec_suple = QLineEdit()
        self.txt_fin_suple = QLineEdit()
        self.txt_fec_anulacion = QLineEdit()

        layout_ident.addRow("Número contrato:", self.txt_ncontrato)
        layout_ident.addRow("Suplemento:", self.txt_suplemento)
        layout_ident.addRow("Compañía:", self.cmb_compania)
        layout_ident.addRow("Código postal:", self.txt_codigo_postal)
        layout_ident.addRow("Población:", self.txt_poblacion)
        layout_ident.addRow("Fecha inicio:", self.txt_fec_inicio)
        layout_ident.addRow("Fecha final:", self.txt_fec_final)
        layout_ident.addRow("Efecto suplemento:", self.txt_efec_suple)
        layout_ident.addRow("Fin suplemento:", self.txt_fin_suple)
        layout_ident.addRow("Fecha anulación:", self.txt_fec_anulacion)

        layout_principal.addWidget(gb_ident)

        # =====================================================
        # ENERGÍA
        # =====================================================
        gb_energia = QGroupBox("Datos de energía")
        layout_energia_principal = QHBoxLayout()
        layout_energia_principal.setSpacing(12)  # antes 24
        layout_energia_principal.setContentsMargins(4, 4, 4, 4)
        gb_energia.setLayout(layout_energia_principal)

        col_izq = QFormLayout()
        col_izq.setSpacing(6)  # antes 8

        col_der = QFormLayout()
        col_der.setSpacing(6)

        self.txt_ppunta = QLineEdit()
        self.txt_pv_ppunta = QLineEdit()
        self.txt_pvalle = QLineEdit()
        self.txt_pv_pvalle = QLineEdit()

        col_izq.addRow("Pot. punta (kW):", self.txt_ppunta)
        col_izq.addRow("Pv. pot. punta (€):", self.txt_pv_ppunta)
        col_izq.addRow("Pot. valle (kW):", self.txt_pvalle)
        col_izq.addRow("Pv. pot. valle (€):", self.txt_pv_pvalle)

        self.txt_pv_conpunta = QLineEdit()
        self.txt_pv_conllano = QLineEdit()
        self.txt_pv_convalle = QLineEdit()
        self.txt_vertido = QLineEdit()
        self.txt_pv_excedent = QLineEdit()

        col_der.addRow("Pv. cons. punta (€):", self.txt_pv_conpunta)
        col_der.addRow("Pv. cons. llano (€):", self.txt_pv_conllano)
        col_der.addRow("Pv. cons. valle (€):", self.txt_pv_convalle)
        col_der.addRow("Vertido (s/n):", self.txt_vertido)
        col_der.addRow("Pv. excedentes (€):", self.txt_pv_excedent)

        layout_energia_principal.addLayout(col_izq)
        layout_energia_principal.addLayout(col_der)

        layout_principal.addWidget(gb_energia)

        # =====================================================
        # GASTOS
        # =====================================================
        gb_gastos = QGroupBox("Gastos asociados")
        layout_gastos = QFormLayout()
        layout_gastos.setSpacing(8)
        gb_gastos.setLayout(layout_gastos)

        self.txt_bono_social = QLineEdit()
        self.txt_alq_contador = QLineEdit()
        self.txt_otros_gastos = QLineEdit()
        self.txt_i_electrico = QLineEdit()
        self.txt_iva = QLineEdit()

        layout_gastos.addRow("Bono social:", self.txt_bono_social)
        layout_gastos.addRow("Alquiler contador:", self.txt_alq_contador)
        layout_gastos.addRow("Otros gastos:", self.txt_otros_gastos)
        layout_gastos.addRow("Imp. eléctrico (%):", self.txt_i_electrico)
        layout_gastos.addRow("IVA (%):", self.txt_iva)

        layout_principal.addWidget(gb_gastos)

        # ---------------------------------------------------------
        # BOTONES
        # ---------------------------------------------------------
        botones = QHBoxLayout()
        botones.setContentsMargins(0, 12, 0, 0)

        btn_volver_supl = QPushButton("Volver a suplementos")
        btn_volver_contr = QPushButton("Volver a contratos")
        btn_salir = QPushButton("Salir al menú")

        for b in (btn_volver_supl, btn_volver_contr, btn_salir):
            b.setFixedHeight(32)

        btn_volver_supl.clicked.connect(self.volver_suplementos)
        btn_volver_contr.clicked.connect(self.volver_contratos)
        btn_salir.clicked.connect(self.salir_menu)

        botones.addWidget(btn_volver_supl)
        botones.addWidget(btn_volver_contr)
        botones.addWidget(btn_salir)

        layout_principal.addLayout(botones)

        self._poner_readonly()

    # ---------------------------------------------------------
    # READONLY
    # ---------------------------------------------------------
    def _poner_readonly(self):
        gris = "background-color: #e0e0e0;"

        for widget in self.findChildren(QLineEdit):
            widget.setReadOnly(True)
            widget.setStyleSheet(gris)
            widget.setFixedHeight(26)

        self.cmb_compania.setEnabled(False)

    # ---------------------------------------------------------
    # CARGA DE DATOS
    # ---------------------------------------------------------
    def cargar_datos(self):
        query = """
            SELECT *
            FROM vista_contratos
            WHERE ncontrato = ? AND suplemento = ?;
        """

        self.cur.execute(query, (self.ncontrato, self.suplemento))
        row = self.cur.fetchone()

        if not row:
            return

        (
            id_contrato,
            ncontrato,
            suplemento,
            compania,
            codigo_postal,
            poblacion,
            fec_inicio,
            fec_final,
            efec_suple,
            fin_suple,
            fec_anulacion,
            ppunta,
            pv_ppunta,
            pvalle,
            pv_pvalle,
            pv_conpunta,
            pv_conllano,
            pv_convalle,
            vertido,
            pv_excedent,
            bono_social,
            alq_contador,
            otros_gastos,
            i_electrico,
            iva,
        ) = row

        # IDENTIFICACIÓN
        self.txt_ncontrato.setText(str(ncontrato))
        self.txt_suplemento.setText(str(suplemento))
        self.cmb_compania.addItem(compania)
        self.txt_codigo_postal.setText(str(codigo_postal))
        self.txt_poblacion.setText(str(poblacion))
        self.txt_fec_inicio.setText(convertir_a_ddmmaaaa(fec_inicio))
        self.txt_fec_final.setText(convertir_a_ddmmaaaa(fec_final))
        self.txt_efec_suple.setText(convertir_a_ddmmaaaa(efec_suple))
        self.txt_fin_suple.setText(convertir_a_ddmmaaaa(fin_suple))
        self.txt_fec_anulacion.setText(
            convertir_a_ddmmaaaa(fec_anulacion) if fec_anulacion else ""
        )

        # ENERGÍA
        self.txt_ppunta.setText(str(ppunta))
        self.txt_pv_ppunta.setText(str(pv_ppunta))
        self.txt_pvalle.setText(str(pvalle))
        self.txt_pv_pvalle.setText(str(pv_pvalle))
        self.txt_pv_conpunta.setText(str(pv_conpunta))
        self.txt_pv_conllano.setText(str(pv_conllano))
        self.txt_pv_convalle.setText(str(pv_convalle))
        self.txt_vertido.setText(str(vertido))
        self.txt_pv_excedent.setText(str(pv_excedent))

        # GASTOS
        self.txt_bono_social.setText(str(bono_social))
        self.txt_alq_contador.setText(str(alq_contador))
        self.txt_otros_gastos.setText(str(otros_gastos))
        self.txt_i_electrico.setText(str(i_electrico))
        self.txt_iva.setText(str(iva))

    # ---------------------------------------------------------
    # NAVEGACIÓN
    # ---------------------------------------------------------
    def volver_suplementos(self):
        from analisis_contrato.lista_suplementos_historico import (
            ListaSuplementosHistorico,
        )

        widget = ListaSuplementosHistorico(
            parent=self.main_window,
            conn=self.conn,
            ncontrato=self.ncontrato,
        )
        self.main_window.cargar_modulo(widget, f"Suplementos {self.ncontrato}")

    def volver_contratos(self):
        from analisis_contrato.lista_contratos_historico import ListaContratosHistorico

        widget = ListaContratosHistorico(
            parent=self.main_window,
            conn=self.conn,
        )
        self.main_window.cargar_modulo(widget, "Histórico — Contratos")

    def salir_menu(self):
        self.main_window.cargar_modulo(self.main_window.crear_pantalla_inicio(), None)
