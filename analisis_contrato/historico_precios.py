#-------------------------------------------------------------
# Módulo: historico_precios.py
# Descripción: Evolución histórica de precios de un contrato
# -------------------------------------------------------------

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


#==========================================================
#CONSULTAS
#==========================================================
def obtener_suplementos(conn, ncontrato):
    cur = conn.cursor()
    sql = """SELECT
        ncontrato,
        compania,
        codigo_postal,
        fec_inicio,
        fec_final,
        suplemento,
        efec_suple,
        pv_ppunta,
        pv_pvalle,
        pv_conpunta,
        pv_conllano,
        pv_convalle
    FROM vista_contratos
    WHERE ncontrato = ?
    ORDER BY suplemento"""
    cur.execute(sql, (ncontrato,))
    filas = cur.fetchall()
    return [dict(fila) for fila in filas]

#==========================================================
#CALCULOS
#==========================================================
def calcular_evolucion(registros, campo):
    if not registros:
        return []
    resultado = []
    valor_base = registros[0][campo]
    valor_anterior = None
    for fila in registros:
        valor_actual = fila[campo]
        if valor_anterior is None:
            dif_sup0 = None
            pct_sup0 = None
            dif_ant = None
            pct_ant = None
        else:
            dif_sup0 = valor_actual - valor_base
            pct_sup0 = ((dif_sup0 / valor_base) * 100 if valor_base else 0)
            dif_ant = valor_actual - valor_anterior
            pct_ant = ((dif_ant / valor_anterior) * 100 if valor_anterior else 0)
        resultado.append({
            "suplemento": fila["suplemento"],
            "fecha": fila["efec_suple"],
            "precio": valor_actual,
            "dif_sup0": dif_sup0,
            "pct_sup0": pct_sup0,
            "dif_ant": dif_ant,
            "pct_ant": pct_ant,
        })
        valor_anterior = valor_actual
    return resultado

def calcular_resumen(registros, campo):
    if not registros:
        return None
    valores = [fila[campo] for fila in registros]
    inicial = valores[0]
    actual = valores[-1]
    variacion = (((actual - inicial) / inicial) * 100 if inicial else 0)
    return {
        "precio_inicial": inicial,
        "precio_actual": actual,
        "variacion_acumulada": variacion,
        "precio_minimo": min(valores),
        "precio_maximo": max(valores),
    }

#==========================================================
#FORMATEO
#==========================================================
def fmt_num(valor, decimales=6):
    if valor is None:
        return "---"
    return f"{valor:.{decimales}f}"

def fmt_pct(valor):
    if valor is None:
        return "---"
    return f"{valor:+.2f} %"

