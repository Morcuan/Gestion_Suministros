# ------------------------------------------#
# Modulo: contrato_baja.py                  #
# Description: Maneja la baja de contratos  #
# Author: Antonio Morales                   #
# Fecha: 2025-12-01                         #
# ------------------------------------------#

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from aux_database import anulacion_contrato, obtener_contrato_por_numero


# ---------------------------------------------------------
# Validación del estado antes de anular
# ---------------------------------------------------------
def validar_estado_para_baja(parent, numero_contrato):
    """
    Valida si un contrato puede ser anulado según las reglas del sistema.
    Reglas:
      - No se puede anular si ya está ANULADO
      - No se puede anular si está CADUCADO
      - Se puede anular si está ACTIVO, PENDIENTE o REHABILITADO
    """

    contrato = obtener_contrato_por_numero(numero_contrato)

    if not contrato:
        QMessageBox.critical(
            parent, "Error", "El contrato no existe en la base de datos."
        )
        return False

    estado_actual = contrato[6].upper().strip()

    if estado_actual == "ANULADO":
        QMessageBox.warning(parent, "No permitido", "El contrato ya está anulado.")
        return False

    if estado_actual == "CADUCADO":
        QMessageBox.warning(
            parent,
            "No permitido",
            "El contrato está caducado y no puede ser anulado.",
        )
        return False

    if estado_actual in ("ACTIVO", "PENDIENTE", "REHABILITADO"):
        return True

    QMessageBox.warning(
        parent,
        "No permitido",
        f"El contrato está en un estado no anulable: {estado_actual}",
    )
    return False


# ---------------------------------------------------------
# Diálogo de confirmación de baja
# ---------------------------------------------------------
class ConfirmacionBajaDialog(QDialog):
    def __init__(self, numero_contrato, estado_actual, parent=None):
        super().__init__(parent)

        self.numero_contrato = numero_contrato
        self.estado_actual = estado_actual

        self.setWindowTitle("Confirmar anulación")
        self.setModal(True)
        self.resize(350, 180)

        layout = QVBoxLayout(self)

        label = QLabel(
            f"¿Desea anular el contrato?\n\n"
            f"Número: {numero_contrato}\n"
            f"Estado actual: {estado_actual}"
        )
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        botones = QHBoxLayout()
        btn_si = QPushButton("Sí")
        btn_no = QPushButton("No")

        btn_si.clicked.connect(self.confirmar)
        btn_no.clicked.connect(self.reject)

        botones.addWidget(btn_si)
        botones.addWidget(btn_no)
        layout.addLayout(botones)

    def confirmar(self):
        if not validar_estado_para_baja(self, self.numero_contrato):
            self.reject()
            return

        try:
            anulacion_contrato(self.numero_contrato)
            QMessageBox.information(
                self,
                "Contrato anulado",
                f"El contrato {self.numero_contrato} ha sido anulado correctamente.",
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo registrar la anulación.\n{e}",
            )
            self.reject()


# ---------------------------------------------------------
# Punto de entrada desde la ventana de detalles
# ---------------------------------------------------------
def mostrar_confirmacion_baja(parent, numero_contrato):
    estado_actual = parent.label_estado.text().strip()
    dialogo = ConfirmacionBajaDialog(numero_contrato, estado_actual, parent)
    return dialogo.exec() == QDialog.Accepted


# ---------------------------------------------------------
# Clase original (NO SE TOCA)
# ---------------------------------------------------------
class ContratoBaja:
    def __init__(self, bd, parent=None):
        self.bd = bd
        self.parent = parent

    def abrir(self, numero_contrato=None):
        parent = self.parent

        # Si no viene número (no debería ocurrir desde menú), avisar
        if not numero_contrato:
            QMessageBox.warning(
                parent, "Aviso", "Debe introducir un número de contrato."
            )
            return

        # Validar existencia del contrato
        contrato = obtener_contrato_por_numero(numero_contrato)
        if not contrato:
            QMessageBox.critical(
                parent,
                "Error",
                f"El contrato {numero_contrato} no existe en la base de datos.",
            )
            return

        # Estado actual desde la BD
        estado_actual = contrato[6].strip()

        # Usar el flujo oficial de anulación (diálogo centralizado)
        dialogo = ConfirmacionBajaDialog(numero_contrato, estado_actual, parent)

        if dialogo.exec() == QDialog.Accepted:
            # Si el parent es una ventana con lista, refrescarla
            try:
                if hasattr(parent, "cargar_contratos"):
                    parent.cargar_contratos()
            except Exception:
                pass
