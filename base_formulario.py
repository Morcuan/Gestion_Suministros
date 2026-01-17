from PySide6.QtWidgets import QWidget, QMessageBox


class BaseFormulario(QWidget):
    """
    Clase base para formularios de captura/edición.
    Proporciona utilidades comunes para todos los módulos.
    """

    # ---------------------------------------------------------
    # MENSAJES
    # ---------------------------------------------------------
    def mostrar_error(self, mensaje):
        QMessageBox.critical(self, "Error", mensaje)

    def mostrar_aviso(self, titulo, mensaje):
        QMessageBox.warning(self, titulo, mensaje)

    def mostrar_info(self, mensaje):
        QMessageBox.information(self, "Información", mensaje)

    def preguntar(self, titulo, mensaje):
        """
        Muestra un diálogo de confirmación.
        Devuelve True si el usuario acepta.
        """
        resp = QMessageBox.question(self, titulo, mensaje)
        return resp == QMessageBox.Yes

    # ---------------------------------------------------------
    # ESTILOS DE ERROR
    # ---------------------------------------------------------
    def marcar_error(self, widget):
        """
        Marca un widget con estilo de error y le da el foco.
        """
        widget.setStyleSheet("background-color: #ffcccc;")
        widget.setFocus()

    def reset_widget(self, widget):
        """
        Limpia el estilo de un widget individual.
        """
        widget.setStyleSheet("")

    def limpiar_estilos(self, widgets=None):
        """
        Limpia estilos de error.
        Si no se pasa lista, no hace nada (compatibilidad).
        """
        if widgets:
            for w in widgets:
                w.setStyleSheet("")
