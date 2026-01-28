Perfecto, Antonio. Vamos a dejar **el DRU definitivo de la tabla `contratos`**, incluyendo **todas las tablas relacionadas** que forman el núcleo del módulo (excepto `cpostales` y `companias`, que ya existen).
He incorporado **tu corrección sobre la distribuidora**, que efectivamente faltaba.

Todo en **Markdown limpio**, listo para copiar a tu documentación.

---

# 📘 **DRU — Módulo Contratos (versión depurada y final)**

Este documento define la estructura, reglas y relaciones del módulo **Contratos**, incluyendo:

- Tabla `contratos`
- Tabla `distribuidoras`
- Tabla `facturas`
- Tabla `consumos` (si se usa separada)
- Relaciones entre todas ellas

---

# #️⃣ **1. Tabla `contratos`**

## 🎯 **Objetivo**
Representar **cada suplemento** de un contrato energético.
Cada fila = un suplemento.
El contrato completo es la unión ordenada de sus suplementos.

---

## 🧱 **Estructura de campos**

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `id_contrato` | INTEGER PK AUTOINCREMENT | Sí | Identificador interno |
| `ncontrato` | TEXT | Sí | Número de contrato (no modificable) |
| `suplemento` | INTEGER | Sí | 0 = inicial, 1..N = modificaciones |
| `id_compania` | INTEGER FK | Sí | Comercializadora |
| `id_distribuidora` | INTEGER FK | Sí | Distribuidora eléctrica |
| `id_postal` | INTEGER FK | Sí | Código postal del punto de suministro |
| `fec_inicio` | TEXT ISO | Sí | Fecha de alta del contrato |
| `fec_final` | TEXT ISO | Sí | Fecha de baja del contrato |
| `efec_suple` | TEXT ISO | Sí | Inicio de vigencia del suplemento |
| `fin_suple` | TEXT ISO | Sí | Fin de vigencia del suplemento |
| `fec_anulado` | TEXT ISO | No | Fecha de anulación |
| `ppunta` | REAL | Sí | Potencia punta (kW) |
| `pv_ppunta` | REAL | Sí | Precio potencia punta |
| `pvalle` | REAL | Sí | Potencia valle (kW) |
| `pv_pvalle` | REAL | Sí | Precio potencia valle |
| `pv_conpunta` | REAL | Sí | Precio energía punta |
| `pv_conllano` | REAL | Sí | Precio energía llano |
| `pv_convalle` | REAL | Sí | Precio energía valle |
| `vertido` | BOOLEAN | Sí | Si hay excedentes |
| `excedentes` | REAL | Sí | Cantidad vertida (kWh) |
| `pv_excedent` | REAL | Sí | Precio excedente |
| `bono_social` | REAL | Sí | Importe |
| `alq_contador` | REAL | Sí | Importe |
| `otros_gastos` | REAL | Sí | Importe |
| `i_electrico` | REAL | Sí | % |
| `iva` | REAL | Sí | % |
| `estado` | TEXT | Sí | Estado calculado y guardado |

---

## 🧮 **Reglas de validación**

### ✔ Fechas
- Entrada: `dd/mm/yyyy`
- Guardado: `yyyy-mm-dd`
- `fec_inicio` y `fec_final` **inamovibles** en todos los suplementos
- Suplemento 0:
  - `efec_suple = fec_inicio`
  - `fin_suple = fec_final`
- Suplementos >0:
  - `efec_suple` = día siguiente a `fin_suple` del suplemento anterior
  - `fin_suple` = `fec_final` del contrato
- `fec_anulado` opcional
- Si `fec_anulado` existe → estado = "Anulado" salvo que sea futura

---

### ✔ Estado del contrato
Reglas aplicadas al **suplemento actual**:

- Si hoy ∈ `[efec_suple, fin_suple]` → **Activo**
- Si hoy < `efec_suple` → **Futuro**
- Si `fec_anulado` no nula:
  - hoy < `fec_anulado` → **Activo**
  - hoy ≥ `fec_anulado` → **Anulado**
- Si `fin_suple` < hoy y no anulado → **Caducado**

---

### ✔ Potencias
- Valores > 0 y < 10
- Punta y valle no pueden ser ambos 0
- Decimales permitidos

---

### ✔ Precios energía
- Valores > 0
- `pv_conpunta`, `pv_conllano`, `pv_convalle` < 1 (€/kWh)

---

### ✔ Excedentes
- Si `vertido = False` → `excedentes = 0` y `pv_excedent = 0`
- `excedentes` < 1000
- `pv_excedent` < 1

---

### ✔ Gastos
- Todos positivos
- `i_electrico` e `iva` en %

---

## 🔗 **Relaciones**

- `id_compania` → `companias(id_compania)`
- `id_distribuidora` → `distribuidoras(id_distribuidora)`
- `id_postal` → `cpostales(id_postal)`
- `id_contrato` → `facturas(id_contrato)`

---

# #️⃣ **2. Tabla `distribuidoras`**

## 🎯 Objetivo
Almacenar las distribuidoras eléctricas oficiales.

## 🧱 Estructura

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_distribuidora` | INTEGER PK | Identificador |
| `nombre` | TEXT | Nombre comercial |
| `cif` | TEXT | Opcional |
| `zona` | TEXT | Opcional |

---

# #️⃣ **3. Tabla `facturas`**

## 🎯 Objetivo
Registrar cada factura asociada a un suplemento de contrato.

## 🧱 Estructura

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_factura` | INTEGER PK |  |
| `id_contrato` | INTEGER FK | Suplemento al que pertenece |
| `fecha_factura` | TEXT ISO | Fecha |
| `periodo_inicio` | TEXT ISO | Inicio periodo facturado |
| `periodo_fin` | TEXT ISO | Fin periodo facturado |
| `importe_total` | REAL | Total factura |

---

# #️⃣ **4. Tabla `consumos`** (opcional si no van dentro de facturas)

## 🎯 Objetivo
Registrar consumos por factura y periodo.

## 🧱 Estructura

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_consumo` | INTEGER PK |  |
| `id_factura` | INTEGER FK | Factura asociada |
| `con_punta` | REAL | kWh |
| `con_llano` | REAL | kWh |
| `con_valle` | REAL | kWh |

---

# #️⃣ **5. Relaciones globales del módulo**

```
companias (1) ─── (N) contratos (N) ─── (N) facturas (1) ─── (1) consumos
distribuidoras (1) ─── (N) contratos
cpostales (1) ─── (N) contratos
```
