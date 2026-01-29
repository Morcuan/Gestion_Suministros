import sys
import sqlite3

from PySide6.QtWidgets import QApplication
from main_window import MainWindow

DB_PATH = "data/almacen.db"


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
