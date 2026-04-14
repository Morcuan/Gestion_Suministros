# -------------------------------------------------------------#
# Módulo: control_rectif_anular.py                             #
# Descripción: Controlador para rectificar y anular facturas   #
# Autor: Antonio Morales                                       #
# Fecha: 2026-04-01 (alineado motor 2.0.0)                     #
# -------------------------------------------------------------#

from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Motor 2.0.0
from facturas.calculo import (
    VERSION_MOTOR,
    calcular_bono_solar_cloud,
    calcular_cargos_para_factura,
    calcular_energia_para_factura,
    calcular_iva_para_factura,
    calcular_saldos_pendientes,
    calcular_servicios_para_factura,
    generar_json_calculo,
    guardar_calculo_factura,
    obtener_datos_factura,
)
from facturas.formulario_factura import FormularioFactura
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
        self.parent.volver_menu_principal()

    # ---------------------------------------------------------
    # CARGA DE FACTURA EXISTENTE
    # ---------------------------------------------------------
    def cargar_factura_existente(self):
        cursor = self.conn.cursor()

        # Obtener TODAS las columnas de la factura
        cursor.execute(
            "SELECT * FROM facturas WHERE nfactura = ?",
            (self.nfactura,),
        )

        row = cursor.fetchone()
        if not row:
            QMessageBox.critical(self, "Error", "Factura no encontrada.")
            return

        # Obtener nombres reales de columnas desde la BD
        columnas = [d[0] for d in cursor.description]

        # Crear diccionario {columna: valor}
        datos = dict(zip(columnas, row))

        # Normalizar fechas ISO → dd/mm/yyyy
        for clave in ("fec_emision", "inicio_factura", "fin_factura"):
            valor = datos.get(clave)
            if isinstance(valor, str) and "-" in valor:
                datos[clave] = convertir_a_ddmmaaaa(valor)

        # Cargar datos en el formulario
        self.form.set_datos(datos)

    # ---------------------------------------------------------
    def aplicar_modo(self):
        if self.modo == "edicion":
            self.setWindowTitle(f"Rectificar factura {self.nfactura}")
            self.form.txt_ncontrato.setReadOnly(True)
            self.form.txt_suplemento.setReadOnly(True)
            self.form.txt_nfactura.setReadOnly(True)

        elif self.modo == "anulacion":
            self.setWindowTitle(f"Confirmar anulación de factura {self.nfactura}")

            for attr in dir(self.form):
                if attr.startswith("txt_"):
                    getattr(self.form, attr).setReadOnly(True)

            self.form.gb_con.setVisible(False)
            self.form.gb_srv.setVisible(False)

            self.form.lbl_aviso.setText(
                "Esta acción eliminará la factura y sus cálculos asociados. No se puede deshacer."
            )
            self.form.lbl_aviso.setVisible(True)

    # ---------------------------------------------------------
    def on_guardar(self):
        if self.modo == "edicion":
            self.guardar_cambios_factura()
        elif self.modo == "anulacion":
            self.anular_factura()

    # ---------------------------------------------------------
    # RECTIFICAR FACTURA (motor 2.0.0)
    # ---------------------------------------------------------
    def guardar_cambios_factura(self):
        cursor_update = self.conn.cursor()
        datos = self.form.get_datos()

        # Normalizar fechas a ISO
        for clave in ("fec_emision", "inicio_factura", "fin_factura"):
            valor = datos.get(clave)
            if isinstance(valor, str) and "/" in valor:
                datos[clave] = convertir_a_iso(valor)

        # Guardar cambios básicos
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

        # ---------------------------------------------------------
        # MOTOR 2.0.0 — FLUJO COMPLETO
        # ---------------------------------------------------------
        cursor_calc = self.conn.cursor()

        # 1) Datos base
        datos_base = obtener_datos_factura(cursor_calc, self.nfactura)

        # 2) Cargos normativos
        cargos = calcular_cargos_para_factura(datos_base)

        # 3) Energía
        energia, datos_base = calcular_energia_para_factura(
            cursor_calc, self.nfactura, cargos.bono_social
        )

        # 4) Servicios
        servicios = calcular_servicios_para_factura(datos_base)

        # 5) IVA
        iva = calcular_iva_para_factura(energia, cargos, servicios, datos_base)

        # 6) Saldos pendientes
        saldos_obj, total_con_saldos = calcular_saldos_pendientes(
            datos_base, iva.total_con_iva
        )

        # 7) Cloud
        total_final, aplicado_cloud, nuevo_saldo = calcular_bono_solar_cloud(
            cursor_calc,
            datos_base["ncontrato"],
            total_con_saldos,
            energia.sobrante_excedentes,
        )

        # 8) JSON
        detalles_json = generar_json_calculo(
            energia,
            cargos,
            servicios,
            iva,
            saldos_obj,
            aplicado_cloud,
            nuevo_saldo,
            datos_base,
        )

        # 9) Guardado final
        guardar_calculo_factura(
            cursor_calc,
            self.nfactura,
            VERSION_MOTOR,
            energia,
            cargos,
            servicios,
            iva,
            saldos_obj,
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
