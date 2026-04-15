# -------------------------------------------------------------#
# Módulo: nueva_factura.py                                     #
# Descripción: Controlador completo para captura de factura    #
# Autor: Antonio Morales                                       #
# Fecha: 2026-02-10                                            #
# -------------------------------------------------------------#

from sqlite3 import Connection, Cursor

from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from facturas.calculo import (
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
from utilidades.logica_negocio import convertir_a_iso, dias_entre_fechas, validar_fecha


class NuevaFactura(QWidget):
    """
    Caso de uso 'Nueva factura':
    - Valida datos
    - Inserta en facturas
    - Lanza motor de cálculo (calculo.py)
    - Inserta en factura_calculos
    """

    def __init__(
        self,
        parent=None,
        conn: Connection | None = None,
        ncontrato: str | None = None,
        suplemento: int | None = None,
    ):
        super().__init__(parent)

        assert conn is not None, "La conexión no puede ser None"

        self.parent = parent
        self.conn: Connection = conn
        self.cursor: Cursor = conn.cursor()

        self.ncontrato = ncontrato
        self.suplemento = suplemento

        self.crear_ui()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def crear_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        self.form = FormularioFactura(parent=self)

        # OCULTAR CAMPOS NO EDITABLES (solo nueva factura)
        self.form.ocultar_campos_no_editables()

        self.form.set_identificacion(self.ncontrato, self.suplemento)
        layout.addWidget(self.form)

        botones = QHBoxLayout()

        self.btn_guardar = QPushButton("Guardar factura")
        self.btn_guardar.clicked.connect(self.guardar_factura)
        botones.addWidget(self.btn_guardar)

        self.btn_otro = QPushButton("Otra factura")
        self.btn_otro.setEnabled(False)
        self.btn_otro.clicked.connect(self.nueva_factura)
        botones.addWidget(self.btn_otro)

        self.btn_salir = QPushButton("Salir")
        self.btn_salir.clicked.connect(self.volver_menu)
        botones.addWidget(self.btn_salir)

        layout.addLayout(botones)

    # ---------------------------------------------------------
    # VALIDACIONES
    # ---------------------------------------------------------
    def validar_datos(self, datos: dict[str, str]):
        obligatorios = ["nfactura", "fec_emision", "inicio_factura", "fin_factura"]

        for campo in obligatorios:
            if not datos[campo]:
                return False, f"El campo '{campo}' es obligatorio."

        for campo in ["fec_emision", "inicio_factura", "fin_factura"]:
            if not validar_fecha(datos[campo]):
                return False, f"Fecha inválida en '{campo}'."

        # días factura (incluyendo ambos extremos)
        dias = dias_entre_fechas(datos["inicio_factura"], datos["fin_factura"])
        datos["dias_factura"] = dias

        # coherencia fechas
        fec_ini_iso = convertir_a_iso(datos["inicio_factura"])
        fec_fin_iso = convertir_a_iso(datos["fin_factura"])
        if fec_fin_iso < fec_ini_iso:
            return False, "La fecha final no puede ser anterior a la inicial."

        campos_num = [
            "consumo_punta",
            "consumo_llano",
            "consumo_valle",
            "excedentes",
            "servicios",
            "dcto_servicios",
            "saldos_pendientes",
            "bat_virtual",
        ]

        for campo in campos_num:
            if datos[campo]:
                try:
                    float(datos[campo])
                except ValueError:
                    return False, f"El campo '{campo}' debe ser numérico."

        return True, datos

    # ---------------------------------------------------------
    # GUARDAR + MOTOR
    # ---------------------------------------------------------
    def guardar_factura(self):
        datos: dict[str, str] = self.form.get_datos()

        ok, resultado = self.validar_datos(datos)
        if not ok:
            QMessageBox.warning(self, "Error", str(resultado))
            return

        assert isinstance(resultado, dict)
        datos = resultado

        # Conversión fechas a ISO para BD
        fec_emision_iso = convertir_a_iso(datos["fec_emision"])
        fec_ini_iso = convertir_a_iso(datos["inicio_factura"])
        fec_fin_iso = convertir_a_iso(datos["fin_factura"])

        # -----------------------------------------------------
        # INSERTAR EN TABLA FACTURAS
        # -----------------------------------------------------
        sql = """
            INSERT INTO facturas
            (ncontrato, suplemento, nfactura,
             fec_emision, inicio_factura, fin_factura, dias_factura,
             consumo_punta, consumo_llano, consumo_valle,
             excedentes, servicios, dcto_servicios,
             saldos_pendientes, bat_virtual)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        self.cursor.execute(
            sql,
            (
                datos["ncontrato"],
                datos["suplemento"],
                datos["nfactura"],
                fec_emision_iso,
                fec_ini_iso,
                fec_fin_iso,
                datos["dias_factura"],
                float(datos["consumo_punta"] or 0),
                float(datos["consumo_llano"] or 0),
                float(datos["consumo_valle"] or 0),
                float(datos["excedentes"] or 0),
                float(datos["servicios"] or 0),
                -float(datos["dcto_servicios"] or 0),  # SIEMPRE NEGATIVO
                -float(datos["saldos_pendientes"] or 0),
                float(datos["bat_virtual"] or 0),
            ),
        )

        self.conn.commit()

        # -----------------------------------------------------
        # MOTOR DE CÁLCULO (calculo.py)
        # -----------------------------------------------------
        datos_base = obtener_datos_factura(self.cursor, datos["nfactura"])

        # 1) Cargos normativos
        cargos_obj = calcular_cargos_para_factura(datos_base)

        # 2) Energía
        energia_obj, datos_base = calcular_energia_para_factura(
            self.cursor, datos["nfactura"], cargos_obj.bono_social
        )

        # 3) Servicios
        servicios_obj = calcular_servicios_para_factura(datos_base)

        # 4) IVA
        iva_obj = calcular_iva_para_factura(
            energia_obj, cargos_obj, servicios_obj, datos_base
        )

        # 5) Saldos pendientes
        total_con_iva = iva_obj.total_con_iva
        saldos_obj, total_con_saldos = calcular_saldos_pendientes(
            datos_base, total_con_iva
        )

        # 6) Cloud
        total_final, aplicado_cloud, nuevo_saldo = calcular_bono_solar_cloud(
            self.cursor,
            datos_base["ncontrato"],
            total_con_saldos,
            energia_obj.sobrante_excedentes,
        )

        # 7) JSON ampliado
        detalles_json = generar_json_calculo(
            energia_obj,
            cargos_obj,
            servicios_obj,
            iva_obj,
            saldos_obj,
            aplicado_cloud,
            nuevo_saldo,
            datos_base,
        )

        # Versión de motor desde tabla version_motor
        from facturas.calculo import VERSION_MOTOR

        version_motor = VERSION_MOTOR

        # 8) Guardar cálculo
        guardar_calculo_factura(
            self.cursor,
            datos["nfactura"],
            version_motor,
            energia_obj,
            cargos_obj,
            servicios_obj,
            iva_obj,
            saldos_obj,
            aplicado_cloud,
            nuevo_saldo,
            detalles_json,
            datos_base,
        )

        self.conn.commit()

        QMessageBox.information(
            self,
            "Factura calculada",
            f"Factura {datos['nfactura']} guardada y calculada correctamente.\n"
            f"Total final: {total_final:.2f} €",
        )

        # -----------------------------------------------------
        # LIMPIEZA DEL FORMULARIO TRAS GUARDAR
        # -----------------------------------------------------
        self.form.limpiar()
        self.form.set_identificacion(self.ncontrato, self.suplemento)

        # Volver a ocultar campos no editables
        self.form.ocultar_campos_no_editables()

        self.btn_otro.setEnabled(True)
        self.btn_guardar.setEnabled(False)

    # ---------------------------------------------------------
    # NUEVA FACTURA (limpia formulario)
    # ---------------------------------------------------------
    def nueva_factura(self):
        self.form.limpiar()
        self.form.set_identificacion(self.ncontrato, self.suplemento)

        # Volver a ocultar campos no editables
        self.form.ocultar_campos_no_editables()

        self.btn_guardar.setEnabled(True)
        self.btn_otro.setEnabled(False)

    # ---------------------------------------------------------
    # Volver al menú principal
    # ---------------------------------------------------------
    def volver_menu(self):
        mw = self.window()
        mw.volver_inicio()
