# ----------------------------------------------------------#
# Modulo: main.py                                          #
# Descripción: Formulario general y menús de la aplicación #
#              usando PySide6                              #
# Autor: Antonio Morales                                   #
# Fecha: 2025-12-01                                        #
# ----------------------------------------------------------#

import sys

from PySide6.QtGui import QAction, QColor, QFont, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

import config
import paletas
from base_bd import BaseBD
from comparativas import ComparativasWidget
from consumos import ConsumosWidget
from contrato_main import ContratoMain
from facturas import FacturasWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestión de Suministros - Formulario General")
        self.resize(600, 200)

        # ---------------------------------------------------------
        # Cargar configuración persistente
        # ---------------------------------------------------------
        self.config = config.cargar_config()
        self.apariencia_oscura = False  # se ajustará según la paleta cargada

        # ---------------------------------------------------------
        # Inicializar BD y propagar instancia global
        # ---------------------------------------------------------
        self.bd = BaseBD("data/almacen.db")

        import aux_database

        aux_database.set_bd(self.bd)

        # Router principal de contratos
        self.contratos = ContratoMain(self.bd)

        # ---------------------------------------------------------
        # Zona central (fondo blanco + firma)
        # ---------------------------------------------------------
        central_widget = QWidget()
        palette = central_widget.palette()
        palette.setColor(QPalette.Window, QColor("white"))
        central_widget.setAutoFillBackground(True)
        central_widget.setPalette(palette)

        layout = QVBoxLayout()
        layout.addStretch()

        firma_layout = QHBoxLayout()
        firma_layout.addStretch()
        firma = QLabel("Gestión de Suministros v1.0 - By A. Morales")
        firma.setStyleSheet("color: gray; font-style: italic;")
        firma_layout.addWidget(firma)

        layout.addLayout(firma_layout)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        # ---------------------------------------------------------
        # Barra de menús
        # ---------------------------------------------------------
        menubar = self.menuBar()

        # ------------------ Menú Archivo ------------------
        archivo_menu = menubar.addMenu("Archivo")

        # Submenú de Apariencia
        apariencia_menu = archivo_menu.addMenu("Apariencia")

        apariencia_menu.addAction("Tema claro", lambda: self.cambiar_paleta("clara"))
        apariencia_menu.addAction("Tema oscuro", lambda: self.cambiar_paleta("oscura"))
        apariencia_menu.addSeparator()
        apariencia_menu.addAction("Tema solar", lambda: self.cambiar_paleta("solar"))
        apariencia_menu.addAction("Tema azul", lambda: self.cambiar_paleta("azul"))
        apariencia_menu.addAction("Tema cálido", lambda: self.cambiar_paleta("calida"))
        apariencia_menu.addAction("Tema morado", lambda: self.cambiar_paleta("morada"))

        archivo_menu.addSeparator()
        archivo_menu.addAction("Salir", self.close)

        # ------------------ Menú Contratos ------------------
        contratos_menu = menubar.addMenu("Contratos")

        contratos_menu.addAction("Nuevo Contrato", self.contratos.abrir_nuevo)

        operaciones_contratos = contratos_menu.addMenu("Operaciones en Contratos")
        operaciones_contratos.addAction(
            "Listado de Contratos", self.contratos.abrir_consulta
        )
        operaciones_contratos.addAction(
            "Modificar Contrato", self.contratos.abrir_modificacion
        )
        operaciones_contratos.addAction("Anular Contrato", self.contratos.abrir_baja)

        # ------------------ Menú Facturas ------------------
        facturas_menu = menubar.addMenu("Facturas")
        facturas_menu.addAction("Nueva Factura", self.abrir_facturas)

        operaciones_facturas = facturas_menu.addMenu("Operaciones en Facturas")
        operaciones_facturas.addAction("Listado de facturas", self.abrir_facturas)
        operaciones_facturas.addAction("Modificar factura", self.abrir_facturas)
        operaciones_facturas.addAction("Anular factura", self.abrir_facturas)

        # ------------------ Menú Comparativas ------------------
        comparativas_menu = menubar.addMenu("Comparativas")
        comparativas_menu.addAction("Comparar Contratos", self.abrir_comparativas)
        comparativas_menu.addAction("Comparar Facturas", self.abrir_comparativas)
        comparativas_menu.addAction("Comparar Consumos", self.abrir_comparativas)

        # ------------------ Menú Ayuda ------------------
        ayuda_menu = menubar.addMenu("Ayuda")
        acerca_action = QAction("Acerca de...", self)
        acerca_action.triggered.connect(self.mostrar_acerca_action)
        ayuda_menu.addAction(acerca_action)

        # ---------------------------------------------------------
        # Aplicar paleta inicial desde config.json
        # ---------------------------------------------------------
        tema_inicial = self.config.get("tema", "clara")
        self.cambiar_paleta(tema_inicial)

    # ---------------------------------------------------------
    # Métodos de apertura de formularios
    # ---------------------------------------------------------
    def abrir_facturas(self):
        self.setCentralWidget(FacturasWidget())

    def abrir_consumos(self):
        self.setCentralWidget(ConsumosWidget())

    def abrir_comparativas(self):
        self.setCentralWidget(ComparativasWidget())

    def mostrar_acerca_action(self):
        QMessageBox.information(
            self,
            "Acerca de Gestión de Suministros",
            """<h2 style='color:#2c3e50;'>Gestión de Suministros</h2>
            <p><b>Versión:</b> 1.0</p>
            <p><b>Autor:</b> Antonio Morales</p>
            <p><b>Framework:</b> PySide6</p>
            <hr>
            <p style='color:gray; font-style:italic;'>
            Sistema de gestión energética doméstica<br>
            Proyecto modular y trazable con validaciones inteligentes
            </p>
        """,
        )

    # ---------------------------------------------------------
    # Cambio de apariencia con submenú + guardado persistente
    # ---------------------------------------------------------
    def cambiar_paleta(self, nombre):
        if nombre == "clara":
            QApplication.instance().setPalette(paletas.paleta_clara())
            self.apariencia_oscura = False

        elif nombre == "oscura":
            QApplication.instance().setPalette(paletas.paleta_oscura())
            self.apariencia_oscura = True

        elif nombre == "solar":
            QApplication.instance().setPalette(paletas.paleta_solar())
            self.apariencia_oscura = False

        elif nombre == "azul":
            QApplication.instance().setPalette(paletas.paleta_azul())
            self.apariencia_oscura = False

        elif nombre == "calida":
            QApplication.instance().setPalette(paletas.paleta_calida())
            self.apariencia_oscura = False

        elif nombre == "morada":
            QApplication.instance().setPalette(paletas.paleta_morada())
            self.apariencia_oscura = False

        # Guardar configuración persistente
        self.config["tema"] = nombre
        config.guardar_config(self.config)


# ---------------------------------------------------------
# Ejecutar la aplicación
# ---------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Noto Sans", 12))
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec())
