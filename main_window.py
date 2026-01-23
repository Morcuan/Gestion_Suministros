from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestion_suministros 2.0.A")
        self.resize(1200, 800)

        # --- CONTENEDOR PRINCIPAL ---
        contenedor = QWidget()
        layout_principal = QHBoxLayout(contenedor)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # --- MENÚ LATERAL ---
        self.menu_lateral = self.crear_menu_lateral()
        layout_principal.addWidget(self.menu_lateral)

        # --- ZONA DE CONTENIDO ---
        self.zona_contenido = QWidget()
        self.zona_contenido_layout = QVBoxLayout(self.zona_contenido)
        self.zona_contenido_layout.setContentsMargins(20, 20, 20, 20)

        layout_principal.addWidget(self.zona_contenido, stretch=1)

        self.setCentralWidget(contenedor)

        # Cargar pantalla inicial
        self.cargar_modulo(self.crear_pantalla_inicio())

    # ---------------------------------------------------------
    # MENÚ LATERAL
    # ---------------------------------------------------------
    def crear_menu_lateral(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)

        # Botón Inicio
        btn_inicio = QPushButton("Inicio")
        btn_inicio.clicked.connect(
            lambda: self.cargar_modulo(self.crear_pantalla_inicio())
        )
        layout.addWidget(btn_inicio)

        # Ejemplo de sección Contratos (aún sin acordeón)
        btn_contratos = QPushButton("Contratos")
        btn_contratos.clicked.connect(
            lambda: self.cargar_modulo(self.crear_placeholder("Contratos"))
        )
        layout.addWidget(btn_contratos)

        # Espaciador
        layout.addStretch()

        return panel

    # ---------------------------------------------------------
    # CARGA DE MÓDULOS
    # ---------------------------------------------------------
    def cargar_modulo(self, widget):
        # Limpiar zona de contenido
        for i in reversed(range(self.zona_contenido_layout.count())):
            item = self.zona_contenido_layout.itemAt(i)
            w = item.widget()
            if w:
                w.setParent(None)

        # Insertar nuevo módulo
        self.zona_contenido_layout.addWidget(widget)

    # ---------------------------------------------------------
    # PANTALLA INICIAL
    # ---------------------------------------------------------
    def crear_pantalla_inicio(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Pantalla de Inicio"))
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
