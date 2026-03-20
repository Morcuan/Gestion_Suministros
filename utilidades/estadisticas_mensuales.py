# ------------------------------------------------#
# Modulo: estadisticas_mensuales.py               #
# Descripción: Estadísticas mensuales FV          #
# Autor: Antonio Morales                          #
# Fecha: 2026-03-18                               #
# ------------------------------------------------#

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from estilo import aplicar_estilo_boton

# ---------------------------------------------------------
# MESES
# ---------------------------------------------------------

MESES = [
    ("01", "Enero"),
    ("02", "Febrero"),
    ("03", "Marzo"),
    ("04", "Abril"),
    ("05", "Mayo"),
    ("06", "Junio"),
    ("07", "Julio"),
    ("08", "Agosto"),
    ("09", "Septiembre"),
    ("10", "Octubre"),
    ("11", "Noviembre"),
    ("12", "Diciembre"),
]


# ---------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------


def calcular_fechas_inicio_fin(anio: int, mes_num: int):
    if mes_num == 12:
        anio_fin = anio + 1
        mes_fin = 1
    else:
        anio_fin = anio
        mes_fin = mes_num + 1

    fecha_inicio = f"{anio:04d}-{mes_num:02d}-01"
    fecha_fin = f"{anio_fin:04d}-{mes_fin:02d}-01"
    return fecha_inicio, fecha_fin


def existe_mes_registrado(cursor, anio: int, mes_num: int) -> bool:
    fecha_inicio, _ = calcular_fechas_inicio_fin(anio, mes_num)
    cursor.execute(
        "SELECT COUNT(*) FROM estadisticas_mensuales WHERE fecha_inicio = ?",
        (fecha_inicio,),
    )
    return cursor.fetchone()[0] > 0


# ---------------------------------------------------------
# CLASE DETALLE
# ---------------------------------------------------------


class DetalleEstadistica(QWidget):
    def __init__(self, parent, registro):
        super().__init__(parent)
        self.setObjectName("DetalleEstadistica")

        layout = QVBoxLayout(self)

        titulo = QLabel("Detalle estadística mensual")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo, alignment=Qt.AlignHCenter)

        layout.addStretch()

        grid = QGridLayout()
        etiquetas = [
            ("ID:", registro[0]),
            ("Fecha inicio:", registro[1]),
            ("Fecha fin:", registro[2]),
            ("Producción (kWh):", registro[3]),
            ("Consumo (kWh):", registro[4]),
            ("Excedentes (kWh):", registro[5]),
            ("Comprado (kWh):", registro[6]),
            ("Fuente:", registro[7]),
        ]

        for fila, (txt, val) in enumerate(etiquetas):
            grid.addWidget(QLabel(txt), fila, 0, alignment=Qt.AlignRight)
            grid.addWidget(QLabel(str(val)), fila, 1, alignment=Qt.AlignLeft)

        layout.addLayout(grid)

        layout.addStretch()

        btn_cerrar = QPushButton("Salir")
        aplicar_estilo_boton(btn_cerrar, principal=False)
        btn_cerrar.clicked.connect(self.volver_inicio)
        layout.addWidget(btn_cerrar, alignment=Qt.AlignRight)

    # Obtener MainWindow real
    def get_main_window(self):
        w = self
        while w is not None:
            if isinstance(w, QMainWindow):
                return w
            w = w.parent()
        return None

    def volver_inicio(self):
        mw = self.get_main_window()
        if mw:
            mw.cargar_modulo(mw.crear_pantalla_inicio(), "Pantalla de Inicio")


# ---------------------------------------------------------
# CLASE CAPTURA
# ---------------------------------------------------------


