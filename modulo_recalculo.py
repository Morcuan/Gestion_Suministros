# --------------------------------------------#
# Modulo: modulo_recalculo.py                 #
# Descripción: Recalculo de facturas marcadas #
# Autor: Antonio Morales + Copilot            #
# Fecha: 2026-02-24                           #
# --------------------------------------------#
# Este módulo permite listar las facturas que tienen el flag "recalcular" activo,
# recalcularlas individualmente o en lote, y guardar los nuevos cálculos en la tabla
# "factura_calculos". Al finalizar el recálculo, se limpia el flag "recalcular"
# para evitar recálculos futuros innecesarios.

# ============================================================
#  IMPORTACIONES
# ============================================================
import json
import sqlite3

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

from calculo import (
    calcular_bono_solar_cloud,
    calcular_cargos_para_factura,
    calcular_energia_para_factura,
    calcular_iva_para_factura,
    calcular_servicios_para_factura,
    generar_json_calculo,
    guardar_calculo_factura,
    obtener_datos_factura,
)

DB_PATH = "data/almacen.db"


# ============================================================
#  CONEXIÓN
# ============================================================
def get_conn():
    return sqlite3.connect(DB_PATH)


# ============================================================
#  MÓDULO PRINCIPAL
# ============================================================
class ModuloRecalculo(QWidget):
    """
    Módulo para:
    - Listar facturas con recalcular = 1
    - Recalcularlas en lote o individualmente
    - Guardar nuevos cálculos en factura_calculos
    - Limpiar flag recalcular
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Recalcular facturas pendientes")
        self.conn = get_conn()

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(
            ["ID Contrato", "Factura", "Inicio periodo", "Fin periodo"]
        )

        self.btn_recalcular_sel = QPushButton("Recalcular seleccionada")
        self.btn_recalcular_todas = QPushButton("Recalcular todas")
        self.btn_cerrar = QPushButton("Cerrar")

        self.btn_recalcular_sel.clicked.connect(self.recalcular_seleccionada)
        self.btn_recalcular_todas.clicked.connect(self.recalcular_todas)
        self.btn_cerrar.clicked.connect(self.cerrar)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Facturas pendientes de recálculo:"))
        layout.addWidget(self.tabla)

        botones = QHBoxLayout()
        botones.addWidget(self.btn_recalcular_sel)
        botones.addWidget(self.btn_recalcular_todas)
        botones.addStretch()
        botones.addWidget(self.btn_cerrar)

        layout.addLayout(botones)
        self.setLayout(layout)

        self.cargar_facturas()

    # ============================================================
    #  CARGA DE FACTURAS PENDIENTES
    # ============================================================
    def cargar_facturas(self):
        cur = self.conn.cursor()

        cur.execute(
            """
            SELECT id_contrato, nfactura, inicio_factura, fin_factura
            FROM facturas
            WHERE recalcular = 1
            ORDER BY id_contrato, inicio_factura
            """
        )

        rows = cur.fetchall()
        self.tabla.setRowCount(len(rows))

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.tabla.setItem(i, j, QTableWidgetItem(str(value)))

    # ============================================================
    #  RECÁLCULO DE UNA FACTURA
    # ============================================================
    def recalcular_factura(self, id_contrato, nfactura):
        cur = self.conn.cursor()

        # ---------------------------------------------------------
        # 0) ELIMINAR CÁLCULOS PREVIOS
        # ---------------------------------------------------------
        cur.execute(
            "DELETE FROM factura_calculos WHERE id_factura = ?",
            (nfactura,),
        )

        # ---------------------------------------------------------
        # 1) Cargar datos base desde la vista
        # ---------------------------------------------------------
        datos_base = obtener_datos_factura(cur, nfactura)
        if not datos_base:
            raise Exception(f"No se encontraron datos para factura {nfactura}")

        # ---------------------------------------------------------
        # 2) Calcular CARGOS
        # ---------------------------------------------------------
        cargos_obj = calcular_cargos_para_factura(datos_base)
        bono_social = cargos_obj.bono_social

        # ---------------------------------------------------------
        # 3) Calcular ENERGÍA
        # ---------------------------------------------------------
        energia_obj, datos = calcular_energia_para_factura(cur, nfactura, bono_social)

        # ---------------------------------------------------------
        # 4) Calcular SERVICIOS
        # ---------------------------------------------------------
        servicios_obj = calcular_servicios_para_factura(datos_base)

        # ---------------------------------------------------------
        # 5) Calcular IVA
        # ---------------------------------------------------------
        iva_obj = calcular_iva_para_factura(
            energia_obj.total_energia,
            cargos_obj.total_cargos,
            servicios_obj.total_servicios_otros,
        )

        # ---------------------------------------------------------
        # 6) Aplicar Bono Solar Cloud
        # ---------------------------------------------------------
        sobrante = energia_obj.sobrante_excedentes

        total_final, aplicado_cloud, nuevo_saldo = calcular_bono_solar_cloud(
            cur, id_contrato, iva_obj.total_con_iva, sobrante
        )

        # ---------------------------------------------------------
        # 7) Generar JSON
        # ---------------------------------------------------------
        detalles_json = generar_json_calculo(
            energia_obj,
            cargos_obj,
            servicios_obj,
            iva_obj,
            aplicado_cloud,
            nuevo_saldo,
            datos_base,
        )

        # ---------------------------------------------------------
        # 8) Guardar cálculo nuevo
        # ---------------------------------------------------------
        guardar_calculo_factura(
            cur,
            nfactura,
            "1.0",
            energia_obj,
            cargos_obj,
            servicios_obj,
            iva_obj,
            aplicado_cloud,
            nuevo_saldo,
            detalles_json,
        )

        # ---------------------------------------------------------
        # 9) Limpiar flag
        # ---------------------------------------------------------
        cur.execute(
            """
            UPDATE facturas
            SET recalcular = 0
            WHERE id_contrato = ? AND nfactura = ?
            """,
            (id_contrato, nfactura),
        )

        self.conn.commit()

    # ============================================================
    #  RECÁLCULO SELECCIONADO
    # ============================================================
    def recalcular_seleccionada(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Atención", "Debe seleccionar una factura.")
            return

        id_contrato = int(self.tabla.item(fila, 0).text())
        nfactura = self.tabla.item(fila, 1).text()

        try:
            self.recalcular_factura(id_contrato, nfactura)
            QMessageBox.information(
                self, "OK", f"Factura {nfactura} recalculada correctamente."
            )
            self.cargar_facturas()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ============================================================
    #  RECÁLCULO EN LOTE
    # ============================================================
    def recalcular_todas(self):
        filas = self.tabla.rowCount()
        if filas == 0:
            QMessageBox.information(
                self, "Nada que hacer", "No hay facturas pendientes."
            )
            return

        ok = QMessageBox.question(
            self,
            "Confirmar",
            "¿Desea recalcular TODAS las facturas pendientes?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if ok != QMessageBox.Yes:
            return

        errores = []
        for i in range(filas):
            id_contrato = int(self.tabla.item(i, 0).text())
            nfactura = self.tabla.item(i, 1).text()

            try:
                self.recalcular_factura(id_contrato, nfactura)
            except Exception as e:
                errores.append(f"{nfactura}: {e}")

        self.cargar_facturas()

        if errores:
            QMessageBox.warning(
                self,
                "Finalizado con errores",
                "Algunas facturas no pudieron recalcularse:\n" + "\n".join(errores),
            )
        else:
            QMessageBox.information(
                self, "OK", "Todas las facturas recalculadas correctamente."
            )

    # ============================================================
    #  CERRAR
    # ============================================================
    def cerrar(self):
        self.conn.close()
        self.close()
