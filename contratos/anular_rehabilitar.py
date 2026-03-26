# anular_rehabilitar.py

from formulario_anulacion import FormularioAnulacion
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QWidget


class AnularRehabilitar(QWidget):
    def __init__(self, parent=None, conn=None, ncontrato=None):
        super().__init__(parent)
        self.parent = parent
        self.conn = conn  # <<< conexión heredada
        self.cur = conn.cursor()  # <<< cursor propio
        self.ncontrato = ncontrato

        self.suple_vigente = None
        self.suple_futuro = None

        self.cargar_suplementos()
        self.crear_formulario()

    # ---------------------------------------------------------
    # CARGA DE SUPLEMENTOS
    # ---------------------------------------------------------
    def cargar_suplementos(self):

        # Suplemento vigente
        self.cur.execute(
            """
            SELECT suplemento, efec_suple, fin_suple, fec_anulacion
            FROM vista_contratos
            WHERE ncontrato = ?
              AND DATE('now') BETWEEN efec_suple AND fin_suple
            LIMIT 1;
            """,
            (self.ncontrato,),
        )
        self.suple_vigente = self.cur.fetchone()

        if not self.suple_vigente:
            QMessageBox.critical(self, "Error", "No se encontró suplemento vigente.")
            return

        # Suplemento futuro
        self.cur.execute(
            """
            SELECT suplemento, efec_suple
            FROM vista_contratos
            WHERE ncontrato = ?
              AND efec_suple > DATE('now')
            ORDER BY suplemento DESC
            LIMIT 1;
            """,
            (self.ncontrato,),
        )
        self.suple_futuro = self.cur.fetchone()

    # ---------------------------------------------------------
    # CREAR FORMULARIO
    # ---------------------------------------------------------
    def crear_formulario(self):
        layout = QVBoxLayout(self)

        suplemento, efec, fin, anul = self.suple_vigente

        self.form = FormularioAnulacion(
            parent=self,
            conn=self.conn,  # <<< conexión heredada
            ncontrato=self.ncontrato,
            suplemento=suplemento,
            efec_suple=efec,
            fin_suple=fin,
            fec_anulacion=anul,
            suple_futuro=self.suple_futuro,
        )

        layout.addWidget(self.form)
