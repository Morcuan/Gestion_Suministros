

# 📘 **DRU v3 – Módulo Nueva Factura**
*(Documento de Reglas de Usuario – Versión 3)*

## 1. Naturaleza del módulo

El módulo **Nueva factura** permite:

- Capturar una factura asociada a un contrato.
- Validar los datos introducidos.
- Guardar la factura en la tabla `facturas`.
- Ejecutar el cálculo de la factura mediante el motor de cálculo.
- Guardar el resultado del cálculo en la tabla `factura_calculos`.

Características clave:

- Una factura pertenece siempre a un único contrato.
- No existe factura sin contrato asociado.
- La captura incluye consumos (punta, llano, valle) y servicios.
- La tabla `facturas` contiene directamente los consumos.
- Tras guardar la factura, se ejecuta el cálculo automáticamente.
- El usuario puede capturar otra factura o volver al menú.

Este módulo **no incluye** rectificación de facturas ni recalculo masivo.

---

## 2. Flujo funcional

### 2.1 Entrada al módulo
Menú principal → Facturas → Nueva factura.

### 2.2 Selección del contrato
- Se muestra una lista de contratos disponibles.
- Se incluyen:
  - Contrato en vigor.
  - Contratos futuros.
- Se excluyen:
  - Suplementos futuros.
- El botón “Seleccionar contrato” se habilita solo con una selección válida.
- “Cancelar” vuelve al menú principal.

### 2.3 Formulario de factura
Tras seleccionar contrato, se abre el formulario con:

- Datos informativos del contrato y suplemento.
- Campos de identificación de la factura.
- Fechas del periodo.
- Consumos.
- Servicios y ajustes.

### 2.4 Validaciones
El sistema valida:

- `nfactura` único dentro del contrato.
- Ningún campo obligatorio vacío.
- Fechas válidas y coherentes.
- `dias_factura` entre 1 y 61 (se corrige si es necesario).
- Consumos ≥ 0.
- Importes ≥ 0.
- El inicio del periodo debe estar dentro del suplemento.
- No se permite que todos los importes de potencia/consumo sean cero.
- Validaciones adicionales según se detecten.

### 2.5 Guardado de la factura
- Se inserta un registro en la tabla `facturas`.
- La ventana **no se cierra** tras guardar.
- Opciones posteriores:
  - “Otra factura” → nueva captura para el mismo contrato.
  - “Salir” → vuelve al menú principal.

### 2.6 Cálculo de la factura
Tras guardar:

1. Se llama al motor de cálculo.
2. El motor devuelve:
   - Totales de energía, cargos, servicios, IVA, total final.
   - Cloud aplicado y sobrante.
   - Detalles en JSON.
   - Versión del motor.
3. El sistema guarda el cálculo en `factura_calculos`.

### 2.7 Grabación del cálculo
- Se inserta un registro en `factura_calculos` por cada cálculo.
- No se borran cálculos anteriores.
- Se mantiene trazabilidad completa.

---

## 3. Bloques del formulario

### 3.1 Bloque Identificación
- ncontrato (informativo)
- suplemento (informativo)
- nfactura
- fec_emision
- inicio_factura
- fin_factura
- dias_factura

### 3.2 Bloque Consumos
- consumo_punta
- consumo_llano
- consumo_valle
- excedentes
- importe_compensado

### 3.3 Bloque Servicios
- servicios
- dcto_servicios
- saldos_pendientes
- bat_virtual

---

## 4. Valores por defecto
- `ncontrato` → desde selección previa
- `suplemento` → desde selección previa
- `rectifica_a` → vacío
- `recalcular` → 0
- `estado` → “Emitida”

---

## 5. Navegación y comportamiento
- Flujo vertical, botones abajo.
- “Cancelar” siempre vuelve al menú.
- Tras guardar:
  - Mantener ventana abierta.
  - Permitir capturar otra factura.
  - Permitir salir.

---

