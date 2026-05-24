# ------------------------------------------------------------
# Módulo: db_init.py
# Limpieza y reinicialización de la base de datos
# Gestión Suministros 2.0
# ------------------------------------------------------------
# Este módulo recibe la CONEXIÓN completa (conn)
# y crea su propio cursor interno.
# ------------------------------------------------------------

TABLAS_A_VACIAR = [
    "companias",
    "contratos_energia",
    "contratos_energia_test",
    "contratos_gastos",
    "contratos_gastos_test",
    "contratos_identificacion",
    "contratos_identificacion_test",
    "estadisticas_mensuales",
    "factura_calculos",
    "factura_calculos_test",
    "facturas",
    "facturas_test",
    "saldo_cloud",
    "saldo_cloud_test",
]


def limpiar_tablas(cursor):
    for tabla in TABLAS_A_VACIAR:
        try:
            cursor.execute(f"DELETE FROM {tabla};")
            print(f"✔ Registros eliminados en {tabla}")
        except Exception as e:
            print(f"⚠ No se pudo vaciar {tabla}: {e}")


def reiniciar_secuencias(cursor):
    try:
        cursor.execute("DELETE FROM sqlite_sequence;")
        print("✔ Secuencias reiniciadas")

        cursor.execute("""
            INSERT INTO sqlite_sequence (name, seq)
            VALUES ('contratos_identificacion_test', 900000)
            ON CONFLICT(name) DO UPDATE SET seq = 900000;
        """)
        print("✔ contratos_identificacion_test inicializado a 900000")

    except Exception as e:
        print(f"⚠ Error reiniciando secuencias: {e}")


def inicializar_saldos(cursor, saldo_inicial):
    try:
        cursor.execute("DELETE FROM saldo_cloud;")
        cursor.execute(
            "INSERT INTO saldo_cloud (ncontrato, saldo) VALUES (1, ?);",
            (saldo_inicial,),
        )
        print("✔ saldo_cloud inicializado")
    except Exception as e:
        print(f"⚠ Error inicializando saldo_cloud: {e}")

    try:
        cursor.execute("DELETE FROM saldo_cloud_inicial_test;")
        cursor.execute(
            """
            INSERT INTO saldo_cloud_inicial_test (id, saldo_inicial, fecha)
            VALUES (1, ?, DATE('now'));
            """,
            (saldo_inicial,),
        )
        print("✔ saldo_cloud_inicial_test inicializado")
    except Exception as e:
        print(f"⚠ Error inicializando saldo_cloud_inicial_test: {e}")


def ejecutar_limpieza(conn, saldo_inicial):
    print("=== INICIO LIMPIEZA BD ===")

    cursor = conn.cursor()

    limpiar_tablas(cursor)
    reiniciar_secuencias(cursor)
    inicializar_saldos(cursor, saldo_inicial)

    conn.commit()

    print("=== LIMPIEZA COMPLETADA ===")
