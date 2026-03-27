# guardar_anulacion.py

from datetime import datetime


def validar_fecha(f):
    if f == "":
        return True, None  # NULL permitido

    try:
        dt = datetime.strptime(f, "%d/%m/%Y")
        return True, dt.strftime("%Y-%m-%d")
    except ValueError:
        return False, "Formato de fecha incorrecto. Use dd/mm/yyyy."


def guardar_anulacion(
    conn, ncontrato, suplemento_vigente, fec_anulacion_str, suple_futuro
):
    ok, result = validar_fecha(fec_anulacion_str)
    if not ok:
        return False, result

    fec_anulacion_iso = result
    cur = conn.cursor()

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

    if fec_anulacion_iso is None:
        return True, "Contrato rehabilitado correctamente."
    else:
        return True, "Contrato anulado correctamente."
