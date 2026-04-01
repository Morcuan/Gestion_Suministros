# -------------------------------------------------------------#
# Módulo: control_rectif_anular.py                             #
# Descripción: Controlador para rectificar y anular facturas   #
# Autor: Antonio Morales                                       #
# Fecha: 2026-04-01                                            #
# -------------------------------------------------------------#

from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from facturas.formulario_factura import FormularioFactura
from facturas.version_motor import obtener_version_motor
from utilidades.logica_negocio import (
    convertir_a_ddmmaaaa,
    convertir_a_iso,
)


class ControlRectifAnular(QWidget):
    """
    Controlador para gestionar:
    - Rectificación de factura (modo='edicion')
    - Anulación de factura (modo='anulacion')
    """

    def __init__(
        self,
        parent=None,
        conn=None,
        modo="edicion",
        ncontrato=None,
        suplemento=None,
        nfactura=None,
    ):
        super().__init__(parent)

        self.parent = parent
        self.conn = conn
        self.modo = modo
        self.ncontrato = ncontrato
        self.suplemento = suplemento
        self.nfactura = nfactura

        self.init_ui()

        if self.modo in ("edicion", "anulacion"):
            self.cargar_factura_existente()
            self.aplicar_modo()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def init_ui(self):
        layout = QVBoxLayout(self)

        self.form = FormularioFactura(self)
        layout.addWidget(self.form)

        # Botones inferiores
        botones = QHBoxLayout()

        self.btn_guardar = QPushButton()
        botones.addWidget(self.btn_guardar)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.volver_lista_facturas)
        botones.addWidget(self.btn_cancelar)

        layout.addLayout(botones)

        if self.modo == "edicion":
            self.btn_guardar.setText("Guardar cambios")
        elif self.modo == "anulacion":
            self.btn_guardar.setText("Anular factura")

        self.btn_guardar.clicked.connect(self.on_guardar)

    # ---------------------------------------------------------
    def volver_lista_facturas(self):
        """Vuelve a la lista de facturas del contrato."""
        self.parent.volver_menu_principal()

    # ---------------------------------------------------------
    # CARGA DE FACTURA EXISTENTE
    # ---------------------------------------------------------
    def cargar_factura_existente(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT ncontrato, suplemento, nfactura,
                   fec_emision, inicio_factura, fin_factura,
                   dias_factura,
                   consumo_punta, consumo_llano, consumo_valle,
                   excedentes, importe_compensado,
                   servicios, dcto_servicios, saldos_pendientes, bat_virtual
            FROM facturas
            WHERE nfactura = ?
        """,
            (self.nfactura,),
        )

        row = cursor.fetchone()
        if not row:
            QMessageBox.critical(self, "Error", "Factura no encontrada.")
            return

        columnas = [
            "ncontrato",
            "suplemento",
            "nfactura",
            "fec_emision",
            "inicio_factura",
            "fin_factura",
            "dias_factura",
            "consumo_punta",
            "consumo_llano",
            "consumo_valle",
            "excedentes",
            "importe_compensado",
            "servicios",
            "dcto_servicios",
            "saldos_pendientes",
            "bat_virtual",
        ]

        datos = dict(zip(columnas, row))

        # Normalizar fechas ISO → dd/mm/yyyy
        for clave in ("fec_emision", "inicio_factura", "fin_factura"):
            valor = datos.get(clave)
            if isinstance(valor, str) and "-" in valor:
                datos[clave] = convertir_a_ddmmaaaa(valor)

        self.form.set_datos(datos)

    # ---------------------------------------------------------
    # APLICAR MODO
    # ---------------------------------------------------------
    def aplicar_modo(self):
        if self.modo == "edicion":
            self.setWindowTitle(f"Rectificar factura {self.nfactura}")
            self.form.txt_ncontrato.setReadOnly(True)
            self.form.txt_suplemento.setReadOnly(True)
            self.form.txt_nfactura.setReadOnly(True)

        elif self.modo == "anulacion":
            self.setWindowTitle(f"Confirmar anulación de factura {self.nfactura}")

            # 1) Poner todos los campos en modo lectura
            for attr in dir(self.form):
                if attr.startswith("txt_"):
                    getattr(self.form, attr).setReadOnly(True)

            # 2) Ocultar bloques no relevantes
            self.form.gb_con.setVisible(False)
            self.form.gb_srv.setVisible(False)

            # 3) Mostrar mensaje de advertencia
            self.form.lbl_aviso.setText(
                "Esta acción eliminará la factura y sus cálculos asociados. No se puede deshacer."
            )
            self.form.lbl_aviso.setVisible(True)

    # ---------------------------------------------------------
    # BOTÓN GUARDAR
    # ---------------------------------------------------------
    def on_guardar(self):
        if self.modo == "edicion":
            self.guardar_cambios_factura()
        elif self.modo == "anulacion":
            self.anular_factura()

    # ---------------------------------------------------------
    # RECTIFICAR FACTURA (con recálculo completo)
    # ---------------------------------------------------------
    def guardar_cambios_factura(self):
        cursor_update = self.conn.cursor()
        datos = self.form.get_datos()

        # Normalizar fechas a ISO si vienen en dd/mm/yyyy
        for clave in ("fec_emision", "inicio_factura", "fin_factura"):
            valor = datos.get(clave)
            if isinstance(valor, str) and "/" in valor:
                datos[clave] = convertir_a_iso(valor)

        cursor_update.execute(
            """
            UPDATE facturas
            SET fec_emision=?, inicio_factura=?, fin_factura=?, dias_factura=?,
                consumo_punta=?, consumo_llano=?, consumo_valle=?,
                excedentes=?, importe_compensado=?,
                servicios=?, dcto_servicios=?, saldos_pendientes=?, bat_virtual=?
            WHERE nfactura=?
        """,
            (
                datos["fec_emision"],
                datos["inicio_factura"],
                datos["fin_factura"],
                datos["dias_factura"],
                datos["consumo_punta"],
                datos["consumo_llano"],
                datos["consumo_valle"],
                datos["excedentes"],
                datos["importe_compensado"],
                datos["servicios"],
                datos["dcto_servicios"],
                datos["saldos_pendientes"],
                datos["bat_virtual"],
                self.nfactura,
            ),
        )

        from facturas.calculo import (
            calcular_bono_solar_cloud,
            calcular_cargos_para_factura,
            calcular_energia_para_factura,
            calcular_iva_para_factura,
            calcular_servicios_para_factura,
            generar_json_calculo,
            guardar_calculo_factura,
            obtener_datos_factura,
        )

        cursor_calc = self.conn.cursor()

        datos_base = obtener_datos_factura(cursor_calc, self.nfactura)
        cargos = calcular_cargos_para_factura(datos_base)
        energia, datos_base = calcular_energia_para_factura(
            cursor_calc, self.nfactura, cargos.bono_social
        )
        servicios = calcular_servicios_para_factura(datos_base)
        iva = calcular_iva_para_factura(
            energia.total_energia, cargos.total_cargos, servicios.total_servicios_otros
        )

        total_final, aplicado_cloud, nuevo_saldo = calcular_bono_solar_cloud(
            cursor_calc,
            datos_base["ncontrato"],
            iva.total_con_iva,
            energia.sobrante_excedentes,
        )

        detalles_json = generar_json_calculo(
            energia, cargos, servicios, iva, aplicado_cloud, nuevo_saldo, datos_base
        )

        # Versión de motor desde tabla version_motor
        from facturas.calculo import VERSION_MOTOR

        version_motor = VERSION_MOTOR

        guardar_calculo_factura(
            cursor_calc,
            self.nfactura,
            version_motor,
            energia,
            cargos,
            servicios,
            iva,
            aplicado_cloud,
            nuevo_saldo,
            detalles_json,
        )

        self.conn.commit()

        QMessageBox.information(
            self, "OK", "Factura rectificada y recalculada correctamente."
        )
        self.parent.volver_menu_principal()

    # ---------------------------------------------------------
    # ANULAR FACTURA
    # ---------------------------------------------------------
    def anular_factura(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM factura_calculos WHERE nfactura=?", (self.nfactura,)
        )
        cursor.execute("DELETE FROM facturas WHERE nfactura=?", (self.nfactura,))
        self.conn.commit()

        QMessageBox.information(self, "OK", "Factura anulada correctamente.")
        self.parent.volver_menu_principal()
