# --------------------------------------------#
# Modulo: ventana_detalle_json.py             #
# Descripción: Ventana de detalle de cálculo  #
# Autor: Antonio Morales                      #
# Fecha: 2026-02-09 (revisado flujo DRU)      #
# --------------------------------------------#
# Esta ventana muestra el análisis detallado de la factura,
# con TODOS los bloques de cálculo en texto plano,
# con títulos en negrita y líneas separadoras.


# ---------------------------------------------------------
# IMPORTACIONES
# ---------------------------------------------------------
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QTextEdit, QVBoxLayout, QWidget


# ---------------------------------------------------------
# CLASE PRINCIPAL
# ---------------------------------------------------------
class VentanaDetalleJSON(QWidget):
    """
    Ventana de análisis detallado de la factura.
    Muestra TODOS los bloques de cálculo en texto plano,
    con títulos en negrita y líneas separadoras.
    """

    # ---------------------------------------------------------
    # INICIALIZACIÓN
    # ---------------------------------------------------------
    def __init__(self, conn, id_contrato, nfactura, detalles_dict, parent=None):
        super().__init__(parent)

        self.conn = conn
        self.id_contrato = id_contrato
        self.nfactura = nfactura
        self.detalles = detalles_dict

        self.init_ui()

    # ---------------------------------------------------------
    # INTERFAZ GRÁFICA
    # ---------------------------------------------------------
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Texto de detalles
        self.texto = QTextEdit()
        self.texto.setReadOnly(True)
        self.texto.setAcceptRichText(True)
        self.texto.setStyleSheet("font-size: 16px;")

        contenido = self.generar_texto_detalle()
        self.texto.setHtml(contenido)

        layout.addWidget(self.texto)

        # Botón Cerrar
        botones = QHBoxLayout()
        botones.addStretch()

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.cerrar_y_volver_detalle_factura)

        botones.addWidget(btn_cerrar)
        layout.addLayout(botones)

        self.setLayout(layout)

    # ---------------------------------------------------------
    # GENERACIÓN DEL TEXTO
    # ---------------------------------------------------------
    def generar_texto_detalle(self) -> str:
        """
        Genera el texto HTML simple con títulos en negrita y
        líneas separadoras para todos los bloques del cálculo.
        Se asume que self.detalles es el dict devuelto por generar_json_calculo.
        """

        partes = []

        # Helper para separadores
        def sep():
            partes.append("----------------------------------------<br>")

        # POTENCIA / ENERGÍA / EXCEDENTES

        # ---------------------------------------------------------
        # POTENCIA
        # ---------------------------------------------------------
        pot = self.detalles.get("potencia", {})
        if pot:
            sep()
            partes.append("<b>POTENCIA</b><br>")
            sep()

            periodos = pot.get("periodos", {})
            for periodo, datos in periodos.items():
                kW = datos.get("kW", "")
                precio = datos.get("precio_unitario", "")
                importe = datos.get("importe", "")
                partes.append(
                    f"&nbsp;&nbsp;{periodo} → "
                    f"kW: {kW} | Pvp kW: {precio} | Importe: {importe}<br>"
                )

            if "total" in pot:
                partes.append(f"Total potencia: {pot.get('total', '')}<br>")

        # ---------------------------------------------------------
        # CONSUMO
        # ---------------------------------------------------------
        con = self.detalles.get("consumo", {})
        if con:
            sep()
            partes.append("<b>CONSUMO</b><br>")
            sep()

            periodos = con.get("periodos", {})
            for periodo, datos in periodos.items():
                kWh = datos.get("kWh", "")
                precio = datos.get("precio_unitario", "")
                importe = datos.get("importe", "")
                partes.append(
                    f"&nbsp;&nbsp;{periodo} → "
                    f"kWh: {kWh} | Pvp kWh: {precio} | Importe: {importe}<br>"
                )

            if "total" in con:
                partes.append(f"Total consumo: {con.get('total', '')}<br>")

        # ---------------------------------------------------------
        # EXCEDENTES
        # ---------------------------------------------------------
        exc = self.detalles.get("excedentes", {})
        if exc:
            sep()
            partes.append("<b>EXCEDENTES</b><br>")
            sep()

            for k, v in exc.items():
                etiqueta = "A Bat. Virtual" if k == "sobrante" else k
                partes.append(f"{etiqueta}: {v}<br>")

        # CARGOS NORMATIVOS
        cargos = self.detalles.get("cargos", {})
        if cargos:
            sep()
            partes.append("<b>CARGOS NORMATIVOS</b><br>")
            sep()
            for k, v in cargos.items():
                partes.append(f"{k}: {v}<br>")

        # SERVICIOS Y OTROS
        servicios = self.detalles.get("servicios", {})
        if servicios:
            sep()
            partes.append("<b>SERVICIOS Y OTROS</b><br>")
            sep()
            for k, v in servicios.items():
                partes.append(f"{k}: {v}<br>")

        # IVA
        iva = self.detalles.get("iva", {})
        if iva:
            sep()
            partes.append("<b>IVA</b><br>")
            sep()
            for k, v in iva.items():
                partes.append(f"{k}: {v}<br>")

        # BONO SOLAR CLOUD / APLICADO CLOUD
        cloud = self.detalles.get("bono_solar_cloud", {})
        if not cloud:
            # según cómo lo guardes, puede que venga como 'aplicado_cloud' o similar
            cloud = self.detalles.get("aplicado_cloud", {})

        if cloud:
            sep()
            partes.append("<b>BONO SOLAR CLOUD</b><br>")
            sep()
            for k, v in cloud.items():
                partes.append(f"{etiqueta}: {v}<br>")

        # TOTAL FINAL
        total_final = self.detalles.get("total_final", None)
        if total_final is not None:
            sep()
            partes.append("<b>TOTAL FINAL</b><br>")
            sep()
            partes.append(f"Total factura: {total_final}<br>")

        # Por si quieres incluir algún bloque extra del JSON:
        otros = self.detalles.get("otros", {})
        if otros:
            sep()
            partes.append("<b>OTROS</b><br>")
            sep()
            for k, v in otros.items():
                partes.append(f"{k}: {v}<br>")

        return "".join(partes) if partes else "No hay detalles de cálculo disponibles."

    # ---------------------------------------------------------
    # NAVEGACIÓN
    # ---------------------------------------------------------
    def cerrar_y_volver_detalle_factura(self):
        """
        Cierra esta ventana y vuelve a DetallesFactura,
        siguiendo el flujo lineal definido en el DRU.
        """
        from detalles_factura import DetallesFactura

        marco = self.window()  # MainWindow
        vista = DetallesFactura(
            self.conn, self.id_contrato, self.nfactura, parent=marco
        )
        marco.cargar_modulo(vista, "Detalles de factura")
        marco.cargar_modulo(vista, "Detalles de factura")
        marco.cargar_modulo(vista, "Detalles de factura")
