# ------------------------------------------------------#
# Modulo: validador_bd.py                               #
# Descripción: Valida integridad y coherencia de la BD  #
# Autor: Antonio Morales                                #
# Fecha: 2026-01-11                                     #
# ------------------------------------------------------#

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "almacen.db")


def ejecutar(cur, sql):
    cur.execute(sql)
    return cur.fetchall()


def validar_tablas(cur):
    print("\n🔍 Validando existencia de tablas...")

    tablas = [
        "contratos",
        "companias",
        "cpostales",
        "facturas",
        "consumos",
        "contratos_estados",
    ]
    existentes = ejecutar(cur, "SELECT name FROM sqlite_master WHERE type='table'")

    existentes = {t[0] for t in existentes}

    for t in tablas:
        if t in existentes:
            print(f"  ✔ {t}")
        else:
            print(f"  ❌ {t} NO existe")


def validar_claves_foraneas(cur):
    print("\n🔍 Validando claves foráneas...")

    cur.execute("PRAGMA foreign_key_check")
    errores = cur.fetchall()

    if not errores:
        print("  ✔ No hay errores de claves foráneas")
    else:
        print("  ❌ Errores detectados:")
        for e in errores:
            print("   ", e)


def validar_duplicados(cur):
    print("\n🔍 Buscando duplicados en claves únicas...")

    duplicados = ejecutar(
        cur,
        """
        SELECT numero_contrato, COUNT(*)
        FROM contratos
        GROUP BY numero_contrato
        HAVING COUNT(*) > 1
    """,
    )

    if not duplicados:
        print("  ✔ No hay contratos duplicados")
    else:
        print("  ❌ Contratos duplicados:")
        for d in duplicados:
            print("   ", d)


def validar_estados(cur):
    print("\n🔍 Validando coherencia de estados...")

    inconsistentes = ejecutar(
        cur,
        """
        SELECT numero_contrato, estado
        FROM contratos_estados
        WHERE estado NOT IN ('ANULADO', 'MODIFICADO', 'REHABILITADO')
    """,
    )

    if not inconsistentes:
        print("  ✔ Estados válidos")
    else:
        print("  ❌ Estados desconocidos:")
        for i in inconsistentes:
            print("   ", i)


def validar_vista(cur):
    print("\n🔍 Probando vista_contratos...")

    try:
        datos = ejecutar(cur, "SELECT * FROM vista_contratos LIMIT 3")
        print("  ✔ Vista operativa")
        for fila in datos:
            print("   ", fila)
    except Exception as e:
        print("  ❌ Error en vista_contratos:", e)


def main():
    print("==============================================")
    print("   VALIDACIÓN DE INTEGRIDAD DE LA BASE DE DATOS")
    print("==============================================")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    validar_tablas(cur)
    validar_claves_foraneas(cur)
    validar_duplicados(cur)
    validar_estados(cur)
    validar_vista(cur)

    conn.close()

    print("\nValidación completada.")
    print("==============================================")


if __name__ == "__main__":
    main()
