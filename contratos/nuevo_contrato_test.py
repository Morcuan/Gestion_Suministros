# -------------------------------------------------------------#
# Modulo: nuevo_contrato_test.py                               #
# Descripción: Alta de contrato ficticio para comparativas     #
# Autor: Antonio Morales                                       #
# Fecha: 2026-02-14 (versión corregida 2026-04-28)             #
# -------------------------------------------------------------#

from PySide6.QtCore import Signal
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
    obtener_companias,
    validar_codigo_postal,
)


class NuevoContratoTest(QWidget):
    """
    Controlador del proceso de alta de contrato ficticio (oferta externa).
    Guarda en tablas *_test para simulaciones.
    """

    cerrado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # ---------------------------------------------------------
        # ACCESO A BD (heredado de MainWindow)
        # ---------------------------------------------------------
        self.main_window = parent
        self.conn = parent.conn
        self.cursor = parent.conn.cursor()

        # ---------------------------------------------------------
        # LAYOUT PRINCIPAL
        # ---------------------------------------------------------
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # ---------------------------------------------------------
        # FORMULARIO (IMPORTANTE: parent=MainWindow)
        # ---------------------------------------------------------
        self.formulario = FormularioContrato(parent=self.main_window, modo="test")
        layout.addWidget(self.formulario)

        # ---------------------------------------------------------
        # CARGA DE COMPAÑÍAS
        # ---------------------------------------------------------
        lista = obtener_companias(self.cursor)
        self.formulario.cargar_companias(lista)

        # ---------------------------------------------------------
        # CONEXIONES
        # ---------------------------------------------------------
        self.formulario.btn_guardar.clicked.connect(self.guardar)
        self.formulario.btn_cancelar.clicked.connect(self.cancelar)

    # ---------------------------------------------------------
    # GENERAR ID DE CONTRATO TEST
    # ---------------------------------------------------------
    def generar_id_contrato_test(self):
        self.cursor.execute(
            "SELECT MAX(id_contrato) FROM contratos_identificacion_test"
        )
        row = self.cursor.fetchone()
        return (row[0] + 1) if row and row[0] else 900000

    # ---------------------------------------------------------
    # GUARDAR CONTRATO FICTICIO
    # ---------------------------------------------------------
    def guardar(self):

        # ==========================================================
        # 1. OBTENER DATOS DEL FORMULARIO
        # ==========================================================
        try:
            datos_ident, datos_energia, datos_gastos = self.formulario.obtener_datos()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            return

        # ==========================================================
        # 2. VALIDACIONES BÁSICAS
        # ==========================================================
        if datos_ident["codigo_postal"] == "":
            QMessageBox.warning(self, "Error", "Debe introducir un código postal.")
            return

        if self.formulario.txt_fec_inicio.text().strip() == "":
            QMessageBox.warning(self, "Error", "Debe introducir una fecha de inicio.")
            return

        # ==========================================================
        # 3. VALIDAR FECHA
        # ==========================================================
        fec_inicio_str = self.formulario.txt_fec_inicio.text().strip()

        if not validar_fecha(fec_inicio_str):
            QMessageBox.warning(
                self, "Error", "La fecha de inicio no es válida (dd/mm/yyyy)."
            )
            return

        datos_ident["fec_inicio"] = convertir_a_iso(fec_inicio_str)

        # ==========================================================
        # 4. VALIDAR CÓDIGO POSTAL
        # ==========================================================
        ok, poblacion = validar_codigo_postal(self.cursor, datos_ident["codigo_postal"])

        if not ok:
            resp = QMessageBox.question(
                self,
                "Código postal no encontrado",
                f"El código postal {datos_ident['codigo_postal']} no existe.\n"
                "¿Desea crearlo?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if resp == QMessageBox.No:
                return

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
        # 6. REGLA: SI VERTIDO = N → pv_excedentes = 0
        # ==========================================================
        if datos_energia["vertido"] == "N":
            datos_energia["pv_excedentes"] = "0"

        # ==========================================================
        # 7. INSERTAR CONTRATO EN TABLAS TEST
        # ==========================================================
        try:
            idc = self.generar_id_contrato_test()

            datos_ident["ncontrato"] = f"TEST_{datos_ident['compania']}_{idc}"

            sql_ident = """
                INSERT INTO contratos_identificacion_test (
                    id_contrato, ncontrato, suplemento, compania,
                    codigo_postal, fec_inicio, fec_final,
                    efec_suple, fin_suple, fec_anulacion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            self.cursor.execute(
                sql_ident,
                (
                    idc,
                    datos_ident["ncontrato"],
                    datos_ident["suplemento"],
                    datos_ident["compania"],
                    datos_ident["codigo_postal"],
                    datos_ident["fec_inicio"],
                    datos_ident["fec_final"],
                    datos_ident["efec_suple"],
                    datos_ident["fin_suple"],
                    datos_ident["fec_anulacion"],
                ),
            )

            sql_energia = """
                INSERT INTO contratos_energia_test (
                    id_contrato, ppunta, pv_ppunta,
                    pvalle, pv_pvalle,
                    pv_conpunta, pv_conllano, pv_convalle,
                    vertido, pv_excedent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            self.cursor.execute(
                sql_energia,
                (
                    idc,
                    datos_energia["ppunta"],
                    datos_energia["pv_ppunta"],
                    datos_energia["pvalle"],
                    datos_energia["pv_pvalle"],
                    datos_energia["pv_conpunta"],
                    datos_energia["pv_conllano"],
                    datos_energia["pv_convalle"],
                    datos_energia["vertido"],
                    datos_energia["pv_excedentes"],
                ),
            )

            sql_gastos = """
                INSERT INTO contratos_gastos_test (
                    id_contrato, bono_social, alq_contador,
                    otros_gastos, i_electrico, iva
                ) VALUES (?, ?, ?, ?, ?, ?)
            """

            self.cursor.execute(
                sql_gastos,
                (
                    idc,
                    datos_gastos["bono_social"],
                    datos_gastos["alq_contador"],
                    datos_gastos["otros_gastos"],
                    datos_gastos["i_electrico"],
                    datos_gastos["iva"],
                ),
            )

            self.conn.commit()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"No se pudo guardar el contrato ficticio:\n{e}"
            )
            return

        # ==========================================================
        # 8. ÉXITO
        # ==========================================================
        QMessageBox.information(
            self,
            "Contrato ficticio",
            f"Contrato ficticio guardado correctamente con ID {idc}.",
        )

        self.formulario.limpiar()

    # ---------------------------------------------------------
    # CANCELAR
    # ---------------------------------------------------------
    def cancelar(self):
        self.cerrado.emit()
