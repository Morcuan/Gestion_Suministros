# ----------------------------------------------------#
# Modulo: contrato_nuevo.py                           #
# Descripcion: Gestión de nuevo contrato y edición    #
# Autor: Antonio Morales                              #
# Fecha: 2025-12                                      #
# ----------------------------------------------------#

from PySide6.QtCore import QRegularExpression, Qt, Signal
from PySide6.QtGui import QFont, QRegularExpressionValidator
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from aux_database import (
    actualizar_contrato,
    construir_tupla_contrato,
    construir_tupla_contrato_edicion,
    existe_contrato,
    insertar_contrato,
    listar_companias,
    obtener_poblaciones_por_cp,
)
from aux_fechas import a_ddmm, a_iso
from aux_presentacion import estilo_boton
from aux_validacion import validar_rango
from base_formulario import BaseFormulario


class NuevoContratoWidget(BaseFormulario):
    contrato_guardado = Signal()

    def __init__(self, modo="nuevo", datos=None, bd=None, parent=None):
        super().__init__(parent)

        self.modo = modo
        self.datos = datos
        self.bd = bd

        self.setFont(QFont("Noto Sans", 12))
        self.resize(600, 400)
        self.setWindowTitle("Gestión de Contratos")

        layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        # ---------------------------------------------------------
        # CAMPOS PRINCIPALES
        # ---------------------------------------------------------
        self.compania_combo = QComboBox()
        vista = QListView()
        vista.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.compania_combo.setView(vista)
        self.compania_combo.setMaxVisibleItems(10)
        self._cargar_companias()
        self.form_layout.addRow("Compañía:", self.compania_combo)

        self.codigo_postal_edit = QLineEdit()
        self.codigo_postal_edit.editingFinished.connect(self.validar_codigo_postal)
        self.form_layout.addRow("Código postal:", self.codigo_postal_edit)

        self.label_poblacion = QLabel("Población:")
        self.poblacion_edit = QLineEdit()
        self.poblacion_edit.setReadOnly(True)
        self.form_layout.addRow(self.label_poblacion, self.poblacion_edit)

        self.numero_contrato_edit = QLineEdit()
        self.form_layout.addRow("Número de contrato:", self.numero_contrato_edit)

        self.fecha_inicio_edit = QLineEdit()
        self.fecha_inicio_edit.setPlaceholderText("DD/MM/YYYY")
        self.form_layout.addRow("Fecha inicio:", self.fecha_inicio_edit)

        self.fecha_final_edit = QLineEdit()
        self.fecha_final_edit.setPlaceholderText("DD/MM/YYYY")
        self.form_layout.addRow("Fecha final:", self.fecha_final_edit)

        # ---------------------------------------------------------
        # CAMPOS DECIMALES
        # ---------------------------------------------------------
        self.potencia_punta_edit = self._crear_campo_decimal("Potencia punta (kW):")
        self.importe_potencia_punta_edit = self._crear_campo_decimal(
            "Importe potencia punta (€):"
        )
        self.potencia_valle_edit = self._crear_campo_decimal("Potencia valle (kW):")
        self.importe_potencia_valle_edit = self._crear_campo_decimal(
            "Importe potencia valle (€):"
        )
        self.importe_consumo_punta_edit = self._crear_campo_decimal(
            "Importe consumo punta (€/kWh):"
        )
        self.importe_consumo_llano_edit = self._crear_campo_decimal(
            "Importe consumo llano (€/kWh):"
        )
        self.importe_consumo_valle_edit = self._crear_campo_decimal(
            "Importe consumo valle (€/kWh):"
        )
        self.importe_excedentes_edit = self._crear_campo_decimal(
            "Importe excedentes (€/kWh):"
        )
        self.importe_bono_social_edit = self._crear_campo_decimal(
            "Importe bono social (€):"
        )
        self.importe_alquiler_contador_edit = self._crear_campo_decimal(
            "Importe alquiler contador (€):"
        )
        self.importe_asistente_smart_edit = self._crear_campo_decimal(
            "Importe otros conceptos (€):"
        )
        self.impuesto_electricidad_edit = self._crear_campo_decimal(
            "Impuesto electricidad (%):"
        )
        self.iva_edit = self._crear_campo_decimal("IVA (%):")

        self.vertido_edit = QCheckBox("Vertido permitido")
        self.form_layout.addRow("", self.vertido_edit)

        layout.addLayout(self.form_layout)

        # ---------------------------------------------------------
        # BOTONES
        # ---------------------------------------------------------
        botones = QHBoxLayout()
        self.guardar_btn = QPushButton("Guardar")
        self.cancelar_btn = QPushButton("Cancelar")

        self.guardar_btn.setStyleSheet(estilo_boton("guardar"))
        self.cancelar_btn.setStyleSheet(estilo_boton("cancelar"))

        botones.addWidget(self.guardar_btn)
        botones.addWidget(self.cancelar_btn)
        layout.addLayout(botones)

        self.setLayout(layout)

        # Conexiones
        self.guardar_btn.clicked.connect(self.guardar_contrato)
        self.cancelar_btn.clicked.connect(self.close)

        # Modo edición
        if self.modo == "edicion" and self.datos:
            self.cargar_datos(self.datos)

    # ---------------------------------------------------------
    # VALIDAR CÓDIGO POSTAL
    # ---------------------------------------------------------
    def validar_codigo_postal(self):
        cp = self.codigo_postal_edit.text().strip()

        if len(cp) != 5 or not cp.isdigit():
            self.marcar_error(self.codigo_postal_edit)
            self.poblacion_edit.setText("No válido")
            return False

        poblaciones = obtener_poblaciones_por_cp(cp)

        if not poblaciones:
            self.marcar_error(self.codigo_postal_edit)
            self.poblacion_edit.setText("No encontrado")
            return False

        self.reset_widget(self.codigo_postal_edit)
        self.poblacion_edit.setText(poblaciones[0])
        return True

    # ---------------------------------------------------------
    # CREAR CAMPO DECIMAL
    # ---------------------------------------------------------
    def _crear_campo_decimal(self, etiqueta):
        campo = QLineEdit()
        campo.setPlaceholderText("Ej: 4,4 o 4.4")
        rx = QRegularExpression(r"^[0-9]+([.,][0-9]+)?$")
        campo.setValidator(QRegularExpressionValidator(rx))
        self.form_layout.addRow(etiqueta, campo)
        return campo

    # ---------------------------------------------------------
    # CARGAR COMPAÑÍAS
    # ---------------------------------------------------------
    def _cargar_companias(self):
        self.compania_combo.clear()
        for cid, nombre in listar_companias():
            self.compania_combo.addItem(nombre, cid)

    # ---------------------------------------------------------
    # GUARDAR CONTRATO
    # ---------------------------------------------------------
    def guardar_contrato(self):
        try:
            self.limpiar_estilos()

            numero = self.numero_contrato_edit.text().strip()

            # Validar número duplicado SOLO en modo nuevo
            if self.modo == "nuevo" and existe_contrato(self.bd, numero):
                self.marcar_error(self.numero_contrato_edit)
                QMessageBox.warning(
                    self, "Número duplicado", "Ya existe un contrato con ese número."
                )
                return

            # Validar CP
            if not self.validar_codigo_postal():
                QMessageBox.warning(self, "Atención", "El código postal no existe.")
                return

            # Validar fechas
            fecha_inicio_raw = self.fecha_inicio_edit.text().strip()
            fecha_final_raw = self.fecha_final_edit.text().strip()

            fecha_inicio_iso = a_iso(fecha_inicio_raw)
            fecha_final_iso = a_iso(fecha_final_raw)

            if not fecha_inicio_iso:
                self.marcar_error(self.fecha_inicio_edit)
                QMessageBox.warning(
                    self, "Fecha incorrecta", "La fecha de inicio no es válida."
                )
                return

            if not fecha_final_iso:
                self.marcar_error(self.fecha_final_edit)
                QMessageBox.warning(
                    self, "Fecha incorrecta", "La fecha final no es válida."
                )
                return

            if fecha_final_iso <= fecha_inicio_iso:
                self.marcar_error(self.fecha_final_edit)
                QMessageBox.warning(
                    self,
                    "Fechas incorrectas",
                    "La fecha final debe ser posterior a la fecha de inicio.",
                )
                return

            # Validar potencias
            if not validar_rango(self.potencia_punta_edit.text(), 0, 10):
                self.marcar_error(self.potencia_punta_edit)
                QMessageBox.warning(
                    self, "Potencia punta", "Debe estar entre 0 y 10 kW."
                )
                return

            if not validar_rango(self.potencia_valle_edit.text(), 0, 10):
                self.marcar_error(self.potencia_valle_edit)
                QMessageBox.warning(
                    self, "Potencia valle", "Debe estar entre 0 y 10 kW."
                )
                return

            # Validar importes
            campos_importe = [
                (self.importe_potencia_punta_edit, "Importe potencia punta"),
                (self.importe_potencia_valle_edit, "Importe potencia valle"),
                (self.importe_consumo_punta_edit, "Importe consumo punta"),
                (self.importe_consumo_llano_edit, "Importe consumo llano"),
                (self.importe_consumo_valle_edit, "Importe consumo valle"),
                (self.importe_excedentes_edit, "Importe excedentes"),
            ]

            for widget, nombre in campos_importe:
                if not validar_rango(widget.text().strip(), 0, 1):
                    self.marcar_error(widget)
                    QMessageBox.warning(
                        self, nombre, f"{nombre} debe estar entre 0 y 1."
                    )
                    return

            # Recoger datos
            datos = self.recoger_datos()
            datos["fecha_inicio"] = fecha_inicio_iso
            datos["fecha_final"] = fecha_final_iso

            # Guardar según modo
            if self.modo == "nuevo":
                tupla = construir_tupla_contrato(datos)
                insertar_contrato(tupla)
                QMessageBox.information(
                    self, "Contrato", "Contrato creado correctamente."
                )
                self.contrato_guardado.emit()
                self.close()

            elif self.modo == "edicion":
                numero_original = self.numero_contrato_edit.text().strip()
                tupla = construir_tupla_contrato_edicion(datos, numero_original)
                actualizar_contrato(tupla)

            # Registrar estado MODIFICADO
            try:
                from aux_database import registrar_estado_contrato

                registrar_estado_contrato(numero_original, "MODIFICADO")
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Aviso",
                    f"El contrato se actualizó, pero no se pudo registrar el estado MODIFICADO.\n{e}",
                )

            QMessageBox.information(
                self, "Contrato", "Contrato actualizado correctamente."
            )
            self.contrato_guardado.emit()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el contrato:\n{e}")

    # ---------------------------------------------------------
    # CARGAR DATOS EN MODO EDICIÓN
    # ---------------------------------------------------------
    def cargar_datos(self, t):
        d = {
            "id_compania": t[0],
            "codigo_postal": t[1],
            "poblacion": t[2],
            "numero": t[3],
            "fecha_inicio": t[4],
            "fecha_final": t[5],
            "potencia_punta": t[6],
            "importe_potencia_punta": t[7],
            "potencia_valle": t[8],
            "importe_potencia_valle": t[9],
            "importe_consumo_punta": t[10],
            "importe_consumo_llano": t[11],
            "importe_consumo_valle": t[12],
            "vertido": t[13],
            "importe_excedentes": t[14],
            "importe_bono_social": t[15],
            "importe_alquiler_contador": t[16],
            "importe_asistente_smart": t[17],
            "impuesto_electricidad": t[18],
            "iva": t[19],
        }
        self.cargar_desde_dict(d)

    # ---------------------------------------------------------
    # CARGAR DESDE DICCIONARIO
    # ---------------------------------------------------------
    def cargar_desde_dict(self, d):
        idx = self.compania_combo.findData(d["id_compania"])
        if idx >= 0:
            self.compania_combo.setCurrentIndex(idx)

        self.codigo_postal_edit.setText(d.get("codigo_postal", ""))
        self.poblacion_edit.setText(d.get("poblacion", ""))

        self.numero_contrato_edit.setText(d.get("numero", ""))
        self.fecha_inicio_edit.setText(a_ddmm(d.get("fecha_inicio", "")))
        self.fecha_final_edit.setText(a_ddmm(d.get("fecha_final", "")))

        self.potencia_punta_edit.setText(str(d.get("potencia_punta", "")))
        self.importe_potencia_punta_edit.setText(
            str(d.get("importe_potencia_punta", ""))
        )
        self.potencia_valle_edit.setText(str(d.get("potencia_valle", "")))
        self.importe_potencia_valle_edit.setText(
            str(d.get("importe_potencia_valle", ""))
        )

        self.importe_consumo_punta_edit.setText(str(d.get("importe_consumo_punta", "")))
        self.importe_consumo_llano_edit.setText(str(d.get("importe_consumo_llano", "")))
        self.importe_consumo_valle_edit.setText(str(d.get("importe_consumo_valle", "")))

        self.vertido_edit.setChecked(bool(d.get("vertido", 0)))

        self.importe_excedentes_edit.setText(str(d.get("importe_excedentes", "")))
        self.importe_bono_social_edit.setText(str(d.get("importe_bono_social", "")))
        self.importe_alquiler_contador_edit.setText(
            str(d.get("importe_alquiler_contador", ""))
        )
        self.importe_asistente_smart_edit.setText(
            str(d.get("importe_asistente_smart", ""))
        )
        self.impuesto_electricidad_edit.setText(str(d.get("impuesto_electricidad", "")))
        self.iva_edit.setText(str(d.get("iva", "")))

    # ---------------------------------------------------------
    # RECOGER DATOS
    # ---------------------------------------------------------
    def recoger_datos(self):
        codigo = self.codigo_postal_edit.text().strip()

        datos = {
            "id_compania": self.compania_combo.currentData(),
            "id_postal": codigo,
            "numero": self.numero_contrato_edit.text().strip(),
            "potencia_punta": self.potencia_punta_edit.text().strip(),
            "importe_potencia_punta": self.importe_potencia_punta_edit.text().strip(),
            "potencia_valle": self.potencia_valle_edit.text().strip(),
            "importe_potencia_valle": self.importe_potencia_valle_edit.text().strip(),
            "importe_consumo_punta": self.importe_consumo_punta_edit.text().strip(),
            "importe_consumo_llano": self.importe_consumo_llano_edit.text().strip(),
            "importe_consumo_valle": self.importe_consumo_valle_edit.text().strip(),
            "vertido": int(self.vertido_edit.isChecked()),
            "importe_excedentes": self.importe_excedentes_edit.text().strip(),
            "importe_bono_social": self.importe_bono_social_edit.text().strip(),
            "importe_alquiler_contador": self.importe_alquiler_contador_edit.text().strip(),
            "importe_asistente_smart": self.importe_asistente_smart_edit.text().strip(),
            "impuesto_electricidad": self.impuesto_electricidad_edit.text().strip(),
            "iva": self.iva_edit.text().strip(),
        }

        return datos

    # ---------------------------------------------------------
    # UTILIDADES
    # ---------------------------------------------------------
    def limpiar_estilos(self):
        widgets = [
            self.codigo_postal_edit,
            self.poblacion_edit,
            self.numero_contrato_edit,
            self.fecha_inicio_edit,
            self.fecha_final_edit,
            self.potencia_punta_edit,
            self.importe_potencia_punta_edit,
            self.potencia_valle_edit,
            self.importe_potencia_valle_edit,
            self.importe_consumo_punta_edit,
            self.importe_consumo_llano_edit,
            self.importe_consumo_valle_edit,
            self.importe_excedentes_edit,
            self.importe_bono_social_edit,
            self.importe_alquiler_contador_edit,
            self.importe_asistente_smart_edit,
            self.impuesto_electricidad_edit,
            self.iva_edit,
        ]

        for w in widgets:
            w.setStyleSheet("")

    def reset_form(self):
        self.limpiar_estilos()

        self.compania_combo.setCurrentIndex(0)
        self.codigo_postal_edit.clear()
        self.poblacion_edit.clear()
        self.numero_contrato_edit.clear()
        self.fecha_inicio_edit.clear()
        self.fecha_final_edit.clear()

        self.potencia_punta_edit.clear()
        self.importe_potencia_punta_edit.clear()
        self.potencia_valle_edit.clear()
        self.importe_potencia_valle_edit.clear()
        self.importe_consumo_punta_edit.clear()
        self.importe_consumo_llano_edit.clear()
        self.importe_consumo_valle_edit.clear()

        self.vertido_edit.setChecked(False)

        self.importe_excedentes_edit.clear()
        self.importe_bono_social_edit.clear()
        self.importe_alquiler_contador_edit.clear()
        self.importe_asistente_smart_edit.clear()
        self.impuesto_electricidad_edit.clear()
        self.iva_edit.clear()

    # ---------------------------------------------------------
    # MÉTODO ABRIR (compatibilidad con el menú)
    # ---------------------------------------------------------
    def abrir(self):
        self.show()
