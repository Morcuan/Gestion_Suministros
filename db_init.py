# db_init.py — Versión modularizada y preparada para uso dual

import sqlite3

DB_PATH = "data/almacen.db"


# ---------------------------------------------------------
# FUNCIONES DE CREACIÓN DE TABLAS (MODULARIZADAS)
# ---------------------------------------------------------
def crear_tabla_contratos_identificacion(cursor):
    cursor.execute("DROP TABLE IF EXISTS contratos_identificacion;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contratos_identificacion (
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
            estado          TEXT NOT NULL,
            FOREIGN KEY (codigo_postal)   REFERENCES cpostales(codigo_postal)
        );
    """)


def crear_tabla_contratos_energia(cursor):
    cursor.execute("DROP TABLE IF EXISTS contratos_energia;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contratos_energia (
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
        CREATE TABLE IF NOT EXISTS contratos_gastos (
            id_contrato     INTEGER PRIMARY KEY,
            bono_social     REAL NOT NULL,
            alq_contador    REAL NOT NULL,
            otros_gastos    REAL NOT NULL,
            i_electrico     REAL NOT NULL,
            iva             REAL NOT NULL,
            FOREIGN KEY (id_contrato) REFERENCES contratos_identificacion(id_contrato)
        );
    """)


# ---------------------------------------------------------
# TABLAS AUXILIARES (NO SE CREAN AQUÍ)
# ---------------------------------------------------------
# NOTA IMPORTANTE:
# Las tablas `companias` y `cpostales` ya existen y se cargan desde:
#   - Companias.csv
#   - Postales.csv
# situados en el directorio /data.
# Se mantienen comentadas para referencia del DRU.

"""
def crear_tabla_companias(cursor):
    cursor.execute(\"""
        CREATE TABLE IF NOT EXISTS companias (
            cod_compania TEXT PRIMARY KEY,
            nombre       TEXT NOT NULL
        );
    \""")

def crear_tabla_cpostales(cursor):
    cursor.execute(\"""
        CREATE TABLE IF NOT EXISTS cpostales (
            codigo_postal TEXT PRIMARY KEY,
            poblacion  TEXT NOT NULL
        );
    \""")
"""


# ---------------------------------------------------------
# TABLA FACTURAS
# ---------------------------------------------------------
def crear_tabla_facturas(cursor):
    cursor.execute("DROP TABLE IF EXISTS facturas;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facturas (
            id_contrato        INTEGER NOT NULL,
            nfactura           TEXT NOT NULL,
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
            PRIMARY KEY (id_contrato, nfactura),
            FOREIGN KEY (id_contrato) REFERENCES contratos_identificacion(id_contrato)
        );
        """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_facturas_fec_emision
        ON facturas (fec_emision);
        """)


# ---------------------------------------------------------
# VISTAS
# ---------------------------------------------------------


def crear_vista_contratos_completo(cursor):
    cursor.execute("DROP VIEW IF EXISTS vista_contratos;")
    cursor.execute("""
        CREATE VIEW vista_contratos AS
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
        JOIN cpostales cp ON ci.codigo_postal = cp.codigo_postal;
    """)


def crear_vista_contratos_facturacion(cursor):
    cursor.execute("DROP VIEW IF EXISTS vista_contratos_identificacion;")
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS vista_contratos_facturacion AS
        SELECT
            c.id_contrato,
            c.ncontrato,
            c.estado,
            c.compania,
            c.codigo_postal,
            cp.poblacion
        FROM contratos_identificacion c
        LEFT JOIN cpostales cp
                ON c.codigo_postal = cp.codigo_postal;
    """)


def crear_vista_v_datos_calculo(cursor):
    cursor.execute("DROP VIEW IF EXISTS v_datos_calculo;")
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_datos_calculo AS
        SELECT
            -- Factura
            fa.id_contrato              AS id_contrato_base,
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

            -- Suplemento correcto
            ci.id_contrato              AS id_contrato_suplemento,
            ci.ncontrato,
            ci.suplemento,
            ci.efec_suple,
            ci.fin_suple,

            -- Contratos energía
            ce.ppunta,
            ce.pv_ppunta,
            ce.pvalle,
            ce.pv_pvalle,
            ce.pv_conpunta,
            ce.pv_conllano,
            ce.pv_convalle,
            ce.pv_excedent,

            -- Contratos gastos
            cg.bono_social,
            cg.alq_contador,
            cg.otros_gastos,
            cg.i_electrico,
            cg.iva

        FROM facturas fa
        JOIN contratos_identificacion ci
            ON ci.ncontrato = (
                SELECT ncontrato
                FROM contratos_identificacion
                WHERE id_contrato = fa.id_contrato
            )
            AND fa.inicio_factura BETWEEN ci.efec_suple AND ci.fin_suple
        JOIN contratos_energia ce
            ON ce.id_contrato = ci.id_contrato
        JOIN contratos_gastos cg
            ON cg.id_contrato = ci.id_contrato;
    """)


# ---------------------------------------------------------
# FUNCIÓN PRINCIPAL (RECIBE CURSOR EXTERNO)
# ---------------------------------------------------------


def crear_tablas_y_vistas(cursor):
    crear_tabla_contratos_identificacion(cursor)
    crear_tabla_contratos_energia(cursor)
    crear_tabla_contratos_gastos(cursor)
    crear_tabla_facturas(cursor)
    crear_vista_contratos_completo(cursor)
    crear_vista_contratos_facturacion(cursor)
    crear_vista_v_datos_calculo(cursor)


# ---------------------------------------------------------
# MODO AUTÓNOMO (SOLO SI SE EJECUTA DIRECTAMENTE)
# ---------------------------------------------------------

if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    crear_tablas_y_vistas(cursor)
    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente.")
