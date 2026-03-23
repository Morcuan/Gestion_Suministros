# ------------------------------------------------#
# Modulo: main_window.py                          #
# Descripción: Ventana principal de la aplicación #
# Autor: Antonio Morales                          #
# Fecha: 2026-02-09                               #
# ------------------------------------------------#

# from estadisticas_mensuales import (CapturaEstadisticasMensuales,ConsultaEstadisticasMensuales,)
# from lista_analisis_factura import ListaAnalisisFactura
# from lista_contratos_anulacion import ListaContratosAnulacion
# from lista_contratos_factura import ListaContratosFactura
# from lista_contratos_historia import ListaContratosHistoria
# from lista_contratos_modificar import ListaContratosModificar
# from lista_contratos_rectificar import ListaContratosRectificar
# from modulo_recalculo import ModuloRecalculo

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

from contratos.nuevo_contrato import NuevoContrato
from contratos.lista_contratos import ListaContratos
from contratos.modificar_contrato import ModificarContrato

from estilo import PALETAS, aplicar_estilo_boton, aplicar_estilo_panel_lateral
from utilidades.estadisticas_mensuales import (
    CapturaEstadisticasMensuales,
    ConsultaEstadisticasMensuales,
)

# import db_init


class MainWindow(QMainWindow):

    def __init__(self, conn, cursor):
        super().__init__()

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
        scroll_lateral.setFrameShape(QScrollArea.NoFrame)
        scroll_lateral.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_lateral.setWidget(panel_lateral_widget)
        scroll_lateral.setFixedWidth(260)

        layout_principal.addWidget(scroll_lateral)

        # ---------------------------------------------------------
        # ZONA DE CONTENIDO
        # ---------------------------------------------------------
        self.zona_contenido = QWidget()
        self.zona_contenido_layout = QVBoxLayout(self.zona_contenido)
        self.zona_contenido_layout.setContentsMargins(20, 20, 20, 20)
        self.zona_contenido_layout.setSpacing(15)

        # Título superior (solo para módulos)
        self.encabezado_modulo = QLabel("")
        self.encabezado_modulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.encabezado_modulo.hide()
        self.zona_contenido_layout.addWidget(
            self.encabezado_modulo, alignment=Qt.AlignHCenter
        )

        layout_principal.addWidget(self.zona_contenido)
        self.setCentralWidget(contenedor)

        # Pantalla de inicio sin título
        self.cargar_modulo(self.crear_pantalla_inicio(), None)

    # ---------------------------------------------------------
    # MENÚ LATERAL
    # ---------------------------------------------------------
    def crear_menu_lateral(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        self.secciones_acordeon = {}

        # Inicio
        layout.addWidget(
            self.crear_seccion_acordeon(
                "🏠 Inicio",
                [
                    (
                        "🏡 Pantalla de inicio",
                        lambda: self.cargar_modulo(self.crear_pantalla_inicio(), None),
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

        # Contratos
        layout.addWidget(
            self.crear_seccion_acordeon(
                "📄 Contratos",
                [
                    ("➕ Nuevo contrato", lambda: self.abrir_nuevo_contrato()),
                    ("✏️ Modificación", self.abrir_modificacion_contratos),
                    ("❌ Anulación", lambda: self.abrir_anulacion_contrato()),
                ],
            )
        )
        # Facturas
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
                        "✏️ Rectif. factura",
                        lambda: self.cargar_modulo(
                            ListaContratosRectificar(parent=self, conn=self.conn),
                            "Rectificar factura",
                        ),
                    ),
                ],
            )
        )

        # Análisis
        layout.addWidget(
            self.crear_seccion_acordeon(
                "📊 Análisis",
                [
                    (
                        "🔎 Histórico de contratos",
                        lambda: self.cargar_modulo(
                            ListaContratosHistoria(parent=self), "Histórico contratos"
                        ),
                    ),
                    (
                        "🔎 Explorador de facturas",
                        lambda: self.cargar_modulo(
                            ListaAnalisisFactura(parent=self), "Explorador de facturas"
                        ),
                    ),
                    (
                        "📈 Comparativas",
                        lambda: self.cargar_modulo(
                            self.crear_placeholder("Comparativas"), "Comparativas"
                        ),
                    ),
                ],
            )
        )

        # Utilidades
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
                    (
                        "📅 Estadísticas mensuales",
                        lambda: self.cargar_modulo(
                            ConsultaEstadisticasMensuales(
                                parent=self, conn=self.conn, cursor=self.cursor
                            ),
                            "Estadísticas mensuales",
                        ),
                    ),
                    (
                        "➕ Capturar estadísticas",
                        lambda: self.cargar_modulo(
                            CapturaEstadisticasMensuales(
                                parent=self, conn=self.conn, cursor=self.cursor
                            ),
                            "Captura estadísticas mensuales",
                        ),
                    ),
                ],
            )
        )

        # Sistema
        layout.addWidget(
            self.crear_seccion_acordeon(
                "🛠️ Sistema",
                [("🧱 Inicializar BD", self.opcion_inicializar_bd)],
            )
        )

        layout.addStretch()

        btn_salir = QPushButton("🚪 Salir")
        aplicar_estilo_boton(btn_salir, principal=False)
        btn_salir.clicked.connect(self.close)
        layout.addWidget(btn_salir)

        return panel

    # ---------------------------------------------------------
    # NUEVO CONTRATO
    # ---------------------------------------------------------
    def abrir_nuevo_contrato(self):
        modulo = NuevoContrato(parent=self)
        modulo.cerrado.connect(self.volver_inicio)
        self.cargar_modulo(modulo, "Nuevo contrato")

    def volver_inicio(self):
        self.cargar_modulo(self.crear_pantalla_inicio(), None)

    # ---------------------------------------------------------
    # MODIFICAR CONTRATO (FLUJO NUEVO)
    # ---------------------------------------------------------
    def abrir_modificacion_contratos(self):
        lista = ListaContratos(
            parent=self, conn=self.conn, callback=self._abrir_modificar_contrato
        )
        self.cargar_modulo(lista, "Modificar contrato")

    def _abrir_modificar_contrato(self, ncontrato):
        ModificarContrato(parent=self, conn=self.conn, ncontrato=ncontrato)

    # ---------------------------------------------------------
    # ACORDEÓN
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
    # CARGAR MÓDULO (CORREGIDO)
    # ---------------------------------------------------------
    def cargar_modulo(self, widget, titulo):
        # Limpiar contenido anterior excepto encabezado
        for i in reversed(range(self.zona_contenido_layout.count())):
            item = self.zona_contenido_layout.itemAt(i)
            w = item.widget()
            if w is not None and w is not self.encabezado_modulo:
                self.zona_contenido_layout.removeWidget(w)
                w.deleteLater()

        # Mostrar u ocultar título
        if titulo is None:
            self.encabezado_modulo.hide()
        else:
            self.encabezado_modulo.setText(titulo)
            self.encabezado_modulo.show()

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # 🔥 LÍNEA CRÍTICA
        widget.setMinimumHeight(600)

        layout.addWidget(widget)

        scroll.setWidget(contenedor)
        self.zona_contenido_layout.addWidget(scroll)

    # ---------------------------------------------------------
    # INICIALIZAR BD
    # ---------------------------------------------------------
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
    # ANULACIÓN
    # ---------------------------------------------------------
    def abrir_anulacion_contrato(self):
        widget = ListaContratosAnulacion(parent=self)
        self.cargar_modulo(widget, "Anulación de contrato")

    # ---------------------------------------------------------
    # PALETA
    # ---------------------------------------------------------
    def aplicar_paleta(self, paleta):
        from estilo import generar_stylesheet

        self.setStyleSheet(generar_stylesheet(paleta))
