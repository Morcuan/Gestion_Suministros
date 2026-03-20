# -------------------------------------------------------------#
# Modulo: formulario_contrato.py                               #
# Descripción: Vista pura para el formulario de contrato       #
# Autor: Antonio Morales                                       #
# Fecha: 2026-02-10                                            #
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

from utilidades.logica_negocio import convertir_a_iso, sumar_10_anios
from utilidades.utilidades_bd import obtener_companias


class FormularioContrato(QWidget):
    """
    Vista pura del formulario de contrato.
    No contiene lógica de negocio, validaciones ni acceso a BD.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # ---------------------------------------------------------
        # LAYOUT PRINCIPAL
        # ---------------------------------------------------------
        layout_principal = QVBoxLayout(self)
        layout_principal.setSpacing(12)
        layout_principal.setContentsMargins(12, 12, 12, 12)

        # =========================================================
        # 1. BLOQUE IDENTIFICACIÓN
        # =========================================================
        gb_ident = QGroupBox("Identificación del contrato")
        layout_ident = QFormLayout()
        layout_ident.setSpacing(8)
        gb_ident.setLayout(layout_ident)

        self.txt_ncontrato = QLineEdit()
        self.txt_suplemento = QLineEdit()

        self.txt_codigo_postal = QLineEdit()
        self.txt_fec_inicio = QLineEdit()
        self.txt_fec_final = QLineEdit()
        self.txt_efec_suple = QLineEdit()
        self.txt_fin_suple = QLineEdit()
        self.txt_fec_anulacion = QLineEdit()

        layout_ident.addRow("Número contrato:", self.txt_ncontrato)
        layout_ident.addRow("Suplemento:", self.txt_suplemento)
        self.cmb_compania = QComboBox()
        layout_ident.addRow("Compañía:", self.cmb_compania)
        layout_ident.addRow("Código postal:", self.txt_codigo_postal)
        layout_ident.addRow("Fecha inicio:", self.txt_fec_inicio)
        layout_ident.addRow("Fecha final:", self.txt_fec_final)
        layout_ident.addRow("Efecto suplemento:", self.txt_efec_suple)
        layout_ident.addRow("Fin suplemento:", self.txt_fin_suple)
        layout_ident.addRow("Fecha anulación:", self.txt_fec_anulacion)

        layout_principal.addWidget(gb_ident)

        # =========================================================
        # 2. BLOQUE ENERGÍA (dos columnas)
        # =========================================================
        gb_energia = QGroupBox("Datos de energía")
        layout_energia_principal = QHBoxLayout()
        layout_energia_principal.setSpacing(24)
        gb_energia.setLayout(layout_energia_principal)

        # Columna izquierda
        col_izq = QFormLayout()
        col_izq.setSpacing(8)

        self.txt_ppunta = QLineEdit()
        self.txt_pvalle = QLineEdit()
        self.txt_pv_ppunta = QLineEdit()
        self.txt_pv_pvalle = QLineEdit()

        col_izq.addRow("Pot. punta (kW):", self.txt_ppunta)
        col_izq.addRow("Pot. valle (kW):", self.txt_pvalle)
        col_izq.addRow("Pv. pot. punta (€):", self.txt_pv_ppunta)
        col_izq.addRow("Pv. pot. llano (€):", self.txt_pv_pvalle)

        # Columna derecha
        col_der = QFormLayout()
        col_der.setSpacing(8)

        self.txt_pv_conpunta = QLineEdit()
        self.txt_pv_conllano = QLineEdit()
        self.txt_pv_convalle = QLineEdit()
        self.txt_vertido = QLineEdit()
        self.txt_pv_excedentes = QLineEdit()

        col_der.addRow("Pv. cons. punta (€):", self.txt_pv_conpunta)
        col_der.addRow("Pv. cons. llano (€):", self.txt_pv_conllano)
        col_der.addRow("Pv. cons. valle (€):", self.txt_pv_convalle)
        col_der.addRow("Vertido (s/n):", self.txt_vertido)
        col_der.addRow("Pv. excedentes (€):", self.txt_pv_excedentes)

        layout_energia_principal.addLayout(col_izq)
        layout_energia_principal.addLayout(col_der)

        layout_principal.addWidget(gb_energia)

        # =========================================================
        # 3. BLOQUE GASTOS
        # =========================================================
        gb_gastos = QGroupBox("Gastos asociados")
        layout_gastos = QFormLayout()
        layout_gastos.setSpacing(8)
        gb_gastos.setLayout(layout_gastos)

        self.txt_bono_social = QLineEdit()
        self.txt_i_electrico = QLineEdit()
        self.txt_alq_contador = QLineEdit()
        self.txt_otros_gastos = QLineEdit()
        self.txt_iva = QLineEdit()

        layout_gastos.addRow("Bono social:", self.txt_bono_social)
        layout_gastos.addRow("Imp. electricidad (%):", self.txt_i_electrico)
        layout_gastos.addRow("Alquiler equipos (cts):", self.txt_alq_contador)
        layout_gastos.addRow("Otros gastos (cts):", self.txt_otros_gastos)
        layout_gastos.addRow("IVA (%):", self.txt_iva)

        layout_principal.addWidget(gb_gastos)

        # ---------------------------------------------------------
        # BOTONES
        # ---------------------------------------------------------
        botones = QHBoxLayout()
        botones.setContentsMargins(0, 12, 0, 0)

        self.btn_guardar = QPushButton("Guardar")
        self.btn_cancelar = QPushButton("Cancelar")

        self.btn_guardar.setFixedHeight(32)
        self.btn_cancelar.setFixedHeight(32)

        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_cancelar)

        layout_principal.addLayout(botones)

        # ---------------------------------------------------------
        # AJUSTES VISUALES GENERALES
        # ---------------------------------------------------------
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

        for edit in self.findChildren(QLineEdit):
            edit.setFixedHeight(26)

    # ---------------------------------------------------------
    # MODO NUEVO / MODIFICAR
    # ---------------------------------------------------------
    def set_modo(self, modo):
        """
        Configura el formulario en modo 'nuevo' o 'modificar'.
        """

        if modo == "nuevo":

            # Deshabilitar campos no editables
            self.txt_suplemento.setEnabled(False)
            self.txt_fec_final.setEnabled(False)
            self.txt_efec_suple.setEnabled(False)
            self.txt_fin_suple.setEnabled(False)
            self.txt_fec_anulacion.setEnabled(False)

            # Valores automáticos visibles
            self.txt_suplemento.setText("0")
            self.txt_fec_final.setText("")
            self.txt_efec_suple.setText("")
            self.txt_fin_suple.setText("")
            self.txt_fec_anulacion.setText("")

            # Orden de tabulación
            self.setTabOrder(self.txt_ncontrato, self.cmb_compania)
            self.setTabOrder(self.cmb_compania, self.txt_codigo_postal)
            self.setTabOrder(self.txt_codigo_postal, self.txt_fec_inicio)
            self.setTabOrder(self.txt_fec_inicio, self.txt_ppunta)

        elif modo == "modificar":

            # En modificación, algunos campos siguen bloqueados
            self.txt_suplemento.setEnabled(False)
            self.txt_fec_final.setEnabled(False)
            self.txt_efec_suple.setEnabled(False)
            self.txt_fin_suple.setEnabled(False)

            # fec_anulacion sí puede habilitarse en modificación
            self.txt_fec_anulacion.setEnabled(True)

    # ---------------------------------------------------------
    # CARGAR DATOS (para modificación)
    # ---------------------------------------------------------
    def cargar_datos(self, datos_dict):
        """
        Carga datos en los campos del formulario.
        datos_dict debe contener:
        - identificacion
        - energia
        - gastos
        """

        ident = datos_dict["identificacion"]
        energia = datos_dict["energia"]
        gastos = datos_dict["gastos"]

        # Identificación
        self.txt_ncontrato.setText(str(ident["ncontrato"]))
        self.txt_suplemento.setText(str(ident["suplemento"]))

        # Seleccionar compañía en el combo
        idx = self.cmb_compania.findText(ident["compania"])
        if idx >= 0:
            self.cmb_compania.setCurrentIndex(idx)

        self.txt_codigo_postal.setText(str(ident["codigo_postal"]))
        self.txt_fec_inicio.setText(ident["fec_inicio"])
        self.txt_fec_final.setText(ident["fec_final"])
        self.txt_efec_suple.setText(ident["efec_suple"])
        self.txt_fin_suple.setText(ident["fin_suple"])
        self.txt_fec_anulacion.setText(
            "" if ident["fec_anulacion"] is None else ident["fec_anulacion"]
        )

        # Energía
        self.txt_ppunta.setText(str(energia["ppunta"]))
        self.txt_pvalle.setText(str(energia["pvalle"]))
        self.txt_pv_ppunta.setText(str(energia["pv_ppunta"]))
        self.txt_pv_pvalle.setText(str(energia["pv_pvalle"]))
        self.txt_pv_conpunta.setText(str(energia["pv_conpunta"]))
        self.txt_pv_conllano.setText(str(energia["pv_conllano"]))
        self.txt_pv_convalle.setText(str(energia["pv_convalle"]))
        self.txt_vertido.setText(str(energia["vertido"]))
        self.txt_pv_excedentes.setText(str(energia["pv_excedentes"]))

        # Gastos
        self.txt_bono_social.setText(str(gastos["bono_social"]))
        self.txt_i_electrico.setText(str(gastos["i_electrico"]))
        self.txt_alq_contador.setText(str(gastos["alq_contador"]))
        self.txt_otros_gastos.setText(str(gastos["otros_gastos"]))
        self.txt_iva.setText(str(gastos["iva"]))

    # ---------------------------------------------------------
    # LIMPIAR FORMULARIO
    # ---------------------------------------------------------
    def limpiar(self):
        """Limpia todos los campos del formulario."""

        for gb in self.findChildren(QGroupBox):
            layout = gb.layout()
            for i in range(layout.rowCount()):
                widget = layout.itemAt(i, layout.FieldRole).widget()
                if isinstance(widget, QLineEdit):
                    widget.clear()

        # Reset del combo
        self.cmb_compania.setCurrentIndex(0)

    # -----------------------------------------------
    # CARGAR COMBO COMPAÑIAS
    # ------------------------------------------------
    def cargar_companias(self, lista):
        self.cmb_compania.clear()
        for nombre in lista:
            self.cmb_compania.addItem(nombre)

    # ---------------------------------------------------------
    # OBTENER DATOS
    # ---------------------------------------------------------
    def obtener_datos(self):
        """
        Devuelve tres diccionarios:
        - datos_identificacion
        - datos_energia
        - datos_gastos
        """

        # ---------------------------------------------------------
        # VALIDACIÓN VERTIDO
        # ---------------------------------------------------------
        vertido_val = self.txt_vertido.text().strip().upper()
        if vertido_val not in ("S", "N", ""):
            raise ValueError("El campo 'Vertido' solo admite S o N.")

        # ---------------------------------------------------------
        # FECHAS (DRU)
        # ---------------------------------------------------------
        fec_inicio_iso = convertir_a_iso(self.txt_fec_inicio.text().strip())
        fec_final_iso = sumar_10_anios(fec_inicio_iso)

        efec_suple_iso = fec_inicio_iso
        fin_suple_iso = fec_final_iso

        # ---------------------------------------------------------
        # IDENTIFICACIÓN
        # ---------------------------------------------------------
        datos_identificacion = {
            "ncontrato": self.txt_ncontrato.text().strip(),
            "suplemento": 0,
            "compania": self.cmb_compania.currentText().strip(),
            "codigo_postal": self.txt_codigo_postal.text().strip(),
            "fec_inicio": fec_inicio_iso,
            "fec_final": fec_final_iso,
            "efec_suple": efec_suple_iso,
            "fin_suple": fin_suple_iso,
            "fec_anulacion": None,
        }

        # ---------------------------------------------------------
        # ENERGÍA
        # ---------------------------------------------------------
        datos_energia = {
            "ppunta": self.txt_ppunta.text().strip(),
            "pvalle": self.txt_pvalle.text().strip(),
            "pv_ppunta": self.txt_pv_ppunta.text().strip(),
            "pv_pvalle": self.txt_pv_pvalle.text().strip(),
            "pv_conpunta": self.txt_pv_conpunta.text().strip(),
            "pv_conllano": self.txt_pv_conllano.text().strip(),
            "pv_convalle": self.txt_pv_convalle.text().strip(),
            "vertido": vertido_val,
            "pv_excedentes": self.txt_pv_excedentes.text().strip(),
        }

        # ---------------------------------------------------------
        # GASTOS
        # ---------------------------------------------------------
        datos_gastos = {
            "bono_social": self.txt_bono_social.text().strip(),
            "i_electrico": self.txt_i_electrico.text().strip(),
            "alq_contador": self.txt_alq_contador.text().strip(),
            "otros_gastos": self.txt_otros_gastos.text().strip(),
            "iva": self.txt_iva.text().strip(),
        }

        return datos_identificacion, datos_energia, datos_gastos
