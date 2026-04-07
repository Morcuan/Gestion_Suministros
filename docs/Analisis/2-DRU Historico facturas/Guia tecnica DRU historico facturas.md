
---

# 📘 **GUÍA TÉCNICA — HISTÓRICO DE FACTURAS**
Proyecto: **Gestión Suministros 2.0**
Basada en: **DRU – Histórico de Facturas (versión actual)**
Fecha: 2026-02-09
Versión: 1.0

---

# 🧩 1. OBJETIVO DEL MÓDULO

El módulo **Histórico de Facturas** permite:

- Consultar facturas asociadas a un contrato.
- Visualizar los datos identificativos de cada factura.
- Mostrar el desglose completo de los cálculos almacenados en `factura_calculos`.
- Interpretar y mostrar el contenido de `detalles_json`.
- Verificar que los cálculos coinciden con la factura física recibida.
- Navegar entre pantallas sin recalcular nada.

**Este módulo es exclusivamente de consulta.**
No modifica datos, no recalcula, no altera contratos ni facturas.

---

# 🧩 2. UBICACIÓN Y ORGANIZACIÓN DE MÓDULOS

Todos los módulos del histórico se ubican en:

```
/analisis_factura/
```

Los módulos existentes que deben adaptarse:

- `lista_con_his_factura.py`
- `seleccionar_his_factura.py`
- `formulario_his_factura.py`

El módulo nuevo:

- `detalles_calculo_his_factura.py`

---

# 🧩 3. FLUJO COMPLETO DEL PROCESO

El flujo consta de **cuatro pantallas**, todas en modo consulta:

---

## **3.1 Pantalla 1 — Lista de contratos**

### Función
Mostrar todos los contratos disponibles en BD para iniciar la consulta.

### Comportamiento
- Lista correcta y funcional.
- Requiere selección obligatoria.

### Botones
- **Seleccionar contrato** → abre lista de facturas del contrato.
- **Cancelar** → vuelve al menú general.

### Trabajo técnico necesario
- Eliminar modos heredados de facturas.
- Eliminar llamadas a módulos de alta/modificación/anulación.
- Mantener solo la navegación hacia la lista de facturas.

---

## **3.2 Pantalla 2 — Lista de facturas del contrato**

### Función
Mostrar las facturas asociadas al contrato seleccionado.

### Ajustes visuales necesarios
Reducir ancho de columnas:

- Fecha emisión
- Inicio periodo
- Fin periodo
- Importe total

Para que **Nº Factura** se vea completo.

### Botones
- **Seleccionar factura** → abre Detalles de factura.
- **Cancelar** → vuelve a lista de contratos.

### Trabajo técnico necesario
- Eliminar modos heredados.
- Eliminar llamadas a módulos de rectificación/anulación.
- Mantener solo la navegación hacia Detalles de factura.

---

## **3.3 Pantalla 3 — Detalles de factura**

### Función
Mostrar los datos identificativos de la factura en modo solo lectura.

**CORRECCION**
**Los datos a mostrar son los que en el formulario se presentan, no son otros ni distintos. Los del formulario divididos en tres bloques: Identificacion, Consumos y Servicios y ajustes, igual que los que se capturan en el formulario de nueva factura, no son los que se representan en el siguiente apartado "Datos mostrados" aunque alguno de ellos pueda estar incluido**

### Datos mostrados
- Nº factura
- Fechas
- Periodo
- Consumos
- Servicios
- Suplemento
- Estado
- Etc.

**FIN DE CORRECCION**

### Botones
- **Mostrar cálculos** → abre Detalles de cálculo.
- **Cancelar** → vuelve a lista de facturas.

### Trabajo técnico necesario
- Adaptar el formulario a modo consulta.
- Añadir botón “Mostrar cálculos”.
- Eliminar cualquier lógica de modificación.

---

## **3.4 Pantalla 4 — Detalles de cálculo (NUEVA)**

### Función
Mostrar el desglose completo de la factura, incluyendo:

- Totales de `factura_calculos`.
- Desglose completo de `detalles_json`.
- Fórmulas utilizadas para cada importe.
- Valores intermedios (días, potencias, precios unitarios, etc.).

### Ejemplo de fórmula mostrada
```
28 días * 4.4 kW * 0.091074 €/kW/día = 11.22 €
```

### Botones
- **Cancelar** → vuelve a Detalles de factura.

### Trabajo técnico necesario
- Construcción completa del módulo.
- Parseo del JSON.
- Presentación clara y ordenada por bloques.
- Ajustes visuales durante pruebas.

---

# 🧩 4. DEPENDENCIAS DEL PROCESO

El histórico depende de:

### ✔️ 4.1 Vista `factura_calculos`
Contiene:

- Totales por bloque
- Cloud aplicado
- Cloud sobrante
- Total final
- `detalles_json` con el desglose completo

### ✔️ 4.2 Tabla `facturas`
Necesaria para:

- Datos identificativos
- Periodos
- Consumos
- Servicios
- Suplemento
- Estado
- Campo `recalcular`

### ✔️ 4.3 Módulo de **recalculo de facturas** (pendiente de construir)
Necesario porque:

- Hay facturas antiguas sin cálculo.
- Hay facturas marcadas con `recalcular = 1`.
- Debe integrarse en **Utilidades → Recalcular facturas**.
- Debe insertar los cálculos faltantes en `factura_calculos`.

Este módulo es **independiente del histórico**, pero el histórico depende de que exista.

---

# 🧩 5. ESTRUCTURA DE TABLAS (RESUMEN TÉCNICO)

## ✔️ 5.1 Vista `factura_calculos`
Incluye:

- Totales por bloque
- Cloud aplicado
- Cloud sobrante
- Total final
- JSON completo del cálculo

## ✔️ 5.2 Tabla `facturas`
Incluye:

- Datos identificativos
- Periodos
- Consumos
- Servicios
- Suplemento
- Estado
- Campo `recalcular`
- Relación con contrato y suplemento

---

# 🧩 6. REGLAS DRU APLICADAS

### ✔️ 1. No abrir pantallas sin selección previa
Evita ventanas huérfanas.

### ✔️ 2. No recalcular nada en el histórico
Solo lectura.

### ✔️ 3. `detalles_json` es la única fuente de verdad
No se reconstruyen cálculos.

### ✔️ 4. El histórico debe ser tolerante a versiones del motor
Si faltan campos → no romper.
Si sobran campos → ignorar.

### ✔️ 5. Ajustes visuales durante pruebas
Especialmente en Detalles de cálculo.

---

# 🧩 7. RESUMEN EJECUTIVO

El Histórico de Facturas es un módulo de **consulta estructurada**, compuesto por cuatro pantallas encadenadas, que permiten:

- Seleccionar contrato
- Seleccionar factura
- Ver datos de factura
- Ver desglose completo del cálculo

El módulo:

- No modifica datos
- No recalcula
- No interactúa con el motor
- Solo lee y muestra

El módulo de recalculo es independiente, pero necesario para que el histórico funcione con facturas antiguas.

---

Antonio, aquí tienes la guía técnica completa, totalmente alineada con tu DRU.

Cuando quieras, revisamos juntos:

- Ajustes
- Ampliaciones
- Correcciones
- O el siguiente paso del desarrollo.
