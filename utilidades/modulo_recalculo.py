# -------------------------------------------------------------#
# Módulo: modulo_recalculo.py                                  #
# Descripción: Interfaz para el recálculo masivo de facturas   #
# Autor: Antonio Morales                                       #
# Fecha: 2026-04                                               #
# -------------------------------------------------------------#

from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from utilidades.recalculo import recalcular_facturas


class ModuloRecalculo(QWidget):
    """
    Módulo visual para lanzar el recálculo masivo de facturas.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.conn = parent.conn  # MainWindow expone la conexión
        self.crear_ui()
        self.cargar_pendientes()  # ← Información inicial al abrir la ventana

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def crear_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Área de log
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        layout.addWidget(self.txt_log)

        # Botones
        botones = QHBoxLayout()

        self.btn_iniciar = QPushButton("Iniciar recálculo")
        self.btn_iniciar.clicked.connect(self.iniciar_recalculo)
        botones.addWidget(self.btn_iniciar)

        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.cerrar)
        botones.addWidget(self.btn_cerrar)

        layout.addLayout(botones)

    # ---------------------------------------------------------
    # Información inicial
    # ---------------------------------------------------------
    def cargar_pendientes(self):
        """
        Muestra en pantalla las facturas que tienen flag 'recalcular = 1'.
        Se ejecuta automáticamente al abrir la ventana.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT nfactura, ncontrato, fec_emision
            FROM facturas
            WHERE recalcular = 1
            ORDER BY fec_emision ASC
        """
        )
        filas = cursor.fetchall()

        self.txt_log.clear()

        if not filas:
            self.log("No hay facturas pendientes de recálculo.")
            return

        self.log(f"Facturas pendientes de recálculo: {len(filas)}\n")

        for nf, nc, fecha in filas:
            self.log(f" - {nf} | Contrato {nc} | {fecha}")

        self.log("\nEstado: En espera.")

    # ---------------------------------------------------------
    # Lógica
    # ---------------------------------------------------------
    def log(self, texto):
        self.txt_log.append(texto)

    def iniciar_recalculo(self):
        self.log("\n🔄 Iniciando recálculo de facturas pendientes...\n")

        try:
            resultado = recalcular_facturas(self.conn)

            self.log(f"Total pendientes: {resultado['total']}")
            self.log(f"Procesadas correctamente: {resultado['procesadas']}")

            if resultado["errores"]:
                self.log("\n⚠️ Errores encontrados:")
                for err in resultado["errores"]:
                    self.log(f"  - {err}")

            self.log("\n✅ Proceso finalizado.")

            QMessageBox.information(
                self,
                "Recalculo finalizado",
                f"Facturas procesadas: {resultado['procesadas']}\n"
                f"Errores: {len(resultado['errores'])}",
            )

        except Exception as e:
            self.log(f"❌ Error crítico: {str(e)}")
            QMessageBox.critical(self, "Error", str(e))

    def cerrar(self):
        self.parent.volver_menu_principal()
