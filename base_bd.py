# ------------------------------------------#
# Modulo: base_bd.py                        #
# Description: Maneja la base de datos      #
# Author: Antonio Morales                   #
# Fecha: 2025-12-01                         #
# ------------------------------------------#

import sqlite3


class BaseBD:
    """
    Capa de acceso a datos para SQLite.
    Gestiona conexión, ejecución de consultas y utilidades básicas.
    """

    def __init__(self, ruta_bd):
        self.ruta = ruta_bd
        self.conn = sqlite3.connect(self.ruta)
        self.conn.row_factory = sqlite3.Row  # Acceso por nombre de columna

    # ---------------------------------------------------------
    # EJECUTAR (INSERT, UPDATE, DELETE)
    # ---------------------------------------------------------
    def ejecutar(self, sql, params=()):
        """
        Ejecuta una sentencia SQL que modifica la BD.
        Devuelve el cursor para permitir obtener lastrowid si se necesita.
        """
        try:
            cur = self.conn.cursor()
            cur.execute(sql, params)
            self.conn.commit()
            return cur
        except Exception as e:
            raise Exception(
                f"[BD] Error al ejecutar SQL: {e}\nSQL: {sql}\nParams: {params}"
            )

    # ---------------------------------------------------------
    # CONSULTAR (SELECT)
    # ---------------------------------------------------------
    def consultar(self, sql, params=()):
        """
        Ejecuta una consulta SELECT y devuelve todas las filas.
        """
        try:
            cur = self.conn.cursor()
            cur.execute(sql, params)
            return cur.fetchall()
        except Exception as e:
            raise Exception(
                f"[BD] Error al consultar SQL: {e}\nSQL: {sql}\nParams: {params}"
            )

    # ---------------------------------------------------------
    # EJECUTAR MUCHAS (executemany)
    # ---------------------------------------------------------
    def ejecutar_muchos(self, sql, lista_tuplas):
        """
        Ejecuta una sentencia SQL con múltiples tuplas (executemany).
        """
        try:
            cur = self.conn.cursor()
            cur.executemany(sql, lista_tuplas)
            self.conn.commit()
            return cur
        except Exception as e:
            raise Exception(f"[BD] Error en ejecutemany: {e}\nSQL: {sql}")

    # ---------------------------------------------------------
    # TRANSACCIONES MANUALES
    # ---------------------------------------------------------
    def iniciar_transaccion(self):
        self.conn.execute("BEGIN")

    def confirmar_transaccion(self):
        self.conn.commit()

    def cancelar_transaccion(self):
        self.conn.rollback()

    # ---------------------------------------------------------
    # UTILIDADES
    # ---------------------------------------------------------
    def obtener_id_postal(self, codigo_postal):
        """
        Compatibilidad con código antiguo.
        En tu BD, el id_postal ES el código postal.
        """
        return codigo_postal

    # ---------------------------------------------------------
    # CIERRE DE CONEXIÓN
    # ---------------------------------------------------------
    def close(self):
        """
        Cierra la conexión a la base de datos.
        """
        try:
            self.conn.close()
        except Exception:
            pass


# Fin del archivo base_bd.py
