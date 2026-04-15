# -------------------------------------------------------------#
# Modulo: clonador_facturas_test.py                            #
# Descripción: Clona facturas reales → TEST para simulaciones  #
# Autor: Antonio Morales                                       #
# Fecha: 2026-02-14                                            #
# -------------------------------------------------------------#

from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ClonadorFacturasTest(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conn = parent.conn
        self.cursor = self.conn.cursor()

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Seleccione contrato real a clonar:"))

        # Lista de contratos reales
        self.lista = QListWidget()
        layout.addWidget(self.lista)

        self.cargar_contratos_reales()

        # Botón principal
        btn = QPushButton("Clonar facturas reales")
        btn.clicked.connect(self.clonar)
        layout.addWidget(btn)

        # Botón de salida
        btn_salir = QPushButton("Salir")
        btn_salir.clicked.connect(self.close)
        layout.addWidget(btn_salir)

    # ---------------------------------------------------------
    # Cargar contratos reales
    # ---------------------------------------------------------
    def cargar_contratos_reales(self):

        self.cursor.execute(
            """
            SELECT ncontrato
            FROM contratos_identificacion
                WHERE suplemento = 0
            ORDER BY ncontrato
        """
        )

        for row in self.cursor.fetchall():
            self.lista.addItem(row[0])

    # ---------------------------------------------------------
    # Clonación completa
    # ---------------------------------------------------------
    def clonar(self):
        item = self.lista.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Debe seleccionar un contrato real.")
            return

        # ---------------------------------------------------------
        # LIMPIAR TABLAS TEST ANTES DE CLONAR
        # ---------------------------------------------------------
        self.cursor.execute("DELETE FROM facturas_test")
        self.cursor.execute("DELETE FROM factura_calculos_test")
        self.cursor.execute("DELETE FROM saldo_cloud_test")

        ncontrato_real = item.text()

        # Obtener contrato ficticio
        self.cursor.execute(
            "SELECT ncontrato FROM contratos_identificacion_test LIMIT 1"
        )
        row = self.cursor.fetchone()

        if row is None:
            QMessageBox.warning(self, "Error", "No existe contrato ficticio.")
            return

        ncontrato_test = row[0]

        try:
            # ---------------------------------------------------------
            # 1. Clonar facturas → facturas_test
            # ---------------------------------------------------------
            self.cursor.execute(
                """
                SELECT nfactura, inicio_factura, fin_factura, dias_factura,
                       fec_emision, consumo_punta, consumo_llano, consumo_valle,
                       excedentes, importe_compensado, servicios, dcto_servicios,
                       saldos_pendientes, bat_virtual, recalcular, estado,
                       rectifica_a, suplemento
                FROM facturas
                WHERE ncontrato = ?
                """,
                (ncontrato_real,),
            )

            facturas = self.cursor.fetchall()

            sql_insert_facturas = """
                INSERT INTO facturas_test (
                    nfactura, inicio_factura, fin_factura, dias_factura,
                    fec_emision, consumo_punta, consumo_llano, consumo_valle,
                    excedentes, importe_compensado, servicios, dcto_servicios,
                    saldos_pendientes, bat_virtual, recalcular, estado,
                    rectifica_a, ncontrato, suplemento
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            for f in facturas:
                f = list(f)
                f.insert(
                    17, ncontrato_test
                )  # insertar ncontrato en la posición correcta
                self.cursor.execute(sql_insert_facturas, f)

            # ---------------------------------------------------------
            # 2. Clonar cálculos → factura_calculos_test
            # ---------------------------------------------------------
            self.cursor.execute(
                """
                SELECT nfactura, fecha_calculo, version_motor, total_energia,
                       total_cargos, total_servicios, total_iva,
                       cloud_aplicado, cloud_sobrante, total_final,
                       detalles_json,
                       bono_social, alq_contador, otros_gastos, i_electrico, iva
                FROM factura_calculos
                WHERE nfactura IN (
                    SELECT nfactura FROM facturas WHERE ncontrato = ?
                )
                """,
                (ncontrato_real,),
            )

            calculos = self.cursor.fetchall()

            sql_insert_calculos = """
                INSERT INTO factura_calculos_test (
                    nfactura, fecha_calculo, version_motor, total_energia,
                    total_cargos, total_servicios, total_iva,
                    cloud_aplicado, cloud_sobrante, total_final,
                    detalles_json,
                    bono_social, alq_contador, otros_gastos, i_electrico, iva
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            for c in calculos:
                self.cursor.execute(sql_insert_calculos, c)

            # ---------------------------------------------------------
            # 3. Insertar saldo inicial en saldo_cloud_test
            # ---------------------------------------------------------
            self.cursor.execute(
                "SELECT saldo FROM saldo_cloud WHERE ncontrato = ?",
                (ncontrato_real,),
            )
            row = self.cursor.fetchone()
            saldo_inicial = row[0] if row else 0.0

            self.cursor.execute(
                "INSERT OR REPLACE INTO saldo_cloud_test (ncontrato, saldo) VALUES (?, ?)",
                (ncontrato_test, saldo_inicial),
            )

            self.conn.commit()

            QMessageBox.information(self, "Éxito", "Facturas clonadas correctamente.")

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"No se pudieron clonar los datos:\n{e}"
            )
            self.conn.rollback()
