import os
import shutil
import sqlite3

DB_PATH = "data/almacen.db"
BACKUP_PATH = "data/backup_facturas_sin_id_contrato.db"

print("=== Migración: eliminar id_contrato de facturas ===")

# 1. Copia de seguridad
if not os.path.exists(DB_PATH):
    print(f"ERROR: No se encuentra la base de datos en {DB_PATH}")
    exit(1)

print("Creando copia de seguridad...")
shutil.copy(DB_PATH, BACKUP_PATH)
print(f"Copia creada en: {BACKUP_PATH}")

# 2. Conexión
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Ejecutando migración...")

script = """
PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

---------------------------------------------------------
-- 1. Borrar vistas dependientes de facturas
---------------------------------------------------------
DROP VIEW IF EXISTS v_datos_calculo;

---------------------------------------------------------
-- 2. Crear tabla nueva sin id_contrato
---------------------------------------------------------
CREATE TABLE facturas_new (
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

---------------------------------------------------------
-- 3. Copiar datos desde la tabla antigua
---------------------------------------------------------
INSERT INTO facturas_new (
    nfactura, inicio_factura, fin_factura,
    dias_factura, fec_emision,
    consumo_punta, consumo_llano, consumo_valle,
    excedentes, importe_compensado,
    servicios, dcto_servicios, saldos_pendientes, bat_virtual,
    recalcular, estado, rectifica_a, ncontrato, suplemento
)
SELECT
    nfactura, inicio_factura, fin_factura,
    dias_factura, fec_emision,
    consumo_punta, consumo_llano, consumo_valle,
    excedentes, importe_compensado,
    servicios, dcto_servicios, saldos_pendientes, bat_virtual,
    recalcular, estado, rectifica_a, ncontrato, suplemento
FROM facturas;

---------------------------------------------------------
-- 4. Borrar tabla antigua
---------------------------------------------------------
DROP TABLE facturas;

---------------------------------------------------------
-- 5. Renombrar la nueva
---------------------------------------------------------
ALTER TABLE facturas_new RENAME TO facturas;

---------------------------------------------------------
-- 6. Recrear índice
---------------------------------------------------------
CREATE INDEX idx_facturas_fec_emision
    ON facturas (fec_emision);

---------------------------------------------------------
-- 7. Recrear vista v_datos_calculo (versión corregida)
---------------------------------------------------------
CREATE VIEW v_datos_calculo AS
SELECT
    -- Factura
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

    -- Suplemento correcto
    ci.id_contrato              AS id_contrato_base,
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
    ON ci.ncontrato = fa.ncontrato
    AND ci.suplemento = fa.suplemento
    AND fa.inicio_factura BETWEEN ci.efec_suple AND ci.fin_suple
JOIN contratos_energia ce
    ON ce.id_contrato = ci.id_contrato
JOIN contratos_gastos cg
    ON cg.id_contrato = ci.id_contrato;

---------------------------------------------------------

COMMIT;
PRAGMA foreign_keys = ON;
"""

try:
    cursor.executescript(script)
    conn.commit()
    print("Migración completada con éxito.")
except Exception as e:
    conn.rollback()
    print("ERROR durante la migración:")
    print(e)

conn.close()
print("Conexión cerrada.")
