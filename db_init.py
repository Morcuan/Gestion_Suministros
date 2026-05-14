# ------------------------------------------------------------
# Módulo: db_init.py
# Inicialización completa de la base de datos
# Gestión Suministros 2.0
# ------------------------------------------------------------

# Este módulo NO abre ni cierra la conexión.
# Recibe un cursor externo desde main_window.

# ============================================================
# ===============   CREACIÓN DE TABLAS REALES   ===============
# ============================================================


def crear_tabla_contratos_identificacion(cursor):
    cursor.execute("DROP TABLE IF EXISTS contratos_identificacion;")
    cursor.execute("""
        CREATE TABLE contratos_identificacion (
            id_contrato     INTEGER PRIMARY KEY AUTOINCREMENT,
            ncontrato       TEXT NOT NULL,
            suplemento      INTEGER NOT NULL,
            compania        TEXT NOT NULL,
            codigo_postal   TEXT NOT NULL,
            fec_inicio      TEXT NOT NULL,
            fec_final       TEXT NOT NULL,
            efec_suple      TEXT NOT NULL,
            fin_suple       TEXT NOT NULL,
            fec_anulacion   TEXT,
            FOREIGN KEY (codigo_postal) REFERENCES cpostales(codigo_postal)
        );
    """)


def crear_tabla_contratos_energia(cursor):
    cursor.execute("DROP TABLE IF EXISTS contratos_energia;")
    cursor.execute("""
        CREATE TABLE contratos_energia (
            id_contrato     INTEGER PRIMARY KEY,
            ppunta          REAL NOT NULL,
            pv_ppunta       REAL NOT NULL,
            pvalle          REAL NOT NULL,
            pv_pvalle       REAL NOT NULL,
            pv_conpunta     REAL NOT NULL,
            pv_conllano     REAL NOT NULL,
            pv_convalle     REAL NOT NULL,
            vertido         INTEGER NOT NULL,
            pv_excedent     REAL NOT NULL,
            FOREIGN KEY (id_contrato) REFERENCES contratos_identificacion(id_contrato)
        );
    """)


def crear_tabla_contratos_gastos(cursor):
    cursor.execute("DROP TABLE IF EXISTS contratos_gastos;")
    cursor.execute("""
        CREATE TABLE contratos_gastos (
            id_contrato     INTEGER PRIMARY KEY,
            bono_social     REAL NOT NULL,
            alq_contador    REAL NOT NULL,
            otros_gastos    REAL NOT NULL,
            i_electrico     REAL NOT NULL,
            iva             REAL NOT NULL,
            FOREIGN KEY (id_contrato) REFERENCES contratos_identificacion(id_contrato)
        );
    """)


def crear_tabla_facturas(cursor):
    cursor.execute("DROP TABLE IF EXISTS facturas;")
    cursor.execute("""
        CREATE TABLE facturas (
            nfactura           TEXT PRIMARY KEY,
            inicio_factura     TEXT NOT NULL,
            fin_factura        TEXT NOT NULL,
            dias_factura       INTEGER NOT NULL,
            fec_emision        TEXT NOT NULL,
            consumo_punta      REAL,
            consumo_llano      REAL,
            consumo_valle      REAL,
            excedentes         REAL,
            importe_compensado REAL,
            servicios          REAL,
            dcto_servicios     REAL,
            saldos_pendientes  REAL,
            bat_virtual        REAL,
            recalcular         INTEGER DEFAULT 0,
            estado             TEXT DEFAULT 'Emitida',
            rectifica_a        TEXT,
            ncontrato          TEXT,
            suplemento         INTEGER
        );
    """)

    cursor.execute("""
        CREATE INDEX idx_facturas_fec_emision
        ON facturas (fec_emision);
    """)


