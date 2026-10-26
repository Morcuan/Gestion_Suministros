#-------------------------------------------------------------
# Módulo: historico_precios.py
# Descripción: Evolución histórica de precios de un contrato
# -------------------------------------------------------------

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
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
# CONSULTAS
#==========================================================

def obtener_suplementos(conn, ncontrato):
    cur = conn.cursor()
    sql = """
        SELECT ncontrato, compania, codigo_postal, fec_inicio, fec_final,
               suplemento, efec_suple, pv_ppunta, pv_pvalle, pv_conpunta,
               pv_conllano, pv_convalle
        FROM vista_contratos
        WHERE ncontrato = ?
        ORDER BY suplemento
    """
    cur.execute(sql, (ncontrato,))
    filas = cur.fetchall()
    return [dict(fila) for fila in filas]

#==========================================================
# CALCULOS
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
# FORMATEO Y ESTILOS AUXILIARES
#==========================================================

def fmt_num(valor, decimales=6):
    if valor is None:
        return "---"
    return f"{valor:.{decimales}f}"

def fmt_pct(valor):
    if valor is None:
        return "---"
    return f"{valor:+.2f} %"

def obtener_color_por_valor(valor):
    """
    Devuelve estilo CSS para etiquetas HTML según el valor:
    - Negativo (< 0): Verde (#27AE60) y negrita
    - Entre 0 y 10 (0 < valor <= 10): Naranja (#D35400) y negrita (cubre el rango 5-10 visto en pantallas)
    - Mayor que 10 (> 10): Rojo (#C0392B) y negrita
    - Cero (= 0): Sin color especial
    """
    if valor is None:
        return ""
    if valor < 0:
        return "color: #27AE60; font-weight: bold;"
    elif 0 < valor <= 10:
        return "color: #D35400; font-weight: bold;"
    elif valor > 10:
        return "color: #C0392B; font-weight: bold;"
    return ""

def obtener_qcolor_por_valor(valor):
    """
    Devuelve un QColor para las celdas de QTableWidget de forma equivalente:
    - Negativo (< 0): Verde
    - Entre 0 y 10 (0 < valor <= 10): Naranja
    - Mayor que 10 (> 10): Rojo
    """
    if valor is None:
        return None
    if valor < 0:
        return QColor("#27AE60")
    elif 0 < valor <= 10:
        return QColor("#D35400")
    elif valor > 10:
        return QColor("#C0392B")
    return None

