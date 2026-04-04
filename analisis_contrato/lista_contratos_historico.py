# -------------------------------------------------------------#
# Módulo: lista_contratos_historico.p                          #
# Descripción: Selección de contratos                          #
# Autor: Antonio Morales                                       #
# Fecha: 2026-03                                               #
# -------------------------------------------------------------#

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from utilidades.logica_negocio import determinar_estado_contrato


class ListaContratos(QWidget):
    def __init__(self, parent=None, modo="modificacion"):
        super().__init__(parent)
        self.parent = parent
        self.modo = modo  # modificacion / anulacion

        self.conn = self.parent.conn
        self.cur = self.conn.cursor()

        self.crear_ui()
        self.cargar_datos()

    def crear_ui(self):
        layout = QVBoxLayout(self)

        titulo = QLabel("Listado de contratos")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels(
            [
                "Contrato",
                "Fec_inicio",
                "Compañía",
                "C.P.",
                "Inicio",
                "Final",
                "Anulación",
                "Estado",
            ]
        )
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)

        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.tabla)

        botones = QHBoxLayout()
        btn_sel = QPushButton("Seleccionar contrato")
        btn_sel.clicked.connect(self.seleccionar_contrato)
        botones.addWidget(btn_sel)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.cancelar)
        botones.addWidget(btn_cancelar)

        layout.addLayout(botones)

    def cargar_datos(self):
        """
        Carga solo el suplemento máximo de cada contrato.

        - En modo 'modificacion': solo estados En vigor / Futuro.
        - En modo 'anulacion': En vigor / Futuro / Anulado / Sin efecto,
          pero siempre con fin_suple >= hoy (nada caducado).
        """

        query = """
            SELECT vc.ncontrato,
                   vc.compania,
                   vc.codigo_postal,
                   vc.efec_suple,
                   vc.fin_suple,
                   vc.fec_anulacion,
                   vc.fec_inicio
            FROM vista_contratos vc
            WHERE vc.suplemento = (
                    SELECT MAX(v2.suplemento)
                    FROM vista_contratos v2
                    WHERE v2.ncontrato = vc.ncontrato
                  )
              AND (
                    DATE('now') BETWEEN vc.efec_suple AND vc.fin_suple
                    OR DATE('now') < vc.efec_suple
                  )
            ORDER BY vc.ncontrato ASC;
        """

        self.cur.execute(query)
        rows = self.cur.fetchall()

        self.tabla.setRowCount(0)
        fila_visual = 0

        for row in rows:
            ncontrato, compania, cp, efec, fin, anul, fec_inicio = row

            # Fechas de efecto de todos los suplementos del contrato
            self.cur.execute(
                "SELECT efec_suple FROM contratos_identificacion WHERE ncontrato = ?",
                (ncontrato,),
            )
            fechas = [f[0] for f in self.cur.fetchall()]

            estado = determinar_estado_contrato(
                efec_suple=efec,
                fin_suple=fin,
                fec_anulacion=anul,
                lista_fechas_efecto=fechas,
            )

            # Filtrado según modo
            if self.modo == "modificacion":
                # Solo En vigor o Futuro
                if estado in ("Anulado", "Sin efecto"):
                    continue

            elif self.modo == "anulacion":
                # Aquí ya no entran caducados por el WHERE de fechas.
                # Aceptamos En vigor, Futuro, Anulado, Sin efecto.
                pass

            self.tabla.insertRow(fila_visual)

            valores = [
                ncontrato,
                fec_inicio,
                compania,
                cp,
                efec,
                fin,
                anul,
                estado,
            ]

            for c, value in enumerate(valores):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.tabla.setItem(fila_visual, c, item)

            fila_visual += 1

    def seleccionar_contrato(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Debe seleccionar un contrato.")
            return

        ncontrato = self.tabla.item(row, 0).text()
        mw = self.window()

        if self.modo == "modificacion":
            from contratos.modificar_contrato import ModificarContrato

            widget = ModificarContrato(parent=mw, conn=self.conn, ncontrato=ncontrato)
            mw.cargar_modulo(widget, f"Modificación contrato {ncontrato}")
            return

        if self.modo == "anulacion":
            from contratos.anular_rehabilitar import AnularRehabilitar

            widget = AnularRehabilitar(parent=mw, conn=self.conn, ncontrato=ncontrato)
            mw.cargar_modulo(widget, f"Anulación contrato {ncontrato}")
            return

        QMessageBox.critical(self, "Error", f"Modo desconocido: {self.modo}")

    def cancelar(self):
        mw = self.window()
        mw.volver_inicio()
