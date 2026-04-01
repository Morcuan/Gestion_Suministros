# -------------------------------------------------------------#
# Módulo: version_motor.py                                     #
# Descripción: Utilidades para versión del motor de cálculo    #
# Autor: Antonio Morales                                       #
# Fecha: 2026-04-01                                            #
# -------------------------------------------------------------#


def obtener_version_motor(cursor):
    """
    Devuelve la versión de motor activa según la fecha actual.
    Si no encuentra ninguna, devuelve '1.0.0' como valor por defecto defensivo.
    """
    cursor.execute(
        """
        SELECT version
        FROM version_motor
        WHERE fecha_inicio <= DATE('now')
          AND (fecha_fin IS NULL OR fecha_fin >= DATE('now'))
        LIMIT 1
        """
    )
    row = cursor.fetchone()
    return row[0] if row else "1.0.0"
