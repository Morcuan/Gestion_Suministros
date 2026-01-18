# ------------------------------------------------------#
# Modulo: db_init.py                                   #
# Descripcion: Inicializa la base de datos             #
# Autor: Antonio Morales                               #
# Fecha: 2025-12-01                                    #
# ------------------------------------------------------#

import os
import sqlite3

import pandas as pd

# Ruta absoluta a la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "almacen.db")

# Conexión directa (script técnico, no forma parte del proyecto)
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# --------------------------------------------
# DROP de tablas si existen
# --------------------------------------------
tables = [
    "consumos",
    "facturas",
    "contratos_estados",
    "contratos",
    "companias",
    "cpostales",
]

for t in tables:
    cur.execute(f"DROP TABLE IF EXISTS {t}")

# --------------------------------------------
# Creación de tablas y vista
# --------------------------------------------
cur.executescript(
    """
CREATE TABLE cpostales (
    codigo_postal INTEGER PRIMARY KEY,
    poblacion TEXT
);

CREATE TABLE companias (
    id_compania INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE contratos (
    id_contrato INTEGER PRIMARY KEY AUTOINCREMENT,
    id_compania INTEGER NOT NULL,
    codigo_postal INTEGER NOT NULL,
    numero_contrato TEXT NOT NULL UNIQUE,
    fecha_inicio TEXT NOT NULL,
    fecha_final TEXT NOT NULL,
    potencia_punta REAL CHECK(potencia_punta >=0 AND potencia_punta <=10) NOT NULL,
    importe_potencia_punta REAL CHECK(importe_potencia_punta >=0 AND importe_potencia_punta <=1) NOT NULL,
    potencia_valle REAL CHECK(potencia_valle >=0 AND potencia_valle <=10) NOT NULL,
    importe_potencia_valle REAL CHECK(importe_potencia_valle >=0 AND importe_potencia_valle <=1) NOT NULL,
    importe_consumo_punta REAL CHECK(importe_consumo_punta >=0 AND importe_consumo_punta <=1) NOT NULL,
    importe_consumo_llano REAL CHECK(importe_consumo_llano >=0 AND importe_consumo_llano <=1) NOT NULL,
    importe_consumo_valle REAL CHECK(importe_consumo_valle >=0 AND importe_consumo_valle <=1) NOT NULL,
    vertido INTEGER CHECK(vertido IN (0,1)) NOT NULL,
    importe_excedentes REAL CHECK(importe_excedentes >=0 AND importe_excedentes <=1),
    importe_bono_social REAL CHECK(importe_bono_social >=0) NOT NULL,
    importe_alquiler_contador REAL CHECK(importe_alquiler_contador >=0) NOT NULL,
    importe_asistente_smart REAL,
    impuesto_electricidad REAL NOT NULL,
    iva REAL NOT NULL,
    FOREIGN KEY (id_compania) REFERENCES companias(id_compania),
    FOREIGN KEY (codigo_postal) REFERENCES cpostales(codigo_postal)
);

CREATE TABLE facturas (
    id_factura INTEGER PRIMARY KEY AUTOINCREMENT,
    id_contrato INTEGER NOT NULL,
    factura TEXT NOT NULL,
    dias_factura REAL,
    fecha_emision TEXT,
    importe_energia REAL,
    cargos_normativos REAL,
    servicios_y_otros REAL,
    iva REAL,
    bateria_virtual REAL,
    total_factura REAL,
    pendiente_consumos BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (id_contrato) REFERENCES contratos(id_contrato)
);

CREATE TABLE consumos (
    id_consumo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_contrato INTEGER NOT NULL,
    id_factura INTEGER NOT NULL UNIQUE,
    consumo_punta REAL,
    consumo_llano REAL,
    consumo_valle REAL,
    excedentes_vertidos REAL,
    FOREIGN KEY (id_contrato) REFERENCES contratos(id_contrato),
    FOREIGN KEY (id_factura) REFERENCES facturas(id_factura)
);

CREATE TABLE contratos_estados (
    id_estado INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_contrato TEXT NOT NULL,
    estado TEXT NOT NULL,
    fecha_baja TEXT NOT NULL,
    fecha_modificacion TEXT NOT NULL
);

CREATE VIEW vista_contratos AS
SELECT
    c.numero_contrato,
    co.nombre AS comercializadora,
    printf('%05d', c.codigo_postal) AS codigo_postal,
    cp.poblacion,
    strftime('%d/%m/%Y', c.fecha_inicio) AS fecha_inicio,
    strftime('%d/%m/%Y', c.fecha_final) AS fecha_final,

    CASE
        WHEN ult.estado = 'ANULADO' THEN 'ANULADO'
        WHEN date(c.fecha_inicio) > date('now') THEN 'PENDIENTE'
        WHEN date(c.fecha_final) < date('now') THEN 'CADUCADO'
        ELSE 'ACTIVO'
    END AS estado_actual,

    c.potencia_punta,
    c.importe_potencia_punta,
    c.potencia_valle,
    c.importe_potencia_valle,
    c.importe_consumo_punta,
    c.importe_consumo_llano,
    c.importe_consumo_valle,
    CASE c.vertido WHEN 1 THEN 'SI' ELSE 'NO' END AS vertido,
    c.importe_excedentes,
    c.importe_bono_social,
    c.importe_alquiler_contador,
    c.importe_asistente_smart,
    c.impuesto_electricidad,
    c.iva

FROM contratos c
LEFT JOIN companias co ON co.id_compania = c.id_compania
LEFT JOIN cpostales cp ON cp.codigo_postal = c.codigo_postal

LEFT JOIN (
    SELECT numero_contrato, estado
    FROM contratos_estados
    WHERE fecha_modificacion = (
        SELECT MAX(fecha_modificacion)
        FROM contratos_estados ce2
        WHERE ce2.numero_contrato = contratos_estados.numero_contrato
    )
) AS ult ON ult.numero_contrato = c.numero_contrato;
"""
)

# --------------------------------------------
# Índices
# --------------------------------------------
cur.executescript(
    """
CREATE INDEX idx_contratos_compania ON contratos(id_compania);
CREATE INDEX idx_contratos_postal ON contratos(codigo_postal);
CREATE INDEX idx_contratos_vigencia ON contratos(fecha_inicio, fecha_final);
CREATE INDEX idx_facturas_contrato ON facturas(id_contrato);
CREATE INDEX idx_consumos_contrato ON consumos(id_contrato);
CREATE UNIQUE INDEX idx_facturas_contrato_factura ON facturas (id_contrato, factura);
"""
)

# --------------------------------------------
# Carga inicial desde Excel
# --------------------------------------------
postales_file = os.path.join("data/Postales.xlsx")
df_postales = pd.read_excel(postales_file)
df_postales.to_sql("cpostales", conn, if_exists="append", index=False)

companias_file = os.path.join("data/Companias.xlsx")
df_companias = pd.read_excel(companias_file)
df_companias.to_sql("companias", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print("Base de datos inicializada correctamente.")
print("Proceda con los insert de pruebas")
