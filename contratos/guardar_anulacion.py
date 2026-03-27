# guardar_anulacion.py

from datetime import datetime, date


def validar_fecha(f):
    if f == "":
        return True, None
    try:
        dt = datetime.strptime(f, "%d/%m/%Y")
        return True, dt.strftime("%Y-%m-%d")
    except ValueError:
        return False, "Formato de fecha incorrecto. Use dd/mm/yyyy."


def guardar_anulacion(
    conn,
    ncontrato,
    suplemento_vigente,
    fec_anulacion_str,
    suple_futuro,
    fec_inicio,  # <<< NUEVO
):
    ok, result = validar_fecha(fec_anulacion_str)
    if not ok:
        return False, result

    fec_anulacion_iso = result
    cur = conn.cursor()

    hoy = date.today()
    fec_inicio_dt = datetime.strptime(fec_inicio, "%Y-%m-%d").date()

    es_contrato_futuro = fec_inicio_dt > hoy

    # ---------------------------------------------------------
    # REHABILITACIÓN
    # ---------------------------------------------------------
    if fec_anulacion_iso is None:

        if es_contrato_futuro:
            # Rehabilitar TODOS los suplementos del contrato
            cur.execute(
                """
                UPDATE contratos_identificacion
                SET fec_anulacion = NULL
                WHERE ncontrato = ?;
                """,
                (ncontrato,),
            )
        else:
            # Rehabilitar suplemento vigente
            cur.execute(
                """
                UPDATE contratos_identificacion
                SET fec_anulacion = NULL
                WHERE ncontrato = ?
                  AND suplemento = ?;
                """,
                (ncontrato, suplemento_vigente),
            )

            # Rehabilitar suplemento futuro si existe
            if suple_futuro:
                suple_f, efec_futuro = suple_futuro
                cur.execute(
                    """
                    UPDATE contratos_identificacion
                    SET fec_anulacion = NULL
                    WHERE ncontrato = ?
                      AND suplemento = ?;
                    """,
                    (ncontrato, suple_f),
                )

        conn.commit()
        return True, "Contrato rehabilitado correctamente."

    # ---------------------------------------------------------
    # ANULACIÓN
    # ---------------------------------------------------------
    # Suplemento vigente
    cur.execute(
        """
        UPDATE contratos_identificacion
        SET fec_anulacion = ?
        WHERE ncontrato = ?
          AND suplemento = ?;
        """,
        (fec_anulacion_iso, ncontrato, suplemento_vigente),
    )

    # Suplemento futuro
    if suple_futuro:
        suple_f, efec_futuro = suple_futuro
        cur.execute(
            """
            UPDATE contratos_identificacion
            SET fec_anulacion = efec_suple
            WHERE ncontrato = ?
              AND suplemento = ?;
            """,
            (ncontrato, suple_f),
        )

    conn.commit()
    return True, "Contrato anulado correctamente."
