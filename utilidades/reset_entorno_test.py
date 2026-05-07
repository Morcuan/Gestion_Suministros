# -------------------------------------------------------------#
# Módulo: reset_entorno_test.py                                #
# Descripción: Limpia y recrea todas las tablas TEST           #
# Autor: Antonio Morales                                       #
# Fecha: 2026-05                                               #
# -------------------------------------------------------------#


def reset_entorno_test(conn):
    cursor = conn.cursor()

    # 1) Borrar tablas test (orden correcto por dependencias)

    cursor.executescript("""
        DROP VIEW IF EXISTS v_datos_calculo_test;

        -- Primero las tablas que dependen de contratos_identificacion_test
        DROP TABLE IF EXISTS contratos_gastos_test;
        DROP TABLE IF EXISTS contratos_energia_test;

        -- Ahora la tabla padre
        DROP TABLE IF EXISTS contratos_identificacion_test;

        -- Tablas independientes
        DROP TABLE IF EXISTS factura_calculos_test;
        DROP TABLE IF EXISTS saldo_cloud_test;
        DROP TABLE IF EXISTS facturas_test;
    """)

    # 2) Recrear tablas test

    cursor.executescript("""
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

        CREATE TABLE saldo_cloud_test (
            ncontrato TEST PRIMARY KEY,
            saldo REAL NOT NULL
        );

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
            pv_excedent     REAL NOT NULL,
            FOREIGN KEY (id_contrato) REFERENCES contratos_identificacion_test(id_contrato)
        );

        CREATE TABLE contratos_gastos_test (
            id_contrato     INTEGER PRIMARY KEY,
            bono_social     REAL NOT NULL,
            alq_contador    REAL NOT NULL,
            otros_gastos    REAL NOT NULL,
            i_electrico     REAL NOT NULL,
            iva             REAL NOT NULL,
            FOREIGN KEY (id_contrato) REFERENCES contratos_identificacion_test(id_contrato)
        );
    """)

    # 3) Recrear vista test

    cursor.executescript("""
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

    conn.commit()
