# --------------------------------------------#
# Modulo: base_consulta.py                    #
# Descripción: Clase base para ventanas de    #
#   consulta (contratos, facturas, consumos). #
# Autor: Antonio Morales                      #
# Fecha: 2026-02-09                           #
# --------------------------------------------#

# Esta clase base proporciona una fuente por defecto, eliminación automática al cerrar
# y un método estándar para mostrar avisos. Las ventanas de consulta específicas
# (contratos, facturas, consumos) heredan de esta clase para mantener una
# interfaz consistente y reducir código repetitivo.


# ------------------------------------------------------------
# IMPORTACIONES
# ------------------------------------------------------------
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QMessageBox, QWidget


# ------------------------------------------------------------
# CLASE BASE DE CONSULTA
# ------------------------------------------------------------
class BaseConsulta(QWidget):
    """
    Clase base ligera para ventanas de consulta.
    Proporciona:
      - Fuente por defecto
      - Eliminación automática al cerrar
      - Método estándar de avisos
    """

    # ---------------------------------------------------------
    # INICIALIZACIÓN
    # ---------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)

        # Fuente general
        self.setFont(QFont("Noto Sans", 12))

        # Al cerrar, destruir la ventana
        self.setAttribute(Qt.WA_DeleteOnClose, True)

    # ---------------------------------------------------------
    # Mostrar aviso estándar
    # ---------------------------------------------------------
    def mostrar_aviso(self, titulo, mensaje):
        QMessageBox.information(self, titulo, mensaje)
