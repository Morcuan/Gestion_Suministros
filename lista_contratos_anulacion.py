# ------------------------------------------------------------
# lista_contratos_anulacion.py
# ------------------------------------------------------------
# Lista de contratos anulables (solo suplemento activo)
# para iniciar el proceso de anulación.
# ------------------------------------------------------------

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from db import get_conn
from form_anulacion import FormAnulacion  # <-- ahora sí, formulario correcto


class ListaContratosAnulacion(QWidget):
    """
    Lista de contratos anulables (solo suplemento activo).
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._parent_ref = parent
        self.setWindowTitle("Anulación de contratos")
        self.conn = get_conn()

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(
            [
                "Nº contrato",
                "Suplemento",
                "Efecto",
                "Fin",
                "Estado",
                "Compañía",
                "Población",
            ]
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)

        # Botones
        self.btn_anular = QPushButton("Anular contrato")
        self.btn_cancelar = QPushButton("Cancelar")

        self.btn_anular.clicked.connect(self.on_anular)
        self.btn_cancelar.clicked.connect(self.volver_menu)

        layout_botones = QHBoxLayout()
        layout_botones.addWidget(self.btn_anular)
        layout_botones.addStretch()
        layout_botones.addWidget(self.btn_cancelar)

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.tabla)
        layout.addLayout(layout_botones)
        self.setLayout(layout)

        self.cargar_contratos()

    # ------------------------------------------------------------
    # Cargar contratos anulables
    # ------------------------------------------------------------
    def cargar_contratos(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT ncontrato, suplemento, efec_suple, fin_suple, estado,
                   compania, poblacion
            FROM vista_contratos
            WHERE estado = 'Activo'
            ORDER BY ncontrato, suplemento
            """
        )
        rows = cursor.fetchall()

        self.tabla.setRowCount(len(rows))

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(i, j, item)

    # ------------------------------------------------------------
    # Obtener referencia al MainWindow
    # ------------------------------------------------------------
    def get_mainwindow(self):
        w = self._parent_ref
        while w is not None and not hasattr(w, "cargar_modulo"):
            w = w.parent()
        return w

    # ------------------------------------------------------------
    # Botón cancelar → volver al menú
    # ------------------------------------------------------------
    def volver_menu(self):
        main = self.get_mainwindow()
        if main is None:
            QMessageBox.critical(
                self, "Error", "No se pudo localizar la ventana principal."
            )
            return
        main.volver_inicio()

    # ------------------------------------------------------------
    # Botón anular → abrir formulario de anulación
    # ------------------------------------------------------------
    def on_anular(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Atención", "Debe seleccionar un contrato.")
            return

        # Datos visibles
        ncontrato = self.tabla.item(fila, 0).text()
        suplemento = self.tabla.item(fila, 1).text()
        efec_suple = self.tabla.item(fila, 2).text()
        fin_suple = self.tabla.item(fila, 3).text()
        estado = self.tabla.item(fila, 4).text()

        datos = {
            "ncontrato": ncontrato,
            "suplemento": suplemento,
            "efec_suple": efec_suple,
            "fin_suple": fin_suple,
            "estado": estado,
        }

        # Obtener MainWindow real
        main = self.get_mainwindow()
        if main is None:
            QMessageBox.critical(
                self, "Error", "No se pudo localizar la ventana principal."
            )
            return

        # Crear formulario de anulación
        form = FormAnulacion(datos, parent=main)
        form.anulacion_confirmada.connect(self.procesar_anulacion)
        form.cancelado.connect(self.reabrir_lista)

        # Cargar el formulario dentro del marco principal
        main.cargar_modulo(form, f"Anulación del contrato {ncontrato}-{suplemento}")

    # ------------------------------------------------------------
    # Procesar anulación (UPDATE en BD)
    # ------------------------------------------------------------
    def procesar_anulacion(self, datos):
        ncontrato = datos["ncontrato"]
        suplemento = datos["suplemento"]
        fec_anul = datos["fec_anulacion"]

        cursor = self.conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE contratos_identificacion
                SET
                    fec_anulacion = ?,
                    fin_suple = ?,
                    estado = 'Anulado'
                WHERE ncontrato = ? AND suplemento = ?
                """,
                (fec_anul, fec_anul, ncontrato, suplemento),
            )
            self.conn.commit()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo anular el contrato:\n{e}")
            return

        QMessageBox.information(
            self,
            "Anulación realizada",
            f"Contrato {ncontrato}-{suplemento} anulado correctamente.",
        )

        # Recargar la tabla para que desaparezca el contrato anulado
        self.cargar_contratos()

    # ------------------------------------------------------------
    # Cancelar desde el formulario
    # ------------------------------------------------------------
    def reabrir_lista(self):
        pass
