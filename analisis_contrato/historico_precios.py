# -------------------------------------------------------------
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
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# ==========================================================
# CONSULTAS
# ==========================================================

def obtener_suplementos(conn, ncontrato):

    cur = conn.cursor()

    sql = """
        SELECT
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
        ORDER BY suplemento
    """

    cur.execute(sql, (ncontrato,))
    filas = cur.fetchall()

    return [dict(fila) for fila in filas]


# ==========================================================
# CALCULOS
# ==========================================================

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

            pct_sup0 = (
                (dif_sup0 / valor_base) * 100
                if valor_base
                else 0
            )

            dif_ant = valor_actual - valor_anterior

            pct_ant = (
                (dif_ant / valor_anterior) * 100
                if valor_anterior
                else 0
            )

        resultado.append(
            {
                "suplemento": fila["suplemento"],
                "fecha": fila["efec_suple"],
                "precio": valor_actual,
                "dif_sup0": dif_sup0,
                "pct_sup0": pct_sup0,
                "dif_ant": dif_ant,
                "pct_ant": pct_ant,
            }
        )

        valor_anterior = valor_actual

    return resultado


def calcular_resumen(registros, campo):

    if not registros:
        return None

    valores = [fila[campo] for fila in registros]

    inicial = valores[0]
    actual = valores[-1]

    variacion = (
        ((actual - inicial) / inicial) * 100
        if inicial
        else 0
    )

    return {
        "precio_inicial": inicial,
        "precio_actual": actual,
        "variacion_acumulada": variacion,
        "precio_minimo": min(valores),
        "precio_maximo": max(valores),
    }


# ==========================================================
# FORMATEO
# ==========================================================

def fmt_num(valor, decimales=6):

    if valor is None:
        return "---"

    return f"{valor:.{decimales}f}"


def fmt_pct(valor):

    if valor is None:
        return "---"

    return f"{valor:+.2f} %"


# ==========================================================
# CLASE PRINCIPAL
# ==========================================================

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

        self.datos = obtener_suplementos(
            self.conn,
            self.ncontrato
        )

        self.crear_ui()

    # ------------------------------------------------------

    def crear_ui(self):

        layout = QVBoxLayout(self)

        if not self.datos:

            layout.addWidget(
                QLabel("Contrato sin datos.")
            )

            return

        primero = self.datos[0]

        titulo = QLabel(
            f"EVOLUCIÓN HISTÓRICA DE PRECIOS"
        )

        titulo.setStyleSheet(
            "font-size:18px; font-weight:bold;"
        )

        titulo.setAlignment(Qt.AlignCenter)

        layout.addWidget(titulo)

        cabecera = QLabel(
            f"""
            <b>COMPAÑÍA:</b> {primero['compania']}<br>
            <b>C.P.:</b> {primero['codigo_postal']} &nbsp;&nbsp;&nbsp;
            <b>EFECTO:</b> {primero['fec_inicio']} &nbsp;&nbsp;&nbsp;
            <b>FIN:</b> {primero['fec_final']} &nbsp;&nbsp;&nbsp;
            <b>SUPLEMENTOS:</b> {len(self.datos)}
            """
        )

        layout.addWidget(cabecera)

        for titulo_bloque, campo in self.BLOQUES:

            self.crear_bloque(
                layout,
                titulo_bloque,
                campo
            )

        botones = QHBoxLayout()

        botones.addStretch()

        btn_pdf = QPushButton("PDF")
        btn_pdf.clicked.connect(self.exportar_pdf)

        btn_print = QPushButton("Imprimir")
        btn_print.clicked.connect(self.imprimir)

        btn_salir = QPushButton("Salir")
        btn_salir.clicked.connect(self.salir)

        botones.addWidget(btn_print)
        botones.addWidget(btn_pdf)
        botones.addWidget(btn_salir)

        layout.addLayout(botones)

    # ------------------------------------------------------

    def crear_bloque(
            self,
            layout_principal,
            titulo,
            campo,
        ):

            lbl = QLabel(titulo)

            lbl.setStyleSheet(
                """
                font-size:14px;
                font-weight:bold;
                margin-top:3px;
                """
            )

            layout_principal.addWidget(lbl)

            tabla = QTableWidget()

            tabla.setColumnCount(7)

            tabla.setHorizontalHeaderLabels(
                [
                    "SUP",
                    "EFECTO",
                    "PRECIO",
                    "DIF SUP0",
                    "% SUP0",
                    "DIF ANT",
                    "% ANT",
                ]
            )

            tabla.horizontalHeader().setSectionResizeMode(
                QHeaderView.Stretch
            )

            evolucion = calcular_evolucion(
                self.datos,
                campo
            )

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

                    item.setFlags(
                        item.flags()
                        ^ Qt.ItemIsEditable
                    )

                    tabla.setItem(
                        fila,
                        col,
                        item
                    )

            # -------------------------------------------------
            # AJUSTAR ALTURA AUTOMÁTICA
            # -------------------------------------------------

            tabla.resizeRowsToContents()

            if tabla.rowCount() > 0:

                altura = (
                    tabla.horizontalHeader().height()
                    + sum(
                        tabla.rowHeight(f)
                        for f in range(tabla.rowCount())
                    )
                    + 8
                )

                tabla.setFixedHeight(altura)

            layout_principal.addWidget(tabla)

            resumen = calcular_resumen(
                self.datos,
                campo
            )

            lbl_resumen = QLabel(
                f"<b>Inicial:</b> {fmt_num(resumen['precio_inicial'])}"
                f" &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Final:</b> {fmt_num(resumen['precio_actual'])}"
                f" &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Var.:</b> {fmt_pct(resumen['variacion_acumulada'])}"
                f" &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Mín.:</b> {fmt_num(resumen['precio_minimo'])}"
                f" &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Máx.:</b> {fmt_num(resumen['precio_maximo'])}"
            )

            layout_principal.addWidget(lbl_resumen)
    # ------------------------------------------------------

    def imprimir(self):

        QMessageBox.information(
            self,
            "Pendiente",
            "Función de impresión pendiente de implementar."
        )

    # ------------------------------------------------------

    def exportar_pdf(self):

        QMessageBox.information(
            self,
            "Pendiente",
            "Exportación a PDF pendiente de implementar."
        )

    # ------------------------------------------------------

    def salir(self):

        from analisis_contrato.lista_contratos_precios import (
            ListaContratosPrecios,
        )

        mw = self.window()

        widget = ListaContratosPrecios(
            parent=mw
        )

        mw.cargar_modulo(
            widget,
            "Evolución histórica de precios",
        )
