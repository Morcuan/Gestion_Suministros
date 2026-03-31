# 📗 **Guía Técnica v3 – Módulo Nueva Factura**

## 1. Estructura de BD

### 1.1 Tabla `facturas`
*(Se mantiene la estructura completa porque es necesaria para la implementación técnica)*

```
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
```

Índice recomendado:

```
CREATE INDEX idx_facturas_fec_emision
ON facturas (fec_emision);
```

### 1.2 Tabla `factura_calculos`

```
id_calculo INTEGER PRIMARY KEY AUTOINCREMENT,
id_factura INTEGER NOT NULL,
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
FOREIGN KEY (id_factura) REFERENCES facturas(id)
```

---

## 2. Validaciones técnicas

### 2.1 Fechas
- Entrada en formato `dd/mm/yyyy`.
- Conversión a ISO `yyyy-mm-dd` antes de guardar.
- Validar coherencia: inicio ≤ fin.
- Calcular `dias_factura` como diferencia + 1.

### 2.2 Numéricos
- Convertir a `float`.
- Vacíos → 0.
- No permitir negativos.

### 2.3 Unicidad
- `nfactura` debe ser único dentro del contrato.

### 2.4 Consumos
- Al menos uno de los consumos o importes debe ser > 0.

---

## 3. Flujo de ventanas

### 3.1 Lista de contratos
- Tabla con contratos disponibles.
- Botón “Seleccionar contrato”.
- Botón “Cancelar”.

### 3.2 Formulario de factura
- Campos organizados por bloques.
- Botones:
  - Guardar
  - Otra factura
  - Salir
  - Cancelar

### 3.3 Comportamiento tras guardar
- No cerrar ventana.
- Mostrar mensaje de éxito.
- Habilitar “Otra factura”.

---

## 4. Inserciones en BD

### 4.1 Inserción en `facturas`
- Preparar diccionario con todos los campos.
- Convertir fechas a ISO.
- Insertar mediante cursor.

### 4.2 Inserción en `factura_calculos`
- Tras recibir datos del motor:
  - Preparar registro.
  - Insertar en tabla.

---

## 5. Integración con el motor de cálculo

### 5.1 Entrada al motor
Se envían:

- Fechas
- Consumos
- Servicios
- Datos del contrato
- Suplemento
- Parámetros necesarios según versión del motor

### 5.2 Salida del motor
El motor devuelve:

- Totales
- IVA
- Cloud aplicado y sobrante
- Total final
- Detalles JSON
- Versión del motor

### 5.3 Grabación
- Insertar un registro en `factura_calculos`.
- No borrar cálculos anteriores.

---

# ✔️ Antonio, DRU v3 y Guía Técnica v3 completados

Si quieres, ahora puedo:

- Generar **el pseudocódigo del módulo**
- Generar **la estructura de archivos**
- Preparar **el esqueleto Python listo para pegar**
- O continuar con el siguiente módulo del proyecto

Tú decides el siguiente movimiento.
