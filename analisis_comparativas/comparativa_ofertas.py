# -------------------------------------------------------------#
# Modulo: comparativa_ofertas.py                               #
# Descripción: Comparativa real vs simulada (oferta externa)   #
# Autor: Antonio Morales + Copilot                             #
# Fecha: 2026-05-04                                            #
# -------------------------------------------------------------#

import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QFileDialog,
)


class ComparativaOfertas(QWidget):
    """
    Comparativa profesional del bloque de energía:
    Real vs Test (oferta externa), emparejando por nfactura.
    """

    # ---------------------------------------------------------
    # FORMATEADORES DE DIFERENCIAS (flechas + colores)
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

                # REAL
                self.tabla.setItem(fila, 1, QTableWidgetItem(f"{real:.2f}"))

                # TEST
                self.tabla.setItem(fila, 2, QTableWidgetItem(f"{sim:.2f}"))

                # DIFERENCIA (coloreada)
                item_dif = QTableWidgetItem(f"{dif:.2f}")
                if dif < 0:
                    item_dif.setForeground(Qt.green)
                elif dif > 0:
                    item_dif.setForeground(Qt.red)
                else:
                    item_dif.setForeground(Qt.gray)
                self.tabla.setItem(fila, 3, item_dif)

                # PORCENTAJE (coloreado)
                item_pct = QTableWidgetItem(f"{pct:.2f}%")
                if pct < 0:
                    item_pct.setForeground(Qt.green)
                elif pct > 0:
                    item_pct.setForeground(Qt.red)
                else:
                    item_pct.setForeground(Qt.gray)
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

            # Guardamos JSON para detalle
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
    # PANEL DETALLE (coloreado)
    # ---------------------------------------------------------
    def actualizar_panel_detalle(self, real, test):
        if real is None:
            return

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

        # POTENCIA
        add(0, 0, "<b>Potencia punta</b>")
        add(
            0,
            1,
            f"{real['potencia']['punta']['kw']} kW / {real['potencia']['punta']['precio']} € / {real['potencia']['punta']['importe']} €",
        )
        add(
            0,
            2,
            f"{test['potencia']['punta']['kw']} kW / {test['potencia']['punta']['precio']} € / {test['potencia']['punta']['importe']} €",
        )

        add(1, 0, "<b>Potencia valle</b>")
        add(
            1,
            1,
            f"{real['potencia']['valle']['kw']} kW / {real['potencia']['valle']['precio']} € / {real['potencia']['valle']['importe']} €",
        )
        add(
            1,
            2,
            f"{test['potencia']['valle']['kw']} kW / {test['potencia']['valle']['precio']} € / {test['potencia']['valle']['importe']} €",
        )

        # CONSUMO
        add(2, 0, "<b>Consumo punta</b>")
        add(
            2,
            1,
            f"{real['consumo']['punta']['kwh']} kWh / {real['consumo']['punta']['precio']} € / {real['consumo']['punta']['importe']} €",
        )
        add(
            2,
            2,
            f"{test['consumo']['punta']['kwh']} kWh / {test['consumo']['punta']['precio']} € / {test['consumo']['punta']['importe']} €",
        )

        add(3, 0, "<b>Consumo llano</b>")
        add(
            3,
            1,
            f"{real['consumo']['llano']['kwh']} kWh / {real['consumo']['llano']['precio']} € / {real['consumo']['llano']['importe']} €",
        )
        add(
            3,
            2,
            f"{test['consumo']['llano']['kwh']} kWh / {test['consumo']['llano']['precio']} € / {test['consumo']['llano']['importe']} €",
        )

        add(4, 0, "<b>Consumo valle</b>")
        add(
            4,
            1,
            f"{real['consumo']['valle']['kwh']} kWh / {real['consumo']['valle']['precio']} € / {real['consumo']['valle']['importe']} €",
        )
        add(
            4,
            2,
            f"{test['consumo']['valle']['kwh']} kWh / {test['consumo']['valle']['precio']} € / {test['consumo']['valle']['importe']} €",
        )

        # EXCEDENTES
        add(5, 0, "<b>Excedentes generados</b>")
        add(5, 1, f"{real['excedentes']['generados_kwh']} kWh")
        add(5, 2, f"{test['excedentes']['generados_kwh']} kWh")

        add(6, 0, "<b>Precio excedentes</b>")
        add(6, 1, f"{real['excedentes']['precio_unitario']} €/kWh")
        add(6, 2, f"{test['excedentes']['precio_unitario']} €/kWh")

        add(7, 0, "<b>Compensados</b>")
        add(7, 1, f"{real['excedentes']['compensados']} €")
        add(7, 2, f"{test['excedentes']['compensados']} €")

        add(8, 0, "<b>Sobrante</b>")
        add(8, 1, f"{real['excedentes']['sobrante']} €")
        add(8, 2, f"{test['excedentes']['sobrante']} €")

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

        dif = total_test - total_real
        pct = (dif / total_real * 100) if total_real != 0 else 0.0

        add(10, 0, "<b>Total energía</b>")
        add(10, 1, f"{total_real:.2f} €")
        add(10, 2, f"{total_test:.2f} €")

        add(11, 0, "<b>Diferencia</b>")
        add(11, 1, "")
        add(11, 2, f"{self._fmt_diff(dif)} ({self._fmt_pct(pct)})")

    # ---------------------------------------------------------
    # GENERAR HTML PARA PDF / IMPRESIÓN
    # ---------------------------------------------------------
    def _generar_html_informe(self):
        # Tabla resumen
        filas_html = ""
        for r in range(self.tabla.rowCount()):
            cols = []
            for c in range(self.tabla.columnCount()):
                item = self.tabla.item(r, c)
                cols.append(item.text() if item else "")
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

        # Detalle de la factura seleccionada
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
                dif = total_test - total_real
                pct = (dif / total_real * 100) if total_real != 0 else 0.0

                detalle_html = f"""
<h3>Detalle de energía – factura {nfact}</h3>
<table border='1' cellspacing='0' cellpadding='3'>
<tr><th>Concepto</th><th>Real</th><th>Test</th></tr>

<tr><td>Potencia punta</td>
    <td>{real['potencia']['punta']['kw']} kW / {real['potencia']['punta']['precio']} € / {real['potencia']['punta']['importe']} €</td>
    <td>{test['potencia']['punta']['kw']} kW / {test['potencia']['punta']['precio']} € / {test['potencia']['punta']['importe']} €</td></tr>

<tr><td>Potencia valle</td>
    <td>{real['potencia']['valle']['kw']} kW / {real['potencia']['valle']['precio']} € / {real['potencia']['valle']['importe']} €</td>
    <td>{test['potencia']['valle']['kw']} kW / {test['potencia']['valle']['precio']} € / {test['potencia']['valle']['importe']} €</td></tr>

<tr><td>Consumo punta</td>
    <td>{real['consumo']['punta']['kwh']} kWh / {real['consumo']['punta']['precio']} € / {real['consumo']['punta']['importe']} €</td>
    <td>{test['consumo']['punta']['kwh']} kWh / {test['consumo']['punta']['precio']} € / {test['consumo']['punta']['importe']} €</td></tr>

<tr><td>Consumo llano</td>
    <td>{real['consumo']['llano']['kwh']} kWh / {real['consumo']['llano']['precio']} € / {real['consumo']['llano']['importe']} €</td>
    <td>{test['consumo']['llano']['kwh']} kWh / {test['consumo']['llano']['precio']} € / {test['consumo']['llano']['importe']} €</td></tr>

<tr><td>Consumo valle</td>
    <td>{real['consumo']['valle']['kwh']} kWh / {real['consumo']['valle']['precio']} € / {real['consumo']['valle']['importe']} €</td>
    <td>{test['consumo']['valle']['kwh']} kWh / {test['consumo']['valle']['precio']} € / {test['consumo']['valle']['importe']} €</td></tr>

<tr><td>Excedentes generados</td>
    <td>{real['excedentes']['generados_kwh']} kWh</td>
    <td>{test['excedentes']['generados_kwh']} kWh</td></tr>

<tr><td>Precio excedentes</td>
    <td>{real['excedentes']['precio_unitario']} €/kWh</td>
    <td>{test['excedentes']['precio_unitario']} €/kWh</td></tr>

<tr><td>Compensados</td>
    <td>{real['excedentes']['compensados']} €</td>
    <td>{test['excedentes']['compensados']} €</td></tr>

<tr><td>Sobrante</td>
    <td>{real['excedentes']['sobrante']} €</td>
    <td>{test['excedentes']['sobrante']} €</td></tr>

<tr><td><b>Total energía</b></td>
    <td><b>{total_real:.2f} €</b></td>
    <td><b>{total_test:.2f} €</b></td></tr>

<tr><td><b>Diferencia</b></td>
    <td></td>
    <td><b>{self._fmt_diff(dif)} ({self._fmt_pct(pct)})</b></td></tr>

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
