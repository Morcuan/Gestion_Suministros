# --------------------------------------------#
# Modulo: contrato_consulta.py               #
# Descripción: Ventana de consulta de        #
#   contratos.                               #
# Autor: Antonio Morales                     #
# Fecha: 2025-12-01                          #
# --------------------------------------------#

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from aux_database import listar_contratos, obtener_contrato_por_numero
from aux_fechas import a_ddmm
from aux_presentacion import color_estado, color_fila_estado, estilo_boton
from base_formulario import BaseFormulario
from contrato_baja import ConfirmacionBajaDialog
from historico_estados import HistoricoEstadosWidget


# ---------------------------------------------------------
# Crear grupo de campos con estilo
# ---------------------------------------------------------
def crear_grupo(titulo, campos):
    grupo = QGroupBox(titulo)
    layout = QVBoxLayout()

    for etiqueta, valor in campos:
        fila = QHBoxLayout()
        fila.addWidget(QLabel(etiqueta + ":"))

        if isinstance(valor, QWidget):
            label_valor = valor
        else:
            label_valor = QLabel(str(valor))

            if etiqueta == "Estado":
                estado = str(valor).upper().strip()
                col = color_estado(estado)
                label_valor.setStyleSheet(f"color: {col.name()}; font-weight: bold;")

        fila.addWidget(label_valor)
        layout.addLayout(fila)

    grupo.setLayout(layout)
    return grupo


