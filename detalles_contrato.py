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

from consulta_facturas import ConsultaFacturasWidget


class DetallesContratoWidget(QWidget):
    """
    Vista de detalles del contrato según DRU.
    Tres bloques: Identificación, Energía, Gastos e Impuestos.
    Consulta filtrada por suplemento activo o por suplemento específico.
    """

    def __init__(
        self, conn, ncontrato, suplemento=None, parent=None, mostrar_botones=True
    ):
        super().__init__(parent)

        self.conn = conn
        self.ncontrato = ncontrato
        self.suplemento = suplemento
        self.mostrar_botones = mostrar_botones

        layout = QVBoxLayout(self)

        # ---------------------------------------------------------
        # TÍTULO LOCAL
        # ---------------------------------------------------------
        titulo = QLabel("Detalles del contrato")
        titulo.setFont(QFont("DejaVu Sans", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # ---------------------------------------------------------
        # SCROLL
        # ---------------------------------------------------------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        contenedor = QWidget()
        scroll.setWidget(contenedor)
        layout.addWidget(scroll)

        cuerpo = QVBoxLayout(contenedor)

        # ---------------------------------------------------------
        # CARGAR DATOS
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

        cuerpo.addWidget(
            self._crear_bloque_gastos(
                bono_social, i_electrico, alq_contador, otros_gastos, iva
            )
        )

        # ---------------------------------------------------------
        # BOTONES (solo si se permite mostrarlos)
        # ---------------------------------------------------------
        if self.mostrar_botones:
            botones = QHBoxLayout()
            self.btn_facturas = QPushButton("Ver facturas")
            self.btn_cerrar = QPushButton("Cerrar")

            botones.addWidget(self.btn_facturas)
            botones.addStretch()
            botones.addWidget(self.btn_cerrar)

            layout.addLayout(botones)

            # Eventos
            self.btn_cerrar.clicked.connect(self.volver)
            self.btn_facturas.clicked.connect(self.ver_facturas)

    # ============================================================
    #   CONSULTA SQL: SUPLEMENTO ACTIVO O HISTÓRICO
    # ============================================================
    def cargar_datos(self):
        cur = self.conn.cursor()

        # ---------------------------------------------
        # CASO 1: SIN suplemento → comportamiento original
        # ---------------------------------------------
        if self.suplemento is None:
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

        # ---------------------------------------------
        # CASO 2: Con suplemento → consulta histórica exacta
        # ---------------------------------------------
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
              AND ci.suplemento = ?
            LIMIT 1;
            """,
            (self.ncontrato, self.suplemento),
        )

        return cur.fetchone()

    # ============================================================
    #   OBTENER ID_CONTRATO REAL
    # ============================================================
    def obtener_id_contrato(self):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id_contrato FROM contratos_identificacion WHERE ncontrato = ? LIMIT 1;",
            (self.ncontrato,),
        )
        fila = cur.fetchone()
        return fila[0] if fila else None

    # ============================================================
    #   BLOQUES DE DATOS
    # ============================================================
    def _crear_bloque_identificacion(self, *args):
        bloque = QWidget()
        grid = QGridLayout(bloque)

        titulo = QLabel("Identificación")
        titulo.setFont(QFont("DejaVu Sans", 14, QFont.Bold))
        grid.addWidget(titulo, 0, 0, 1, 2)

        etiquetas = [
            ("Nº de contrato", args[0]),
            ("Nº de suplemento", args[1]),
            ("Estado del contrato", args[2]),
            ("Distribuidora", args[3]),
            ("Cod. Postal", args[4]),
            ("Población", args[5]),
            ("Desde", args[6]),
            ("Hasta", args[7]),
            ("Dat. Válidos desde", args[8]),
            ("Dat. Válidos hasta", args[9]),
            ("Fec. Anulación", args[10]),
        ]

        fila = 1
        for etiqueta, valor in etiquetas:
            valor = "" if valor is None else valor
            grid.addWidget(QLabel(etiqueta + ":"), fila, 0)
            grid.addWidget(QLabel(str(valor)), fila, 1)
            fila += 1

        return bloque

    def _crear_bloque_energia(self, *args):
        bloque = QWidget()
        grid = QGridLayout(bloque)

        titulo = QLabel("Energía")
        titulo.setFont(QFont("DejaVu Sans", 14, QFont.Bold))
        grid.addWidget(titulo, 0, 0, 1, 2)

        etiquetas = [
            ("Pot. Punta (kWh)", args[0]),
            ("€ kWh Punta", args[1]),
            ("Pot. Valle (kWh)", args[2]),
            ("€ kWh Valle", args[3]),
            ("Cons. Punta (€)", args[4]),
            ("Cons. Llano (€)", args[5]),
            ("Cons. Valle (€)", args[6]),
            ("Aut. vertido", args[7]),
            ("kWh vertido (€)", args[8]),
        ]

        fila = 1
        for etiqueta, valor in etiquetas:
            grid.addWidget(QLabel(etiqueta + ":"), fila, 0)
            grid.addWidget(QLabel(str(valor)), fila, 1)
            fila += 1

        return bloque

    def _crear_bloque_gastos(self, *args):
        bloque = QWidget()
        grid = QGridLayout(bloque)

        titulo = QLabel("Gastos e Impuestos")
        titulo.setFont(QFont("DejaVu Sans", 14, QFont.Bold))
        grid.addWidget(titulo, 0, 0, 1, 2)

        etiquetas = [
            ("Bono Social (€)", args[0]),
            ("Imp. Electricidad (%)", args[1]),
            ("Equip. de medida (€)", args[2]),
            ("Otros (€)", args[3]),
            ("IVA (%)", args[4]),
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
        idc = self.obtener_id_contrato()
        if idc is None:
            self.mostrar_aviso("Error", "No se pudo obtener el ID del contrato.")
            return

        marco = self.window()
        vista = ConsultaFacturasWidget(self.conn, idc, parent=marco)
        marco.cargar_modulo(vista, "Facturas del contrato")