#==========================================================
# CLASE PRINCIPAL
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

        self.layout_principal = QVBoxLayout(self)

        if not self.datos:
            self.layout_principal.addWidget(QLabel("Contrato sin datos."))
            return

        self.mostrar_vista_general()

    def limpiar_layout(self):
        while self.layout_principal.count():
            item = self.layout_principal.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def mostrar_vista_general(self):
        self.limpiar_layout()

        primero = self.datos[0]
        titulo = QLabel("EVOLUCIÓN HISTÓRICA DE PRECIOS")
        titulo.setStyleSheet("font-size:18px; font-weight:bold;")
        titulo.setAlignment(Qt.AlignCenter)
        self.layout_principal.addWidget(titulo)

        cabecera = QLabel(
            f"<b>COMPAÑÍA:</b> {primero['compania']}<br>"
            f"<b>C.P.:</b> {primero['codigo_postal']}&nbsp;&nbsp;&nbsp;"
            f"<b>EFECTO:</b> {primero['fec_inicio']}&nbsp;&nbsp;&nbsp;"
            f"<b>FIN:</b> {primero['fec_final']}&nbsp;&nbsp;&nbsp;"
            f"<b>SUPLEMENTOS:</b> {len(self.datos)}"
        )
        self.layout_principal.addWidget(cabecera)

        contenedor_scroll = QWidget()
        layout_scroll = QVBoxLayout(contenedor_scroll)

        for titulo_bloque, campo in self.BLOQUES:
            self.crear_bloque_resumen(layout_scroll, titulo_bloque, campo)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(contenedor_scroll)
        self.layout_principal.addWidget(scroll_area)

        botones = QHBoxLayout()
        botones.addStretch()
        btn_salir = QPushButton("Salir")
        btn_salir.clicked.connect(self.salir)
        botones.addWidget(btn_salir)
        self.layout_principal.addLayout(botones)

    def crear_bloque_resumen(self, layout_principal, titulo, campo):
        layout_bloque = QVBoxLayout()
        layout_bloque.setContentsMargins(0, 8, 0, 12)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size:14px; font-weight:bold; color: #2C3E50;")
        layout_bloque.addWidget(lbl_titulo)

        layout_fila = QHBoxLayout()
        resumen = calcular_resumen(self.datos, campo)

        estilo_inicial_min = "color: #2980B9; font-weight: bold;"

        estilo_final = ""
        if resumen['precio_actual'] > resumen['precio_inicial']:
            estilo_final = "color: #C0392B; font-weight: bold;"

        estilo_max = ""
        if resumen['precio_maximo'] > resumen['precio_minimo']:
            estilo_max = "color: #C0392B; font-weight: bold;"

        estilo_var = obtener_color_por_valor(resumen['variacion_acumulada'])

        texto_resumen = (
            f"<b>Inicial:</b> <span style='{estilo_inicial_min}'>{fmt_num(resumen['precio_inicial'])}</span>&nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Final:</b> <span style='{estilo_final}'>{fmt_num(resumen['precio_actual'])}</span>&nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Var.:</b> <span style='{estilo_var}'>{fmt_pct(resumen['variacion_acumulada'])}</span>&nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Mín.:</b> <span style='{estilo_inicial_min}'>{fmt_num(resumen['precio_minimo'])}</span>&nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Máx.:</b> <span style='{estilo_max}'>{fmt_num(resumen['precio_maximo'])}</span>"
        )

        lbl_resumen = QLabel(texto_resumen)
        layout_fila.addWidget(lbl_resumen)
        layout_fila.addStretch()

        btn_detalles = QPushButton("Detalles")
        btn_detalles.clicked.connect(lambda: self.mostrar_vista_detalles(titulo, campo))
        layout_fila.addWidget(btn_detalles)

        layout_bloque.addLayout(layout_fila)
        layout_principal.addLayout(layout_bloque)

    def mostrar_vista_detalles(self, titulo_bloque, campo):
        self.limpiar_layout()

        titulo = QLabel(f"DETALLES - {titulo_bloque}")
        titulo.setStyleSheet("font-size:18px; font-weight:bold;")
        titulo.setAlignment(Qt.AlignCenter)
        self.layout_principal.addWidget(titulo)

        tabla = QTableWidget()
        tabla.setColumnCount(7)
        tabla.setHorizontalHeaderLabels(["SUP", "EFECTO", "PRECIO", "DIF SUP0", "% SUP0", "DIF ANT", "% ANT"])

        header_font = tabla.horizontalHeader().font()
        header_font.setBold(True)
        tabla.horizontalHeader().setFont(header_font)

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

                # Aplicar formato de color en celdas de porcentaje (% SUP0 -> col 4, % ANT -> col 6)
                if col in (4, 6):
                    pct_val = registro["pct_sup0"] if col == 4 else registro["pct_ant"]
                    if pct_val is not None and pct_val != 0:
                        color_q = obtener_qcolor_por_valor(pct_val)
                        if color_q:
                            item.setForeground(color_q)
                            item.setFont(header_font) # Negrita

                tabla.setItem(fila, col, item)

        tabla.resizeRowsToContents()
        self.layout_principal.addWidget(tabla)

        botones = QHBoxLayout()
        botones.addStretch()
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.mostrar_vista_general)
        botones.addWidget(btn_cerrar)
        self.layout_principal.addLayout(botones)

    def imprimir(self):
        QMessageBox.information(self, "Pendiente", "Función de impresión pendiente de implementar.")

    def exportar_pdf(self):
        QMessageBox.information(self, "Pendiente", "Exportación a PDF pendiente de implementar.")

    def salir(self):
        from analisis_contrato.lista_contratos_precios import ListaContratosPrecios
        mw = self.window()
        widget = ListaContratosPrecios(parent=mw)
        mw.cargar_modulo(widget, "Evolución histórica de precios")
