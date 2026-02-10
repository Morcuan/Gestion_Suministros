# ----------------------------------------------------------- #
#  Modulo: detalles_contrato.py                               #
#  Descripción: Vista de detalles del contrato (consulta)     #
#  Autor: Antonio Morales                                      #
#  Fecha: 2026-02-10                                           #
# ----------------------------------------------------------- #

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class DetallesContratoWidget(QWidget):
    """
    Vista de detalles del contrato según DRU.
    Tres bloques: Identificación, Energía, Gastos e Impuestos.
    Consulta filtrada por suplemento activo.
    """

    def __init__(self, conn, ncontrato, parent=None):
        super().__init__(parent)

        self.conn = conn
        self.ncontrato = ncontrato

        self.setWindowTitle(f"Detalles del contrato")

        layout = QVBoxLayout(self)

        # ---------------------------------------------------------
        # TÍTULO
        # ---------------------------------------------------------
        titulo = QLabel(f"Detalles del contrato")
        titulo.setFont(QFont("DejaVu Sans", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # ---------------------------------------------------------
        # SCROLL (por si hay pantallas pequeñas)
        # ---------------------------------------------------------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        contenedor = QWidget()
        scroll.setWidget(contenedor)
        layout.addWidget(scroll)

        cuerpo = QVBoxLayout(contenedor)

        # ---------------------------------------------------------
        # CARGAR DATOS DEL SUPLEMENTO ACTIVO
        # ---------------------------------------------------------
        datos = self.cargar_datos()

        if not datos:
            cuerpo.addWidget(QLabel("No se encontraron datos para este contrato."))
            return

        (
            ncontrato,
            suplemento,
            estado,
            compania,
            cp,
            poblacion,
            fec_inicio,
            fec_final,
            efec_suple,
            fin_suple,
            fec_anulacion,
            ppunta,
            pv_ppunta,
            pvalle,
            pv_pvalle,
            pv_conpunta,
            pv_conllano,
            pv_convalle,
            vertido,
            pv_excedent,
            bono_social,
            alq_contador,
            otros_gastos,
            i_electrico,
            iva,
        ) = datos

        # ---------------------------------------------------------
        # BLOQUE IDENTIFICACIÓN
        # ---------------------------------------------------------
        cuerpo.addWidget(
            self._crear_bloque_identificacion(
                ncontrato,
                suplemento,
                estado,
                compania,
                cp,
                poblacion,
                fec_inicio,
                fec_final,
                efec_suple,
                fin_suple,
                fec_anulacion,
            )
        )

        # ---------------------------------------------------------
        # BLOQUE ENERGÍA
        # ---------------------------------------------------------
        cuerpo.addWidget(
            self._crear_bloque_energia(
                ppunta,
                pv_ppunta,
                pvalle,
                pv_pvalle,
                pv_conpunta,
                pv_conllano,
                pv_convalle,
                vertido,
                pv_excedent,
            )
        )

        # ---------------------------------------------------------
        # BLOQUE GASTOS E IMPUESTOS
        # ---------------------------------------------------------
        cuerpo.addWidget(
            self._crear_bloque_gastos(
                bono_social, i_electrico, alq_contador, otros_gastos, iva
            )
        )

        # ---------------------------------------------------------
        # BOTONES
        # ---------------------------------------------------------
        botones = QHBoxLayout()
        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_facturas = QPushButton("Ver facturas")

        botones.addWidget(self.btn_cerrar)
        botones.addStretch()
        botones.addWidget(self.btn_facturas)

        layout.addLayout(botones)

        # Eventos
        self.btn_cerrar.clicked.connect(self.volver)
        self.btn_facturas.clicked.connect(self.ver_facturas)

    # ============================================================
    #   CONSULTA SQL: SUPLEMENTO ACTIVO
    # ============================================================
    def cargar_datos(self):
        cur = self.conn.cursor()

        hoy = QDate.currentDate().toString("yyyy-MM-dd")

        cur.execute(
            """
            SELECT
                ci.ncontrato, ci.suplemento, ci.estado, ci.compania,
                ci.codigo_postal, cp.poblacion,
                ci.fec_inicio, ci.fec_final, ci.efec_suple, ci.fin_suple,
                ci.fec_anulacion,
                ce.ppunta, ce.pv_ppunta, ce.pvalle, ce.pv_pvalle,
                ce.pv_conpunta, ce.pv_conllano, ce.pv_convalle,
                ce.vertido, ce.pv_excedent,
                cg.bono_social, cg.alq_contador, cg.otros_gastos,
                cg.i_electrico, cg.iva
            FROM contratos_identificacion ci
            JOIN contratos_energia ce ON ci.id_contrato = ce.id_contrato
            JOIN contratos_gastos cg ON ci.id_contrato = cg.id_contrato
            JOIN cpostales cp ON ci.codigo_postal = cp.codigo_postal
            WHERE ci.ncontrato = ?
              AND date(?) BETWEEN date(ci.efec_suple) AND date(ci.fin_suple)
            LIMIT 1;
            """,
            (self.ncontrato, hoy),
        )

        return cur.fetchone()

    # ============================================================
    #   BLOQUES DE DATOS
    # ============================================================
    def _crear_bloque_identificacion(
        self,
        ncontrato,
        suplemento,
        estado,
        compania,
        cp,
        poblacion,
        fec_inicio,
        fec_final,
        efec_suple,
        fin_suple,
        fec_anulacion,
    ):
        bloque = QWidget()
        grid = QGridLayout(bloque)

        titulo = QLabel("Identificación")
        titulo.setFont(QFont("DejaVu Sans", 14, QFont.Bold))
        grid.addWidget(titulo, 0, 0, 1, 2)

        etiquetas = [
            ("Nº de contrato", ncontrato),
            ("Nº de suplemento", suplemento),
            ("Estado del contrato", estado),
            ("Distribuidora", compania),
            ("Cod. Postal", cp),
            ("Población", poblacion),
            ("Desde", fec_inicio),
            ("Hasta", fec_final),
            ("Dat. Válidos desde", efec_suple),
            ("Dat. Válidos hasta", fin_suple),
            ("Fec. Anulación", fec_anulacion),
        ]

        fila = 1
        for etiqueta, valor in etiquetas:
            # Limpieza: si valor es None, vacío
            valor = "" if valor is None else valor

            grid.addWidget(QLabel(etiqueta + ":"), fila, 0)
            grid.addWidget(QLabel(str(valor)), fila, 1)
            fila += 1

        return bloque

    def _crear_bloque_energia(
        self,
        ppunta,
        pv_ppunta,
        pvalle,
        pv_pvalle,
        pv_conpunta,
        pv_conllano,
        pv_convalle,
        vertido,
        pv_excedent,
    ):
        bloque = QWidget()
        grid = QGridLayout(bloque)

        titulo = QLabel("Energía")
        titulo.setFont(QFont("DejaVu Sans", 14, QFont.Bold))
        grid.addWidget(titulo, 0, 0, 1, 2)

        etiquetas = [
            ("Pot. Punta (kWh)", ppunta),
            ("€ kWh Punta", pv_ppunta),
            ("Pot. Valle (kWh)", pvalle),
            ("€ kWh Valle", pv_pvalle),
            ("Cons. Punta (€)", pv_conpunta),
            ("Cons. Llano (€)", pv_conllano),
            ("Cons. Valle (€)", pv_convalle),
            ("Aut. vertido", vertido),
            ("kWh vertido (€)", pv_excedent),
        ]

        fila = 1
        for etiqueta, valor in etiquetas:
            grid.addWidget(QLabel(etiqueta + ":"), fila, 0)
            grid.addWidget(QLabel(str(valor)), fila, 1)
            fila += 1

        return bloque

    def _crear_bloque_gastos(
        self, bono_social, i_electrico, alq_contador, otros_gastos, iva
    ):
        bloque = QWidget()
        grid = QGridLayout(bloque)

        titulo = QLabel("Gastos e Impuestos")
        titulo.setFont(QFont("DejaVu Sans", 14, QFont.Bold))
        grid.addWidget(titulo, 0, 0, 1, 2)

        etiquetas = [
            ("Bono Social (€)", bono_social),
            ("Imp. Electricidad (%)", i_electrico),
            ("Equip. de medida (€)", alq_contador),
            ("Otros (€)", otros_gastos),
            ("IVA (%)", iva),
        ]

        fila = 1
        for etiqueta, valor in etiquetas:
            grid.addWidget(QLabel(etiqueta + ":"), fila, 0)
            grid.addWidget(QLabel(str(valor)), fila, 1)
            fila += 1

        return bloque

    # ============================================================
    #   NAVEGACIÓN
    # ============================================================
    def volver(self):
        from consulta_contratos import ConsultaContratosWidget

        marco = self.window()
        lista = ConsultaContratosWidget(self.conn, parent=marco)
        marco.cargar_modulo(lista, "Consulta contratos")

    def ver_facturas(self):
        if self.parent():
            self.parent().abrir_facturas(self.ncontrato)
