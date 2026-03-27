# anular_rehabilitar.py

from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QWidget

from contratos.formulario_anulacion import FormularioAnulacion


class AnularRehabilitar(QWidget):
    def __init__(self, parent=None, conn=None, ncontrato=None):
        super().__init__(parent)
        self.parent = parent
        self.conn = conn
        self.cur = conn.cursor()
        self.ncontrato = ncontrato

        self.suple_vigente = None
        self.suple_futuro = None
        self.fec_inicio = None  # <<< NUEVO

        self.cargar_suplementos()
        self.crear_formulario()

    # ---------------------------------------------------------
    # CARGA DE SUPLEMENTOS
    # ---------------------------------------------------------
    def cargar_suplementos(self):

        # Suplemento vigente o futuro inmediato
        self.cur.execute(
            """
            SELECT suplemento, efec_suple, fin_suple, fec_anulacion, fec_inicio
            FROM vista_contratos
            WHERE ncontrato = ?
              AND (DATE('now') BETWEEN efec_suple AND fin_suple
                   OR DATE('now') < efec_suple)
            ORDER BY efec_suple ASC
            LIMIT 1;
            """,
            (self.ncontrato,),
        )
        self.suple_vigente = self.cur.fetchone()

        if not self.suple_vigente:
            QMessageBox.critical(self, "Error", "No se encontró suplemento vigente.")
            return

        suplemento, efec, fin, anul, fec_inicio = self.suple_vigente
        self.fec_inicio = fec_inicio  # <<< GUARDAMOS FEC_INICIO

        # Suplemento futuro (si existe)
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

        suplemento, efec, fin, anul, fec_inicio = self.suple_vigente

        self.form = FormularioAnulacion(
            parent=self.parent,  # <<< IMPORTANTE: MainWindow como parent
            conn=self.conn,
            ncontrato=self.ncontrato,
            suplemento=suplemento,
            efec_suple=efec,
            fin_suple=fin,
            fec_anulacion=anul,
            suple_futuro=self.suple_futuro,
            fec_inicio=fec_inicio,  # <<< NUEVO
        )

        layout.addWidget(self.form)
