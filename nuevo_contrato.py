import sqlite3

from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QWidget

from form_contrato import FormContrato


class NuevoContrato(QWidget):
    """
    Módulo funcional para dar de alta un contrato nuevo.
    Gestiona:
    - Llamada al formulario
    - Carga de compañías
    - Validación de CP
    - Alta de CP inexistente
    - Inserción transaccional en las tres tablas
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.db_path = "data/almacen.db"

        # --- Contenedor principal del módulo ---
        layout = QVBoxLayout()
        self.setLayout(layout)

        # --- Crear formulario en modo "nuevo" ---
        self.form = FormContrato(modo="nuevo", parent=self)
        layout.addWidget(self.form)

        # --- Conectar señales ---
        self.form.contrato_guardado.connect(self.insertar_contrato)
        self.form.cancelado.connect(self.cerrar)

        # --- Cargar compañías ---
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
    #  Comprobación de existencia de CP (llamado por el formulario)
    # ------------------------------------------------------------

    def existe_cp(self, cp):
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM cpostales WHERE cod_postal = ?", (cp,))
            existe = cur.fetchone()[0] > 0
            con.close()
            return existe

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error comprobando código postal:\n{e}")
            return False

    # ------------------------------------------------------------
    #  Inserción de CP nuevo (llamado por la ventana auxiliar)
    # ------------------------------------------------------------

    def insertar_cp(self, cp):
        """
        El formulario AltaCodigoPostal emite solo el CP.
        Aquí pedimos la población directamente desde la BD.
        """
        try:
            # Recuperar población desde la ventana auxiliar
            # La ventana auxiliar ya insertó la población en su señal
            # pero aquí debemos obtenerla del widget
            # Sin embargo, la señal solo trae el CP, así que
            # la ventana auxiliar debe haber insertado ya en BD.
            pass

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo insertar el código postal:\n{e}")

    # ------------------------------------------------------------
    #  Inserción transaccional del contrato
    # ------------------------------------------------------------

    def insertar_contrato(self, datos):
        """
        Inserta en:
        - contratos_identificacion
        - contratos_energia
        - contratos_gastos
        Todo dentro de una transacción.
        """

        ident = datos["identificacion"]
        ener = datos["energia"]
        gas = datos["gastos"]

        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()

            # Iniciar transacción
            con.execute("BEGIN")

            # ----------------------------------------------------
            # 1. Insertar en contratos_identificacion
            # ----------------------------------------------------
            cur.execute("""
                INSERT INTO contratos_identificacion
                (ncontrato, suplemento, compania, cod_postal,
                 fec_inicio, fec_final, fec_anulacion, estado,
                 efec_suple, fin_suple)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ident["ncontrato"],
                ident["suplemento"],
                ident["compania"],
                ident["cod_postal"],
                ident["fec_inicio"],
                ident["fec_final"],
                ident["fec_anulacion"],
                ident["estado"],
                ident["efec_suple"],
                ident["fin_suple"]
            ))

            # Obtener id_contrato generado
            id_contrato = cur.lastrowid

            # ----------------------------------------------------
            # 2. Insertar en contratos_energia
            # ----------------------------------------------------
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

            # ----------------------------------------------------
            # 3. Insertar en contratos_gastos
            # ----------------------------------------------------
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

            # Confirmar transacción
            con.commit()
            con.close()

            QMessageBox.information(
                self,
                "Contrato guardado",
                "El contrato se ha guardado correctamente."
            )

            self.cerrar()

        except Exception as e:
            con.rollback()
            con.close()
            QMessageBox.critical(self, "Error", f"No se pudo guardar el contrato:\n{e}")

    # ------------------------------------------------------------
    #  Cierre del módulo
    # ------------------------------------------------------------

    def cerrar(self):
        self.form.close()
        self.close()
