from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from estilo import aplicar_estilo_boton, aplicar_estilo_panel_lateral


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestion_suministros 2.0")
        self.resize(1200, 800)

        # ---------------------------------------------------------
        # CONTENEDOR PRINCIPAL
        # ---------------------------------------------------------
        contenedor = QWidget()
        layout_principal = QHBoxLayout(contenedor)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # ---------------------------------------------------------
        # PANEL LATERAL (scroll + estilo + ancho fijo)
        # ---------------------------------------------------------
        panel_lateral_widget = self.crear_menu_lateral()
        panel_lateral_widget.setFixedWidth(300)
        aplicar_estilo_panel_lateral(panel_lateral_widget)

        scroll_lateral = QScrollArea()
        scroll_lateral.setWidgetResizable(True)
        scroll_lateral.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_lateral.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll_lateral.setWidget(panel_lateral_widget)

        self.panel_lateral = scroll_lateral
        layout_principal.addWidget(self.panel_lateral)

        # ---------------------------------------------------------
        # ZONA DE CONTENIDO
        # ---------------------------------------------------------
        self.zona_contenido = QWidget()
        self.zona_contenido_layout = QVBoxLayout(self.zona_contenido)
        self.zona_contenido_layout.setContentsMargins(20, 20, 20, 20)
        self.zona_contenido_layout.setSpacing(15)

        # Encabezado superior dinámico
        self.encabezado_modulo = QLabel("Pantalla de Inicio")
        self.encabezado_modulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.zona_contenido_layout.addWidget(self.encabezado_modulo)

        layout_principal.addWidget(self.zona_contenido, stretch=1)

        self.setCentralWidget(contenedor)

        # Cargar pantalla inicial
        self.cargar_modulo(self.crear_pantalla_inicio(), "Pantalla de Inicio")

    # ---------------------------------------------------------
    # MENÚ LATERAL CON ACORDEÓN
    # ---------------------------------------------------------
    def crear_menu_lateral(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        self.secciones_acordeon = {}

        # --- Sección Inicio ---
        btn_inicio = QPushButton("Inicio")
        aplicar_estilo_boton(btn_inicio, principal=False)
        btn_inicio.clicked.connect(
            lambda: self.cargar_modulo(
                self.crear_pantalla_inicio(), "Pantalla de Inicio"
            )
        )
        layout.addWidget(btn_inicio)

        # --- Sección Contratos ---
        layout.addWidget(
            self.crear_seccion_acordeon(
                "Contratos",
                [
                    (
                        "Nuevo contrato",
                        lambda: self.cargar_modulo(
                            self.crear_placeholder("Nuevo contrato"), "Nuevo contrato"
                        ),
                    ),
                    (
                        "Consulta",
                        lambda: self.cargar_modulo(
                            self.crear_placeholder("Consulta contratos"),
                            "Consulta contratos",
                        ),
                    ),
                    (
                        "Modificación",
                        lambda: self.cargar_modulo(
                            self.crear_placeholder("Modificar contrato"),
                            "Modificar contrato",
                        ),
                    ),
                    (
                        "Anulación",
                        lambda: self.cargar_modulo(
                            self.crear_placeholder("Anular contrato"), "Anular contrato"
                        ),
                    ),
                ],
            )
        )

        # --- Sección Facturas ---
        layout.addWidget(
            self.crear_seccion_acordeon(
                "Facturas",
                [
                    (
                        "Nueva factura",
                        lambda: self.cargar_modulo(
                            self.crear_placeholder("Nueva factura"), "Nueva factura"
                        ),
                    ),
                    (
                        "Consulta",
                        lambda: self.cargar_modulo(
                            self.crear_placeholder("Consulta facturas"),
                            "Consulta facturas",
                        ),
                    ),
                    (
                        "Modificación",
                        lambda: self.cargar_modulo(
                            self.crear_placeholder("Modificar factura"),
                            "Modificar factura",
                        ),
                    ),
                ],
            )
        )

        # --- Sección Consumos ---
        layout.addWidget(
            self.crear_seccion_acordeon(
                "Consumos",
                [
                    (
                        "Nuevo consumo",
                        lambda: self.cargar_modulo(
                            self.crear_placeholder("Nuevo consumo"), "Nuevo consumo"
                        ),
                    ),
                    (
                        "Consulta",
                        lambda: self.cargar_modulo(
                            self.crear_placeholder("Consulta consumos"),
                            "Consulta consumos",
                        ),
                    ),
                ],
            )
        )

        layout.addStretch()
        return panel

    # ---------------------------------------------------------
    # CREAR UNA SECCIÓN DEL ACORDEÓN
    # ---------------------------------------------------------
    def crear_seccion_acordeon(self, titulo, opciones):
        contenedor = QWidget()
        cont_layout = QVBoxLayout(contenedor)
        cont_layout.setContentsMargins(0, 0, 0, 0)

        btn_seccion = QPushButton(titulo)
        btn_seccion.setCheckable(True)
        aplicar_estilo_boton(btn_seccion)
        btn_seccion.clicked.connect(lambda: self.toggle_acordeon(titulo))
        cont_layout.addWidget(btn_seccion)

        panel_opciones = QWidget()
        panel_layout = QVBoxLayout(panel_opciones)
        panel_layout.setContentsMargins(20, 0, 0, 0)

        for texto, accion in opciones:
            btn = QPushButton(texto)
            aplicar_estilo_boton(btn)
            btn.clicked.connect(accion)
            panel_layout.addWidget(btn)

        panel_opciones.setVisible(False)
        self.secciones_acordeon[titulo] = (btn_seccion, panel_opciones)
        cont_layout.addWidget(panel_opciones)
        return contenedor

    # ---------------------------------------------------------
    # LÓGICA DEL ACORDEÓN
    # ---------------------------------------------------------
    def toggle_acordeon(self, titulo):
        for nombre, (btn, panel) in self.secciones_acordeon.items():
            if nombre == titulo:
                panel.setVisible(btn.isChecked())
            else:
                btn.setChecked(False)
                panel.setVisible(False)

    # ---------------------------------------------------------
    # PANTALLA INICIAL
    # ---------------------------------------------------------
    def crear_pantalla_inicio(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Bienvenido al sistema de gestión"))
        l.addStretch()
        return w

    # ---------------------------------------------------------
    # PLACEHOLDER PARA MÓDULOS
    # ---------------------------------------------------------
    def crear_placeholder(self, nombre):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel(f"Módulo: {nombre}"))
        l.addStretch()
        return w

    # ---------------------------------------------------------
    # CARGA DE MÓDULOS EN LA ZONA DE CONTENIDO
    # ---------------------------------------------------------
    def cargar_modulo(self, widget, titulo):
        # Limpiar zona de contenido (excepto encabezado)
        for i in reversed(range(self.zona_contenido_layout.count())):
            item = self.zona_contenido_layout.itemAt(i)
            w = item.widget()
            if w and w != self.encabezado_modulo:
                w.setParent(None)

        self.encabezado_modulo.setText(titulo)
        self.zona_contenido_layout.addWidget(widget)
