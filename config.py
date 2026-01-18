# ------------------------------------------------------#
# Modulo: config.py                                     #
# Descripción: Gestión de configuración persistente     #
#              para la aplicación                       #
# Autor: Antonio Morales                                #
# Fecha: 2026-01-11                                     #
# ------------------------------------------------------#

import json
import os

CONFIG_FILE = "data/config.json"

# Valores por defecto
CONFIG_DEFAULT = {"tema": "clara"}


def cargar_config():
    """
    Carga la configuración desde el archivo JSON.
    Si no existe, devuelve la configuración por defecto.
    """
    if not os.path.exists(CONFIG_FILE):
        return CONFIG_DEFAULT.copy()

    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return CONFIG_DEFAULT.copy()


def guardar_config(config):
    """
    Guarda la configuración en el archivo JSON.
    """
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[CONFIG] No se pudo guardar la configuración: {e}")
