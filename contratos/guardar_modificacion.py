# -------------------------------------------------------------#
# Módulo: guardar_modificacion.py                              #
# Descripción: Lógica completa del proceso de modificación     #
# Autor: Antonio Morales                                       #
# Fecha: 2026-03-24                                            #
# -------------------------------------------------------------#

from datetime import datetime, timedelta

from PySide6.QtWidgets import QMessageBox

from utilidades.logica_negocio import (
    convertir_a_iso,
    validar_fecha,
)
from utilidades.utilidades_bd import (
    insertar_codigo_postal,
    insertar_contrato_energia,
    insertar_contrato_gastos,
    insertar_contrato_identificacion,
    validar_codigo_postal,
)


class GuardarModificacion:
    """
    Controlador dedicado exclusivamente a la lógica de modificación
    de contratos. Mantiene limpio modificar_contrato.py y encapsula
    todo el proceso de suplementos.
    """

    def __init__(self, parent, conn, cursor, datos_originales, formulario):
        self.parent = parent
        self.conn = conn
        self.cursor = cursor
        self.datos_originales = datos_originales
        self.form = formulario

    # ---------------------------------------------------------
    # MÉTODO PRINCIPAL
    # ---------------------------------------------------------
    def guardar(self):
        """
        Flujo completo del proceso de modificación:
        1. Obtener datos del formulario
        2. Detectar cambios
        3. Validar efec_suple
        4. Validar CP
        5. Validar campos numéricos
        6. Aplicar regla de vertido
        7. Actualizar suplemento anterior
        8. Crear suplemento nuevo
        9. Buscar y marcar facturas afectadas
        10. Mensaje final
        """

        # ======================================================
        # 1. OBTENER DATOS DEL FORMULARIO (MODIFICACIÓN)
        # ======================================================
        try:
            datos_ident, datos_energia, datos_gastos = (
                self.form.obtener_datos_modificacion()
            )
        except ValueError as e:
            QMessageBox.warning(self.parent, "Error", str(e))
            return

        efec_suple_nuevo = datos_ident["efec_suple"]

        # ======================================================
        # 2. DETECTAR CAMBIOS
        # ======================================================
        hay_cambios = self._detectar_cambios(
            datos_ident, datos_energia, datos_gastos, efec_suple_nuevo
        )

        if not hay_cambios:
            QMessageBox.information(
                self.parent,
                "Sin cambios",
                "No se ha modificado ningún dato del contrato.",
            )
            return

        # ======================================================
        # 3. VALIDAR FECHA DE EFECTO DEL NUEVO SUPLEMENTO
        # ======================================================
        if not self._validar_efec_suple(efec_suple_nuevo):
            return

        # ======================================================
        # 4. VALIDAR CÓDIGO POSTAL
        # ======================================================
        if not self._validar_codigo_postal(datos_ident):
            return

        # ======================================================
        # 5. VALIDAR CAMPOS NUMÉRICOS
        # ======================================================
        if not self._validar_numericos(datos_energia, datos_gastos):
            return

        # ======================================================
        # 6. APLICAR REGLA DE VERTIDO
        # ======================================================
        if datos_energia["vertido"] == "N":
            datos_energia["pv_excedentes"] = "0"

        # ======================================================
        # 7. ACTUALIZAR SUPLEMENTO ANTERIOR
        # ======================================================
        self._actualizar_suplemento_anterior(efec_suple_nuevo)

        # ======================================================
        # 8. CREAR SUPLEMENTO NUEVO
        # ======================================================
        suplemento_nuevo = self._insertar_suplemento_nuevo(
            datos_ident, datos_energia, datos_gastos, efec_suple_nuevo
        )

        # ======================================================
        # 9. BUSCAR Y MARCAR FACTURAS AFECTADAS
        # ======================================================
        facturas_afectadas = self._buscar_facturas_afectadas(efec_suple_nuevo)

        if facturas_afectadas:
            self._marcar_facturas_afectadas(facturas_afectadas, suplemento_nuevo)
            QMessageBox.information(
                self.parent,
                "Facturas afectadas",
                f"Existen {len(facturas_afectadas)} facturas que deben recalcularse.",
            )

        # ======================================================
        # 10. ÉXITO
        # ======================================================
        QMessageBox.information(
            self.parent,
            "Suplemento creado",
            f"Suplemento {suplemento_nuevo} creado correctamente.",
        )

        # Limpiar y volver a lista
        self.form.limpiar()
        self.parent.cargar_modulo(self.parent.crear_pantalla_inicio(), None)

    # ---------------------------------------------------------
    # DETECTAR CAMBIOS
    # ---------------------------------------------------------
    def _detectar_cambios(self, ident, energia, gastos, efec_suple_nuevo):
        cambios = []
        orig = self.datos_originales

        # Identificación
        if ident["compania"] != orig["compania"]:
            cambios.append("compania")

        if ident["codigo_postal"] != str(orig["codigo_postal"]):
            cambios.append("codigo_postal")

        if efec_suple_nuevo != orig["efec_suple"]:
            cambios.append("efec_suple")

        # Energía
        for campo in [
            "ppunta",
            "pvalle",
            "pv_ppunta",
            "pv_pvalle",
            "pv_conpunta",
            "pv_conllano",
            "pv_convalle",
            "vertido",
            "pv_excedentes",
        ]:
            if str(energia[campo]) != str(orig[campo]):
                cambios.append(campo)

        # Gastos
        for campo in [
            "bono_social",
            "i_electrico",
            "alq_contador",
            "otros_gastos",
            "iva",
        ]:
            if str(gastos[campo]) != str(orig[campo]):
                cambios.append(campo)

        if len(cambios) == 0:
            return False

        if cambios == ["efec_suple"]:
            return False

        return True

    # ---------------------------------------------------------
    # VALIDAR FECHA DE EFECTO (CORREGIDO)
    # ---------------------------------------------------------
    def _validar_efec_suple(self, efec_suple_iso):
        """
        Regla corregida:
        - La fecha debe ser válida
        - Debe ser posterior al suplemento anterior
        - NO se compara con la fecha de hoy (permitimos retroactividad)
        - No puede superar la fecha final del contrato
        """

        efec_str = self.form.txt_efec_suple.text().strip()
        if not validar_fecha(efec_str):
            QMessageBox.warning(
                self.parent,
                "Fecha incorrecta",
                "La fecha de efecto no es válida (dd/mm/yyyy).",
            )
            return False

        nueva = datetime.strptime(efec_suple_iso, "%Y-%m-%d").date()
        anterior = datetime.strptime(
            self.datos_originales["efec_suple"], "%Y-%m-%d"
        ).date()

        # Regla correcta: debe ser posterior al suplemento anterior
        if nueva <= anterior:
            QMessageBox.warning(
                self.parent,
                "Fecha inválida",
                "La fecha de efecto debe ser posterior a la del suplemento anterior.",
            )
            return False

        # Regla mantenida: no puede superar la fecha final del contrato
        fec_final = datetime.strptime(
            self.datos_originales["fec_final"], "%Y-%m-%d"
        ).date()

        if nueva > fec_final:
            QMessageBox.warning(
                self.parent,
                "Fecha inválida",
                "La fecha de efecto no puede superar la fecha final del contrato.",
            )
            return False

        return True

    # ---------------------------------------------------------
    # VALIDAR CÓDIGO POSTAL
    # ---------------------------------------------------------
    def _validar_codigo_postal(self, ident):
        ok, poblacion = validar_codigo_postal(self.cursor, ident["codigo_postal"])

        if ok:
            return True

        resp = QMessageBox.question(
            self.parent,
            "Código postal no encontrado",
            f"El código postal {ident['codigo_postal']} no existe.\n¿Desea crearlo?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if resp == QMessageBox.No:
            return False

        from PySide6.QtWidgets import QInputDialog

        poblacion, ok2 = QInputDialog.getText(
            self.parent, "Nueva población", "Introduzca el nombre de la población:"
        )

        if not ok2 or poblacion.strip() == "":
            QMessageBox.warning(
                self.parent, "Error", "Debe introducir una población válida."
            )
            return False

        insertar_codigo_postal(
            self.conn, self.cursor, ident["codigo_postal"], poblacion.strip()
        )

        return True

    # ---------------------------------------------------------
    # VALIDAR CAMPOS NUMÉRICOS
    # ---------------------------------------------------------
    def _validar_numericos(self, energia, gastos):
        campos = {
            "Potencia punta": energia["ppunta"],
            "Potencia valle": energia["pvalle"],
            "Pv. pot. punta": energia["pv_ppunta"],
            "Pv. pot. llano": energia["pv_pvalle"],
            "Pv. cons. punta": energia["pv_conpunta"],
            "Pv. cons. llano": energia["pv_conllano"],
            "Pv. cons. valle": energia["pv_convalle"],
            "Pv. excedentes": energia["pv_excedentes"],
            "Bono social": gastos["bono_social"],
            "Imp. eléctrico": gastos["i_electrico"],
            "Alquiler contador": gastos["alq_contador"],
            "Otros gastos": gastos["otros_gastos"],
            "IVA": gastos["iva"],
        }

        for nombre, valor in campos.items():
            if valor.strip() == "":
                QMessageBox.warning(
                    self.parent, "Error", f"El campo '{nombre}' no puede estar vacío."
                )
                return False

            try:
                float(valor)
            except ValueError:
                QMessageBox.warning(
                    self.parent, "Error", f"El campo '{nombre}' debe ser numérico."
                )
                return False

        return True

    # ---------------------------------------------------------
    # ACTUALIZAR SUPLEMENTO ANTERIOR
    # ---------------------------------------------------------
    def _actualizar_suplemento_anterior(self, efec_suple_nuevo):

        ncontrato = self.datos_originales["ncontrato"]
        supl_anterior = self.datos_originales["suplemento"]

        nueva = datetime.strptime(efec_suple_nuevo, "%Y-%m-%d").date()
        fin_anterior = nueva - timedelta(days=1)
        fin_iso = fin_anterior.strftime("%Y-%m-%d")

        sql = """
            UPDATE contratos_identificacion
            SET fin_suple = ?
            WHERE ncontrato = ?
            AND suplemento = ?
        """

        self.cursor.execute(sql, (fin_iso, ncontrato, supl_anterior))
        self.conn.commit()

    # ---------------------------------------------------------
    # INSERTAR SUPLEMENTO NUEVO
    # ---------------------------------------------------------
    def _insertar_suplemento_nuevo(self, ident, energia, gastos, efec_suple_nuevo):

        suplemento_nuevo = self.datos_originales["suplemento"] + 1

        ident["suplemento"] = suplemento_nuevo
        ident["efec_suple"] = efec_suple_nuevo
        ident["fin_suple"] = self.datos_originales["fec_final"]

        idc = insertar_contrato_identificacion(self.cursor, ident)
        insertar_contrato_energia(self.cursor, idc, energia)
        insertar_contrato_gastos(self.cursor, idc, gastos)

        self.conn.commit()

        return suplemento_nuevo

    # ---------------------------------------------------------
    # BUSCAR FACTURAS AFECTADAS
    # ---------------------------------------------------------
    def _buscar_facturas_afectadas(self, efec_suple_nuevo):

        sql = """
            SELECT nfactura, inicio_factura, suplemento
            FROM facturas
            WHERE ncontrato = ?
                AND inicio_factura >= ?
            ORDER BY inicio_factura
        """

        self.cursor.execute(sql, (self.datos_originales["ncontrato"], efec_suple_nuevo))
        filas = self.cursor.fetchall()

        facturas = []
        for f in filas:
            facturas.append(
                {
                    "nfactura": f[0],
                    "inicio_factura": f[1],
                    "suplemento": f[2],
                }
            )

        return facturas

    # ---------------------------------------------------------
    # MARCAR FACTURAS COMO AFECTADAS
    # ---------------------------------------------------------
    def _marcar_facturas_afectadas(self, facturas, nuevo_supl):

        sql = """
            UPDATE facturas
            SET recalcular = 1,
                suplemento = ?
            WHERE nfactura = ?
        """

        for f in facturas:
            self.cursor.execute(sql, (nuevo_supl, f["nfactura"]))

        self.conn.commit()
