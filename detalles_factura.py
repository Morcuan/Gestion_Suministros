# --------------------------------------    ------#
# Modulo: detalles_factura.py                     #
# Descripción: Detalles de factura (solo lectura) #
# Autor: Antonio Morales                          #
# Fecha: 2026-02-09                               #
# ----------------------------------    ----------#
# Esta vista muestra los detalles de una factura seleccionada, con datos cargados desde la base de datos.
# Permite analizar la factura con un cálculo completo y ver el desglose detallado.

# ---------------------------------------------------------
# IMPORTACIONES
# ---------------------------------------------------------

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# ---------------------------------------------------------
# CLASE PRINCIPAL
# ---------------------------------------------------------


class DetallesFactura(QWidget):
    # init recibe conexión, id_contrato y nfactura para cargar datos
    def __init__(self, conn, id_contrato, nfactura, parent=None):
        super().__init__(parent)

        self.conn = conn
        self.id_contrato = id_contrato
        self.nfactura = nfactura

        # Cargar datos desde la BD
        self.datos = self.cargar_datos_factura()

        # Construir interfaz
        self.init_ui()

    # ---------------------------------------------------------
    # CARGA DE DATOS
    # ---------------------------------------------------------
    # Carga los datos de la factura desde la base de datos y los devuelve como tupla
    def cargar_datos_factura(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT
                id_contrato,        -- 0
                nfactura,           -- 1
                inicio_factura,     -- 2
                fin_factura,        -- 3
                dias_factura,       -- 4
                fec_emision,        -- 5
                consumo_punta,      -- 6
                consumo_llano,      -- 7
                consumo_valle,      -- 8
                excedentes,         -- 9
                importe_compensado, -- 10  NUEVO
                servicios,          -- 11
                dcto_servicios,     -- 12
                saldos_pendientes,  -- 13
                bat_virtual         -- 14
            FROM facturas
            WHERE id_contrato = ? AND nfactura = ?
            """,
            (self.id_contrato, self.nfactura),
        )

        return cursor.fetchone()

    # ---------------------------------------------------------
    # INTERFAZ
    # ---------------------------------------------------------
    # Construye la interfaz con los datos cargados y los botones de acción
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        layout.addWidget(self.bloque_identificacion())
        layout.addWidget(self.bloque_energia())
        layout.addWidget(self.bloque_gastos())

        # Botones inferiores
        botones = QHBoxLayout()
        botones.setContentsMargins(0, 20, 0, 0)

        btn_totalizar = QPushButton("Analizar factura")
        btn_totalizar.clicked.connect(self.totalizar_factura)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.volver_lista_facturas)

        botones.addWidget(btn_totalizar)
        botones.addStretch()
        botones.addWidget(btn_cerrar)

        layout.addLayout(botones)

        self.setLayout(layout)

    # bloque energía muestra consumo punta, llano, valle, excedentes e importe compensado
    def bloque_energia(self):
        grupo = QGroupBox("Energía")
        form = QFormLayout()

        d = self.datos

        form.addRow("Consumo punta (kWh):", QLabel(str(d[6])))
        form.addRow("Consumo llano (kWh):", QLabel(str(d[7])))
        form.addRow("Consumo valle (kWh):", QLabel(str(d[8])))
        form.addRow("Excedentes (kWh):", QLabel(str(d[9])))
        form.addRow("Importe compensado (€):", QLabel(str(d[10])))

        grupo.setLayout(form)
        return grupo

    # bloque gastos muestra servicios, descuentos, saldos pendientes y batería virtual
    def bloque_gastos(self):
        grupo = QGroupBox("Gastos y descuentos")
        form = QFormLayout()

        d = self.datos

        form.addRow("Servicios asociados (€):", QLabel(str(d[11])))
        form.addRow("Dctos. servicios (€):", QLabel(str(d[12])))
        form.addRow("Saldos pendientes (€):", QLabel(str(d[13])))
        form.addRow("Batería virtual (€):", QLabel(str(d[14])))

        grupo.setLayout(form)
        return grupo

    # ---------------------------------------------------------
    # BLOQUE IDENTIFICACIÓN
    # ---------------------------------------------------------
    # bloque identificación muestra número de factura, periodo facturado, días y
    # fecha de emisión
    def bloque_identificacion(self):
        grupo = QGroupBox("Identificación")
        form = QFormLayout()

        d = self.datos

        form.addRow("Número de factura:", QLabel(str(d[1])))
        form.addRow("Inicio factura:", QLabel(str(d[2])))
        form.addRow("Fin factura:", QLabel(str(d[3])))
        form.addRow("Días facturados:", QLabel(str(d[4])))
        form.addRow("Fecha emisión:", QLabel(str(d[5])))

        grupo.setLayout(form)
        return grupo

    # -------------------------------------------------
    # ACCIONES
    # -------------------------------------------------
    # totalizar_factura realiza el cálculo completo de la factura, muestra el resultado
    # y guarda el cálculo en la base de datos para futuras consultas
    def totalizar_factura(self):

        nfactura = self.nfactura
        if not nfactura:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(
                self, "Sin selección", "No hay ninguna factura seleccionada."
            )
            return

        cursor = self.conn.cursor()

        try:
            import json

            from calculo import (
                calcular_bono_solar_cloud,
                calcular_cargos_para_factura,
                calcular_energia_para_factura,
                calcular_iva_para_factura,
                calcular_servicios_para_factura,
                generar_json_calculo,
                guardar_calculo_factura,
                obtener_datos_factura,
            )
            from ventana_detalle_json import VentanaDetalleJSON

            # ---------------------------------------------------------
            # 0) Comprobar si la factura ya está calculada
            # ---------------------------------------------------------
            cursor.execute(
                """
                SELECT total_final, detalles_json
                FROM factura_calculos
                WHERE id_factura = ?
            """,
                (self.nfactura,),
            )
            row = cursor.fetchone()

            if row:
                total_guardado = row[0]
                detalles_json = row[1]

                # Abrir directamente la ventana de análisis detallado
                detalles_dict = json.loads(detalles_json)

                marco = self.window()  # MainWindow
                vista = VentanaDetalleJSON(
                    self.conn,
                    self.id_contrato,
                    self.nfactura,
                    detalles_dict,
                    parent=marco,
                )
                marco.cargar_modulo(vista, "Análisis de factura")

                return

            # ---------------------------------------------------------
            # 1) Cargar datos base desde la vista
            # ---------------------------------------------------------
            datos_base = obtener_datos_factura(cursor, nfactura)

            # ---------------------------------------------------------
            # 2) Calcular CARGOS (bono social)
            # ---------------------------------------------------------
            cargos_obj = calcular_cargos_para_factura(datos_base)
            bono_social = cargos_obj.bono_social

            # ---------------------------------------------------------
            # 3) Calcular ENERGÍA pasando el bono social
            # ---------------------------------------------------------
            energia_obj, datos = calcular_energia_para_factura(
                cursor, nfactura, bono_social
            )

            # ---------------------------------------------------------
            # 4) Calcular SERVICIOS Y OTROS
            # ---------------------------------------------------------
            servicios_obj = calcular_servicios_para_factura(datos_base)

            # ---------------------------------------------------------
            # 5) Calcular IVA (BLOQUE 4)
            # ---------------------------------------------------------
            iva_obj = calcular_iva_para_factura(
                energia_obj.total_energia,
                cargos_obj.total_cargos,
                servicios_obj.total_servicios_otros,
            )

            # ---------------------------------------------------------
            # 6) TOTAL FACTURA
            # ---------------------------------------------------------
            total_factura = iva_obj.total_con_iva

            # ---------------------------------------------------------
            # 6) Aplicar Bono Solar Cloud
            # ---------------------------------------------------------
            sobrante = energia_obj.sobrante_excedentes

            total_final, aplicado_cloud, nuevo_saldo = calcular_bono_solar_cloud(
                cursor, self.id_contrato, iva_obj.total_con_iva, sobrante
            )

            # ---------------------------------------------------------
            # 7) Generar JSON del cálculo
            # ---------------------------------------------------------
            detalles_json = generar_json_calculo(
                energia_obj,
                cargos_obj,
                servicios_obj,
                iva_obj,
                aplicado_cloud,
                nuevo_saldo,
                datos_base,
            )

            # ---------------------------------------------------------
            # 8) Guardar cálculo en la tabla factura_calculos
            # ---------------------------------------------------------
            guardar_calculo_factura(
                cursor,
                self.nfactura,
                "1.0",
                energia_obj,
                cargos_obj,
                servicios_obj,
                iva_obj,
                aplicado_cloud,
                nuevo_saldo,
                detalles_json,
            )

            self.conn.commit()

            # ---------------------------------------------------------
            # 9) Abrir ventana de análisis detallado
            # ---------------------------------------------------------
            detalles_dict = json.loads(detalles_json)

            from ventana_detalle_json import VentanaDetalleJSON

            marco = self.window()  # MainWindow
            vista = VentanaDetalleJSON(
                self.conn,
                self.id_contrato,
                self.nfactura,
                detalles_dict,
                parent=marco,
            )
            marco.cargar_modulo(vista, "Análisis de factura")

            return

        except Exception as e:
            print(f"[ERROR] Fallo en el cálculo: {e}")
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.critical(
                self,
                "Error en cálculo",
                f"Se produjo un error durante el cálculo:\n{e}",
            )
            return

    # volver_lista_facturas cierra esta vista y vuelve a la lista de facturas del contrato
    def volver_lista_facturas(self):
        from consulta_facturas import ConsultaFacturasWidget

        marco = self.window()
        vista = ConsultaFacturasWidget(self.conn, self.id_contrato, parent=marco)
        marco.cargar_modulo(vista, "Facturas del contrato")
        marco.cargar_modulo(vista, "Facturas del contrato")
