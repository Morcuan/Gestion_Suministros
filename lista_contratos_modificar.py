# --------------------------------------------#
# Modulo: lista_contratos_modificar.py
# Descripción: Selección de contrato a modificar
# Autor: Antonio Morales + Copilot
# Fecha: 2026-02-24 (actualizado)
# --------------------------------------------#

import sys

print(">>> MODULOS CARGADOS RELACIONADOS:")
for m in sys.modules:
    if "formulario_contrato" in m:
        print("   -", m, "=>", sys.modules[m])

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from db import (
    actualizar_suplemento_vigente,
    crear_suplemento_nuevo,
    get_conn,
    obtener_suplemento_vigente,
)

# Usamos el formulario unificado
from formulario_contrato import FormularioContrato

print(">>> FormularioContrato:", FormularioContrato)
print(">>> Cargado desde módulo:", FormularioContrato.__module__)
print(
    ">>> Cargado desde archivo:", FormularioContrato.__dict__.get("__file__", "NO FILE")
)

from lista_contratos import obtener_lista_contratos


class ListaContratosModificar(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Modificar contrato")
        self.conn = get_conn()
        self.resize(1160, 950)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(
            ["Nº contrato", "Supl.", "Compañía", "C.P.", "Inicio", "Efecto", "Estado"]
        )

        # Botones
        self.btn_modificar = QPushButton("Modificar contrato")
        self.btn_cerrar = QPushButton("Cerrar")

        self.btn_modificar.clicked.connect(self.abrir_modificacion)
        self.btn_cerrar.clicked.connect(self.close)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Seleccione un contrato para modificar:"))
        layout.addWidget(self.tabla)

        botones = QHBoxLayout()
        botones.addWidget(self.btn_modificar)
        botones.addStretch()
        botones.addWidget(self.btn_cerrar)

        layout.addLayout(botones)
        self.setLayout(layout)

        self.cargar_contratos()

    # ============================================================
    #  CARGA DE CONTRATOS
    # ============================================================
    def cargar_contratos(self):
        lista = obtener_lista_contratos(
            self.conn,
            solo_activos=False,
            solo_ultimo_suplemento=True,
            incluir_anulados=True,
        )

        self.tabla.setRowCount(len(lista))

        for i, row in enumerate(lista):
            (
                id_contrato,
                ncontrato,
                suplemento,
                estado,
                compania,
                codigo_postal,
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
            ) = row

            datos = [
                ncontrato,
                suplemento,
                compania,
                codigo_postal,
                fec_inicio,
                efec_suple,
                estado,
            ]

            for j, value in enumerate(datos):
                self.tabla.setItem(i, j, QTableWidgetItem(str(value)))

        self.tabla.resizeColumnsToContents()
        self.tabla.horizontalHeader().setStretchLastSection(True)

    # ============================================================
    #  OBTENER MAINWINDOW REAL
    # ============================================================
    def get_mainwindow(self):
        w = self.parent()
        while w is not None and not hasattr(w, "cargar_modulo"):
            w = w.parent()
        return w

    # ============================================================
    #  ABRIR FORMULARIO DE MODIFICACIÓN
    # ============================================================
    def abrir_modificacion(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Atención", "Debe seleccionar un contrato.")
            return

        ncontrato = self.tabla.item(fila, 0).text()

        datos = obtener_suplemento_vigente(ncontrato)
        if not datos:
            QMessageBox.critical(self, "Error", "No se pudo cargar el contrato.")
            return

        # Guardamos los datos originales para comparar
        self.datos_originales = datos.copy()

        main = self.get_mainwindow()
        main.lista_modificacion = self

        # FORMULARIO UNIFICADO EN MODO MODIFICACIÓN
        form = FormularioContrato(modo="modificacion", datos=datos, parent=main)

        form.guardado_modificacion.connect(self.procesar_modificacion)
        form.cancelado.connect(main.lista_modificacion.cancelar_modificacion)

        main.cargar_modulo(form, f"Modificar contrato {ncontrato}")

    # ============================================================
    #  PROCESAR MODIFICACIÓN
    # ============================================================
    def procesar_modificacion(self, datos):
        """
        El formulario unificado devuelve TODOS los datos.
        Aquí decidimos si:
        - solo cambian datos administrativos → actualizar vigente
        - cambian datos económicos → crear suplemento
        """

        campos_economicos = [
            "ppunta",
            "pvalle",
            "pv_ppunta",
            "pv_pvalle",
            "pv_conpunta",
            "pv_conllano",
            "pv_convalle",
            "pv_excedent",
            "bono_social",
            "alq_contador",
            "otros_gastos",
            "i_electrico",
            "iva",
        ]

        cambios_econ = any(
            datos.get(c) != self.datos_originales.get(c) for c in campos_economicos
        )

        if cambios_econ:
            nuevo_id = crear_suplemento_nuevo(datos)
            QMessageBox.information(
                self,
                "OK",
                f"Suplemento creado correctamente (ID {nuevo_id}).\n"
                "Se han marcado facturas para recálculo.",
            )
        else:
            actualizar_suplemento_vigente(datos)
            QMessageBox.information(self, "OK", "Datos administrativos actualizados.")

        self.cargar_contratos()

    # ============================================================
    #  BOTÓN CANCELAR
    # ============================================================
    def cancelar_modificacion(self):
        main = self.get_mainwindow()
        if main is None:
            return

        self.setParent(main)
        main.cargar_modulo(self, "Modificar contrato")
        self.show()
