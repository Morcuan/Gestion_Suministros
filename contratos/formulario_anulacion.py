# formulario_anulacion.py

from guardar_anulacion import guardar_anulacion
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class FormularioAnulacion(QWidget):
    def __init__(
        self,
        parent,
        conn,  # <<< conexión heredada
        ncontrato,
        suplemento,
        efec_suple,
        fin_suple,
        fec_anulacion,
        suple_futuro,
    ):
        super().__init__(parent)

        self.parent = parent
        self.conn = conn  # <<< NUEVO
        self.ncontrato = ncontrato
        self.suplemento = suplemento
        self.efec_suple = efec_suple
        self.fin_suple = fin_suple
        self.fec_anulacion = fec_anulacion
        self.suple_futuro = suple_futuro

        self.crear_widgets()

    def crear_widgets(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"Contrato: {self.ncontrato}"))
        layout.addWidget(QLabel(f"Suplemento vigente: {self.suplemento}"))
        layout.addWidget(QLabel(f"Inicio: {self.efec_suple}"))
        layout.addWidget(QLabel(f"Final: {self.fin_suple}"))

        layout.addWidget(QLabel("Fecha de anulación (dd/mm/yyyy):"))
        self.entry_fec = QLineEdit()
        if self.fec_anulacion:
            self.entry_fec.setText(self.fec_anulacion)
        layout.addWidget(self.entry_fec)

        btns = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_cancelar = QPushButton("Cancelar")

        btn_guardar.clicked.connect(self.guardar)
        btn_cancelar.clicked.connect(self.cancelar)

        btns.addWidget(btn_guardar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)

    def guardar(self):
        fec = self.entry_fec.text().strip()

        ok, msg = guardar_anulacion(
            conn=self.conn,  # <<< NUEVO
            ncontrato=self.ncontrato,
            suplemento_vigente=self.suplemento,
            fec_anulacion_str=fec,
            suple_futuro=self.suple_futuro,
        )

        if ok:
            QMessageBox.information(self, "OK", msg)
            self.parent.parent.volver_menu_principal()
        else:
            QMessageBox.critical(self, "Error", msg)

    def cancelar(self):
        self.parent.parent.volver_menu_principal()
