# db_init.py — Versión modularizada y preparada para uso dual

import sqlite3

DB_PATH = "data/almacen.db"


# ---------------------------------------------------------
# FUNCIONES DE CREACIÓN DE TABLAS (MODULARIZADAS)
# ---------------------------------------------------------

def crear_tabla_contratos_identificacion(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contratos_identificacion (
            id_contrato     INTEGER PRIMARY KEY AUTOINCREMENT,
            ncontrato       TEXT NOT NULL,
            suplemento      INTEGER NOT NULL,
            cod_compania    TEXT NOT NULL,
            cod_postal      TEXT NOT NULL,
            fec_inicio      TEXT NOT NULL,
            fec_final       TEXT NOT NULL,
            efec_suple      TEXT NOT NULL,
            fin_suple       TEXT NOT NULL,
            fec_anulacion   TEXT,
            estado          TEXT NOT NULL,
            FOREIGN KEY (cod_compania) REFERENCES companias(cod_compania),
            FOREIGN KEY (cod_postal)   REFERENCES cpostales(cod_postal)
        );
    """)


def crear_tabla_contratos_energia(cursor):
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
            excedentes      REAL NOT NULL,
            pv_excedent     REAL NOT NULL,
            FOREIGN KEY (id_contrato) REFERENCES contratos_identificacion(id_contrato)
        );
    """)


def crear_tabla_contratos_gastos(cursor):
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
            cod_postal TEXT PRIMARY KEY,
            poblacion  TEXT NOT NULL
        );
    \""")
"""


# ---------------------------------------------------------
# TABLAS FUTURAS (FACTURAS Y CONSUMOS)
# ---------------------------------------------------------

def crear_tabla_facturas(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facturas (
            id_factura      INTEGER PRIMARY KEY AUTOINCREMENT,
            id_contrato     INTEGER NOT NULL,
            fecha_factura   TEXT NOT NULL,
            periodo_inicio  TEXT NOT NULL,
            periodo_fin     TEXT NOT NULL,
            importe_total   REAL NOT NULL,
            FOREIGN KEY (id_contrato) REFERENCES contratos_identificacion(id_contrato)
        );
    """)


def crear_tabla_consumos(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consumos (
            id_consumo  INTEGER PRIMARY KEY AUTOINCREMENT,
            id_factura  INTEGER NOT NULL,
            con_punta   REAL NOT NULL,
            con_llano   REAL NOT NULL,
            con_valle   REAL NOT NULL,
            FOREIGN KEY (id_factura) REFERENCES facturas(id_factura)
        );
    """)


# ---------------------------------------------------------
# VISTAS
# ---------------------------------------------------------

def crear_vista_contratos_completo(cursor):
    cursor.execute("DROP VIEW IF EXISTS vw_contratos_completo;")
    cursor.execute("""
        CREATE VIEW vw_contratos_completo AS
        SELECT
            ci.*,
            ce.ppunta, ce.pv_ppunta, ce.pvalle, ce.pv_pvalle,
            ce.pv_conpunta, ce.pv_conllano, ce.pv_convalle,
            ce.vertido, ce.excedentes, ce.pv_excedent,
            cg.bono_social, cg.alq_contador, cg.otros_gastos,
            cg.i_electrico, cg.iva,
            co.nombre AS nombre_compania,
            cp.poblacion AS nombre_poblacion
        FROM contratos_identificacion ci
        JOIN contratos_energia ce ON ci.id_contrato = ce.id_contrato
        JOIN contratos_gastos cg ON ci.id_contrato = cg.id_contrato
        JOIN companias co ON ci.cod_compania = co.cod_compania
        JOIN cpostales cp ON ci.cod_postal = cp.cod_postal;
    """)


# ---------------------------------------------------------
# FUNCIÓN PRINCIPAL (RECIBE CURSOR EXTERNO)
# ---------------------------------------------------------

def crear_tablas_y_vistas(cursor):
    crear_tabla_contratos_identificacion(cursor)
    crear_tabla_contratos_energia(cursor)
    crear_tabla_contratos_gastos(cursor)
    crear_tabla_facturas(cursor)
    crear_tabla_consumos(cursor)
    crear_vista_contratos_completo(cursor)


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
