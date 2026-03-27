# formulario_anulacion.py

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from contratos.guardar_anulacion import guardar_anulacion


class FormularioAnulacion(QWidget):
    def __init__(
        self,
        parent,
        conn,
        ncontrato,
        suplemento,
        efec_suple,
        fin_suple,
        fec_anulacion,
        suple_futuro,
        fec_inicio,  # <<< NUEVO
    ):
        super().__init__(parent)

        self.parent = parent
        self.conn = conn
        self.ncontrato = ncontrato
        self.suplemento = suplemento
        self.efec_suple = efec_suple
        self.fin_suple = fin_suple
        self.fec_anulacion = fec_anulacion
        self.suple_futuro = suple_futuro
        self.fec_inicio = fec_inicio  # <<< NUEVO

        self.crear_widgets()

    def crear_widgets(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setSpacing(12)
        layout_principal.setContentsMargins(12, 12, 12, 12)

        # =========================================================
        # 1. BLOQUE IDENTIFICACIÓN (idéntico al formulario contrato)
        # =========================================================
        gb_ident = QGroupBox("Identificación del contrato")
        layout_ident = QFormLayout()
        layout_ident.setSpacing(8)
        gb_ident.setLayout(layout_ident)

        # Campos mostrados como QLabel (no editables)
        lbl_ncontrato = QLabel(str(self.ncontrato))
        lbl_suplemento = QLabel(str(self.suplemento))
        lbl_efec_suple = QLabel(str(self.efec_suple))
        lbl_fin_suple = QLabel(str(self.fin_suple))
        lbl_fec_inicio = QLabel(str(self.fec_inicio))

        # Si quieres mostrar compañía y CP, deben pasarse desde anular_rehabilitar
        # lbl_compania = QLabel(self.compania)
        # lbl_cp = QLabel(self.cp)

        layout_ident.addRow("Número contrato:", lbl_ncontrato)
        layout_ident.addRow("Suplemento:", lbl_suplemento)
        layout_ident.addRow("Fecha inicio:", lbl_fec_inicio)
        layout_ident.addRow("Efecto suplemento:", lbl_efec_suple)
        layout_ident.addRow("Fin suplemento:", lbl_fin_suple)

        layout_principal.addWidget(gb_ident)

        # =========================================================
        # 2. FECHA DE ANULACIÓN
        # =========================================================
        lbl_fec = QLabel("Fecha de anulación (dd/mm/yyyy):")
        self.entry_fec = QLineEdit()
        if self.fec_anulacion:
            self.entry_fec.setText(self.fec_anulacion)

        layout_principal.addWidget(lbl_fec)
        layout_principal.addWidget(self.entry_fec)

        # =========================================================
        # 3. BOTONES
        # =========================================================
        botones = QHBoxLayout()
        botones.setContentsMargins(0, 12, 0, 0)

        btn_guardar = QPushButton("Guardar")
        btn_cancelar = QPushButton("Cancelar")

        btn_guardar.clicked.connect(self.guardar)
        btn_cancelar.clicked.connect(self.cancelar)

        btn_guardar.setFixedHeight(32)
        btn_cancelar.setFixedHeight(32)

        botones.addWidget(btn_guardar)
        botones.addWidget(btn_cancelar)

        layout_principal.addLayout(botones)

        # =========================================================
        # 4. ESTILO GENERAL (idéntico al formulario contrato)
        # =========================================================
        self.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
            }
            QLineEdit {
                font-size: 16px;
                padding: 3px;
            }
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                margin-top: 14px;
            }
            """
        )

        self.entry_fec.setFixedHeight(26)

    def guardar(self):
        fec = self.entry_fec.text().strip()

        ok, msg = guardar_anulacion(
            conn=self.conn,
            ncontrato=self.ncontrato,
            suplemento_vigente=self.suplemento,
            fec_anulacion_str=fec,
            suple_futuro=self.suple_futuro,
            fec_inicio=self.fec_inicio,  # <<< NUEVO
        )

        if ok:
            QMessageBox.information(self, "OK", msg)
            self.parent.volver_menu_principal()
        else:
            QMessageBox.critical(self, "Error", msg)

    def cancelar(self):
        self.parent.volver_menu_principal()
