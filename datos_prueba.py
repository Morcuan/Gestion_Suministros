# datos de prueba excepto
# cpostales y companias que van en db_init

from modules_backup.utilidades_bd import get_connection
import sqlite3

conn = get_connection()
cur = conn.cursor()

# contratos
print("Tabla contratos")

cur.execute(
    """
INSERT INTO contratos (
    id_compania, id_postal, numero_contrato, fecha_inicio, fecha_final,
    potencia_punta, importe_potencia_punta, potencia_valle, importe_potencia_valle,
    importe_consumo_punta, importe_consumo_llano, importe_consumo_valle,
    vertido, importe_excedentes, importe_bono_social, importe_alquiler_contador,
    importe_asistente_smart, impuesto_electricidad, iva
    ) VALUES 
    (25, 45638, 'C-2025-001', '2025-01-01', '2025-12-31',
    4.4, 0.086301, 4, 0.013014,
    0.172576, 0.119892, 0.087904,
    1, 0.07, 0.012742, 0.02663,
    3.45, 5.11269632, 21),

    (25, 28050, 'C-2024-001', '2024-01-01', '2024-12-31',
    4.4, 0.086301, 4, 0.013014,
    0.172576, 0.119892, 0.087904,
    1, 0.07, 0.012742, 0.02663,
    3.45, 5.11269632, 21),

    (15, 45600, 'C-2025-002', '2025-01-01', '2025-12-31',
    4.5, 0.25, 3.0, 0.20,
    0.15, 0.10, 0.12,
    0, NULL, 0.00, 1.50,
    NULL, 5.11269632, 21),

    (35, 28222, 'C-2025-003', '2025-03-01', '2026-02-28',
    5.0, 0.30, 2.5, 0.18,
    0.14, 0.09, 0.11,
    1, 0.05, 0.00, 1.50,
    NULL, 5.11, 21);
"""
)
print("Tabla contratos terminada")
print("Tabla Facturas")

cur.execute(
    """
INSERT INTO facturas (
    id_contrato,
    factura,
    dias_factura,
    fecha_emision,
    importe_energia,
    cargos_normativos,
    servicios_y_otros,
    iva,
    bateria_virtual,
    total_factura,
    pendiente_consumos
) VALUES 
    (1, 'FAC-2025-001', 30, '2025-11-27', 120.45,                    
    15.20, 8.75, 21.00, -5.50, 160.90, TRUE),

    (1, 'FAC-2025-002', 30, '2025-10-27', 120.45,                    
    15.20, 8.75, 21.00, -10.50, 144.90, FALSE),

    (2, 'FAC-2025-001', 30, '2025-11-27', 120.45,                    
    15.20, 8.75, 21.00, -7.50, 160.90, FALSE),

    (3, 'FAC-2024-001', 30, '2024-11-27', 120.45,                    
    15.20, 8.75, 21.00, -0.50, 160.90, TRUE);
"""
)

print("Tabla facturas terminada")
print("Tabla Consumos")

cur.execute(
    """
INSERT INTO consumos (
    id_contrato, id_factura,
    consumo_punta, consumo_llano, consumo_valle,
    excedentes_vertidos
) VALUES
(1, 1, 120.0, 80.0, 60.0, 15.0),
(2, 2, 150.0, 90.0, 70.0, 20.0),
(1, 3, 110.0, 70.0, 50.0, 10.0),
(1, 4, 100.0, 60.0, 45.0, 0.0);
"""
)

print("Tabla consumos terminada")

conn.commit()
conn.close()