def crear_tabla_factura_calculos(cursor):
    cursor.execute("DROP TABLE IF EXISTS factura_calculos;")
    cursor.execute("""
        CREATE TABLE factura_calculos (
            id_calculo      INTEGER PRIMARY KEY AUTOINCREMENT,
            nfactura        TEXT NOT NULL,
            fecha_calculo   TEXT NOT NULL,
            version_motor   TEXT NOT NULL,
            total_energia   REAL NOT NULL,
            total_cargos    REAL NOT NULL,
            total_servicios REAL NOT NULL,
            total_iva       REAL NOT NULL,
            cloud_aplicado  REAL NOT NULL,
            cloud_sobrante  REAL NOT NULL,
            total_final     REAL NOT NULL,
            detalles_json   TEXT NOT NULL,
            bono_social REAL,
            alq_contador REAL,
            otros_gastos REAL,
            i_electrico REAL,
            iva REAL
        );
    """)


def crear_tabla_saldo_cloud(cursor):
    cursor.execute("DROP TABLE IF EXISTS saldo_cloud;")
    cursor.execute("""
        CREATE TABLE saldo_cloud (
            ncontrato INTEGER PRIMARY KEY,
            saldo REAL NOT NULL
        );
    """)


def crear_tabla_estadisticas_mensuales(cursor):
    cursor.execute("DROP TABLE IF EXISTS estadisticas_mensuales;")
    cursor.execute("""
        CREATE TABLE estadisticas_mensuales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT NOT NULL,
            produccion REAL NOT NULL,
            consumo REAL NOT NULL,
            excedentes REAL NOT NULL,
            comprado REAL NOT NULL,
            fuente TEXT DEFAULT 'manual'
        );
    """)


# ============================================================
# ===============   TABLAS TEST (MODO PRUEBAS)   =============
# ============================================================


def crear_tablas_test(cursor):

    cursor.execute("DROP TABLE IF EXISTS contratos_identificacion_test;")
    cursor.execute("""
        CREATE TABLE contratos_identificacion_test (
            id_contrato     INTEGER PRIMARY KEY AUTOINCREMENT,
            ncontrato       TEXT NOT NULL,
            suplemento      INTEGER NOT NULL,
            compania        TEXT NOT NULL,
            codigo_postal   TEXT NOT NULL,
            fec_inicio      TEXT NOT NULL,
            fec_final       TEXT NOT NULL,
            efec_suple      TEXT NOT NULL,
            fin_suple       TEXT NOT NULL,
            fec_anulacion   TEXT
        );
    """)

    cursor.execute("DROP TABLE IF EXISTS contratos_energia_test;")
    cursor.execute("""
        CREATE TABLE contratos_energia_test (
            id_contrato     INTEGER PRIMARY KEY,
            ppunta          REAL NOT NULL,
            pv_ppunta       REAL NOT NULL,
            pvalle          REAL NOT NULL,
            pv_pvalle       REAL NOT NULL,
            pv_conpunta     REAL NOT NULL,
            pv_conllano     REAL NOT NULL,
            pv_convalle     REAL NOT NULL,
            vertido         INTEGER NOT NULL,
            pv_excedent     REAL NOT NULL
        );
    """)

    cursor.execute("DROP TABLE IF EXISTS contratos_gastos_test;")
    cursor.execute("""
        CREATE TABLE contratos_gastos_test (
            id_contrato     INTEGER PRIMARY KEY,
            bono_social     REAL NOT NULL,
            alq_contador    REAL NOT NULL,
            otros_gastos    REAL NOT NULL,
            i_electrico     REAL NOT NULL,
            iva             REAL NOT NULL
        );
    """)

    cursor.execute("DROP TABLE IF EXISTS facturas_test;")
    cursor.execute("""
        CREATE TABLE facturas_test (
            nfactura TEXT PRIMARY KEY,
            inicio_factura TEXT NOT NULL,
            fin_factura TEXT NOT NULL,
            dias_factura INTEGER NOT NULL,
            fec_emision TEXT NOT NULL,
            consumo_punta REAL,
            consumo_llano REAL,
            consumo_valle REAL,
            excedentes REAL,
            importe_compensado REAL,
            servicios REAL,
            dcto_servicios REAL,
            saldos_pendientes REAL,
            bat_virtual REAL,
            recalcular INTEGER DEFAULT 0,
            estado TEXT DEFAULT 'Emitida',
            rectifica_a TEXT,
            ncontrato TEXT,
            suplemento INTEGER
        );
    """)

    cursor.execute("DROP TABLE IF EXISTS factura_calculos_test;")
    cursor.execute("""
        CREATE TABLE factura_calculos_test (
            id_calculo INTEGER PRIMARY KEY AUTOINCREMENT,
            nfactura TEXT NOT NULL,
            fecha_calculo TEXT NOT NULL,
            version_motor TEXT NOT NULL,
            total_energia REAL NOT NULL,
            total_cargos REAL NOT NULL,
            total_servicios REAL NOT NULL,
            total_iva REAL NOT NULL,
            cloud_aplicado REAL NOT NULL,
            cloud_sobrante REAL NOT NULL,
            total_final REAL NOT NULL,
            detalles_json TEXT NOT NULL,
            bono_social REAL,
            alq_contador REAL,
            otros_gastos REAL,
            i_electrico REAL,
            iva REAL
        );
    """)

    cursor.execute("DROP TABLE IF EXISTS saldo_cloud_test;")
    cursor.execute("""
        CREATE TABLE saldo_cloud_test (
            ncontrato INTEGER PRIMARY KEY,
            saldo REAL NOT NULL
        );
    """)

    cursor.execute("DROP TABLE IF EXISTS saldo_cloud_inicial_test;")
    cursor.execute("""
        CREATE TABLE saldo_cloud_inicial_test (
            id INTEGER PRIMARY KEY,
            saldo_inicial REAL NOT NULL,
            fecha TEXT NOT NULL
        );
    """)


