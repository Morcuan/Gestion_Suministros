# -----------------------------------------------------------------
# Modulo: grafico_consumos.py
# Descripción: Módulo gráfico de consumos mensuales (Punta, Llano, Valle, Excedentes)
# -----------------------------------------------------------------

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker  # <-- Importante para controlar las escalas y ticks
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class DialogoSeleccionContrato(QDialog):
    """Diálogo previo para seleccionar el contrato antes de mostrar el gráfico."""

    def __init__(self, contratos_disponibles, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar Contrato")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Seleccione el contrato a representar:"))
        self.combo_contratos = QComboBox()
        self.combo_contratos.addItems(contratos_disponibles)
        layout.addWidget(self.combo_contratos)

        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.clicked.connect(self.accept)
        layout.addWidget(btn_aceptar)

    def obtener_contrato_seleccionado(self):
        return self.combo_contratos.currentText()


class WidgetGraficoConsumos(QWidget):
    """Widget principal que contendrá el gráfico en la zona de contenido."""

    def __init__(self, conn, contrato_seleccionado, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.contrato = contrato_seleccionado

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Cargar datos de la vista filtrados por el contrato
        df_datos = self.cargar_datos_vista()

        if df_datos.empty:
            layout.addWidget(
                QLabel("No existen registros de consumos para este contrato.")
            )
            return

        # Crear la figura de Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(10, 6), constrained_layout=True)

        # 1. ORDENACIÓN CRONOLÓGICA CORRECTA (mes-año)
        if "mes_año" in df_datos.columns:
            df_datos["_fecha_temp"] = pd.to_datetime(
                df_datos["mes_año"], format="%m-%Y", errors="coerce"
            )
            df_datos = df_datos.sort_values(by="_fecha_temp")
            df_datos = df_datos.drop(columns=["_fecha_temp"])
            df_datos = df_datos.set_index("mes_año")

        columnas_consumo = ["Punta", "Llano", "Valle", "Excedentes"]
        cols_disponibles = [c for c in columnas_consumo if c in df_datos.columns]

        # 2. COLORES ESPECÍFICOS SOLICITADOS
        mapa_colores = {
            "Excedentes": "#2ca02c",  # Verde
            "Punta": "#d62728",  # Rojo
            "Llano": "#ff7f0e",  # Naranja
            "Valle": "#1f77b4",  # Azul
        }
        colores_lista = [mapa_colores.get(col, "#333333") for col in cols_disponibles]

        # Pintar gráfico de barras apiladas
        df_datos[cols_disponibles].plot(
            kind="bar",
            stacked=True,
            ax=self.ax,
            edgecolor="black",
            color=colores_lista,
        )

        self.ax.set_title(
            f"Consumos y Excedentes Mensuales - Contrato: {self.contrato}",
            fontsize=12,
            fontweight="bold",
        )
        self.ax.set_xlabel("Mes / Año", fontsize=10)
        self.ax.set_ylabel("Energía (kWh)", fontsize=10)
        self.ax.legend(title="Tarifas / Flujos")

        # -------------------------------------------------------------
        # 3. CONFIGURACIÓN DE ESCALAS Y LÍNEAS DE REFERENCIA (EJEY)
        # -------------------------------------------------------------
        # Marcas principales cada 50 unidades (ej: 50, 100, 150, 200...)
        self.ax.yaxis.set_major_locator(ticker.MultipleLocator(50))
        # Marcas secundarias/intermedias cada 10 unidades
        self.ax.yaxis.set_minor_locator(ticker.MultipleLocator(10))

        # Activar la grilla principal para las marcas de 50 (línea punteada visible)
        self.ax.grid(
            True, which="major", linestyle="--", linewidth=0.8, alpha=0.7, color="grey"
        )
        # Activar la grilla secundaria para las marcas de 10 (línea más sutil y punteada fina)
        self.ax.grid(
            True, which="minor", linestyle=":", linewidth=0.4, alpha=0.4, color="grey"
        )

        # Rotar etiquetas del eje X para legibilidad
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha="right")

        # Incrustar el canvas en PySide6
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

    def cargar_datos_vista(self):
        """Consulta la vista de la base de datos para el contrato seleccionado."""
        try:
            query = f"""
                SELECT mes_año, Punta, Llano, Valle, Excedentes
                FROM v_consumos
                WHERE ncontrato = '{self.contrato}'
            """
            df = pd.read_sql(query, self.conn)
            return df
        except Exception as e:
            print(f"Error consultando vista: {e}")
            return pd.DataFrame()
