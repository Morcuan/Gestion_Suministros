# --------------------------------------------#
# Modulo: lista_contratos_modificar.py        #
# Descripción: Selección de contrato a modificar
# Autor: Antonio Morales + Copilot
# Fecha: 2026-02-24
# --------------------------------------------#

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from db import (
    actualizar_suplemento_vigente,
    crear_suplemento_nuevo,
    get_conn,
    obtener_suplemento_vigente,
)
from form_modificacion import FormModificacionContrato


class ListaContratosModificar(QWidget):
    """
    Lista de contratos para seleccionar uno y modificarlo.
    Basado en lista_contratos_factura.py para mantener coherencia.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Modificar contrato")
        self.conn = get_conn()

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["Nº contrato", "Supl.", "Compañía", "Inicio", "Fin", "Estado"]
        )

        # Botones
        self.btn_modificar = QPushButton("Modificar contrato")
        self.btn_cerrar = QPushButton("Cerrar")

        self.btn_modificar.clicked.connect(self.abrir_modificacion)
        self.btn_cerrar.clicked.connect(self.close)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Seleccione un contrato para modificar:"))
        layout.addWidget(self.tabla)

        botones = QHBoxLayout()
        botones.addWidget(self.btn_modificar)
        botones.addStretch()
        botones.addWidget(self.btn_cerrar)

        layout.addLayout(botones)
        self.setLayout(layout)

        self.cargar_contratos()

    # ============================================================
    #  CARGA DE CONTRATOS
    # ============================================================
    def cargar_contratos(self):
        cur = self.conn.cursor()

        cur.execute(
            """
            SELECT ncontrato, suplemento, compania, fec_inicio, fec_final, estado
            FROM vista_contratos
            ORDER BY ncontrato, suplemento DESC
            """
        )

        rows = cur.fetchall()
        self.tabla.setRowCount(len(rows))

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.tabla.setItem(i, j, QTableWidgetItem(str(value)))

        self.tabla.resizeColumnsToContents()
        self.tabla.horizontalHeader().setStretchLastSection(True)

    # ============================================================
    #  OBTENER MAINWINDOW REAL (IGUAL QUE EN lista_contratos_factura)
    # ============================================================
    def get_mainwindow(self):
        w = self.parent()
        while w is not None and not hasattr(w, "cargar_modulo"):
            w = w.parent()
        return w

    # ============================================================
    #  ABRIR FORMULARIO DE MODIFICACIÓN
    # ============================================================
    def abrir_modificacion(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Atención", "Debe seleccionar un contrato.")
            return

        ncontrato = self.tabla.item(fila, 0).text()

        datos = obtener_suplemento_vigente(ncontrato)
        if not datos:
            QMessageBox.critical(self, "Error", "No se pudo cargar el contrato.")
            return

        main = self.get_mainwindow()
        main.lista_modificacion = self  # ← GUARDAMOS LA INSTANCIA REAL

        print("CREANDO FORMULARIO...")
        form = FormModificacionContrato(datos, parent=main)
        print("FORMULARIO CREADO:", form)

        # Conectar señales
        form.actualizar_vigente.connect(self.actualizar_vigente)
        form.crear_suplemento.connect(self.crear_suplemento)
        form.cancelado.connect(main.lista_modificacion.cancelar_modificacion)

        # Cargar en zona de contenido del MainWindow
        main.cargar_modulo(form, f"Modificar contrato {ncontrato}")

    # ============================================================
    #  ACTUALIZAR SUPLEMENTO VIGENTE
    # ============================================================
    def actualizar_vigente(self, datos):
        actualizar_suplemento_vigente(datos)
        QMessageBox.information(self, "OK", "Datos administrativos actualizados.")
        self.cargar_contratos()

    # ============================================================
    #  CREAR SUPLEMENTO NUEVO
    # ============================================================
    def crear_suplemento(self, datos):
        nuevo_id = crear_suplemento_nuevo(datos)
        QMessageBox.information(
            self,
            "OK",
            f"Suplemento creado correctamente (ID {nuevo_id}).\n"
            "Se han marcado facturas para recálculo.",
        )
        self.cargar_contratos()

    # ============================================================
    #  BOTON CANCELAR - VOLVER A LISTA DE CONTRATOS
    # ============================================================
    def cancelar_modificacion(self):
        print("CANCELAR_MODIFICACION EN:", self)
        main = self.get_mainwindow()
        if main is None:
            print("ERROR: get_mainwindow devolvió None")
            return

        self.setParent(main)  # ← ESTA ES LA CLAVE
        main.cargar_modulo(self, "Modificar contrato")
        self.show()  # Aseguramos que se muestre la lista de contratos nuevamente