# ============================================================
# ========================   VISTAS   =========================
# ============================================================


def crear_vistas(cursor):

    cursor.execute("DROP VIEW IF EXISTS vista_contratos;")
    cursor.execute("""
        CREATE VIEW vista_contratos AS
        SELECT
            ci.id_contrato, ci.ncontrato, ci.suplemento,
            ci.compania, ci.codigo_postal,
            cp.poblacion, ci.fec_inicio, ci.fec_final,
            ci.efec_suple, ci.fin_suple, ci.fec_anulacion,
            ce.ppunta, ce.pv_ppunta, ce.pvalle, ce.pv_pvalle,
            ce.pv_conpunta, ce.pv_conllano, ce.pv_convalle,
            ce.vertido, ce.pv_excedent, cg.bono_social,
            cg.alq_contador, cg.otros_gastos, cg.i_electrico, cg.iva
        FROM contratos_identificacion ci
        JOIN contratos_energia ce ON ci.id_contrato = ce.id_contrato
        JOIN contratos_gastos cg ON ci.id_contrato = cg.id_contrato
        JOIN cpostales cp ON ci.codigo_postal = cp.codigo_postal;
    """)

    cursor.execute("DROP VIEW IF EXISTS vista_contratos_facturacion;")
    cursor.execute("""
        CREATE VIEW vista_contratos_facturacion AS
        SELECT
            c.id_contrato,
            c.ncontrato,
            c.compania,
            c.codigo_postal,
            cp.poblacion
        FROM contratos_identificacion c
        LEFT JOIN cpostales cp
            ON c.codigo_postal = cp.codigo_postal;
    """)

    cursor.execute("DROP VIEW IF EXISTS v_datos_calculo;")
    cursor.execute("""
        CREATE VIEW v_datos_calculo AS
        SELECT
            fa.ncontrato,
            fa.suplemento,
            fa.nfactura,
            fa.inicio_factura,
            fa.fin_factura,
            fa.dias_factura,
            fa.consumo_punta,
            fa.consumo_llano,
            fa.consumo_valle,
            fa.excedentes,
            fa.servicios,
            fa.dcto_servicios,
            fa.saldos_pendientes,
            fa.bat_virtual,
            ci.id_contrato,
            ci.efec_suple,
            ci.fin_suple,
            ce.ppunta,
            ce.pv_ppunta,
            ce.pvalle,
            ce.pv_pvalle,
            ce.pv_conpunta,
            ce.pv_conllano,
            ce.pv_convalle,
            ce.pv_excedent,
            cg.bono_social,
            cg.alq_contador,
            cg.otros_gastos,
            cg.i_electrico,
            cg.iva
        FROM facturas fa
        JOIN contratos_identificacion ci
            ON ci.ncontrato = fa.ncontrato
           AND fa.inicio_factura BETWEEN ci.efec_suple AND ci.fin_suple
        JOIN contratos_energia ce
            ON ce.id_contrato = ci.id_contrato
        JOIN contratos_gastos cg
            ON cg.id_contrato = ci.id_contrato;
    """)

    cursor.execute("DROP VIEW IF EXISTS v_datos_calculo_test;")
    cursor.execute("""
        CREATE VIEW v_datos_calculo_test AS
        SELECT
            fa.ncontrato,
            fa.suplemento,
            fa.nfactura,
            fa.inicio_factura,
            fa.fin_factura,
            fa.dias_factura,
            fa.consumo_punta,
            fa.consumo_llano,
            fa.consumo_valle,
            fa.excedentes,
            fa.servicios,
            fa.dcto_servicios,
            fa.saldos_pendientes,
            fa.bat_virtual,
            ci.id_contrato,
            ci.efec_suple,
            ci.fin_suple,
            ce.ppunta,
            ce.pv_ppunta,
            ce.pvalle,
            ce.pv_pvalle,
            ce.pv_conpunta,
            ce.pv_conllano,
            ce.pv_convalle,
            ce.pv_excedent,
            cg.bono_social,
            cg.alq_contador,
            cg.otros_gastos,
            cg.i_electrico,
            cg.iva
        FROM facturas_test fa
        JOIN contratos_identificacion_test ci
            ON ci.ncontrato = fa.ncontrato
           AND fa.inicio_factura BETWEEN ci.efec_suple AND ci.fin_suple
        JOIN contratos_energia_test ce
            ON ce.id_contrato = ci.id_contrato
        JOIN contratos_gastos_test cg
            ON cg.id_contrato = ci.id_contrato;
    """)


