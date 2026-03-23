# modificar_contrato.py
from PySide6.QtWidgets import QWidget

from contratos.formulario_contrato import FormularioContrato
from utilidades.utilidades_bd import obtener_companias


class ModificarContrato(QWidget):
    """
    Controlador para modificar un contrato existente.
    Carga los datos desde vista_contratos (último suplemento)
    y abre el formulario en modo modificación.
    """

    def __init__(self, parent, conn, ncontrato):
        super().__init__(parent)

        self.main_window = parent
        self.conn = conn
        self.ncontrato = ncontrato

        # ---------------------------------------------------------
        # 1. Cargar datos del contrato desde vista_contratos
        # ---------------------------------------------------------
        datos = self._cargar_datos_contrato()

        # ---------------------------------------------------------
        # 2. Crear formulario en modo modificación
        # ---------------------------------------------------------
        form = FormularioContrato(
            parent=self.main_window, conn=self.conn, modo="modificar", datos=datos
        )

        # ---------------------------------------------------------
        # 3. Cargar compañías (IMPRESCINDIBLE)
        # ---------------------------------------------------------
        cursor = self.conn.cursor()
        lista = obtener_companias(cursor)

        form.cargar_companias(lista)

        # ---------------------------------------------------------
        # 4. Mostrar formulario incrustado en la ventana principal
        # ---------------------------------------------------------
        self.main_window.cargar_modulo(form, f"Modificar contrato {self.ncontrato}")

    # ---------------------------------------------------------
    # Cargar datos desde vista_contratos
    # ---------------------------------------------------------
    def _cargar_datos_contrato(self):
        cursor = self.conn.cursor()

        sql = """
            SELECT v.*
            FROM vista_contratos v
            WHERE v.ncontrato = ?
              AND v.suplemento = (
                    SELECT MAX(v2.suplemento)
                    FROM vista_contratos v2
                    WHERE v2.ncontrato = v.ncontrato
              )
        """

        cursor.execute(sql, (self.ncontrato,))
        fila = cursor.fetchone()

        if fila is None:
            raise ValueError(f"No se encontró el contrato {self.ncontrato}")

        columnas = [desc[0] for desc in cursor.description]
        d = dict(zip(columnas, fila))

        # Adaptar a la estructura que espera cargar_datos()
        datos = {
            "identificacion": {
                "ncontrato": d["ncontrato"],
                "suplemento": d["suplemento"],
                "compania": d["compania"],
                "codigo_postal": d["codigo_postal"],
                "fec_inicio": d["fec_inicio"],
                "fec_final": d["fec_final"],
                "efec_suple": d["efec_suple"],
                "fin_suple": d["fin_suple"],
                "fec_anulacion": d["fec_anulacion"],
            },
            "energia": {
                "ppunta": d["ppunta"],
                "pvalle": d["pvalle"],
                "pv_ppunta": d["pv_ppunta"],
                "pv_pvalle": d["pv_pvalle"],
                "pv_conpunta": d["pv_conpunta"],
                "pv_conllano": d["pv_conllano"],
                "pv_convalle": d["pv_convalle"],
                "vertido": d["vertido"],
                "pv_excedentes": d["pv_excedent"],
            },
            "gastos": {
                "bono_social": d["bono_social"],
                "i_electrico": d["i_electrico"],
                "alq_contador": d["alq_contador"],
                "otros_gastos": d["otros_gastos"],
                "iva": d["iva"],
            },
        }

        return datos
