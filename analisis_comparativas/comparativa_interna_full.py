#!/usr/bin/env python3

import sqlite3

from analisis_comparativas.comparador_interno import comparar_facturacion_interna
from analisis_comparativas.crear_entorno_interno import crear_entorno_interno
from analisis_comparativas.recalculo_interno import recalcular_facturas_interno


def ejecutar_proceso_completo():
    print("\n==============================================")
    print("🔧 INICIANDO COMPARATIVA INTERNA")
    print("==============================================\n")

    # 1. Crear entorno interno
    print("1️⃣  Creando entorno interno...")
    crear_entorno_interno("data/contratos.db")
    print("✔️  Entorno interno creado.\n")

    # 2. Recalcular
    print("2️⃣  Recalculando facturas internas...")
    conn = sqlite3.connect("data/contratos.db")
    resultado = recalcular_facturas_interno(conn)
    print("✔️  Recalculo completado.")
    print("   → Total:", resultado["total"])
    print("   → Procesadas:", resultado["procesadas"])
    if resultado["errores"]:
        print("   → Errores:", resultado["errores"])
    print()

    # 3. Comparar
    print("3️⃣  Comparando facturación REAL vs INTERNA...")
    comparar_facturacion_interna(conn)

    print("\n==============================================")
    print("🏁 COMPARATIVA INTERNA FINALIZADA")
    print("==============================================\n")
