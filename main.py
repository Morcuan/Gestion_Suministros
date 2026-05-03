#!/usr/bin/env python3
# --------------------------------------------------#
# Modulo: main.py                                   #
# Descripción: Punto de entrada de la aplicación    #
# Autor: Antonio Morales                            #
# Fecha: 2026-02-09                                 #
# --------------------------------------------------#

import sqlite3
import sys

from PySide6.QtWidgets import QApplication

from main_window import MainWindow

DB_PATH = "data/almacen.db"


def main():
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # <<--- SOLUCIÓN A

    # Crear conexión a la base de datos (persistente durante toda la ejecución)
    conn = sqlite3.connect(DB_PATH)

    # Activar claves foráneas
    conn.execute("PRAGMA foreign_keys = ON;")

    # Permitir acceso a columnas por nombre
    conn.row_factory = sqlite3.Row

    # Pasar solo la conexión a la ventana principal
    ventana = MainWindow(conn)
    ventana.show()

    # Ejecutar la aplicación
    resultado = app.exec()

    # Cerrar la conexión al salir
    conn.close()

    sys.exit(resultado)


if __name__ == "__main__":
    main()
