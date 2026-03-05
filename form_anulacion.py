# ------------------------------------------------------------
# form_anulacion.py
# ------------------------------------------------------------

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from estilo import aplicar_estilo_campo
from utils import a_ddmm, convertir_fecha_a_iso, validar_fecha


class FormAnulacion(QWidget):
    anulacion_confirmada = Signal(dict)
    cancelado = Signal()

    def __init__(self, datos_contrato: dict, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Anulación de contrato")
        self.datos = datos_contrato

        self.bloque = self.crear_bloque()

        self.btn_guardar = QPushButton("Anular contrato")
        self.btn_cancelar = QPushButton("Cancelar")

        self.btn_guardar.clicked.connect(self.on_guardar)
        self.btn_cancelar.clicked.connect(lambda: self.cancelado.emit())

        layout = QVBoxLayout()
        layout.addWidget(self.bloque)

        botones = QHBoxLayout()
        botones.addStretch()
        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_cancelar)

        layout.addLayout(botones)
        self.setLayout(layout)

        self.cargar_datos()

    # ------------------------------------------------------------
    def crear_bloque(self):
        box = QGroupBox("Datos del contrato")
        layout = QFormLayout()

        self.ncontrato = QLineEdit()
        self.ncontrato.setReadOnly(True)

        self.suplemento = QLineEdit()
        self.suplemento.setReadOnly(True)

        self.efec_suple = QLineEdit()
        self.efec_suple.setReadOnly(True)

        self.fin_suple = QLineEdit()
        self.fin_suple.setReadOnly(True)

        self.estado = QLineEdit()
        self.estado.setReadOnly(True)

        self.fec_anulacion = QLineEdit()
        aplicar_estilo_campo(self.fec_anulacion)

        layout.addRow("Nº contrato:", self.ncontrato)
        layout.addRow("Suplemento vigente:", self.suplemento)
        layout.addRow("Efecto suplemento:", self.efec_suple)
        layout.addRow("Fin suplemento:", self.fin_suple)
        layout.addRow("Estado:", self.estado)
        layout.addRow("Fecha anulación (dd/mm/yyyy):", self.fec_anulacion)

        box.setLayout(layout)
        return box

    # ------------------------------------------------------------
    def cargar_datos(self):
        d = self.datos

        self.ncontrato.setText(str(d.get("ncontrato", "")))
        self.suplemento.setText(str(d.get("suplemento", "")))

        self.efec_suple.setText(a_ddmm(d.get("efec_suple")))
        self.fin_suple.setText(a_ddmm(d.get("fin_suple")))
        self.estado.setText(str(d.get("estado", "")))

    # ------------------------------------------------------------
    def on_guardar(self):
        f = self.fec_anulacion.text().strip()

        # Validación formato
        if not validar_fecha(f):
            QMessageBox.warning(
                self, "Error", "Formato de fecha inválido (dd/mm/yyyy)."
            )
            return

        # Conversión a ISO
        try:
            fec_anul_iso = convertir_fecha_a_iso(f)
        except ValueError:
            QMessageBox.warning(self, "Error", "La fecha de anulación no es válida.")
            return

        efec_iso = self.datos["efec_suple"]
        fin_iso = self.datos["fin_suple"]

        # Validación de estado
        if self.datos["estado"] == "Anulado":
            QMessageBox.warning(self, "Error", "El contrato ya está anulado.")
            return

        # Validación de rango
        if not (efec_iso <= fec_anul_iso <= fin_iso):
            QMessageBox.warning(
                self,
                "Error",
                "La fecha de anulación debe estar entre la fecha de efecto y el fin del suplemento.",
            )
            return

        # Emitir datos para el UPDATE (sin id_contrato)
        self.anulacion_confirmada.emit(
            {
                "ncontrato": self.datos["ncontrato"],
                "suplemento": self.datos["suplemento"],
                "fec_anulacion": fec_anul_iso,
            }
        )

        QMessageBox.information(self, "OK", "Contrato anulado correctamente.")
        self.close()
