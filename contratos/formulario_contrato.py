# -------------------------------------------------------------#
# Modulo: formulario_contrato.py                               #
# Descripción: Vista pura del formulario de contrato           #
# Autor: Antonio Morales                                       #
# Fecha: 2026-02-10 (versión corregida 2026-05-03)             #
# -------------------------------------------------------------#

from PySide6.QtCore import Qt, QRect
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from utilidades.logica_negocio import (
    convertir_a_ddmmaaaa,
    convertir_a_iso,
    sumar_10_anios,
)


class FormularioContrato(QWidget):
    """
    Vista pura del formulario de contrato.
    No contiene lógica de negocio, validaciones ni acceso a BD.
    """

    def __init__(self, parent=None, conn=None, modo="nuevo", datos=None):
        super().__init__(parent)

        from main_window import MainWindow

        self.main_window: MainWindow = parent
        self.conn = conn
        self.modo = modo
        self.datos = datos

        # Popup de sugerencias (creado una vez)
        self.popup_sugerencias = QListWidget()
        self.popup_sugerencias.setWindowFlags(Qt.Popup)
        self.popup_sugerencias.hide()
        self.popup_sugerencias.itemClicked.connect(self._seleccionar_sugerencia)

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
        self.txt_ncontrato.setEnabled(False)

        self.txt_suplemento = QLineEdit()
        self.txt_suplemento.setEnabled(False)

        self.txt_codigo_postal = QLineEdit()
        self.txt_fec_inicio = QLineEdit()
        self.txt_fec_final = QLineEdit()
        self.txt_efec_suple = QLineEdit()
        self.txt_fin_suple = QLineEdit()
        self.txt_fec_anulacion = QLineEdit()

        layout_ident.addRow("Número contrato:", self.txt_ncontrato)
        layout_ident.addRow("Suplemento:", self.txt_suplemento)

        # ---------------------------------------------------------
        # CAMPO COMPAÑÍA — AUTOCOMPLETADO INTELIGENTE
        # ---------------------------------------------------------
        self.txt_compania = QLineEdit()
        self.txt_compania.setPlaceholderText("Escribe nombre o parte…")
        self.txt_compania.textChanged.connect(self._buscar_compania)

        layout_ident.addRow("Compañía:", self.txt_compania)

        # ---------------------------------------------------------
        # RESTO DE CAMPOS
        # ---------------------------------------------------------
        layout_ident.addRow("Código postal:", self.txt_codigo_postal)
        layout_ident.addRow("Fecha inicio:", self.txt_fec_inicio)
        layout_ident.addRow("Fecha final:", self.txt_fec_final)
        layout_ident.addRow("Efecto suplemento:", self.txt_efec_suple)
        layout_ident.addRow("Fin suplemento:", self.txt_fin_suple)
        layout_ident.addRow("Fecha anulación:", self.txt_fec_anulacion)

        layout_principal.addWidget(gb_ident)

        # =========================================================
        # 2. BLOQUE ENERGÍA
        # =========================================================
        gb_energia = QGroupBox("Datos de energía")
        layout_energia_principal = QHBoxLayout()
        layout_energia_principal.setSpacing(24)
        gb_energia.setLayout(layout_energia_principal)

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

        col_der = QFormLayout()
        col_der.setSpacing(8)

        self.txt_pv_conpunta = QLineEdit()
        self.txt_pv_conllano = QLineEdit()
        self.txt_pv_convalle = QLineEdit()
        self.txt_vertido = QLineEdit()
        self.txt_vertido.textChanged.connect(self._vertido_upper)
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

        self.btn_cancelar.clicked.connect(self._cancelar)

        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_cancelar)

        layout_principal.addLayout(botones)

        # ---------------------------------------------------------
        # ESTILOS
        # ---------------------------------------------------------
        self.setStyleSheet("""
            QLabel { font-size: 16px; }
            QLineEdit { font-size: 16px; padding: 3px; }
            QGroupBox { font-size: 16px; font-weight: bold; margin-top: 14px; }
        """)

        for edit in self.findChildren(QLineEdit):
            edit.setFixedHeight(26)

        # ---------------------------------------------------------
        # AUTOMATIZACIONES
        # ---------------------------------------------------------
        self.txt_fec_inicio.textChanged.connect(self._recalcular_fechas)

        # ---------------------------------------------------------
        # CONFIGURAR MODO
        # ---------------------------------------------------------
        self.set_modo(self.modo)

        # ---------------------------------------------------------
        # MODO TEST
        # ---------------------------------------------------------
        if self.modo == "test":

            gris = "background-color: #e0e0e0;"

            # Número de contrato NO editable
            self.txt_ncontrato.setEnabled(False)
            self.txt_ncontrato.setReadOnly(True)
            self.txt_ncontrato.setStyleSheet(gris)

            # Suplemento siempre 0
            self.txt_suplemento.setEnabled(False)
            self.txt_suplemento.setReadOnly(True)
            self.txt_suplemento.setText("0")
            self.txt_suplemento.setStyleSheet(gris)

            # Campos automáticos NO editables
            for w in (
                self.txt_fec_final,
                self.txt_efec_suple,
                self.txt_fin_suple,
                self.txt_fec_anulacion,
            ):
                w.setEnabled(False)
                w.setReadOnly(True)
                w.setStyleSheet(gris)

            # Campos editables
            for w in (
                self.txt_compania,
                self.txt_codigo_postal,
                self.txt_fec_inicio,
                self.txt_ppunta,
                self.txt_pvalle,
                self.txt_pv_ppunta,
                self.txt_pv_pvalle,
                self.txt_pv_conpunta,
                self.txt_pv_conllano,
                self.txt_pv_convalle,
                self.txt_vertido,
                self.txt_pv_excedentes,
                self.txt_bono_social,
                self.txt_i_electrico,
                self.txt_alq_contador,
                self.txt_otros_gastos,
                self.txt_iva,
            ):
                w.setEnabled(True)
                w.setReadOnly(False)
                w.setStyleSheet("background-color: white;")

            return

        if self.modo != "modificar":
            self._recalcular_fechas()

        if self.modo == "modificar" and self.datos is not None:
            self.cargar_datos(self.datos)

    # ---------------------------------------------------------
    # AUTOCOMPLETADO DE COMPAÑÍAS
    # ---------------------------------------------------------
    def _buscar_compania(self, texto):
        # Evitar ejecución prematura durante la construcción del formulario
        if not hasattr(self, "conn") or self.conn is None:
            return

        texto = texto.strip().upper()
        if not texto:
            self.popup_sugerencias.hide()
            return

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT nombre FROM companias
            WHERE nombre LIKE ?
            ORDER BY nombre
            """,
            (f"%{texto}%",),
        )

        resultados = [fila[0] for fila in cursor.fetchall()]

        if len(resultados) == 0:
            self.txt_compania.setStyleSheet("color: red;")
            self.popup_sugerencias.hide()
            return

        self.txt_compania.setStyleSheet("color: black;")

        # if len(resultados) == 1:
        # Autocompletar directamente
        #    self.txt_compania.blockSignals(True)
        #    self.txt_compania.setText(resultados[0])
        #    self.txt_compania.blockSignals(False)
        #    self.popup_sugerencias.hide()
        #    return

        # Varias coincidencias → mostrar sugerencias
        self._mostrar_sugerencias(resultados)

    def _mostrar_sugerencias(self, lista):
        self.popup_sugerencias.clear()

        for nombre in lista:
            item = QListWidgetItem(nombre)
            self.popup_sugerencias.addItem(item)

        # Estilo limpio, sin borde Breeze
        self.popup_sugerencias.setStyleSheet("""
            QListWidget {
                background: white;
                border: 1px solid #888;
                outline: none;
                font-size: 15px;
            }
            QListWidget::item {
                padding: 4px;
            }
            QListWidget::item:selected {
                background-color: #3874f2;
                color: white;
            }
        """)

        # Posicionar justo debajo del campo
        rect = self.txt_compania.rect()
        pos = self.txt_compania.mapToGlobal(rect.bottomLeft())

        self.popup_sugerencias.setGeometry(QRect(pos.x(), pos.y(), rect.width(), 140))

        self.popup_sugerencias.show()

    def _seleccionar_sugerencia(self, item):
        self.txt_compania.setText(item.text())
        self.popup_sugerencias.hide()

    # ---------------------------------------------------------
    # MODO NUEVO / MODIFICAR
    # ---------------------------------------------------------
    def set_modo(self, modo):

        self.modo = modo
        gris = "background-color: #e0e0e0;"

        if self.modo != "modificar":

            no_editables = (
                self.txt_suplemento,
                self.txt_fec_final,
                self.txt_efec_suple,
                self.txt_fin_suple,
                self.txt_fec_anulacion,
            )
            for w in no_editables:
                w.setEnabled(False)
                if isinstance(w, QLineEdit):
                    w.setReadOnly(True)
                w.setStyleSheet(gris)

            editables = (
                self.txt_fec_inicio,
                self.txt_codigo_postal,
                self.txt_compania,
                self.txt_ppunta,
                self.txt_pvalle,
                self.txt_pv_ppunta,
                self.txt_pv_pvalle,
                self.txt_pv_conpunta,
                self.txt_pv_conllano,
                self.txt_pv_convalle,
                self.txt_vertido,
                self.txt_pv_excedentes,
                self.txt_bono_social,
                self.txt_i_electrico,
                self.txt_alq_contador,
                self.txt_otros_gastos,
                self.txt_iva,
            )
            for w in editables:
                w.setEnabled(True)
                if isinstance(w, QLineEdit):
                    w.setReadOnly(False)
                w.setStyleSheet("background-color: white;")

            self.txt_suplemento.setText("0")
            self.txt_fec_final.clear()
            self.txt_efec_suple.clear()
            self.txt_fin_suple.clear()
            self.txt_fec_anulacion.clear()

        else:

            no_editables = (
                self.txt_ncontrato,
                self.txt_suplemento,
                self.txt_fec_final,
                self.txt_fin_suple,
            )
            for w in no_editables:
                w.setEnabled(False)
                if isinstance(w, QLineEdit):
                    w.setReadOnly(True)
                w.setStyleSheet(gris)

            self.txt_efec_suple.setEnabled(True)
            self.txt_efec_suple.setReadOnly(False)
            self.txt_efec_suple.setStyleSheet("background-color: white;")

            self.txt_fec_anulacion.setEnabled(True)
            self.txt_fec_anulacion.setReadOnly(False)
            self.txt_fec_anulacion.setStyleSheet("background-color: white;")

    # ---------------------------------------------------------
    # CARGAR DATOS (solo modificar)
    # ---------------------------------------------------------
    def cargar_datos(self, datos_dict):

        ident = datos_dict["identificacion"]
        energia = datos_dict["energia"]
        gastos = datos_dict["gastos"]

        self.txt_ncontrato.setText(str(ident["ncontrato"]))
        self.txt_suplemento.setText(str(ident["suplemento"]))

        # Campo compañía ahora es texto
        self.txt_compania.setText(ident["compania"])

        self.txt_codigo_postal.setText(str(ident["codigo_postal"]))

        self.txt_fec_inicio.setText(convertir_a_ddmmaaaa(ident["fec_inicio"]))
        self.txt_fec_final.setText(convertir_a_ddmmaaaa(ident["fec_final"]))
        self.txt_efec_suple.setText(convertir_a_ddmmaaaa(ident["efec_suple"]))
        self.txt_fin_suple.setText(convertir_a_ddmmaaaa(ident["fin_suple"]))

        if ident["fec_anulacion"]:
            self.txt_fec_anulacion.setText(convertir_a_ddmmaaaa(ident["fec_anulacion"]))
        else:
            self.txt_fec_anulacion.setText("")

        self.txt_ppunta.setText(str(energia["ppunta"]))
        self.txt_pvalle.setText(str(energia["pvalle"]))
        self.txt_pv_ppunta.setText(str(energia["pv_ppunta"]))
        self.txt_pv_pvalle.setText(str(energia["pv_pvalle"]))
        self.txt_pv_conpunta.setText(str(energia["pv_conpunta"]))
        self.txt_pv_conllano.setText(str(energia["pv_conllano"]))
        self.txt_pv_convalle.setText(str(energia["pv_convalle"]))
        self.txt_vertido.setText(str(energia["vertido"]))
        self.txt_pv_excedentes.setText(str(energia["pv_excedentes"]))

        self.txt_bono_social.setText(str(gastos["bono_social"]))
        self.txt_i_electrico.setText(str(gastos["i_electrico"]))
        self.txt_alq_contador.setText(str(gastos["alq_contador"]))
        self.txt_otros_gastos.setText(str(gastos["otros_gastos"]))
        self.txt_iva.setText(str(gastos["iva"]))

    # ---------------------------------------------------------
    # LIMPIAR
    # ---------------------------------------------------------
    def limpiar(self):
        for edit in self.findChildren(QLineEdit):
            edit.clear()

    # ---------------------------------------------------------
    # OBTENER DATOS (nuevo)
    # ---------------------------------------------------------
    def obtener_datos(self):

        vertido_val = self.txt_vertido.text().strip().upper()
        if vertido_val not in ("S", "N", ""):
            raise ValueError("El campo 'Vertido' solo admite S o N.")

        fec_inicio_iso = convertir_a_iso(self.txt_fec_inicio.text().strip())
        fec_final_iso = sumar_10_anios(fec_inicio_iso)

        datos_identificacion = {
            "ncontrato": self.txt_ncontrato.text().strip(),
            "suplemento": 0,
            "compania": self.txt_compania.text().strip(),
            "codigo_postal": self.txt_codigo_postal.text().strip(),
            "fec_inicio": fec_inicio_iso,
            "fec_final": fec_final_iso,
            "efec_suple": fec_inicio_iso,
            "fin_suple": fec_final_iso,
            "fec_anulacion": None,
        }

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

        datos_gastos = {
            "bono_social": self.txt_bono_social.text().strip(),
            "i_electrico": self.txt_i_electrico.text().strip(),
            "alq_contador": self.txt_alq_contador.text().strip(),
            "otros_gastos": self.txt_otros_gastos.text().strip(),
            "iva": self.txt_iva.text().strip(),
        }

        return datos_identificacion, datos_energia, datos_gastos

    # ---------------------------------------------------------
    # OBTENER DATOS (modificar)
    # ---------------------------------------------------------
    def obtener_datos_modificacion(self):

        datos_ident = {
            "ncontrato": self.txt_ncontrato.text().strip(),
            "suplemento": int(self.txt_suplemento.text().strip()),
            "compania": self.txt_compania.text().strip(),
            "codigo_postal": self.txt_codigo_postal.text().strip(),
            "fec_inicio": convertir_a_iso(self.txt_fec_inicio.text().strip()),
            "fec_final": convertir_a_iso(self.txt_fec_final.text().strip()),
            "efec_suple": convertir_a_iso(self.txt_efec_suple.text().strip()),
            "fin_suple": convertir_a_iso(self.txt_fin_suple.text().strip()),
            "fec_anulacion": (
                convertir_a_iso(self.txt_fec_anulacion.text().strip())
                if self.txt_fec_anulacion.text().strip()
                else None
            ),
        }

        datos_energia = {
            "ppunta": self.txt_ppunta.text().strip(),
            "pvalle": self.txt_pvalle.text().strip(),
            "pv_ppunta": self.txt_pv_ppunta.text().strip(),
            "pv_pvalle": self.txt_pv_pvalle.text().strip(),
            "pv_conpunta": self.txt_pv_conpunta.text().strip(),
            "pv_conllano": self.txt_pv_conllano.text().strip(),
            "pv_convalle": self.txt_pv_convalle.text().strip(),
            "vertido": self.txt_vertido.text().strip().upper(),
            "pv_excedentes": self.txt_pv_excedentes.text().strip(),
        }

        datos_gastos = {
            "bono_social": self.txt_bono_social.text().strip(),
            "i_electrico": self.txt_i_electrico.text().strip(),
            "alq_contador": self.txt_alq_contador.text().strip(),
            "otros_gastos": self.txt_otros_gastos.text().strip(),
            "iva": self.txt_iva.text().strip(),
        }

        return datos_ident, datos_energia, datos_gastos

    # ---------------------------------------------------------
    # AUTOMATIZACIÓN DE FECHAS
    # ---------------------------------------------------------
    def _recalcular_fechas(self):
        if self.modo == "modificar":
            return

        texto = self.txt_fec_inicio.text().strip()
        if len(texto) != 10:
            return

        try:
            fec_inicio_iso = convertir_a_iso(texto)
            fec_final_iso = sumar_10_anios(fec_inicio_iso)

            self.txt_fec_final.setText(convertir_a_ddmmaaaa(fec_final_iso))
            self.txt_efec_suple.setText(convertir_a_ddmmaaaa(fec_inicio_iso))
            self.txt_fin_suple.setText(convertir_a_ddmmaaaa(fec_final_iso))

        except Exception:
            pass

    # ---------------------------------------------------------
    # UTILIDADES
    # ---------------------------------------------------------
    def _vertido_upper(self, texto):
        if texto != texto.upper():
            cursor_pos = self.txt_vertido.cursorPosition()
            self.txt_vertido.setText(texto.upper())
            self.txt_vertido.setCursorPosition(cursor_pos)

    def _cancelar(self):
        self.main_window.cargar_modulo(self.main_window.crear_pantalla_inicio(), None)
