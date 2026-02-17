# detalles_factura.py
# Ventana de detalles de factura (modo solo lectura)
# Proyecto: Gestion_suministros / Consultas

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class DetallesFactura(QWidget):
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

        btn_totalizar = QPushButton("Totalizar factura")
        btn_totalizar.clicked.connect(self.totalizar_factura)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.volver_lista_facturas)

        botones.addWidget(btn_totalizar)
        botones.addStretch()
        botones.addWidget(btn_cerrar)

        layout.addLayout(botones)

        self.setLayout(layout)

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

    # ---------------------------------------------------------
    # ACCIONES
    # ---------------------------------------------------------

    def totalizar_factura(self):

        nfactura = self.nfactura
        if not nfactura:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(
                self, "Sin selección", "No hay ninguna factura seleccionada."
            )
            return

        print(f"\n=== TOTALIZANDO FACTURA {nfactura} ===")

        cursor = self.conn.cursor()

        try:
            from calculo import (
                calcular_bono_solar_cloud,
                calcular_cargos_para_factura,
                calcular_energia_para_factura,
                calcular_iva_para_factura,
                calcular_servicios_para_factura,
                obtener_datos_factura,
            )

            # ---------------------------------------------------------
            # 1) Cargar datos base desde la vista
            # ---------------------------------------------------------
            datos_base = obtener_datos_factura(cursor, nfactura)

            # ---------------------------------------------------------
            # 2) Calcular CARGOS (bono social)
            # ---------------------------------------------------------
            cargos_obj = calcular_cargos_para_factura(datos_base)
            bono_social = cargos_obj.bono_social

            print(
                f"\n>>> TOTAL BLOQUE CARGOS PARA {nfactura}: "
                f"{cargos_obj.total_cargos:.2f} €"
            )

            # ---------------------------------------------------------
            # 3) Calcular ENERGÍA pasando el bono social
            # ---------------------------------------------------------
            energia_obj, datos = calcular_energia_para_factura(
                cursor, nfactura, bono_social
            )

            print(
                f"\n>>> TOTAL BLOQUE ENERGÍA PARA {nfactura}: "
                f"{energia_obj.total_energia:.2f} €"
            )

            # ---------------------------------------------------------
            # 4) Calcular SERVICIOS Y OTROS
            # ---------------------------------------------------------
            servicios_obj = calcular_servicios_para_factura(datos_base)

            print(
                f"\n>>> TOTAL BLOQUE SERVICIOS Y OTROS PARA {nfactura}: "
                f"{servicios_obj.total_servicios_otros:.2f} €"
            )

            # ---------------------------------------------------------
            # 5) Calcular IVA (BLOQUE 4)
            # ---------------------------------------------------------
            iva_obj = calcular_iva_para_factura(
                energia_obj.total_energia,
                cargos_obj.total_cargos,
                servicios_obj.total_servicios_otros,
            )

            print(f"\n>>> TOTAL BLOQUE IVA PARA {nfactura}: {iva_obj.cuota_iva:.2f} €")

            # ---------------------------------------------------------
            # 6) TOTAL FACTURA
            # ---------------------------------------------------------
            total_factura = iva_obj.total_con_iva

            print(f"\n===== TOTAL FACTURA {nfactura}: {total_factura:.2f} € =====\n")

            # ---------------------------------------------------------
            # 6) Aplicar Bono Solar Cloud
            # ---------------------------------------------------------
            sobrante = energia_obj.sobrante_excedentes

            total_final, aplicado_cloud, nuevo_saldo = calcular_bono_solar_cloud(
                cursor, self.id_contrato, iva_obj.total_con_iva, sobrante
            )

            print(
                f"\n>>> TOTAL FACTURA TRAS CLOUD PARA {nfactura}: {total_final:.2f} €"
            )

        except Exception as e:
            print(f"[ERROR] Fallo en el cálculo: {e}")
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.critical(
                self,
                "Error en cálculo",
                f"Se produjo un error durante el cálculo:\n{e}",
            )
            return

    def volver_lista_facturas(self):
        from consulta_facturas import ConsultaFacturasWidget

        marco = self.window()
        vista = ConsultaFacturasWidget(self.conn, self.id_contrato, parent=marco)
        marco.cargar_modulo(vista, "Facturas del contrato")
