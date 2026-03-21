# -------------------------------------------------------------#
# Modulo: nuevo_contrato.py                                    #
# Descripción: Controlador inicial del proceso Nuevo Contrato  #
# Autor: Antonio Morales                                       #
# Fecha: 2026-02-10                                            #
# -------------------------------------------------------------#

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import (
    QInputDialog,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from contratos.formulario_contrato import FormularioContrato
from utilidades.logica_negocio import convertir_a_iso, validar_fecha
from utilidades.utilidades_bd import (
    insertar_codigo_postal,
    insertar_contrato,
    obtener_companias,
    validar_codigo_postal,
)


class NuevoContrato(QWidget):
    """
    Controlador del proceso de alta de contrato.
    Versión inicial: solo muestra el formulario incrustado.
    """

    cerrado = Signal()  # Señal para volver al inicio

    def __init__(self, parent=None):
        super().__init__(parent)

        # ---------------------------------------------------------
        # ACCESO A BD (heredado de MainWindow)
        # ---------------------------------------------------------
        self.conn = parent.conn
        self.cursor = parent.cursor

        # ---------------------------------------------------------
        # LAYOUT PRINCIPAL
        # ---------------------------------------------------------
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # ---------------------------------------------------------
        # FORMULARIO
        # ---------------------------------------------------------
        self.formulario = FormularioContrato(parent=self)
        self.formulario.set_modo("nuevo")  # ← MODO NUEVO ACTIVADO
        layout.addWidget(self.formulario)

        # ---------------------------------------------------------
        # CARGA DE COMPAÑÍAS DESDE BD
        # ---------------------------------------------------------
        lista = obtener_companias(self.cursor)  # ← OBTENEMOS LISTA
        self.formulario.cargar_companias(lista)  # ← CARGAMOS EN EL FORMULARIO

        # ---------------------------------------------------------
        # CONEXIONES BÁSICAS (sin lógica aún)
        # ---------------------------------------------------------
        self.formulario.btn_guardar.clicked.connect(self.guardar)
        self.formulario.btn_cancelar.clicked.connect(self.cancelar)

    # ---------------------------------------------------------
    # ACCIONES BÁSICAS
    # ---------------------------------------------------------
    def guardar(self):
        """
        Lógica completa de guardado:
        - Validaciones
        - Correcciones automáticas
        - Confirmaciones
        - Inserción en BD
        """

        # ==========================================================
        # 1. OBTENER DATOS DEL FORMULARIO
        # ==========================================================
        try:
            datos_ident, datos_energia, datos_gastos = self.formulario.obtener_datos()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            return

        # ==========================================================
        # 2. VALIDAR CAMPOS OBLIGATORIOS
        # ==========================================================
        if datos_ident["ncontrato"] == "":
            QMessageBox.warning(self, "Error", "Debe introducir un número de contrato.")
            return

        if datos_ident["codigo_postal"] == "":
            QMessageBox.warning(self, "Error", "Debe introducir un código postal.")
            return

        if self.formulario.txt_fec_inicio.text().strip() == "":
            QMessageBox.warning(self, "Error", "Debe introducir una fecha de inicio.")
            return

        # ==========================================================
        # 3. VALIDAR FECHA (dd/mm/yyyy)
        # ==========================================================

        fec_inicio_str = self.formulario.txt_fec_inicio.text().strip()

        if not validar_fecha(fec_inicio_str):
            QMessageBox.warning(
                self, "Error", "La fecha de inicio no es válida (dd/mm/yyyy)."
            )
            return

        # Convertimos a ISO (regla del proyecto)
        datos_ident["fec_inicio"] = convertir_a_iso(fec_inicio_str)

        # ==========================================================
        # 4. VALIDAR CÓDIGO POSTAL
        # ==========================================================

        ok, poblacion = validar_codigo_postal(self.cursor, datos_ident["codigo_postal"])

        if not ok:
            # Preguntar si desea crearlo
            resp = QMessageBox.question(
                self,
                "Código postal no encontrado",
                f"El código postal {datos_ident['codigo_postal']} no existe.\n"
                "¿Desea crearlo?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if resp == QMessageBox.No:
                return

            # Pedir población
            poblacion, ok2 = QInputDialog.getText(
                self, "Nueva población", "Introduzca el nombre de la población:"
            )

            if not ok2 or poblacion.strip() == "":
                QMessageBox.warning(
                    self, "Error", "Debe introducir una población válida."
                )
                return

            insertar_codigo_postal(
                self.conn, self.cursor, datos_ident["codigo_postal"], poblacion.strip()
            )

        # ==========================================================
        # 5. VALIDAR CAMPOS NUMÉRICOS
        # ==========================================================
        campos_numericos = [
            ("Potencia punta", datos_energia["ppunta"]),
            ("Potencia valle", datos_energia["pvalle"]),
            ("Pv. pot. punta", datos_energia["pv_ppunta"]),
            ("Pv. pot. llano", datos_energia["pv_pvalle"]),
            ("Pv. cons. punta", datos_energia["pv_conpunta"]),
            ("Pv. cons. llano", datos_energia["pv_conllano"]),
            ("Pv. cons. valle", datos_energia["pv_convalle"]),
            ("Pv. excedentes", datos_energia["pv_excedentes"]),
            ("Bono social", datos_gastos["bono_social"]),
            ("Imp. eléctrico", datos_gastos["i_electrico"]),
            ("Alquiler contador", datos_gastos["alq_contador"]),
            ("Otros gastos", datos_gastos["otros_gastos"]),
            ("IVA", datos_gastos["iva"]),
        ]

        for nombre, valor in campos_numericos:
            if valor.strip() == "":
                continue
            try:
                float(valor)
            except ValueError:
                QMessageBox.warning(
                    self, "Error", f"El campo '{nombre}' debe ser numérico."
                )
                return

        # ==========================================================
        # 6. REGLA NUEVA: SI VERTIDO = N → pv_excedentes = 0
        # ==========================================================
        if datos_energia["vertido"] == "N":
            datos_energia["pv_excedentes"] = "0"

        # ==========================================================
        # 7. INSERTAR CONTRATO COMPLETO
        # ==========================================================

        try:
            idc = insertar_contrato(
                self.conn, self.cursor, datos_ident, datos_energia, datos_gastos
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el contrato:\n{e}")
            return

        # ==========================================================
        # 8. ÉXITO
        # ==========================================================
        QMessageBox.information(
            self, "Contrato guardado", f"Contrato guardado correctamente con ID {idc}."
        )

        # Opcional: limpiar formulario
        self.formulario.limpiar()

    def cancelar(self):
        """Cierra el módulo y vuelve al inicio."""
        self.cerrado.emit()