# ---------------------------------------------------------
# Ventana principal de consulta
# ---------------------------------------------------------
class ConsultaContratoWidget(BaseFormulario):
    def __init__(self, contrato_main=None, parent=None):
        super().__init__(parent)
        self.contrato_main = contrato_main

        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle("Lista de contratos")
        self.setFont(QFont("Noto Sans", 12))

        self.resize(900, 500)
        self.setMinimumSize(750, 400)

        layout = QVBoxLayout()

        titulo = QLabel("Listado de Contratos")
        titulo.setFont(QFont("Noto Sans", 14, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(
            [
                "Nº contrato",
                "Comercializadora",
                "Código Postal",
                "Población",
                "Fec. Inicio",
                "Fec. Final",
                "Estado",
            ]
        )

        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("alternate-background-color: #f7f7f7;")
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabla.verticalHeader().setVisible(False)

        layout.addWidget(self.tabla)

        # Botones
        botones = QHBoxLayout()

        detalles_btn = QPushButton("Detalles")
        self.btn_historico = QPushButton("Histórico")
        salir_btn = QPushButton("Salir")

        # Orden: Detalles | Histórico | (espacio) | Salir
        botones.addWidget(detalles_btn)
        botones.addWidget(self.btn_historico)
        botones.addStretch()
        botones.addWidget(salir_btn)

        salir_btn.setStyleSheet(estilo_boton("salir"))

        layout.addLayout(botones)
        self.setLayout(layout)

        # Conexiones
        salir_btn.clicked.connect(self.cerrar_consulta_top_level)
        detalles_btn.clicked.connect(self.abrir_detalles)
        self.btn_historico.clicked.connect(self.abrir_historico)

        self.cargar_contratos()

    # ---------------------------------------------------------
    # Cargar contratos en tabla
    # ---------------------------------------------------------
    def cargar_contratos(self):
        contratos = listar_contratos()
        self.tabla.setRowCount(len(contratos))

        for i, contrato in enumerate(contratos):
            numero, comercializadora, cp, poblacion, f_ini, f_fin, estado = contrato[:7]

            self.tabla.setItem(i, 0, QTableWidgetItem(str(numero)))
            self.tabla.setItem(i, 1, QTableWidgetItem(str(comercializadora)))
            self.tabla.setItem(i, 2, QTableWidgetItem(str(cp)))
            self.tabla.setItem(i, 3, QTableWidgetItem(str(poblacion)))
            self.tabla.setItem(i, 4, QTableWidgetItem(str(f_ini)))
            self.tabla.setItem(i, 5, QTableWidgetItem(str(f_fin)))

            item_estado = QTableWidgetItem(estado)
            self.tabla.setItem(i, 6, item_estado)

            color = color_fila_estado(estado)
            for col in range(self.tabla.columnCount()):
                item = self.tabla.item(i, col)
                if item:
                    item.setForeground(color)

        self.tabla.resizeColumnsToContents()
        self.tabla.resizeRowsToContents()

    # ---------------------------------------------------------
    # Abrir detalles del contrato seleccionado
    # ---------------------------------------------------------
    def abrir_detalles(self):
        items = self.tabla.selectedItems()
        if not items:
            self.mostrar_aviso("Aviso", "Debe seleccionar un contrato.")
            return

        fila = items[0].row()
        numero_contrato = self.tabla.item(fila, 0).text().strip()

        contrato_completo = obtener_contrato_por_numero(numero_contrato)
        if not contrato_completo:
            self.mostrar_aviso(
                "Aviso", "No se encontró el contrato en la base de datos."
            )
            return

        detalles = DetallesContratoWidget(
            contrato_completo, parent=self, contrato_main=self.contrato_main
        )

        detalles.exec()

    def abrir_historico(self):
        fila = self.tabla.currentRow()

        if fila < 0:
            QMessageBox.warning(
                self, "Aviso", "Debe seleccionar un contrato de la lista."
            )
            return

        numero_contrato = self.tabla.item(fila, 0).text().strip()

        ventana = HistoricoEstadosWidget(numero_contrato, parent=self)
        ventana.show()

    # ---------------------------------------------------------
    # Cerrar ventana principal
    # ---------------------------------------------------------
    def cerrar_consulta_top_level(self):
        win = self.window()
        win.setAttribute(Qt.WA_DeleteOnClose, True)
        win.close()


# ---------------------------------------------------------
# Ventana de detalles del contrato
# ---------------------------------------------------------
class DetallesContratoWidget(QDialog):
    def __init__(self, contrato, parent=None, contrato_main=None):
        super().__init__(parent)
        self.contrato_main = contrato_main

        self.setWindowTitle(f"Comercializadora - {contrato[1]}")
        self.resize(550, 900)

        layout_principal = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        contenido = QWidget()
        layout_contenido = QVBoxLayout(contenido)

        # Datos principales
        numero = contrato[0]
        estado_actual = contrato[6]
        fecha_inicio = a_ddmm(contrato[4])
        fecha_final = a_ddmm(contrato[5])

        self.label_estado = QLabel(estado_actual)
        self.label_estado.setStyleSheet(
            f"color: {color_estado(estado_actual).name()}; font-weight: bold;"
        )

        # Grupos
        layout_contenido.addWidget(
            crear_grupo(
                "Detalles del contrato",
                [
                    ("Número de contrato", numero),
                    ("Estado", self.label_estado),
                    ("Código postal", contrato[2]),
                    ("Población", contrato[3]),
                    ("Fecha inicio", fecha_inicio),
                    ("Fecha final", fecha_final),
                ],
            )
        )

        layout_contenido.addWidget(
            crear_grupo(
                "Potencia contratada",
                [
                    ("Potencia punta", contrato[7]),
                    ("Importe potencia punta", contrato[8]),
                    ("Potencia valle", contrato[9]),
                    ("Importe potencia valle", contrato[10]),
                ],
            )
        )

        layout_contenido.addWidget(
            crear_grupo(
                "Precios energía",
                [
                    ("Importe consumo punta", contrato[11]),
                    ("Importe consumo llano", contrato[12]),
                    ("Importe consumo valle", contrato[13]),
                ],
            )
        )

        layout_contenido.addWidget(
            crear_grupo(
                "Excedentes",
                [
                    ("Excedentes", contrato[14]),
                    ("Importe excedentes", contrato[15]),
                ],
            )
        )

        layout_contenido.addWidget(
            crear_grupo(
                "Impuestos y otros cargos",
                [
                    ("Importe bono social", contrato[16]),
                    ("Importe alquiler contador", contrato[17]),
                    ("Importe asistente smart", contrato[18]),
                    ("Impuesto electricidad", contrato[19]),
                    ("IVA", contrato[20]),
                ],
            )
        )

        # Botones
        botones_layout = QHBoxLayout()
        btn_modificar = QPushButton("Modificar contrato")
        btn_anular = QPushButton("Anular contrato")
        btn_cerrar = QPushButton("Cerrar")

        self.btn_anular = btn_anular

        if estado_actual.upper() == "ANULADO":
            btn_anular.setEnabled(False)

        btn_modificar.clicked.connect(lambda: self.abrir_modificacion(numero))
        btn_anular.clicked.connect(lambda: self.preparar_anulacion(numero))
        btn_cerrar.clicked.connect(self.close)

        botones_layout.addWidget(btn_modificar)
        botones_layout.addWidget(btn_anular)
        botones_layout.addWidget(btn_cerrar)

        layout_contenido.addLayout(botones_layout)

        scroll.setWidget(contenido)
        layout_principal.addWidget(scroll)

        self.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px;
            }
            QLabel {
                padding: 2px;
            }
        """
        )

    # ---------------------------------------------------------
    # Abrir modificación (misma vía que el menú, sin pedir número)
    # ---------------------------------------------------------
    def abrir_modificacion(self, numero_contrato):
        self.contrato_main._abrir_edicion(numero_contrato)
        self.close()

    # ---------------------------------------------------------
    # Preparar anulación
    # ---------------------------------------------------------
    def preparar_anulacion(self, numero_contrato):
        estado_actual = self.label_estado.text().strip()
        dialog = ConfirmacionBajaDialog(numero_contrato, estado_actual, self)

        if dialog.exec() == QDialog.Accepted:
            self.label_estado.setText("ANULADO")
            self.label_estado.setStyleSheet("color: red; font-weight: bold;")
            self.btn_anular.setEnabled(False)

    # ---------------------------------------------------------
    # Refrescar lista al cerrar detalles
    # ---------------------------------------------------------
    def closeEvent(self, event):
        if self.parent():
            try:
                self.parent().cargar_contratos()
            except Exception:
                pass
        super().closeEvent(event)


# ---------------------------------------------------------
# Ventana contenedora de consultas
# ---------------------------------------------------------
class ConsultasWindow(QWidget):
    def __init__(self, nuevo_contrato_widget, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.resize(900, 600)
        self.setMinimumSize(800, 500)

        self.ui = ConsultaContratoWidget(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)

        nuevo_contrato_widget.contrato_guardado.connect(self.ui.cargar_contratos)
        self.ui.cargar_contratos()
