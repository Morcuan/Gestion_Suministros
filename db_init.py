# ------------------------------------------------------------
# Módulo: db_init.py
# Limpieza y reinicialización de la base de datos
# Gestión Suministros 2.0
# ------------------------------------------------------------
# Este módulo NO abre ni cierra la conexión.
# Recibe un cursor externo desde main_window.
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

TABLAS_PROTEGIDAS = [
    "cpostales",
    "saldo_cloud_inicial_test",
    "sqlite_sequence",
    "version_motor",
    "version_motor_test",
]


def limpiar_tablas(cursor):
    for tabla in TABLAS_A_VACIAR:
        try:
            cursor.execute(f"DELETE FROM {tabla};")
            print(f"✔ Registros eliminados en {tabla}")
        except Exception as e:
            print(f"⚠ No se pudo vaciar {tabla}: {e}")


def reiniciar_secuencias(cursor):
    """
    Reinicia todas las secuencias y fija contratos_identificacion_test = 900000.
    """
    try:
        cursor.execute("DELETE FROM sqlite_sequence;")
        print("✔ Secuencias reiniciadas (sqlite_sequence)")

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


def ejecutar_limpieza(cursor, saldo_inicial):
    print("=== INICIO LIMPIEZA BD ===")

    limpiar_tablas(cursor)
    reiniciar_secuencias(cursor)
    inicializar_saldos(cursor, saldo_inicial)

    print("=== LIMPIEZA COMPLETADA ===")
