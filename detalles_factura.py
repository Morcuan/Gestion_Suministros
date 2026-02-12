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
    def __init__(self, conn, id_factura, parent=None):
        super().__init__(parent)

        self.conn = conn
        self.id_factura = id_factura

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
            SELECT *
            FROM factura_identificacion fi
            LEFT JOIN factura_energia fe ON fi.id_factura = fe.id_factura
            LEFT JOIN factura_asociados fa ON fi.id_factura = fa.id_factura
            WHERE fi.id_factura = ?
        """,
            (self.id_factura,),
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
        layout.addWidget(self.bloque_energia_consumida())
        layout.addWidget(self.bloque_cargos_normativos())
        layout.addWidget(self.bloque_servicios())
        layout.addWidget(self.bloque_resto())

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

    # ---------------------------------------------------------
    # BLOQUE IDENTIFICACIÓN
    # ---------------------------------------------------------
    def bloque_identificacion(self):
        grupo = QGroupBox("Identificación de la factura")
        form = QFormLayout()

        d = self.datos

        form.addRow("Número de factura:", QLabel(d[2]))
        form.addRow("Inicio factura:", QLabel(d[3]))
        form.addRow("Fin factura:", QLabel(d[4]))
        form.addRow("Días facturados:", QLabel(str(d[5])))
        form.addRow("Fecha emisión:", QLabel(d[6]))

        grupo.setLayout(form)
        return grupo

    # ---------------------------------------------------------
    # BLOQUE ENERGÍA CONSUMIDA (sin potencia)
    # ---------------------------------------------------------
    def bloque_energia_consumida(self):
        grupo = QGroupBox("Energía consumida")
        form = QFormLayout()

        d = self.datos

        # factura_energia empieza en d[7]
        # d[7] = id_factura (NO se usa)

        form.addRow("Consumo punta (kWh):", QLabel(str(d[11])))
        form.addRow("Importe consumo punta (€):", QLabel(str(d[12])))

        form.addRow("Consumo llano (kWh):", QLabel(str(d[13])))
        form.addRow("Importe consumo llano (€):", QLabel(str(d[14])))

        form.addRow("Consumo valle (kWh):", QLabel(str(d[15])))
        form.addRow("Importe consumo valle (€):", QLabel(str(d[16])))

        form.addRow("Excedentes (kWh):", QLabel(str(d[17])))
        form.addRow("Importe excedentes (€):", QLabel(str(d[18])))

        grupo.setLayout(form)
        return grupo

    # ---------------------------------------------------------
    # BLOQUE 1: CARGOS NORMATIVOS
    # ---------------------------------------------------------
    def bloque_cargos_normativos(self):
        grupo = QGroupBox("Cargos normativos")
        form = QFormLayout()

        d = self.datos

        form.addRow("Bono social:", QLabel(str(d[20])))
        form.addRow("IEE:", QLabel(str(d[21])))

        grupo.setLayout(form)
        return grupo

    # ---------------------------------------------------------
    # BLOQUE 2: SERVICIOS Y OTROS
    # ---------------------------------------------------------
    def bloque_servicios(self):
        grupo = QGroupBox("Servicios y otros")
        form = QFormLayout()

        d = self.datos

        form.addRow("Alquiler equipos:", QLabel(str(d[22])))
        form.addRow("Servicios:", QLabel(str(d[23])))

        grupo.setLayout(form)
        return grupo

    # ---------------------------------------------------------
    # BLOQUE 3: RESTO
    # ---------------------------------------------------------
    def bloque_resto(self):
        grupo = QGroupBox("Resto")
        form = QFormLayout()

        d = self.datos

        form.addRow("IVA:", QLabel(str(d[24])))
        form.addRow("Descuento saldos:", QLabel(str(d[25])))
        form.addRow("Solar cloud:", QLabel(str(d[26])))
        form.addRow("Total factura:", QLabel(str(d[27])))

        grupo.setLayout(form)
        return grupo

    # ---------------------------------------------------------
    # ACCIONES
    # ---------------------------------------------------------
    def totalizar_factura(self):
        # Pendiente de implementar
        pass

    def volver_lista_facturas(self):
        from consulta_facturas import ConsultaFacturasWidget

        d = self.datos
        id_contrato = d[1]  # segundo campo del SELECT *

        marco = self.window()
        vista = ConsultaFacturasWidget(self.conn, id_contrato, parent=marco)
        marco.cargar_modulo(vista, "Facturas del contrato")
