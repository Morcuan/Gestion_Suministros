# ------------------------------------------------#
# Modulo: main_window.py                          #
# Descripción: Ventana principal de la aplicación #
# Autor: Antonio Morales                          #
# Fecha: 2026-02-09                               #
# ------------------------------------------------#

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from analisis_comparativas.informe_interno import generar_html_comparativa_interna
from analisis_contrato.lista_contratos_historico import ListaContratosHistorico
from analisis_factura.lista_con_his_factura import ListaConHisFactura
from contratos.lista_contratos import ListaContratos
from contratos.nuevo_contrato import NuevoContrato
from estilo import PALETAS, aplicar_estilo_boton, aplicar_estilo_panel_lateral
from facturas.lista_contratos_factura import ListaContratosFactura
from facturas.recalculo_test import recalcular_facturas_test
from utilidades.estadisticas_mensuales import (
    CapturaEstadisticasMensuales,
    ConsultaEstadisticasMensuales,
)
from utilidades.modulo_recalculo import ModuloRecalculo


class MainWindow(QMainWindow):

    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.id_contrato_test = None

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
                    ("❌ Anular/Rehabilitar", lambda: self.abrir_anulacion_contrato()),
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
                            ListaContratosFactura(parent=self, modo="nuevo"),
                            "Nueva factura",
                        ),
                    ),
                    (
                        "✏️ Rectif. factura",
                        lambda: self.cargar_modulo(
                            ListaContratosFactura(parent=self, modo="rectificar"),
                            "Rectificar factura",
                        ),
                    ),
                    (
                        "‼️ Anular factura",
                        lambda: self.cargar_modulo(
                            ListaContratosFactura(parent=self, modo="anular"),
                            "Anular factura",
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
                            ListaContratosHistorico(parent=self, conn=self.conn),
                            "Histórico de contratos",
                        ),
                    ),
                    (
                        "🔎 Histórico de facturas",
                        lambda: self.cargar_modulo(
                            ListaConHisFactura(parent=self), "Histórico de facturas"
                        ),
                    ),
                ],
            )
        )

        # ---------------------------------------------------------
        # COMPARATIVAS (TÍTULO VISUAL)
        # ---------------------------------------------------------
        lbl_comp = QLabel("📈 Comparativas")
        lbl_comp.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(lbl_comp)

        # ---------------------------------------------------------
        # 📊 COMPARATIVA INTERNA (ACORDEÓN)
        # ---------------------------------------------------------
        layout.addWidget(
            self.crear_seccion_acordeon(
                "📊 Comparativa interna",
                [
                    (
                        "▶ Comparativa interna",
                        self.ejecutar_comparativa_interna,
                    ),
                    (
                        "🖨 Comparativa interna",
                        self.imprimir_comparativa_interna,
                    ),
                    (
                        "📄 Exportar a PDF",
                        self.exportar_pdf_comparativa_interna,
                    ),
                ],
            )
        )

        # ---------------------------------------------------------
        # 📦 OFERTA EXTERNA (ACORDEÓN)
        # ---------------------------------------------------------
        layout.addWidget(
            self.crear_seccion_acordeon(
                "📦 Oferta externa",
                [
                    ("➕ Nvo. contrato test", self.abrir_nuevo_contrato_test),
                    ("📥 Fact. reales a test", self.abrir_clonador_facturas_test),
                    ("🔄 Recalcular facturas test", self.abrir_recalculo_test),
                    ("📊 Comp. real vs simulada", self.abrir_comparativa_ofertas),
                ],
            )
        )

        # Utilidades
        layout.addWidget(
            self.crear_seccion_acordeon(
                "🛠️ Utilidades",
                [
                    (
                        "♻️ Recalcular facturas",
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
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Bienvenido al sistema de gestión"))
        layout.addStretch()
        return w

    def crear_pantalla_paleta(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Selecciona una paleta de colores"))

        for nombre, paleta in PALETAS.items():
            btn = QPushButton(nombre)
            aplicar_estilo_boton(btn)
            btn.clicked.connect(lambda _, p=paleta: self.aplicar_paleta(p))
            layout.addWidget(btn)

        layout.addStretch()
        return w

    def crear_pantalla_acerca(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        lbl = QLabel(
            "<b>Gestion_suministros 2.0</b><br>"
            "Proyecto iniciado: <b>enero 2025</b><br>"
            "Programador: <b>Antonio Morales</b><br><br>"
            "Aplicación para la gestión modular de contratos, facturas y comparativas."
        )
        lbl.setWordWrap(True)
        layout.addWidget(lbl)
        layout.addStretch()
        return w

    # ---------------------------------------------------------
    # CARGAR MÓDULO
    # ---------------------------------------------------------
    def cargar_modulo(self, widget, titulo):
        for i in reversed(range(self.zona_contenido_layout.count())):
            item = self.zona_contenido_layout.itemAt(i)
            w = item.widget()
            if w is not None and w is not self.encabezado_modulo:
                self.zona_contenido_layout.removeWidget(w)
                w.deleteLater()

        if titulo is None:
            self.encabezado_modulo.hide()
        else:
            self.encabezado_modulo.setText(titulo)
            self.encabezado_modulo.show()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        widget.setMinimumHeight(600)
        layout.addWidget(widget)

        scroll.setWidget(contenedor)
        self.zona_contenido_layout.addWidget(scroll)

    # ---------------------------------------------------------
    # MÉTODOS DE COMPARATIVAS
    # ---------------------------------------------------------
    def ejecutar_comparativa_interna(self):
        try:
            from analisis_comparativas.comparativa_interna_full import (
                ejecutar_proceso_completo,
            )

            resultado = ejecutar_proceso_completo(self.conn)

            # Convertimos saltos de línea a <br>
            resultado_html = resultado.replace("\n", "<br>")

            # Ponemos el mensaje final en negrita
            resultado_html = resultado_html.replace(
                "🏁 COMPARATIVA INTERNA FINALIZADA",
                "<b>🏁 COMPARATIVA INTERNA FINALIZADA</b>",
            )

            # Crear widget para mostrar el resultado
            w = QWidget()
            layout = QVBoxLayout(w)

            lbl = QLabel(resultado_html)
            lbl.setWordWrap(True)
            lbl.setTextFormat(Qt.RichText)
            lbl.setStyleSheet(
                """
                font-size: 19px;
                padding: 16px;
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 6px;
                line-height: 150%;
            """
            )

            layout.addWidget(lbl)

            # Botón cerrar con estilo secundario REAL
            btn_cerrar = QPushButton("Cerrar")
            btn_cerrar.setProperty("clase", "secundario")  # ← activa el borde
            aplicar_estilo_boton(btn_cerrar, principal=False)
            btn_cerrar.setFixedWidth(120)
            btn_cerrar.clicked.connect(self.volver_inicio)

            layout.addWidget(btn_cerrar, alignment=Qt.AlignRight)
            layout.addStretch()

            self.cargar_modulo(w, "Resultado comparativa interna")

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error ejecutando comparativa interna:\n{e}"
            )

    def imprimir_comparativa_interna(self):
        html = generar_html_comparativa_interna(self.conn)

        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)

        if dialog.exec():
            doc = QTextDocument()
            doc.setHtml(html)
            doc.print_(printer)

    def exportar_pdf_comparativa_interna(self):
        html = generar_html_comparativa_interna(self.conn)

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar informe comparativa interna como PDF",
            "comparativa_interna.pdf",
            "PDF (*.pdf)",
        )

        if not ruta:
            return

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(ruta)

        doc = QTextDocument()
        doc.setHtml(html)
        doc.print_(printer)

    # ---------------------------------------------------------
    # NUEVO CONTRATO
    # ---------------------------------------------------------
    def abrir_nuevo_contrato(self):
        modulo = NuevoContrato(parent=self)
        modulo.cerrado.connect(self.volver_inicio)
        self.cargar_modulo(modulo, "Nuevo contrato")

    def volver_inicio(self):
        self.cargar_modulo(self.crear_pantalla_inicio(), None)

    def volver_menu_principal(self):
        self.volver_inicio()

    # ---------------------------------------------------------
    # MODIFICAR CONTRATO
    # ---------------------------------------------------------
    def abrir_modificacion_contratos(self):
        lista = ListaContratos(parent=self, modo="modificacion")
        self.cargar_modulo(lista, "Modificar contrato")

    # ---------------------------------------------------------
    # MÉTODOS PARA OFERTA EXTERNA
    # ---------------------------------------------------------
    def abrir_nuevo_contrato_test(self):
        from contratos.nuevo_contrato_test import NuevoContratoTest

        modulo = NuevoContratoTest(parent=self)

        # 1) Guardar el id del contrato test si existe
        modulo.cerrado.connect(
            lambda: setattr(
                self, "id_contrato_test", getattr(modulo, "id_contrato", None)
            )
        )

        # 2) Volver al menú principal
        modulo.cerrado.connect(self.volver_inicio)

        self.cargar_modulo(modulo, "Nuevo contrato ficticio")

    def abrir_clonador_facturas_test(self):

        # Comprobar si existe contrato ficticio en la BD
        cursor = self.conn.cursor()
        cursor.execute("SELECT ncontrato FROM contratos_identificacion_test LIMIT 1")
        row = cursor.fetchone()

        if row is None:
            QMessageBox.warning(
                self,
                "Contrato ficticio no definido",
                "Debe crear primero un contrato ficticio.",
            )
            return

        from facturas.clonador_facturas_test import ClonadorFacturasTest

        modulo = ClonadorFacturasTest(parent=self)
        self.cargar_modulo(modulo, "Clonar facturas reales")

    def abrir_comparativa_ofertas(self):
        from analisis_comparativas.comparativa_ofertas import ComparativaOfertas

        modulo = ComparativaOfertas(parent=self)
        self.cargar_modulo(modulo, "Comparativa real vs simulada")

    def abrir_recalculo_test(self):
        try:
            resultado = recalcular_facturas_test(self.conn)

            mensaje = (
                f"Total facturas: {resultado['total']}\n"
                f"Procesadas: {resultado['procesadas']}\n"
            )

            if resultado["errores"]:
                mensaje += "\nErrores:\n" + "\n".join(resultado["errores"])

            QMessageBox.information(self, "Recalculo TEST", mensaje)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en recálculo test:\n{str(e)}")

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
        widget = ListaContratos(parent=self, modo="anulacion")
        self.cargar_modulo(widget, "Anulación de contrato")

    # ---------------------------------------------------------
    # PALETA
    # ---------------------------------------------------------
    def aplicar_paleta(self, paleta):
        from estilo import generar_stylesheet

        self.setStyleSheet(generar_stylesheet(paleta))