# ============================================================
# =====================   ÍNDICES   ==========================
# ============================================================


def crear_indices(cursor):
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_facturas_fec_emision
        ON facturas (fec_emision);
    """)


# ============================================================
# ===========   INICIALIZACIÓN DE SECUENCIAS   ===============
# ============================================================


def inicializar_secuencias(cursor):

    cursor.execute("""
        DELETE FROM sqlite_sequence
        WHERE name != 'contratos_identificacion_test';
    """)

    cursor.execute("""
        INSERT INTO sqlite_sequence (name, seq)
        VALUES ('contratos_identificacion_test', 900000)
        ON CONFLICT(name) DO UPDATE SET seq = 900000;
    """)


# ============================================================
# ===========   INICIALIZACIÓN DE SALDOS CLOUD   =============
# ============================================================


def inicializar_saldos(cursor, saldo_inicial):

    cursor.execute("DELETE FROM saldo_cloud;")
    cursor.execute(
        """
        INSERT INTO saldo_cloud (ncontrato, saldo)
        VALUES (1, ?);
    """,
        (saldo_inicial,),
    )

    cursor.execute("DELETE FROM saldo_cloud_inicial_test;")
    cursor.execute(
        """
        INSERT INTO saldo_cloud_inicial_test (id, saldo_inicial, fecha)
        VALUES (1, ?, DATE('now'));
    """,
        (saldo_inicial,),
    )


# ============================================================
# ===================   FUNCIÓN PRINCIPAL   ==================
# ============================================================


def crear_tablas_y_vistas(cursor, saldo_inicial):

    crear_tabla_contratos_identificacion(cursor)
    crear_tabla_contratos_energia(cursor)
    crear_tabla_contratos_gastos(cursor)
    crear_tabla_facturas(cursor)
    crear_tabla_factura_calculos(cursor)
    crear_tabla_saldo_cloud(cursor)
    crear_tabla_estadisticas_mensuales(cursor)

    crear_tablas_test(cursor)

    crear_vistas(cursor)

    crear_indices(cursor)

    inicializar_secuencias(cursor)

    inicializar_saldos(cursor, saldo_inicial)

    print("Inicialización completa ejecutada desde db_init.py")
