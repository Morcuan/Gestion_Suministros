import sqlite3

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMessageBox, QSizePolicy, QVBoxLayout, QWidget

from form_contrato import FormContrato


class NuevoContrato(QWidget):
    """
    Módulo funcional para dar de alta un contrato nuevo.
    Integrado en el contenedor central de MainWindow.
    """
    cerrado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.db_path = "data/almacen.db"

        # ------------------------------------------------------------
        # CONTENEDOR PRINCIPAL DEL MÓDULO
        # ------------------------------------------------------------
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.setLayout(layout)

        # ------------------------------------------------------------
        # FORMULARIO DE CONTRATO
        # ------------------------------------------------------------
        self.form = FormContrato(modo="nuevo", parent=self)
        layout.addWidget(self.form)

        # Ajustes de tamaño dentro del contenedor
        self.form.setMinimumHeight(650)
        self.form.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ------------------------------------------------------------
        # SEÑALES
        # ------------------------------------------------------------
        self.form.contrato_guardado.connect(self.insertar_contrato)
        self.form.cancelado.connect(self.cerrar)

        # ------------------------------------------------------------
        # CARGA DE COMPAÑÍAS
        # ------------------------------------------------------------
        self.cargar_companias()

    # ------------------------------------------------------------
    #  Cargar compañías desde la BD
    # ------------------------------------------------------------
    def cargar_companias(self):
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("SELECT nombre FROM companias ORDER BY nombre")
            filas = cur.fetchall()
            con.close()

            for (nombre,) in filas:
                self.form.compania.addItem(nombre)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las compañías:\n{e}")

    # ------------------------------------------------------------
    #  Comprobación de existencia de CP
    # ------------------------------------------------------------
    def existe_cp(self, cp):
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM cpostales WHERE codigo_postal = ?", (cp,))
            existe = cur.fetchone()[0] > 0
            con.close()
            return existe

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error comprobando código postal:\n{e}")
            return False

    # ------------------------------------------------------------
    #  Inserción transaccional del contrato
    # ------------------------------------------------------------
    def insertar_contrato(self, datos):
        ident = datos["identificacion"]
        ener = datos["energia"]
        gas = datos["gastos"]

        con = None
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()

            con.execute("BEGIN")

            # 1. Identificación
            cur.execute("""
                INSERT INTO contratos_identificacion
                (ncontrato, suplemento, compania, codigo_postal,
                 fec_inicio, fec_final, fec_anulacion, estado,
                 efec_suple, fin_suple)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ident["ncontrato"],
                ident["suplemento"],
                ident["compania"],
                ident["codigo_postal"],
                ident["fec_inicio"],
                ident["fec_final"],
                ident["fec_anulacion"],
                ident["estado"],
                ident["efec_suple"],
                ident["fin_suple"]
            ))

            id_contrato = cur.lastrowid

            # 2. Energía
            cur.execute("""
                INSERT INTO contratos_energia
                (id_contrato, ppunta, pvalle, pv_ppunta, pv_pvalle,
                 pv_conpunta, pv_conllano, pv_convalle,
                 vertido, excedentes, pv_excedent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_contrato,
                ener["ppunta"],
                ener["pvalle"],
                ener["pv_ppunta"],
                ener["pv_pvalle"],
                ener["pv_conpunta"],
                ener["pv_conllano"],
                ener["pv_convalle"],
                1 if ener["vertido"] else 0,
                ener["excedentes"],
                ener["pv_excedent"]
            ))

            # 3. Gastos
            cur.execute("""
                INSERT INTO contratos_gastos
                (id_contrato, bono_social, alq_contador, otros_gastos,
                 i_electrico, iva)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                id_contrato,
                gas["bono_social"],
                gas["alq_contador"],
                gas["otros_gastos"],
                gas["i_electrico"],
                gas["iva"]
            ))

            con.commit()
            con.close()

            QMessageBox.information(
                self,
                "Contrato guardado",
                "El contrato se ha guardado correctamente."
            )

            # 🔁 Tras guardar, cerramos el módulo → MainWindow volverá al inicio
            self.cerrar()

        except Exception as e:
            if con is not None:
                con.rollback()
                con.close()
            QMessageBox.critical(self, "Error", f"No se pudo guardar el contrato:\n{e}")

    # ------------------------------------------------------------
    #  Cierre del módulo
    # ------------------------------------------------------------
    def cerrar(self):
        # No cerramos ventana (no es independiente), solo avisamos al MainWindow
        self.cerrado.emit()