class CapturaEstadisticasMensuales(QWidget):
    def __init__(self, parent, conn, cursor):
        super().__init__(parent)
        self.conn = conn
        self.cursor = cursor

        self.setObjectName("CapturaEstadisticasMensuales")

        layout = QVBoxLayout(self)

        titulo = QLabel("Captura de estadísticas mensuales")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo, alignment=Qt.AlignHCenter)

        layout.addStretch()

        grid = QGridLayout()

        self.cmb_mes = QComboBox()
        for _, nombre in MESES:
            self.cmb_mes.addItem(nombre)

        self.txt_anio = QLineEdit()
        self.txt_produccion = QLineEdit()
        self.txt_consumo = QLineEdit()
        self.txt_excedentes = QLineEdit()
        self.txt_comprado = QLineEdit()
        self.cmb_fuente = QComboBox()
        self.cmb_fuente.addItems(["manual", "app"])

        grid.addWidget(QLabel("Mes:"), 0, 0, alignment=Qt.AlignRight)
        grid.addWidget(self.cmb_mes, 0, 1)

        grid.addWidget(QLabel("Año:"), 1, 0, alignment=Qt.AlignRight)
        grid.addWidget(self.txt_anio, 1, 1)

        grid.addWidget(QLabel("Producción (kWh):"), 2, 0, alignment=Qt.AlignRight)
        grid.addWidget(self.txt_produccion, 2, 1)

        grid.addWidget(QLabel("Consumo (kWh):"), 3, 0, alignment=Qt.AlignRight)
        grid.addWidget(self.txt_consumo, 3, 1)

        grid.addWidget(QLabel("Excedentes (kWh):"), 4, 0, alignment=Qt.AlignRight)
        grid.addWidget(self.txt_excedentes, 4, 1)

        grid.addWidget(QLabel("Comprado (kWh):"), 5, 0, alignment=Qt.AlignRight)
        grid.addWidget(self.txt_comprado, 5, 1)

        grid.addWidget(QLabel("Fuente:"), 6, 0, alignment=Qt.AlignRight)
        grid.addWidget(self.cmb_fuente, 6, 1)

        layout.addLayout(grid)

        layout.addStretch()

        botones = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_limpiar = QPushButton("Limpiar")
        btn_salir = QPushButton("Salir")

        aplicar_estilo_boton(btn_guardar)
        aplicar_estilo_boton(btn_limpiar, principal=False)
        aplicar_estilo_boton(btn_salir, principal=False)

        btn_guardar.clicked.connect(self.guardar)
        btn_limpiar.clicked.connect(self.limpiar)
        btn_salir.clicked.connect(self.volver_inicio)

        botones.addStretch()
        botones.addWidget(btn_guardar)
        botones.addWidget(btn_limpiar)
        botones.addWidget(btn_salir)

        layout.addLayout(botones)

    # Obtener MainWindow real
    def get_main_window(self):
        w = self
        while w is not None:
            if isinstance(w, QMainWindow):
                return w
            w = w.parent()
        return None

    def volver_inicio(self):
        mw = self.get_main_window()
        if mw:
            mw.cargar_modulo(mw.crear_pantalla_inicio(), "Pantalla de Inicio")

    def limpiar(self):
        self.cmb_mes.setCurrentIndex(0)
        self.txt_anio.clear()
        self.txt_produccion.clear()
        self.txt_consumo.clear()
        self.txt_excedentes.clear()
        self.txt_comprado.clear()
        self.cmb_fuente.setCurrentIndex(0)

    def leer_float(self, line_edit: QLineEdit, nombre: str):
        txt = line_edit.text().strip().replace(",", ".")
        try:
            v = float(txt)
        except ValueError:
            QMessageBox.warning(self, "Aviso", f"{nombre} debe ser un número válido.")
            raise
        if v < 0:
            QMessageBox.warning(self, "Aviso", f"{nombre} no puede ser negativo.")
            raise ValueError
        return v

    def guardar(self):
        mes_nombre = self.cmb_mes.currentText().strip()
        anio_txt = self.txt_anio.text().strip()

        if not mes_nombre or not anio_txt:
            QMessageBox.warning(self, "Aviso", "Debe indicar mes y año.")
            return

        try:
            anio = int(anio_txt)
        except ValueError:
            QMessageBox.warning(self, "Aviso", "El año debe ser numérico.")
            return

        mes_num = next((int(num) for num, nom in MESES if nom == mes_nombre), None)
        if mes_num is None:
            QMessageBox.critical(self, "Error", "Mes no válido.")
            return

        try:
            produccion = self.leer_float(self.txt_produccion, "Producción")
            consumo = self.leer_float(self.txt_consumo, "Consumo")
            excedentes = self.leer_float(self.txt_excedentes, "Excedentes")
            comprado = self.leer_float(self.txt_comprado, "Comprado")
        except Exception:
            return

        if existe_mes_registrado(self.cursor, anio, mes_num):
            resp = QMessageBox.question(
                self,
                "Confirmar",
                "Ya existe un registro para ese mes y año.\n¿Desea sobrescribirlo?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if resp != QMessageBox.Yes:
                return
            fecha_inicio_existente, _ = calcular_fechas_inicio_fin(anio, mes_num)
            self.cursor.execute(
                "DELETE FROM estadisticas_mensuales WHERE fecha_inicio = ?",
                (fecha_inicio_existente,),
            )
            self.conn.commit()

        fecha_inicio, fecha_fin = calcular_fechas_inicio_fin(anio, mes_num)
        fuente = self.cmb_fuente.currentText().strip() or "manual"

        self.cursor.execute(
            """
            INSERT INTO estadisticas_mensuales
            (fecha_inicio, fecha_fin, produccion, consumo, excedentes, comprado, fuente)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fecha_inicio,
                fecha_fin,
                produccion,
                consumo,
                excedentes,
                comprado,
                fuente,
            ),
        )
        self.conn.commit()

        QMessageBox.information(self, "Información", "Registro guardado correctamente.")
        self.limpiar()


# ---------------------------------------------------------
# CLASE CONSULTA
# ---------------------------------------------------------


class ConsultaEstadisticasMensuales(QWidget):
    def __init__(self, parent, conn, cursor):
        super().__init__(parent)
        self.conn = conn
        self.cursor = cursor

        self.setObjectName("ConsultaEstadisticasMensuales")

        layout = QVBoxLayout(self)

        titulo = QLabel("Estadísticas mensuales")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo, alignment=Qt.AlignHCenter)

        layout.addStretch()

        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Año:"))

        self.cmb_anio = QComboBox()
        self.cargar_anios()
        filtro_layout.addWidget(self.cmb_anio)

        btn_buscar = QPushButton("Buscar")
        aplicar_estilo_boton(btn_buscar)
        btn_buscar.clicked.connect(self.cargar_datos)
        filtro_layout.addWidget(btn_buscar)

        filtro_layout.addStretch()
        layout.addLayout(filtro_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["Mes", "Producción", "Consumo", "Excedentes", "Comprado", "Fuente"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.tabla)

        layout.addStretch()

        botones = QHBoxLayout()

        btn_detalle = QPushButton("Ver detalle")
        btn_eliminar = QPushButton("Eliminar")
        btn_capturar = QPushButton("Capturar mes")
        btn_salir = QPushButton("Salir")

        aplicar_estilo_boton(btn_detalle, principal=False)
        aplicar_estilo_boton(btn_eliminar, principal=False)
        aplicar_estilo_boton(btn_capturar)
        aplicar_estilo_boton(btn_salir, principal=False)

        btn_detalle.clicked.connect(self.ver_detalle)
        btn_eliminar.clicked.connect(self.eliminar)
        btn_capturar.clicked.connect(self.abrir_captura)
        btn_salir.clicked.connect(self.volver_inicio)

        botones.addWidget(btn_detalle)
        botones.addWidget(btn_eliminar)
        botones.addStretch()
        botones.addWidget(btn_capturar)
        botones.addWidget(btn_salir)

        layout.addLayout(botones)

    # Obtener MainWindow real
    def get_main_window(self):
        w = self
        while w is not None:
            if isinstance(w, QMainWindow):
                return w
            w = w.parent()
        return None

    def volver_inicio(self):
        mw = self.get_main_window()
        if mw:
            mw.cargar_modulo(mw.crear_pantalla_inicio(), "Pantalla de Inicio")

    def cargar_anios(self):
        self.cmb_anio.clear()
        self.cursor.execute(
            "SELECT DISTINCT substr(fecha_inicio,1,4) FROM estadisticas_mensuales ORDER BY 1 DESC"
        )
        anios = [fila[0] for fila in self.cursor.fetchall()]
        self.cmb_anio.addItems(anios)

    def cargar_datos(self):
        self.tabla.setRowCount(0)
        anio = self.cmb_anio.currentText().strip()
        if not anio:
            return

        self.cursor.execute(
            """
            SELECT id, fecha_inicio, produccion, consumo, excedentes, comprado, fuente
            FROM estadisticas_mensuales
            WHERE substr(fecha_inicio,1,4) = ?
            ORDER BY fecha_inicio ASC
            """,
            (anio,),
        )

        filas = self.cursor.fetchall()
        self.tabla.setRowCount(len(filas))

        for fila_idx, fila in enumerate(filas):
            id_, fecha_inicio, prod, cons, exc, comp, fuente = fila
            mes = fecha_inicio[5:7]

            item_mes = QTableWidgetItem(mes)
            item_mes.setData(Qt.UserRole, id_)

            self.tabla.setItem(fila_idx, 0, item_mes)
            self.tabla.setItem(fila_idx, 1, QTableWidgetItem(str(prod)))
            self.tabla.setItem(fila_idx, 2, QTableWidgetItem(str(cons)))
            self.tabla.setItem(fila_idx, 3, QTableWidgetItem(str(exc)))
            self.tabla.setItem(fila_idx, 4, QTableWidgetItem(str(comp)))
            self.tabla.setItem(fila_idx, 5, QTableWidgetItem(fuente or ""))

    def obtener_id_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return None
        item = self.tabla.item(fila, 0)
        if not item:
            return None
        return item.data(Qt.UserRole)

    def ver_detalle(self):
        id_sel = self.obtener_id_seleccionado()
        if id_sel is None:
            QMessageBox.warning(self, "Aviso", "Seleccione un registro.")
            return

        self.cursor.execute(
            "SELECT * FROM estadisticas_mensuales WHERE id = ?", (id_sel,)
        )
        registro = self.cursor.fetchone()
        if not registro:
            QMessageBox.warning(self, "Aviso", "Registro no encontrado.")
            return

        detalle = DetalleEstadistica(self.parent(), registro)
        mw = self.get_main_window()
        if mw:
            mw.cargar_modulo(detalle, "Detalle estadística mensual")

    def eliminar(self):
        id_sel = self.obtener_id_seleccionado()
        if id_sel is None:
            QMessageBox.warning(self, "Aviso", "Seleccione un registro.")
            return

        resp = QMessageBox.question(
            self,
            "Confirmar",
            "¿Eliminar el registro seleccionado?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return

        self.cursor.execute(
            "DELETE FROM estadisticas_mensuales WHERE id = ?", (id_sel,)
        )
        self.conn.commit()
        self.cargar_datos()

    def abrir_captura(self):
        captura = CapturaEstadisticasMensuales(
            parent=self.parent(), conn=self.conn, cursor=self.cursor
        )
        mw = self.get_main_window()
        if mw:
            mw.cargar_modulo(captura, "Captura estadísticas mensuales")