#==========================================================
#CLASE PRINCIPAL
#==========================================================
class HistoricoPrecios(QWidget):
    BLOQUES = [
        ("POTENCIA PUNTA", "pv_ppunta"),
        ("POTENCIA VALLE", "pv_pvalle"),
        ("CONSUMO PUNTA", "pv_conpunta"),
        ("CONSUMO LLANO", "pv_conllano"),
        ("CONSUMO VALLE", "pv_convalle"),
    ]

    def __init__(self, parent=None, conn=None, ncontrato=None):
        super().__init__(parent)
        self.parent = parent
        self.conn = conn
        self.ncontrato = ncontrato
        self.datos = obtener_suplementos(self.conn, self.ncontrato)

        # Layout principal del widget
        self.layout_principal = QVBoxLayout(self)

        if not self.datos:
            self.layout_principal.addWidget(QLabel("Contrato sin datos."))
            return

        # Mostrar la vista general de resúmenes por defecto
        self.mostrar_vista_general()

    def limpiar_layout(self):
        """Elimina todos los widgets del layout principal para cambiar de vista."""
        while self.layout_principal.count():
            item = self.layout_principal.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def mostrar_vista_general(self):
        """Muestra la cabecera administrativa y la lista de resúmenes con el botón Detalles."""
        self.limpiar_layout()

        primero = self.datos[0]
        titulo = QLabel("EVOLUCIÓN HISTÓRICA DE PRECIOS")
        titulo.setStyleSheet("font-size:18px; font-weight:bold;")
        titulo.setAlignment(Qt.AlignCenter)
        self.layout_principal.addWidget(titulo)

        cabecera = QLabel(f"""<b>COMPAÑÍA:</b> {primero['compania']}<br>
            <b>C.P.:</b> {primero['codigo_postal']} &nbsp;&nbsp;&nbsp;
            <b>EFECTO:</b> {primero['fec_inicio']} &nbsp;&nbsp;&nbsp;
            <b>FIN:</b> {primero['fec_final']} &nbsp;&nbsp;&nbsp;
            <b>SUPLEMENTOS:</b> {len(self.datos)}""")
        self.layout_principal.addWidget(cabecera)

        # Contenedor con scroll para los bloques resumen
        contenedor_scroll = QWidget()
        layout_scroll = QVBoxLayout(contenedor_scroll)

        for titulo_bloque, campo in self.BLOQUES:
            self.crear_bloque_resumen(layout_scroll, titulo_bloque, campo)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(contenedor_scroll)
        self.layout_principal.addWidget(scroll_area)

        # Botones inferiores generales (Imprimir, PDF, Salir)
        botones = QHBoxLayout()
        botones.addStretch()

        #btn_print = QPushButton("Imprimir")
        #btn_print.clicked.connect(self.imprimir)

        #btn_pdf = QPushButton("PDF")
        #btn_pdf.clicked.connect(self.exportar_pdf)

        btn_salir = QPushButton("Salir")
        btn_salir.clicked.connect(self.salir)

        #botones.addWidget(btn_print)
        #botones.addWidget(btn_pdf)
        botones.addWidget(btn_salir)

        self.layout_principal.addLayout(botones)

    def crear_bloque_resumen(self, layout_principal, titulo, campo):
        """Crea el bloque de resumen con el título arriba y los datos/botón abajo."""
        # Layout vertical para estructurar el bloque en dos alturas
        layout_bloque = QVBoxLayout()
        layout_bloque.setContentsMargins(0, 8, 0, 12) # Margen superior e inferior para separar bloques

        # 1. LÍNEA SUPERIOR: Título del bloque
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size:14px; font-weight:bold; color: #2C3E50;")
        layout_bloque.addWidget(lbl_titulo)

        # 2. LÍNEA INFERIOR: Horizontales (Datos y Botón Detalles)
        layout_fila = QHBoxLayout()

        resumen = calcular_resumen(self.datos, campo)
        lbl_resumen = QLabel(
            f"<b>Inicial:</b> {fmt_num(resumen['precio_inicial'])} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Final:</b> {fmt_num(resumen['precio_actual'])} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Var.:</b> {fmt_pct(resumen['variacion_acumulada'])} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Mín.:</b> {fmt_num(resumen['precio_minimo'])} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Máx.:</b> {fmt_num(resumen['precio_maximo'])}"
        )
        layout_fila.addWidget(lbl_resumen)
        layout_fila.addStretch()

        btn_detalles = QPushButton("Detalles")
        # Usamos lambda para capturar el campo y el título específicos de este bloque
        btn_detalles.clicked.connect(lambda: self.mostrar_vista_detalles(titulo, campo))
        layout_fila.addWidget(btn_detalles)

        # Añadimos la fila horizontal al layout vertical del bloque
        layout_bloque.addLayout(layout_fila)

        # Añadimos el bloque completo al contenedor principal
        layout_principal.addLayout(layout_bloque)
    def mostrar_vista_detalles(self, titulo_bloque, campo):
        """Muestra la tabla detallada del bloque seleccionado dentro de la zona de trabajo."""
        self.limpiar_layout()

        # Título de la sección de detalles
        titulo = QLabel(f"DETALLES - {titulo_bloque}")
        titulo.setStyleSheet("font-size:18px; font-weight:bold;")
        titulo.setAlignment(Qt.AlignCenter)
        self.layout_principal.addWidget(titulo)

        # Creación de la tabla
        tabla = QTableWidget()
        tabla.setColumnCount(7)
        tabla.setHorizontalHeaderLabels([
            "SUP", "EFECTO", "PRECIO", "DIF SUP0", "% SUP0", "DIF ANT", "% ANT"
        ])
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        evolucion = calcular_evolucion(self.datos, campo)
        tabla.setRowCount(len(evolucion))

        for fila, registro in enumerate(evolucion):
            valores = [
                registro["suplemento"],
                registro["fecha"],
                fmt_num(registro["precio"]),
                fmt_num(registro["dif_sup0"]),
                fmt_pct(registro["pct_sup0"]),
                fmt_num(registro["dif_ant"]),
                fmt_pct(registro["pct_ant"]),
            ]
            for col, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                tabla.setItem(fila, col, item)

        tabla.resizeRowsToContents()
        self.layout_principal.addWidget(tabla)

        # Botón de Cerrar para volver a la pantalla de resúmenes
        botones = QHBoxLayout()
        botones.addStretch()

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.mostrar_vista_general)
        botones.addWidget(btn_cerrar)

        self.layout_principal.addLayout(botones)

    # ------------------------------------------------------
    def imprimir(self):
        QMessageBox.information(self, "Pendiente", "Función de impresión pendiente de implementar.")

    # ------------------------------------------------------
    def exportar_pdf(self):
        QMessageBox.information(self, "Pendiente", "Exportación a PDF pendiente de implementar.")

    # ------------------------------------------------------
    def salir(self):
        from analisis_contrato.lista_contratos_precios import ListaContratosPrecios
        mw = self.window()
        widget = ListaContratosPrecios(parent=mw)
        mw.cargar_modulo(widget, "Evolución histórica de precios")
