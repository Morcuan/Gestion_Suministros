# ----------------------------------------------------------#
# Módulo: contrato_modificacion.py                         #
# Descripción: Modificación de contratos existentes        #
# Autor: Antonio Morales                                   #
# Fecha: 2026-01-11                                        #
# ----------------------------------------------------------#

from PySide6.QtWidgets import QMessageBox

from aux_database import (
    actualizar_contrato,
    modificacion_contrato,
    obtener_contrato_para_edicion,
    obtener_contrato_por_numero,
    rehabilitacion_contrato,
)
from aux_fechas import a_iso
from base_formulario import BaseFormulario
from contrato_nuevo import NuevoContratoWidget


class ContratoModificacion(BaseFormulario):
    """
    Ventana de modificación de un contrato.
    Se abre exclusivamente desde la ventana de detalles.
    """

    def __init__(self, numero_contrato, parent_detalles=None):
        super().__init__(parent_detalles)

        self.numero_contrato = numero_contrato
        self.parent_detalles = parent_detalles

        # Reutilizamos la ventana de contrato nuevo en modo edición
        self.form = NuevoContratoWidget(modo="edicion", parent=self)
        self._cargar_datos()

        # Conectar el botón Guardar
        self.form.guardar_btn.clicked.connect(self._guardar)

        self.form.show()

    # ---------------------------------------------------------
    # Cargar datos del contrato
    # ---------------------------------------------------------
    def _cargar_datos(self):
        datos = obtener_contrato_para_edicion(self.numero_contrato)

        if not datos:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron cargar los datos del contrato {self.numero_contrato}",
            )
            self.close()
            return

        self.form.cargar_datos(datos)

    # ---------------------------------------------------------
    # Guardar cambios
    # ---------------------------------------------------------
    def _guardar(self):
        datos_modificados = self.form.recoger_datos()

        # Validación de fechas
        fecha_inicio_iso = a_iso(datos_modificados["fecha_inicio"])
        fecha_final_iso = a_iso(datos_modificados["fecha_final"])

        if not fecha_inicio_iso or not fecha_final_iso:
            QMessageBox.warning(self, "Error", "Las fechas no son válidas.")
            return

        datos_modificados["fecha_inicio"] = fecha_inicio_iso
        datos_modificados["fecha_final"] = fecha_final_iso

        # Construir tupla para UPDATE
        valores = (
            datos_modificados["id_compania"],
            datos_modificados["id_postal"],
            datos_modificados["numero_contrato"],
            datos_modificados["fecha_inicio"],
            datos_modificados["fecha_final"],
            datos_modificados["potencia_punta"],
            datos_modificados["importe_potencia_punta"],
            datos_modificados["potencia_valle"],
            datos_modificados["importe_potencia_valle"],
            datos_modificados["importe_consumo_punta"],
            datos_modificados["importe_consumo_llano"],
            datos_modificados["importe_consumo_valle"],
            datos_modificados["vertido"],
            datos_modificados["importe_excedentes"],
            datos_modificados["importe_bono_social"],
            datos_modificados["importe_alquiler_contador"],
            datos_modificados["importe_asistente_smart"],
            datos_modificados["impuesto_electricidad"],
            datos_modificados["iva"],
            self.numero_contrato,  # WHERE numero_contrato = ?
        )

        try:
            actualizar_contrato(valores)

            # Registrar modificación
            modificacion_contrato(self.numero_contrato)

            # Si estaba ANULADO → REHABILITADO
            vista = obtener_contrato_por_numero(self.numero_contrato)
            estado_anterior = vista[6] if vista else ""

            if estado_anterior.upper() == "ANULADO":
                rehabilitacion_contrato(self.numero_contrato)

            QMessageBox.information(
                self,
                "Éxito",
                f"Contrato {self.numero_contrato} actualizado correctamente.",
            )

            # ---------------------------------------------------------
            # Refrescar ventana de detalles
            # ---------------------------------------------------------
            if self.parent_detalles:
                self.parent_detalles.close()

                from contrato_consulta import DetallesContratoWidget

                vista = obtener_contrato_por_numero(self.numero_contrato)
                estado_nuevo = vista[6] if vista else "DESCONOCIDO"

                detalles = DetallesContratoWidget(vista, self.parent())
                detalles.exec()

            self.form.close()
            self.close()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo actualizar el contrato {self.numero_contrato}.\n{e}",
            )
