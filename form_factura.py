# ============================================================
#  form_factura.py  (VERSIÓN DRU CORREGIDA)
# ============================================================

from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from utils import dias_entre_fechas, validar_fecha


def to_float(valor, etiqueta):
    if valor.strip() == "":
        return 0.0
    try:
        return float(valor.replace(",", "."))
    except:
        raise ValueError(f"El campo '{etiqueta}' debe ser numérico.")


class FormFactura(QWidget):
    def __init__(self, parent=None, id_contrato=None, ncontrato=None, compania=None):
        super().__init__(parent)

        self.id_contrato = id_contrato
        self.ncontrato = ncontrato
        self.compania = compania

        self.setWindowTitle(f"Nueva factura – {ncontrato} – {compania}")

        layout = QVBoxLayout()

        # ============================================================
        #  BLOQUE 1: IDENTIFICACIÓN
        # ============================================================

        self.nfactura = QLineEdit()
        self.fec_inicio = QLineEdit()
        self.fec_final = QLineEdit()
        self.dias = QLineEdit()
        self.fec_emision = QLineEdit()

        ident = QGridLayout()
        ident.addWidget(QLabel("Nº de factura:"), 0, 0)
        ident.addWidget(self.nfactura, 0, 1)
        ident.addWidget(QLabel("Inicio factura (dd/mm/yyyy):"), 1, 0)
        ident.addWidget(self.fec_inicio, 1, 1)
        ident.addWidget(QLabel("Fin factura (dd/mm/yyyy):"), 2, 0)
        ident.addWidget(self.fec_final, 2, 1)
        ident.addWidget(QLabel("Días factura:"), 3, 0)
        ident.addWidget(self.dias, 3, 1)
        ident.addWidget(QLabel("Fec. emisión (dd/mm/yyyy):"), 4, 0)
        ident.addWidget(self.fec_emision, 4, 1)

        layout.addLayout(ident)

        # ============================================================
        #  BLOQUE 2: ENERGÍA
        # ============================================================

        self.pot_imp_punta = QLineEdit()
        self.pot_imp_valle = QLineEdit()
        self.total_potencia = QLineEdit()

        self.con_punta = QLineEdit()
        self.imp_con_punta = QLineEdit()
        self.con_llano = QLineEdit()
        self.imp_con_llano = QLineEdit()
        self.con_valle = QLineEdit()
        self.imp_con_valle = QLineEdit()

        self.excedentes = QLineEdit()
        self.imp_excedentes = QLineEdit()

        ene = QGridLayout()
        ene.addWidget(QLabel("Pot. punta (€):"), 0, 0)
        ene.addWidget(self.pot_imp_punta, 0, 1)
        ene.addWidget(QLabel("Pot. valle (€):"), 1, 0)
        ene.addWidget(self.pot_imp_valle, 1, 1)
        ene.addWidget(QLabel("Total potencia (€):"), 2, 0)
        ene.addWidget(self.total_potencia, 2, 1)

        ene.addWidget(QLabel("Consumo punta (kWh):"), 3, 0)
        ene.addWidget(self.con_punta, 3, 1)
        ene.addWidget(QLabel("Imp. consumo punta (€):"), 4, 0)
        ene.addWidget(self.imp_con_punta, 4, 1)

        ene.addWidget(QLabel("Consumo llano (kWh):"), 5, 0)
        ene.addWidget(self.con_llano, 5, 1)
        ene.addWidget(QLabel("Imp. consumo llano (€):"), 6, 0)
        ene.addWidget(self.imp_con_llano, 6, 1)

        ene.addWidget(QLabel("Consumo valle (kWh):"), 7, 0)
        ene.addWidget(self.con_valle, 7, 1)
        ene.addWidget(QLabel("Imp. consumo valle (€):"), 8, 0)
        ene.addWidget(self.imp_con_valle, 8, 1)

        ene.addWidget(QLabel("Excedentes (kWh):"), 9, 0)
        ene.addWidget(self.excedentes, 9, 1)
        ene.addWidget(QLabel("Imp. excedentes (€):"), 10, 0)
        ene.addWidget(self.imp_excedentes, 10, 1)

        layout.addLayout(ene)

        # ============================================================
        #  BLOQUE 3: CARGOS Y RESUMEN
        # ============================================================

        self.imp_bono_social = QLineEdit()
        self.imp_iee = QLineEdit()
        self.alq_equipos = QLineEdit()
        self.servicios = QLineEdit()
        self.iva = QLineEdit()
        self.dcto_saldos = QLineEdit()
        self.solar_cloud = QLineEdit()
        self.total_factura = QLineEdit()

        car = QGridLayout()
        car.addWidget(QLabel("Imp. bono social (€):"), 0, 0)
        car.addWidget(self.imp_bono_social, 0, 1)
        car.addWidget(QLabel("Imp. impuesto eléctrico (€):"), 1, 0)
        car.addWidget(self.imp_iee, 1, 1)
        car.addWidget(QLabel("Alq. de contador (€):"), 2, 0)
        car.addWidget(self.alq_equipos, 2, 1)
        car.addWidget(QLabel("Serv. asociados (€):"), 3, 0)
        car.addWidget(self.servicios, 3, 1)
        car.addWidget(QLabel("I.V.A. (€):"), 4, 0)
        car.addWidget(self.iva, 4, 1)
        car.addWidget(QLabel("Dctos. saldos (€):"), 5, 0)
        car.addWidget(self.dcto_saldos, 5, 1)
        car.addWidget(QLabel("Saldo bat. virtual (€):"), 6, 0)
        car.addWidget(self.solar_cloud, 6, 1)
        car.addWidget(QLabel("Total factura (€):"), 7, 0)
        car.addWidget(self.total_factura, 7, 1)

        layout.addLayout(car)

        # ============================================================
        #  BOTONES
        # ============================================================

        botones = QHBoxLayout()
        self.btn_guardar = QPushButton("Grabar factura")
        self.btn_otra = QPushButton("Otra factura")
        self.btn_salir = QPushButton("Salir")

        self.btn_guardar.setEnabled(True)
        self.btn_otra.setEnabled(False)

        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_otra)
        botones.addWidget(self.btn_salir)

        layout.addLayout(botones)
        self.setLayout(layout)

        self.btn_guardar.clicked.connect(self.guardar_factura)
        self.btn_otra.clicked.connect(self.limpiar_formulario)
        self.btn_salir.clicked.connect(self.volver_lista)

    # ============================================================
    #  LOCALIZAR MAINWINDOW REAL
    # ============================================================

    def get_mainwindow(self):
        w = self.parent()
        while w is not None and not hasattr(w, "cargar_modulo"):
            w = w.parent()
        return w

    # ============================================================
    #  VALIDACIÓN DE DÍAS
    # ============================================================

    def validar_dias(self):
        inicio = self.fec_inicio.text()
        fin = self.fec_final.text()

        if not validar_fecha(inicio) or not validar_fecha(fin):
            return False

        dias_correctos = dias_entre_fechas(inicio, fin)

        try:
            dias_usuario = int(self.dias.text())
        except:
            return False

        if dias_correctos != dias_usuario:
            self.dias.setStyleSheet("background-color: #ffcccc;")
            QMessageBox.warning(
                self,
                "Error en días",
                f"Los días correctos son {dias_correctos}. Corrija el valor.",
            )
            self.dias.setFocus()
            return False

        self.dias.setStyleSheet("")
        return True

    # ============================================================
    #  GUARDADO REAL
    # ============================================================

    def guardar_factura(self):
        if not self.validar_dias():
            return

        main = self.get_mainwindow()
        conn = main.conn
        cursor = main.cursor

        # Validación fechas
        for campo in [self.fec_inicio, self.fec_final, self.fec_emision]:
            if not validar_fecha(campo.text()):
                QMessageBox.warning(self, "Error", "Formato de fecha incorrecto.")
                return

        def iso(f):
            d, m, a = f.split("/")
            return f"{a}-{m}-{d}"

        datos_ident = {
            "id_contrato": self.id_contrato,
            "nfactura": self.nfactura.text(),
            "inicio_factura": iso(self.fec_inicio.text()),
            "fin_factura": iso(self.fec_final.text()),
            "dias_factura": int(self.dias.text()),
            "fec_emision": iso(self.fec_emision.text()),
        }

        try:
            datos_energia = {
                "pot_imp_punta": to_float(self.pot_imp_punta.text(), "Pot. punta"),
                "pot_imp_valle": to_float(self.pot_imp_valle.text(), "Pot. valle"),
                "total_potencia": to_float(
                    self.total_potencia.text(), "Total potencia"
                ),
                "con_punta": to_float(self.con_punta.text(), "Consumo punta"),
                "imp_con_punta": to_float(
                    self.imp_con_punta.text(), "Imp. consumo punta"
                ),
                "con_llano": to_float(self.con_llano.text(), "Consumo llano"),
                "imp_con_llano": to_float(
                    self.imp_con_llano.text(), "Imp. consumo llano"
                ),
                "con_valle": to_float(self.con_valle.text(), "Consumo valle"),
                "imp_con_valle": to_float(
                    self.imp_con_valle.text(), "Imp. consumo valle"
                ),
                "excedentes": to_float(self.excedentes.text(), "Excedentes"),
                "imp_excedentes": to_float(
                    self.imp_excedentes.text(), "Imp. excedentes"
                ),
            }
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            return

        try:
            datos_asociados = {
                "imp_bono_social": to_float(
                    self.imp_bono_social.text(), "Imp. bono social"
                ),
                "imp_iee": to_float(self.imp_iee.text(), "Imp. impuesto eléctrico"),
                "alq_equipos": to_float(self.alq_equipos.text(), "Alq. contador"),
                "servicios": to_float(self.servicios.text(), "Servicios asociados"),
                "iva": to_float(self.iva.text(), "IVA"),
                "dcto_saldos": to_float(self.dcto_saldos.text(), "Dctos. saldos"),
                "solar_cloud": to_float(self.solar_cloud.text(), "Saldo bat. virtual"),
                "total_factura": to_float(self.total_factura.text(), "Total factura"),
            }
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            return

        try:
            cursor.execute(
                """
                INSERT INTO factura_identificacion (
                    id_contrato, nfactura, inicio_factura, fin_factura,
                    dias_factura, fec_emision
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                tuple(datos_ident.values()),
            )

            id_factura = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO factura_energia (
                    id_factura, pot_imp_punta, pot_imp_valle, total_potencia,
                    con_punta, imp_con_punta, con_llano, imp_con_llano,
                    con_valle, imp_con_valle, excedentes, imp_excedentes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (id_factura, *datos_energia.values()),
            )

            cursor.execute(
                """
                INSERT INTO factura_asociados (
                    id_factura, imp_bono_social, imp_iee, alq_equipos,
                    servicios, iva, dcto_saldos, solar_cloud, total_factura
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (id_factura, *datos_asociados.values()),
            )

            conn.commit()

            QMessageBox.information(self, "OK", "Factura guardada correctamente.")

            # Deshabilitar grabar, habilitar otra
            self.btn_guardar.setEnabled(False)
            self.btn_otra.setEnabled(True)

        except Exception as e:
            conn.rollback()

            # Error por número de factura duplicado
            if "UNIQUE constraint failed" in str(e):
                QMessageBox.warning(
                    self,
                    "Número de factura duplicado",
                    "El número de factura ya existe. Introduzca uno diferente.",
                )
                self.nfactura.setStyleSheet("background-color: #ffcccc;")
                self.nfactura.setFocus()
                return

            # Otros errores SQL
            QMessageBox.critical(self, "Error", str(e))
            return

    # ============================================================
    #  LIMPIAR FORMULARIO PARA "OTRA FACTURA"
    # ============================================================

    def limpiar_formulario(self):
        for widget in self.findChildren(QLineEdit):
            widget.clear()
            widget.setStyleSheet("")

        self.btn_guardar.setEnabled(True)
        self.btn_otra.setEnabled(False)

        self.nfactura.setFocus()

    # ============================================================
    #  VOLVER A LA LISTA DE CONTRATOS
    # ============================================================

    def volver_lista(self):
        from lista_contratos_factura import ListaContratosFactura

        main = self.get_mainwindow()
        main.cargar_modulo(ListaContratosFactura(parent=main), "Seleccionar contrato")
