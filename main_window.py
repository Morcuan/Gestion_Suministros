# ------------------------------------------------#
# Modulo: main_window.py                          #
# Descripción: Ventana principal de la aplicación #
# Autor: Antonio Morales                          #
# Fecha: 2026-02-09                               #
# ------------------------------------------------#


from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

import db_init
from consulta_contratos import ConsultaContratosWidget  # <--- AÑADIDO
from estilo import PALETAS, aplicar_estilo_boton, aplicar_estilo_panel_lateral
from lista_contratos_factura import ListaContratosFactura
from lista_contratos_modificar import ListaContratosModificar
from modulo_recalculo import ModuloRecalculo
from nuevo_contrato import NuevoContrato


# class MainWindow(QMainWindow):
class MainWindow(QMainWindow):
    # init recibe la conexión y cursor de la BD desde main.py
    def __init__(self, conn, cursor):
        super().__init__()

        # ---------------------------------------------------------
        # CONEXIÓN A BD (RECIBIDA DESDE main.py)
        # ---------------------------------------------------------
        self.conn = conn
        self.cursor = cursor

        self.setWindowTitle("Gestion_suministros 2.0")
        self.resize(1160, 950)

        # ---------------------------------------------------------
        # CONTENEDOR PRINCIPAL
        # ---------------------------------------------------------
        contenedor = QWidget()
        layout_principal = QHBoxLayout(contenedor)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # ---------------------------------------------------------
        # PANEL LATERAL
        # ---------------------------------------------------------
        panel_lateral_widget = self.crear_menu_lateral()
        aplicar_estilo_panel_lateral(panel_lateral_widget)

        scroll_lateral = QScrollArea()
        scroll_lateral.setWidgetResizable(True)
        scroll_lateral.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_lateral.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_lateral.setWidget(panel_lateral_widget)
        scroll_lateral.setFixedWidth(260)

        self.panel_lateral = scroll_lateral
        layout_principal.addWidget(self.panel_lateral)

        # ---------------------------------------------------------
        # ZONA DE CONTENIDO
        # ---------------------------------------------------------
        self.zona_contenido = QWidget()
        self.zona_contenido_layout = QVBoxLayout(self.zona_contenido)
        self.zona_contenido_layout.setContentsMargins(20, 20, 20, 20)
        self.zona_contenido_layout.setSpacing(15)

        self.encabezado_modulo = QLabel("Pantalla de Inicio")
        self.encabezado_modulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.encabezado_modulo.hide()
        self.zona_contenido_layout.addWidget(self.encabezado_modulo)

        layout_principal.addWidget(self.zona_contenido, stretch=1)
        self.setCentralWidget(contenedor)

        self.cargar_modulo(self.crear_pantalla_inicio(), "Pantalla de Inicio")

    # ---------------------------------------------------------
    # MENÚ LATERAL
    # ---------------------------------------------------------
    # Cada sección del menú se crea con crear_seccion_acordeon, que recibe
    # un título y una lista de opciones (texto y función a ejecutar)
    def crear_menu_lateral(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        self.secciones_acordeon = {}

        # --- Sección Inicio ---
        layout.addWidget(
            self.crear_seccion_acordeon(
                "🏠 Inicio",
                [
                    (
                        "🏡 Pantalla de inicio",
                        lambda: self.cargar_modulo(
                            self.crear_pantalla_inicio(), "Pantalla de Inicio"
                        ),
                    ),
                    (
                        "🎨 Paleta de colores",
                        lambda: self.cargar_modulo(
                            self.crear_pantalla_paleta(), "Paleta de colores"
                        ),
                    ),
                    (
                        "ℹ️ Acerca de...",
                        lambda: self.cargar_modulo(
                            self.crear_pantalla_acerca(), "Acerca de..."
                        ),
                    ),
                ],
            )
        )

        # --- Sección Contratos ---
        layout.addWidget(
            self.crear_seccion_acordeon(
                "📄 Contratos",
                [
                    ("➕ Nuevo contrato", lambda: self.abrir_nuevo_contrato()),
                    (
                        "✏️ Modificación",
                        lambda: self.cargar_modulo(
                            ListaContratosModificar(parent=self),
                            "Modificar contrato",
                        ),
                    ),
                    (
                        "❌ Anulación",
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
                "💡 Facturas",
                [
                    (
                        "➕ Nueva factura",
                        lambda: self.cargar_modulo(
                            ListaContratosFactura(parent=self), "Nueva factura"
                        ),
                    ),
                    (
                        "✏️ Modificación",
                        lambda: self.cargar_modulo(
                            self.crear_placeholder("Modificar factura"),
                            "Modificar factura",
                        ),
                    ),
                ],
            )
        )

        # --- Sección ANÁLISIS ---
        layout.addWidget(
            self.crear_seccion_acordeon(
                "📊 Análisis",
                [
                    (
                        "🔎 Explorador de facturas",
                        lambda: self.cargar_modulo(
                            ConsultaContratosWidget(self.conn, parent=self),
                            "Explorador de facturas",
                        ),
                    ),
                    (
                        "📈 Comparativas",
                        lambda: self.cargar_modulo(
                            self.crear_placeholder("Comparativas"),
                            "Comparativas",
                        ),
                    ),
                ],
            )
        )
        # --- Sección Utilidades ---
        layout.addWidget(
            self.crear_seccion_acordeon(
                "🛠️ Utilidades",
                [
                    (
                        "♻️ Recalcular facturas pdtes",
                        lambda: self.cargar_modulo(
                            ModuloRecalculo(parent=self),
                            "Recalcular facturas pendientes",
                        ),
                    ),
                ],
            )
        )
        # --- Sección Sistema ---
        layout.addWidget(
            self.crear_seccion_acordeon(
                "🛠️ Sistema",
                [
                    ("🧱 Inicializar BD", self.opcion_inicializar_bd),
                ],
            )
        )

        layout.addStretch()

        # --- Botón Salir ---
        btn_salir = QPushButton("🚪 Salir")
        aplicar_estilo_boton(btn_salir, principal=False)
        btn_salir.clicked.connect(self.close)
        layout.addWidget(btn_salir)

        return panel

    # inserta un nuevo código postal en la tabla cpostales
    def insertar_cp(self, cp, poblacion):
        """
        Inserta un código postal nuevo en la tabla cpostales.
        """
        try:
            self.cursor.execute(
                "INSERT INTO cpostales (codigo_postal, poblacion) VALUES (?, ?)",
                (cp, poblacion),
            )
            self.conn.commit()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al insertar código postal",
                f"No se pudo insertar el código postal {cp}.\n\n{e}",
            )

    # ---------------------------------------------------------
    # OPCIÓN: NUEVO CONTRATO (INTEGRACIÓN EN CONTENEDOR)
    # ---------------------------------------------------------
    # En lugar de abrir una ventana nueva, cargamos el módulo dentro de la zona de contenido
    def abrir_nuevo_contrato(self):
        modulo = NuevoContrato(parent=self)
        modulo.cerrado.connect(self.volver_inicio)
        self.cargar_modulo(modulo, "Nuevo contrato")

    # ---------------------------------------------------------
    # VOLVER A PANTALLA DE INICIO
    # ---------------------------------------------------------
    # Función para volver a la pantalla de inicio, se conecta a la señal
    # 'cerrado' del módulo NuevoContrato
    def volver_inicio(self):
        self.cargar_modulo(self.crear_pantalla_inicio(), "Pantalla de Inicio")

    # ---------------------------------------------------------
    # OPCIÓN: INICIALIZAR BD
    # ---------------------------------------------------------
    # Esta función muestra un mensaje de advertencia antes de ejecutar
    # la inicialización de la base de datos.
    def opcion_inicializar_bd(self):
        self.cargar_modulo(QWidget(), "Inicialización BD")

        msg = QMessageBox(self)
        msg.setWindowTitle("Inicializar Base de Datos")
        msg.setIcon(QMessageBox.Warning)
        msg.setText(
            "Esta operación creará o actualizará la estructura de la base de datos.\n"
            "Debe usarse solo en instalaciones nuevas o bajo supervisión.\n\n"
            "¿Deseas continuar?"
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        respuesta = msg.exec()

        if respuesta == QMessageBox.Yes:
            db_init.crear_tablas_y_vistas(self.cursor)
            self.conn.commit()

            ok = QMessageBox(self)
            ok.setWindowTitle("BD Inicializada")
            ok.setIcon(QMessageBox.Information)
            ok.setText("La base de datos ha sido inicializada correctamente.")
            ok.exec()

    # ---------------------------------------------------------
    # ACORDEÓN
    # ---------------------------------------------------------
    # Esta función crea una sección de acordeón para el menú lateral.
    # Recibe un título y una lista de opciones,
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

    # Esta función se encarga de mostrar u ocultar el panel de opciones del acordeón
    # según el botón que se haya pulsado. Si se pulsa un botón de sección, se muestra
    # su panel y se ocultan los demás.
    def toggle_acordeon(self, titulo):
        for nombre, (btn, panel) in self.secciones_acordeon.items():
            if nombre == titulo:
                panel.setVisible(btn.isChecked())
            else:
                btn.setChecked(False)
                panel.setVisible(False)

    # ---------------------------------------------------------
    # PANTALLAS
    # ---------------------------------------------------------
    # Estas funciones crean los widgets que se mostrarán en la zona de contenido al
    # seleccionar cada opción del menú. Por ahora son pantallas de ejemplo,
    # pero luego se reemplazarán por los módulos reales.
    def crear_pantalla_inicio(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Bienvenido al sistema de gestión"))
        l.addStretch()
        return w

    def crear_pantalla_paleta(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Selecciona una paleta de colores"))

        for nombre, paleta in PALETAS.items():
            btn = QPushButton(nombre)
            aplicar_estilo_boton(btn)
            btn.clicked.connect(lambda _, p=paleta: self.aplicar_paleta(p))
            l.addWidget(btn)

        l.addStretch()
        return w

    def crear_pantalla_acerca(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lbl = QLabel(
            "<b>Gestion_suministros 2.0</b><br>"
            "Proyecto iniciado: <b>enero 2025</b><br>"
            "Programador: <b>Antonio Morales</b><br><br>"
            "Aplicación para la gestión modular de contratos, facturas y comparativas."
        )
        lbl.setWordWrap(True)
        l.addWidget(lbl)
        l.addStretch()
        return w

    def crear_placeholder(self, nombre):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel(f"Módulo: {nombre}"))
        l.addStretch()
        return w

    # ---------------------------------------------------------
    # CARGA DE MÓDULOS
    # ---------------------------------------------------------
    # Esta función se encarga de cargar un widget en la zona de contenido, eliminando
    # el que estuviera antes (excepto el encabezado, que se mantiene). Recibe el widget
    # a cargar y el título que se mostrará en el encabezado.
    def cargar_modulo(self, widget, titulo):
        for i in reversed(range(self.zona_contenido_layout.count())):
            item = self.zona_contenido_layout.itemAt(i)
            w = item.widget()
            if w is not None and w is not self.encabezado_modulo:
                self.zona_contenido_layout.removeWidget(w)
                w.hide()
            #   w.setParent(None)

        # self.encabezado_modulo.setText(titulo)
        self.zona_contenido_layout.addWidget(widget, stretch=1)

    # ---------------------------------------------------------
    # APLICAR PALETA
    # ---------------------------------------------------------
    def aplicar_paleta(self, paleta):
        from estilo import generar_stylesheet

        self.setStyleSheet(generar_stylesheet(paleta))
        self.setStyleSheet(generar_stylesheet(paleta))
        self.setStyleSheet(generar_stylesheet(paleta))
