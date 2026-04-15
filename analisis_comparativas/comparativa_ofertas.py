# -------------------------------------------------------------#
# Modulo: comparativa_ofertas.py                               #
# Descripción: Comparativa real vs simulada (oferta externa)   #
# Autor: Antonio Morales                                       #
# Fecha: 2026-02-14                                            #
# -------------------------------------------------------------#

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
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
    Módulo que compara facturación real vs simulada (TEST).
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.conn = parent.conn
        self.cursor = parent.conn.cursor()

        self.setWindowTitle("Comparativa de ofertas")

        # ---------------------------------------------------------
        # LAYOUT PRINCIPAL
        # ---------------------------------------------------------
        layout = QVBoxLayout(self)

        # ---------------------------------------------------------
        # TABLA
        # ---------------------------------------------------------
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["Factura", "Real (€)", "Simulada (€)", "Diferencia (€)", "%"]
        )
        layout.addWidget(self.tabla)

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
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        botones.addWidget(btn_cerrar)

        layout.addLayout(botones)

        # ---------------------------------------------------------
        # CARGAR DATOS
        # ---------------------------------------------------------
        self.cargar_datos()

    # ---------------------------------------------------------
    # CARGAR DATOS REAL + TEST
    # ---------------------------------------------------------
    def cargar_datos(self):

        try:
            # ============================
            # 1. LEER REAL
            # ============================
            self.cursor.execute(
                """
                SELECT id_factura, total_factura
                FROM factura_calculos
                ORDER BY id_factura
            """
            )
            reales = {row[0]: row[1] for row in self.cursor.fetchall()}

            # ============================
            # 2. LEER TEST
            # ============================
            self.cursor.execute(
                """
                SELECT id_factura, total_factura
                FROM factura_calculos_test
                ORDER BY id_factura
            """
            )
            test = {row[0]: row[1] for row in self.cursor.fetchall()}

            # ============================
            # 3. EMPAREJAR
            # ============================
            ids = sorted(reales.keys())

            self.tabla.setRowCount(len(ids))

            total_real = 0
            total_test = 0

            for fila, idf in enumerate(ids):
                real = reales.get(idf, 0)
                sim = test.get(idf, 0)
                dif = sim - real
                pct = (dif / real * 100) if real != 0 else 0

                total_real += real
                total_test += sim

                self.tabla.setItem(fila, 0, QTableWidgetItem(str(idf)))
                self.tabla.setItem(fila, 1, QTableWidgetItem(f"{real:.2f}"))
                self.tabla.setItem(fila, 2, QTableWidgetItem(f"{sim:.2f}"))
                self.tabla.setItem(fila, 3, QTableWidgetItem(f"{dif:.2f}"))
                self.tabla.setItem(fila, 4, QTableWidgetItem(f"{pct:.2f}%"))

            # ============================
            # 4. TOTALES
            # ============================
            dif_total = total_test - total_real
            pct_total = (dif_total / total_real * 100) if total_real != 0 else 0

            resumen = (
                f"<b>Total real:</b> {total_real:.2f} €<br>"
                f"<b>Total simulado:</b> {total_test:.2f} €<br>"
                f"<b>Diferencia:</b> {dif_total:.2f} € ({pct_total:.2f}%)<br><br>"
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

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"No se pudo generar la comparativa:\n{e}"
            )
