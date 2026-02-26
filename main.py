# --------------------------------------------------#
# Modulo: main.py                                   #
# Descripción: Punto de entrada de la aplicación    #
# Autor: Antonio Morales                            #
# Fecha: 2026-02-09                                 #
# --------------------------------------------------#
# Este módulo contiene la función principal que inicia la aplicación,
# establece la conexión a la base de datos y muestra la ventana principal.

# Importaciones necesarias
import sqlite3
import sys

from PySide6.QtWidgets import QApplication

from main_window import MainWindow

DB_PATH = "data/almacen.db"


# Función principal
def main():
    # Crear aplicación Qt
    app = QApplication(sys.argv)

    # Crear conexión a la base de datos (persistente durante toda la ejecución)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Pasar la conexión a la ventana principal
    ventana = MainWindow(conn, cursor)
    ventana.show()

    # Ejecutar la aplicación
    resultado = app.exec()

    # Cerrar la conexión al salir
    cursor.close()
    conn.close()

    sys.exit(resultado)


if __name__ == "__main__":
    main()
