#!/usr/bin/env python3
# --------------------------------------------------#
# Modulo: main.py                                   #
# Descripción: Punto de entrada de la aplicación    #
# Autor: Antonio Morales                            #
# Fecha: 2026-02-09                                 #
# --------------------------------------------------#

import os
import shutil
import sqlite3
import sys

from PySide6.QtWidgets import QApplication

from main_window import MainWindow

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_NAME = "gestion-suministros"

# Detección automática de entorno (Producción vs Desarrollo)
ES_PRODUCCION = BASE_DIR.startswith("/usr/share") or BASE_DIR.startswith("/opt")

if ES_PRODUCCION:
    # Entorno de Producción (Instalado mediante paquete .deb)
    DATA_DIR = os.path.join(os.path.expanduser("~"), ".local", "share", APP_NAME)
else:
    # Entorno de Desarrollo (Carpeta local Proyectos/gestion_suministros/data/)
    DATA_DIR = os.path.join(BASE_DIR, "data")

DB_PATH = os.path.join(DATA_DIR, "almacen.db")


def preparar_base_datos():
    """Asegura que el directorio de datos existe y que la BD está presente

    sin machacar datos previos en actualizaciones de producción.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    if ES_PRODUCCION:
        # En producción: si no existe la BD del usuario, copiar la plantilla del paquete
        if not os.path.exists(DB_PATH):
            template_path = os.path.join(BASE_DIR, "data", "almacen.db")
            if os.path.exists(template_path):
                shutil.copy2(template_path, DB_PATH)
                print(f"[PRODUCCIÓN] Base de datos inicializada en: {DB_PATH}")
            else:
                print(
                    f"[PRODUCCIÓN] No se encontró plantilla, se creará una nueva en: {DB_PATH}"
                )
    else:
        # En desarrollo: se trabaja directamente sobre Proyectos/gestion_suministros/data/almacen.db
        print(f"[MODO DESARROLLO] Usando base de datos local: {DB_PATH}")


def main():
    # Asegurar la persistencia y disponibilidad de la BD antes de abrirla
    preparar_base_datos()

    # Crear aplicación Qt[cite: 2]
    app = QApplication(sys.argv)  # [cite: 2]
    app.setStyle("Fusion")  # <<--- SOLUCIÓN A[cite: 2]

    # Crear conexión a la base de datos (persistente durante toda la ejecución)[cite: 2]
    conn = sqlite3.connect(DB_PATH)  # [cite: 2]

    # Activar claves foráneas[cite: 2]
    conn.execute("PRAGMA foreign_keys = ON;")  # [cite: 2]

    # Permitir acceso a columnas por nombre[cite: 2]
    conn.row_factory = sqlite3.Row  # [cite: 2]

    # Pasar solo la conexión a la ventana principal[cite: 2]
    ventana = MainWindow(conn)  # [cite: 2]
    ventana.show()  # [cite: 2]

    # Ejecutar la aplicación[cite: 2]
    resultado = app.exec()  # [cite: 2]

    # Cerrar la conexión al salir[cite: 2]
    conn.close()  # [cite: 2]

    sys.exit(resultado)  # [cite: 2]


if __name__ == "__main__":  # [cite: 2]
    main()  # [cite: 2]
