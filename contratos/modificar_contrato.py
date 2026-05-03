# ---------------------------------------------------------
# Modulo: modificar_contrato.py
# Widget contenedor + controlador de modificación
# ---------------------------------------------------------

from PySide6.QtWidgets import QVBoxLayout, QWidget

from contratos.formulario_contrato import FormularioContrato
from contratos.guardar_modificacion import GuardarModificacion
from utilidades.logica_negocio import convertir_a_iso


class ModificarContrato(QWidget):
    """
    Widget que contiene el formulario de contrato en modo modificación
    y coordina la lógica de guardado mediante GuardarModificacion.
    """

    def __init__(self, parent, conn, ncontrato):
        super().__init__(parent)

        self.main_window = parent
        self.conn = conn
        self.cursor = conn.cursor()
        self.ncontrato = ncontrato

        layout = QVBoxLayout(self)

        # ---------------------------------------------------------
        # 1. Cargar datos del contrato desde vista_contratos
        # ---------------------------------------------------------
        datos = self._cargar_datos_contrato()

        # ---------------------------------------------------------
        # 2. Crear formulario en modo modificación
        # ---------------------------------------------------------
        self.form = FormularioContrato(
            parent=self.main_window,
            conn=self.conn,
            modo="modificar",
            datos=datos,
        )
        self.form.cargar_datos(datos)

        # ---------------------------------------------------------
        # 3. Conectar botón GUARDAR
        # ---------------------------------------------------------
        self.form.btn_guardar.clicked.connect(self._guardar_modificacion)

        layout.addWidget(self.form)

    # ---------------------------------------------------------
    # Slot del botón GUARDAR
    # ---------------------------------------------------------
    def _guardar_modificacion(self):

        controlador = GuardarModificacion(
            parent=self.main_window,
            conn=self.conn,
            cursor=self.cursor,
            datos_originales=self.datos_originales,
            formulario=self.form,
        )

        controlador.guardar()

    # ---------------------------------------------------------
    # Cargar suplemento actual REAL desde la BD
    # ---------------------------------------------------------
    def _cargar_suplemento_actual(self):
        sql = """
            SELECT suplemento
            FROM contratos_identificacion
            WHERE ncontrato = ?
            ORDER BY suplemento DESC
            LIMIT 1
        """
        self.cursor.execute(sql, (self.ncontrato,))
        fila = self.cursor.fetchone()
        return fila[0] if fila else 0

    # ---------------------------------------------------------
    # Cargar datos desde vista_contratos (último suplemento)
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

        # ---------------------------------------------------------
        # NORMALIZAR FECHAS A ISO PARA EL FORMULARIO
        # ---------------------------------------------------------
        def iso(valor):
            if valor is None or valor == "":
                return None

            s = str(valor).strip()

            # Ya es ISO
            if "-" in s and len(s) == 10 and s[4] == "-" and s[7] == "-":
                return s

            # dd/mm/yyyy
            if "/" in s:
                return convertir_a_iso(s)

            # Heurística: si empieza por año
            if len(s) >= 4 and s[:4].isdigit():
                return s

            # Último recurso
            try:
                return convertir_a_iso(s)
            except Exception:
                return None

        datos = {
            "identificacion": {
                "ncontrato": d["ncontrato"],
                "suplemento": d["suplemento"],
                "compania": d["compania"],
                "codigo_postal": d["codigo_postal"],
                "fec_inicio": iso(d["fec_inicio"]),
                "fec_final": iso(d["fec_final"]),
                "efec_suple": iso(d["efec_suple"]),
                "fin_suple": iso(d["fin_suple"]),
                "fec_anulacion": iso(d["fec_anulacion"]),
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

        # Datos originales para GuardarModificacion
        suplemento_real = self._cargar_suplemento_actual()

        self.datos_originales = {
            **datos["identificacion"],
            **datos["energia"],
            **datos["gastos"],
        }

        self.datos_originales["ncontrato"] = datos["identificacion"]["ncontrato"]
        self.datos_originales["suplemento"] = suplemento_real

        return datos
