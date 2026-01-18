# ------------------------------------------------------#
# Modulo: paletas.py                                   #
# Descripción: Paletas de colores para la aplicación   #
#              usando PySide6                          #
# Autor: Antonio Morales                               #
# Fecha: 2025-12-01                                    #
# ------------------------------------------------------#

from PySide6.QtGui import QColor, QPalette


# ---------------------------------------------------------
# PALETA CLARA (mejorada)
# ---------------------------------------------------------
def paleta_clara():
    paleta = QPalette()
    paleta.setColor(QPalette.Window, QColor("#f7f7f7"))
    paleta.setColor(QPalette.WindowText, QColor("#1e1e1e"))
    paleta.setColor(QPalette.Base, QColor("#ffffff"))
    paleta.setColor(QPalette.AlternateBase, QColor("#ececec"))
    paleta.setColor(QPalette.ToolTipBase, QColor("#ffffe0"))
    paleta.setColor(QPalette.ToolTipText, QColor("#000000"))
    paleta.setColor(QPalette.Text, QColor("#1e1e1e"))
    paleta.setColor(QPalette.Button, QColor("#e0e0e0"))
    paleta.setColor(QPalette.ButtonText, QColor("#1e1e1e"))
    return paleta


# ---------------------------------------------------------
# PALETA OSCURA (modernizada)
# ---------------------------------------------------------
def paleta_oscura():
    paleta = QPalette()
    paleta.setColor(QPalette.Window, QColor("#2b2b2b"))
    paleta.setColor(QPalette.WindowText, QColor("#e6e6e6"))
    paleta.setColor(QPalette.Base, QColor("#3c3f41"))
    paleta.setColor(QPalette.AlternateBase, QColor("#2b2b2b"))
    paleta.setColor(QPalette.ToolTipBase, QColor("#ffffe0"))
    paleta.setColor(QPalette.ToolTipText, QColor("#000000"))
    paleta.setColor(QPalette.Text, QColor("#ffffff"))
    paleta.setColor(QPalette.Button, QColor("#3c3f41"))
    paleta.setColor(QPalette.ButtonText, QColor("#ffffff"))
    return paleta


# ---------------------------------------------------------
# PALETA SOLAR (tema solar)
# ---------------------------------------------------------
def paleta_solar():
    paleta = QPalette()
    paleta.setColor(QPalette.Window, QColor("#fff8e1"))  # amarillo suave
    paleta.setColor(QPalette.WindowText, QColor("#4e342e"))  # marrón cálido
    paleta.setColor(QPalette.Base, QColor("#ffffff"))
    paleta.setColor(QPalette.AlternateBase, QColor("#ffecb3"))
    paleta.setColor(QPalette.ToolTipBase, QColor("#fff3cd"))
    paleta.setColor(QPalette.ToolTipText, QColor("#4e342e"))
    paleta.setColor(QPalette.Text, QColor("#4e342e"))
    paleta.setColor(QPalette.Button, QColor("#ffe082"))
    paleta.setColor(QPalette.ButtonText, QColor("#4e342e"))
    return paleta


# ---------------------------------------------------------
# PALETA AZUL PROFESIONAL
# ---------------------------------------------------------
def paleta_azul():
    paleta = QPalette()
    paleta.setColor(QPalette.Window, QColor("#e3f2fd"))
    paleta.setColor(QPalette.WindowText, QColor("#0d47a1"))
    paleta.setColor(QPalette.Base, QColor("#ffffff"))
    paleta.setColor(QPalette.AlternateBase, QColor("#bbdefb"))
    paleta.setColor(QPalette.ToolTipBase, QColor("#e1f5fe"))
    paleta.setColor(QPalette.ToolTipText, QColor("#0d47a1"))
    paleta.setColor(QPalette.Text, QColor("#0d47a1"))
    paleta.setColor(QPalette.Button, QColor("#90caf9"))
    paleta.setColor(QPalette.ButtonText, QColor("#0d47a1"))
    return paleta


# ---------------------------------------------------------
# PALETA CÁLIDA (naranjas y rojos suaves)
# ---------------------------------------------------------
def paleta_calida():
    paleta = QPalette()
    paleta.setColor(QPalette.Window, QColor("#fff3e0"))
    paleta.setColor(QPalette.WindowText, QColor("#bf360c"))
    paleta.setColor(QPalette.Base, QColor("#ffffff"))
    paleta.setColor(QPalette.AlternateBase, QColor("#ffe0b2"))
    paleta.setColor(QPalette.ToolTipBase, QColor("#ffe8cc"))
    paleta.setColor(QPalette.ToolTipText, QColor("#bf360c"))
    paleta.setColor(QPalette.Text, QColor("#bf360c"))
    paleta.setColor(QPalette.Button, QColor("#ffb74d"))
    paleta.setColor(QPalette.ButtonText, QColor("#4e342e"))
    return paleta


# ---------------------------------------------------------
# PALETA MORADA ELEGANTE
# ---------------------------------------------------------
def paleta_morada():
    paleta = QPalette()
    paleta.setColor(QPalette.Window, QColor("#f3e5f5"))
    paleta.setColor(QPalette.WindowText, QColor("#4a148c"))
    paleta.setColor(QPalette.Base, QColor("#ffffff"))
    paleta.setColor(QPalette.AlternateBase, QColor("#e1bee7"))
    paleta.setColor(QPalette.ToolTipBase, QColor("#f8e1ff"))
    paleta.setColor(QPalette.ToolTipText, QColor("#4a148c"))
    paleta.setColor(QPalette.Text, QColor("#4a148c"))
    paleta.setColor(QPalette.Button, QColor("#ce93d8"))
    paleta.setColor(QPalette.ButtonText, QColor("#4a148c"))
    return paleta
