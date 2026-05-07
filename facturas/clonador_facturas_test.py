# -------------------------------------------------------------#
# Modulo: clonador_facturas_test.py                            #
# Descripción: Clona facturas reales → TEST para simulaciones  #
#          usando condiciones económicas del contrato TEST     #
# Autor: Antonio Morales                                       #
# Fecha: 2026-02-14 (revisado y corregido)                     #
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

        layout.addWidget(QLabel("Seleccione contrato REAL a clonar:"))

        # Lista de contratos reales
        self.lista = QListWidget()
        layout.addWidget(self.lista)

        self.cargar_contratos_reales()

        # Botón principal
        btn = QPushButton("Clonar facturas reales → TEST")
        btn.clicked.connect(self.clonar)
        layout.addWidget(btn)

        # Botón de salida
        btn_salir = QPushButton("Salir")
        btn_salir.clicked.connect(self.close)
        layout.addWidget(btn_salir)

    # ---------------------------------------------------------
    # Cargar contratos reales (solo suplemento 0)
    # ---------------------------------------------------------
    def cargar_contratos_reales(self):

        self.cursor.execute("""
            SELECT ncontrato
            FROM contratos_identificacion
            WHERE suplemento = 0
            ORDER BY ncontrato
        """)

        for row in self.cursor.fetchall():
            self.lista.addItem(row[0])

    # ---------------------------------------------------------
    # Clonación completa
    # ---------------------------------------------------------
    def clonar(self):
        item = self.lista.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Debe seleccionar un contrato REAL.")
            return

        ncontrato_real = item.text()

        # Obtener contrato ficticio (TEST)
        self.cursor.execute(
            "SELECT ncontrato FROM contratos_identificacion_test LIMIT 1"
        )
        row = self.cursor.fetchone()

        if row is None:
            QMessageBox.warning(
                self,
                "Error",
                "No existe contrato ficticio en contratos_identificacion_test.",
            )
            return

        ncontrato_test = row[0]

        try:
            # ---------------------------------------------------------
            # 1. Clonar facturas → facturas_test
            #    Suplemento TEST = 0 SIEMPRE
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
                (
                    nfactura,
                    inicio_factura,
                    fin_factura,
                    dias_factura,
                    fec_emision,
                    consumo_punta,
                    consumo_llano,
                    consumo_valle,
                    excedentes,
                    importe_compensado,
                    servicios,
                    dcto_servicios,
                    saldos_pendientes,
                    bat_virtual,
                    recalcular,
                    estado,
                    rectifica_a,
                    suplemento_real,  # ignorado
                ) = f

                # Suplemento TEST siempre = 0
                suplemento_test = 0

                valores_insert = [
                    nfactura,
                    inicio_factura,
                    fin_factura,
                    dias_factura,
                    fec_emision,
                    consumo_punta,
                    consumo_llano,
                    consumo_valle,
                    excedentes,
                    importe_compensado,
                    servicios,
                    dcto_servicios,
                    saldos_pendientes,
                    bat_virtual,
                    recalcular,
                    estado,
                    rectifica_a,
                    str(ncontrato_test),  # ← CORRECCIÓN CRÍTICA
                    suplemento_test,
                ]

                self.cursor.execute(sql_insert_facturas, valores_insert)

            # ---------------------------------------------------------
            # 2. NO clonar cálculos → factura_calculos_test
            #    Se rellenará solo con los cálculos de la oferta analizada
            # ---------------------------------------------------------
            # (Intencionadamente vacío)

            # ---------------------------------------------------------
            # 3. Insertar saldo inicial en saldo_cloud_test
            # ---------------------------------------------------------

            self.cursor.execute("""
                SELECT saldo_inicial
                FROM saldo_cloud_inicial_test
                ORDER BY id
                LIMIT 1
            """)
            row = self.cursor.fetchone()
            saldo_inicial = row[0] if row else 0.0

            self.cursor.execute(
                """
                INSERT OR REPLACE INTO saldo_cloud_test (ncontrato, saldo)
                VALUES (?, ?)
                """,
                (str(ncontrato_test), saldo_inicial),
            )

            self.conn.commit()

            QMessageBox.information(
                self,
                "Éxito",
                "Facturas clonadas correctamente.\n"
                "• facturas_test con suplemento TEST = 0\n"
                "• factura_calculos_test vacía para nuevos cálculos\n"
                "• saldo_cloud_test inicializado desde saldo_cloud_inicial_test",
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"No se pudieron clonar los datos:\n{e}"
            )
            self.conn.rollback()
