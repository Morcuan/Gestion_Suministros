def guardar_factura(datos_ident, datos_energia, datos_asociados):
    """
    Inserta una factura completa en las tres tablas:
    - factura_identificacion
    - factura_energia
    - factura_asociados

    Los parámetros son diccionarios con los valores ya validados.
    """

    import sqlite3
    conn = sqlite3.connect(RUTA_BD)
    cursor = conn.cursor()

    try:
        # ------------------------------
        # 1. Insertar en factura_identificacion
        # ------------------------------
        cursor.execute("""
            INSERT INTO factura_identificacion (
                id_contrato, nfactura, inicio_factura, fin_factura,
                dias_factura, fec_emision
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datos_ident["id_contrato"],
            datos_ident["nfactura"],
            datos_ident["inicio_factura"],
            datos_ident["fin_factura"],
            datos_ident["dias_factura"],
            datos_ident["fec_emision"]
        ))

        # Obtener id_factura generado
        id_factura = cursor.lastrowid

        # ------------------------------
        # 2. Insertar en factura_energia
        # ------------------------------
        cursor.execute("""
            INSERT INTO factura_energia (
                id_factura, pot_imp_punta, pot_imp_valle, total_potencia,
                con_punta, imp_con_punta, con_llano, imp_con_llano,
                con_valle, imp_con_valle, excedentes, imp_excedentes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_factura,
            datos_energia["pot_imp_punta"],
            datos_energia["pot_imp_valle"],
            datos_energia["total_potencia"],
            datos_energia["con_punta"],
            datos_energia["imp_con_punta"],
            datos_energia["con_llano"],
            datos_energia["imp_con_llano"],
            datos_energia["con_valle"],
            datos_energia["imp_con_valle"],
            datos_energia["excedentes"],
            datos_energia["imp_excedentes"]
        ))

        # ------------------------------
        # 3. Insertar en factura_asociados
        # ------------------------------
        cursor.execute("""
            INSERT INTO factura_asociados (
                id_factura, imp_bono_social, imp_iee, alq_equipos,
                servicios, iva, dcto_saldos, solar_cloud, total_factura
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_factura,
            datos_asociados["imp_bono_social"],
            datos_asociados["imp_iee"],
            datos_asociados["alq_equipos"],
            datos_asociados["servicios"],
            datos_asociados["iva"],
            datos_asociados["dcto_saldos"],
            datos_asociados["solar_cloud"],
            datos_asociados["total_factura"]
        ))

        # ------------------------------
        # 4. Confirmar transacción
        # ------------------------------
        conn.commit()
        return True, id_factura

    except Exception as e:
        conn.rollback()
        return False, str(e)

    finally:
        conn.close()
