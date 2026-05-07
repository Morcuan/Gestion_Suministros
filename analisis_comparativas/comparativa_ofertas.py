# -------------------------------------------------------------#
# Modulo: comparativa_ofertas.py                               #
# Descripción: Comparativa real vs simulada (oferta externa)   #
# Autor: Antonio Morales + Copilot                             #
# Fecha: 2026-05-04                                            #
# -------------------------------------------------------------#

import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QGroupBox,
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


class ComparativaOfertas(QWidget):
    """
    Comparativa profesional del bloque de energía:
    Real vs Test (oferta externa), emparejando por nfactura.
    """

    # ---------------------------------------------------------
    # FORMATEADORES DE DIFERENCIAS Y VALORES (flechas + colores)
    # ---------------------------------------------------------

    def _fmt_diff(self, valor):
        if valor < 0:
            return f"<span style='color:green;'><b>⬇️ {valor:.2f}</b></span>"
        elif valor > 0:
            return f"<span style='color:red;'><b>⬆️ {valor:.2f}</b></span>"
        else:
            return f"<span style='color:gray;'><b>➖ {valor:.2f}</b></span>"

    def _fmt_pct(self, valor):
        if valor < 0:
            return f"<span style='color:green;'><b>{valor:.2f}%</b></span>"
        elif valor > 0:
            return f"<span style='color:red;'><b>{valor:.2f}%</b></span>"
        else:
            return f"<span style='color:gray;'><b>{valor:.2f}%</b></span>"

    def _fmt_val_real(self, real, test):
        # REAL siempre azul
        return f"<span style='color:blue;'><b>{real:.2f}</b></span>"

    def _fmt_val_test(self, real, test):
        dif = test - real
        if dif < 0:
            return f"<span style='color:green;'><b>{test:.2f}</b></span>"
        elif dif > 0:
            return f"<span style='color:red;'><b>{test:.2f}</b></span>"
        else:
            return f"<span style='color:gray;'><b>{test:.2f}</b></span>"

    # ---------------------------------------------------------
    # INICIO
    # ---------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)

        self.conn = parent.conn
        self.cursor = parent.conn.cursor()

        self.setWindowTitle("Comparativa real vs simulada")
        self.resize(950, 650)
        self.setMinimumSize(950, 650)

        layout = QVBoxLayout(self)

        # ---------------------------------------------------------
        # TABLA SUPERIOR (RESUMEN)
        # ---------------------------------------------------------
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            [
                "Factura real",
                "Energía Real (€)",
                "Energía Test (€)",
                "Diferencia (€)",
                "%",
            ]
        )
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla)

        # ---------------------------------------------------------
        # PANEL DETALLE
        # ---------------------------------------------------------
        self.gb_detalle = QGroupBox("Detalle de energía")
        self.layout_detalle = QGridLayout()
        self.gb_detalle.setLayout(self.layout_detalle)
        layout.addWidget(self.gb_detalle)

        # ---------------------------------------------------------
        # PANEL DE TOTALES
        # ---------------------------------------------------------
        self.lbl_totales = QLabel("")
        self.lbl_totales.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.lbl_totales)

        # ---------------------------------------------------------
        # BOTONES
        # ---------------------------------------------------------
        botones = QHBoxLayout()

        btn_pdf = QPushButton("Exportar PDF")
        btn_pdf.clicked.connect(self.exportar_pdf)
        botones.addWidget(btn_pdf)

        btn_print = QPushButton("Imprimir")
        btn_print.clicked.connect(self.imprimir)
        botones.addWidget(btn_print)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        botones.addWidget(btn_cerrar)

        layout.addLayout(botones)

        # ---------------------------------------------------------
        # CARGAR DATOS
        # ---------------------------------------------------------
        self.reales_json = {}
        self.test_json = {}
        self.cargar_datos()
        self.tabla.itemSelectionChanged.connect(self.mostrar_detalle)

    # ---------------------------------------------------------
    # CARGAR DATOS REAL + TEST (emparejando por nfactura)
    # ---------------------------------------------------------
    def cargar_datos(self):
        try:
            # REAL
            self.cursor.execute("""
                SELECT nfactura, detalles_json
                FROM factura_calculos
                WHERE nfactura IS NOT NULL
                ORDER BY nfactura
                """)
            reales = {}
            for nfactura, js in self.cursor.fetchall():
                datos = json.loads(js)
                total_energia = (
                    datos["potencia"]["total"]
                    + datos["consumo"]["total"]
                    + datos["excedentes"]["compensados"]
                )
                reales[str(nfactura)] = {
                    "energia": total_energia,
                    "json": datos,
                }

            # TEST
            self.cursor.execute("""
                SELECT nfactura, detalles_json
                FROM factura_calculos_test
                WHERE nfactura IS NOT NULL
                ORDER BY nfactura
                """)
            test = {}
            for nfactura, js in self.cursor.fetchall():
                datos = json.loads(js)
                total_energia = (
                    datos["potencia"]["total"]
                    + datos["consumo"]["total"]
                    + datos["excedentes"]["compensados"]
                )
                test[str(nfactura)] = {
                    "energia": total_energia,
                    "json": datos,
                }

            # EMPAREJAR POR NFACTURA
            nfs = sorted(reales.keys())
            self.tabla.setRowCount(len(nfs))

            total_real = 0.0
            total_test = 0.0

            for fila, nfactura in enumerate(nfs):
                real = reales[nfactura]["energia"]
                sim = test.get(nfactura, {}).get("energia", 0.0)

                dif = sim - real
                pct = (dif / real * 100) if real != 0 else 0.0

                total_real += real
                total_test += sim

                # FACTURA
                self.tabla.setItem(fila, 0, QTableWidgetItem(nfactura))

                # REAL (siempre azul)
                item_real = QTableWidgetItem(f"{real:.2f}")
                item_real.setForeground(Qt.blue)

                # TEST (según diferencia)
                item_test = QTableWidgetItem(f"{sim:.2f}")
                if dif < 0:
                    item_test.setForeground(Qt.green)
                elif dif > 0:
                    item_test.setForeground(Qt.red)
                else:
                    item_test.setForeground(Qt.gray)

                # DIFERENCIA
                item_dif = QTableWidgetItem(f"{dif:.2f}")
                if dif < 0:
                    item_dif.setForeground(Qt.green)
                elif dif > 0:
                    item_dif.setForeground(Qt.red)
                else:
                    item_dif.setForeground(Qt.gray)

                # PORCENTAJE
                item_pct = QTableWidgetItem(f"{pct:.2f}%")
                if pct < 0:
                    item_pct.setForeground(Qt.green)
                elif pct > 0:
                    item_pct.setForeground(Qt.red)
                else:
                    item_pct.setForeground(Qt.gray)

                # Insertar en tabla
                self.tabla.setItem(fila, 1, item_real)
                self.tabla.setItem(fila, 2, item_test)
                self.tabla.setItem(fila, 3, item_dif)
                self.tabla.setItem(fila, 4, item_pct)

            # TOTALES
            dif_total = total_test - total_real
            pct_total = (dif_total / total_real * 100) if total_real != 0 else 0.0

            resumen = (
                f"<b>Total energía real:</b> {total_real:.2f} €<br>"
                f"<b>Total energía test:</b> {total_test:.2f} €<br>"
                f"<b>Diferencia:</b> {self._fmt_diff(dif_total)} "
                f"({self._fmt_pct(pct_total)})<br><br>"
            )

            if dif_total < 0:
                resumen += "<b style='color:green;'>La oferta externa habría supuesto un ahorro.</b>"
            elif dif_total > 0:
                resumen += (
                    "<b style='color:red;'>La oferta externa habría sido más cara.</b>"
                )
            else:
                resumen += "<b>No hay diferencia entre ambas opciones.</b>"

            self.lbl_totales.setText(resumen)

            self.reales_json = {k: v["json"] for k, v in reales.items()}
            self.test_json = {k: v["json"] for k, v in test.items()}

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"No se pudo generar la comparativa:\n{e}"
            )

    # ---------------------------------------------------------
    # MOSTRAR DETALLE
    # ---------------------------------------------------------
    def mostrar_detalle(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return

        nfact = self.tabla.item(fila, 0).text()

        real = self.reales_json.get(nfact)
        test = self.test_json.get(nfact)

        self.actualizar_panel_detalle(real, test)

    # ---------------------------------------------------------
    # PANEL DETALLE (ESTILO B – tabla compacta con colores)
    # ---------------------------------------------------------
    def actualizar_panel_detalle(self, real, test):
        if real is None:
            return

        # Si no hay test, rellenamos con ceros
        if test is None:
            test = {
                "potencia": {
                    "punta": {"kw": 0, "precio": 0, "dias": 0, "importe": 0},
                    "valle": {"kw": 0, "precio": 0, "dias": 0, "importe": 0},
                    "total": 0,
                },
                "consumo": {
                    "punta": {"kwh": 0, "precio": 0, "importe": 0},
                    "llano": {"kwh": 0, "precio": 0, "importe": 0},
                    "valle": {"kwh": 0, "precio": 0, "importe": 0},
                    "total": 0,
                },
                "excedentes": {
                    "generados_kwh": 0,
                    "precio_unitario": 0,
                    "compensados": 0,
                    "sobrante": 0,
                },
            }

        # Limpiar panel
        for i in reversed(range(self.layout_detalle.count())):
            w = self.layout_detalle.itemAt(i).widget()
            if w:
                w.deleteLater()

        def add(row, col, text):
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignLeft)
            self.layout_detalle.addWidget(lbl, row, col)

        # ---------------------------------------------------------
        # TABLA DETALLE ESTILO B
        # ---------------------------------------------------------
        fila = 0

        def fila_detalle(nombre, real_val, test_val):
            nonlocal fila
            dif = test_val - real_val
            pct = (dif / real_val * 100) if real_val != 0 else 0.0

            add(fila, 0, f"<b>{nombre}</b>")
            add(fila, 1, self._fmt_val_real(real_val, test_val))  # REAL azul
            add(fila, 2, self._fmt_val_test(real_val, test_val))  # TEST coloreado
            add(fila, 3, self._fmt_diff(dif))  # DIF coloreado
            add(fila, 4, self._fmt_pct(pct))  # % coloreado

            fila += 1

        # POTENCIA
        fila_detalle(
            "Potencia punta",
            real["potencia"]["punta"]["importe"],
            test["potencia"]["punta"]["importe"],
        )
        fila_detalle(
            "Potencia valle",
            real["potencia"]["valle"]["importe"],
            test["potencia"]["valle"]["importe"],
        )
        fila_detalle(
            "Total potencia",
            real["potencia"]["total"],
            test["potencia"]["total"],
        )

        # CONSUMO
        fila_detalle(
            "Consumo punta",
            real["consumo"]["punta"]["importe"],
            test["consumo"]["punta"]["importe"],
        )
        fila_detalle(
            "Consumo llano",
            real["consumo"]["llano"]["importe"],
            test["consumo"]["llano"]["importe"],
        )
        fila_detalle(
            "Consumo valle",
            real["consumo"]["valle"]["importe"],
            test["consumo"]["valle"]["importe"],
        )
        fila_detalle(
            "Total consumo",
            real["consumo"]["total"],
            test["consumo"]["total"],
        )

        # EXCEDENTES
        fila_detalle(
            "Excedentes compensados",
            real["excedentes"]["compensados"],
            test["excedentes"]["compensados"],
        )
        fila_detalle(
            "Excedentes sobrante",
            real["excedentes"]["sobrante"],
            test["excedentes"]["sobrante"],
        )

        # TOTAL ENERGÍA
        total_real = (
            real["potencia"]["total"]
            + real["consumo"]["total"]
            + real["excedentes"]["compensados"]
        )
        total_test = (
            test["potencia"]["total"]
            + test["consumo"]["total"]
            + test["excedentes"]["compensados"]
        )

        fila_detalle("TOTAL ENERGÍA", total_real, total_test)

    # ---------------------------------------------------------
    # GENERAR HTML PARA PDF / IMPRESIÓN (ESTILO B + COLORES)
    # ---------------------------------------------------------
    def _generar_html_informe(self):
        # Tabla resumen (superior)
        filas_html = ""
        for r in range(self.tabla.rowCount()):
            cols = []
            for c in range(self.tabla.columnCount()):
                item = self.tabla.item(r, c)
                texto = item.text() if item else ""

                # -------------------------------------------------
                # Colorear según columna (REAL azul, TEST según dif)
                # -------------------------------------------------
                if c == 1:  # REAL → azul
                    texto = f"<span style='color:blue;'><b>{texto}</b></span>"

                elif c == 2:  # TEST → según diferencia
                    dif = float(self.tabla.item(r, 3).text())
                    if dif < 0:
                        color = "green"
                    elif dif > 0:
                        color = "red"
                    else:
                        color = "gray"
                    texto = f"<span style='color:{color};'><b>{texto}</b></span>"

                elif c == 3:  # DIFERENCIA → según signo
                    dif = float(texto)
                    if dif < 0:
                        color = "green"
                    elif dif > 0:
                        color = "red"
                    else:
                        color = "gray"
                    texto = f"<span style='color:{color};'><b>{texto}</b></span>"

                elif c == 4:  # PORCENTAJE → según signo
                    pct = float(texto.replace("%", ""))
                    if pct < 0:
                        color = "green"
                    elif pct > 0:
                        color = "red"
                    else:
                        color = "gray"
                    texto = f"<span style='color:{color};'><b>{texto}</b></span>"

                cols.append(texto)

            filas_html += "<tr>" + "".join(f"<td>{v}</td>" for v in cols) + "</tr>"

        tabla_html = (
            "<h2>Comparativa real vs simulada</h2>"
            "<table border='1' cellspacing='0' cellpadding='3'>"
            "<tr>"
            + "".join(
                f"<th>{self.tabla.horizontalHeaderItem(c).text()}</th>"
                for c in range(self.tabla.columnCount())
            )
            + "</tr>"
            + filas_html
            + "</table><br>"
        )

        # ---------------------------------------------------------
        # DETALLE ESTILO B COLOREADO
        # ---------------------------------------------------------
        detalle_html = ""
        fila_sel = self.tabla.currentRow()
        if fila_sel >= 0:
            nfact = self.tabla.item(fila_sel, 0).text()
            real = self.reales_json.get(nfact)
            test = self.test_json.get(nfact)

            if real is not None:
                if test is None:
                    test = {
                        "potencia": {
                            "punta": {"importe": 0},
                            "valle": {"importe": 0},
                            "total": 0,
                        },
                        "consumo": {
                            "punta": {"importe": 0},
                            "llano": {"importe": 0},
                            "valle": {"importe": 0},
                            "total": 0,
                        },
                        "excedentes": {
                            "compensados": 0,
                            "sobrante": 0,
                        },
                    }

                def fila_html(nombre, real_val, test_val):
                    dif = test_val - real_val
                    pct = (dif / real_val * 100) if real_val != 0 else 0.0

                    # REAL siempre azul
                    col_real = "blue"

                    # TEST según diferencia
                    if dif < 0:
                        col_test = "green"
                    elif dif > 0:
                        col_test = "red"
                    else:
                        col_test = "gray"

                    # DIF y % mismo color que TEST
                    col_dif = col_test
                    col_pct = col_test

                    return f"""
<tr>
<td><b>{nombre}</b></td>
<td><span style='color:{col_real};'><b>{real_val:.2f}</b></span></td>
<td><span style='color:{col_test};'><b>{test_val:.2f}</b></span></td>
<td><span style='color:{col_dif};'><b>{dif:.2f}</b></span></td>
<td><span style='color:{col_pct};'><b>{pct:.2f}%</b></span></td>
</tr>
"""

                total_real = (
                    real["potencia"]["total"]
                    + real["consumo"]["total"]
                    + real["excedentes"]["compensados"]
                )
                total_test = (
                    test["potencia"]["total"]
                    + test["consumo"]["total"]
                    + test["excedentes"]["compensados"]
                )

                detalle_html = f"""
<h3>Detalle de energía – factura {nfact}</h3>
<table border='1' cellspacing='0' cellpadding='3'>
<tr><th>Concepto</th><th>Real</th><th>Test</th><th>Diferencia</th><th>%</th></tr>

{fila_html("Potencia punta", real["potencia"]["punta"]["importe"], test["potencia"]["punta"]["importe"])}
{fila_html("Potencia valle", real["potencia"]["valle"]["importe"], test["potencia"]["valle"]["importe"])}
{fila_html("Total potencia", real["potencia"]["total"], test["potencia"]["total"])}

{fila_html("Consumo punta", real["consumo"]["punta"]["importe"], test["consumo"]["punta"]["importe"])}
{fila_html("Consumo llano", real["consumo"]["llano"]["importe"], test["consumo"]["llano"]["importe"])}
{fila_html("Consumo valle", real["consumo"]["valle"]["importe"], test["consumo"]["valle"]["importe"])}
{fila_html("Total consumo", real["consumo"]["total"], test["consumo"]["total"])}

{fila_html("Excedentes compensados", real["excedentes"]["compensados"], test["excedentes"]["compensados"])}
{fila_html("Excedentes sobrante", real["excedentes"]["sobrante"], test["excedentes"]["sobrante"])}

{fila_html("TOTAL ENERGÍA", total_real, total_test)}

</table>
"""

        # Totales (ya formateados en lbl_totales)
        totales_html = f"<br>{self.lbl_totales.text()}"

        return tabla_html + detalle_html + totales_html

    # ---------------------------------------------------------
    # EXPORTAR PDF
    # ---------------------------------------------------------
    def exportar_pdf(self):
        nombre, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", "", "PDF (*.pdf)")
        if not nombre:
            return

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(nombre)

        html = self._generar_html_informe()
        doc = QTextDocument()
        doc.setHtml(html)
        doc.print_(printer)

    # ---------------------------------------------------------
    # IMPRIMIR
    # ---------------------------------------------------------
    def imprimir(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            html = self._generar_html_informe()
            doc = QTextDocument()
            doc.setHtml(html)
            doc.print_(printer)
