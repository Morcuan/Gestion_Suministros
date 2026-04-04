Perfecto, Antonio.
Y gracias por el aviso, porque **esto cambia un punto clave del DRU**: la factura ya no se identifica por `id_factura`, sino por **`nfactura` como clave primaria real y operativa**.

Esto no es un detalle menor: afecta a cómo seleccionamos, cargamos, editamos y guardamos la factura.
Así que vamos a ajustar el DRU para que quede **coherente con la nueva arquitectura**, limpio y sin ambigüedades.

Aquí tienes la **versión corregida y definitiva del DRU**, con el punto 5 revisado y el concepto de clave basado en `nfactura`.

---

# 🧩 **DRU – Rectificación/Modificación de Factura (versión corregida)**

## 🔑 **Clave primaria operativa**
- La factura se identifica **únicamente por `nfactura`**.
- `id_factura` ha sido eliminado del modelo conceptual y físico.
- Todas las operaciones de selección, carga, edición y actualización se basan en `nfactura`.

---

# 1️⃣ Alcance funcional

### ✔ Campos modificables
Todos los campos de la tabla `facturas` excepto los protegidos:

- `fecha_emision`
- `inicio_factura`
- `fin_factura`
- `consumo`
- `excedentes`
- `importe_compensado`
- `servicios`
- `descuento_servicios`
- `saldos_pendientes`
- `bateria_virtual`
- Campos económicos derivados (si procede)

### ❌ Campos NO modificables
- `nfactura`
  → Si está mal, implica **anulación**, no rectificación.
  → DRU independiente.
- `recalcular`
- `estado`
- `rectifica_a`
- `ncontrato`
- `suplemento`

### 📝 Nota sobre `dias_facturados`
- **No editable**
- **Se recalcula automáticamente** al modificar fechas.

---

# 2️⃣ Flujo general

## Paso 1 – Selección del contrato
- Igual que en “Nueva factura”.

## Paso 2 – Listado de facturas del contrato
- Se muestran todas las facturas asociadas al contrato.
- La selección se hace por **`nfactura`**.

## Paso 3 – Apertura de ventana de edición
- Misma ventana que “Nueva factura”, pero:
  - Modo edición
  - Campos protegidos deshabilitados
  - Botón “Guardar cambios”

## Paso 4 – Validaciones
- Fechas en formato dd/mm/yyyy → conversión a ISO
- Recalcular `dias_facturados`
- Validación numérica
- Coherencia con el contrato

## Paso 5 – Guardado (corregido)
- Se actualiza la factura **identificada por `nfactura`**.
- Se recalculan importes y valores derivados.
- Se actualiza la entrada correspondiente en `factura_calculos` usando **`nfactura` como referencia**.
- No se crea ninguna factura nueva.
- No se altera el número de factura.

---

# 3️⃣ Requisitos técnicos

### ✔ Independencia total de la rama “Nueva factura”
- No se toca su lógica.
- Se reutiliza la ventana con un parámetro `modo="edicion"`.

### ✔ Motor de cálculo reutilizado
- Igual que en factura nueva.
- La diferencia es que se hace un **UPDATE** en lugar de un INSERT.

### ✔ Actualización de factura_calculos
- Se recalcula el JSON.
- Se recalculan importes.
- Se actualiza la fila correspondiente a `nfactura`.

---

# 4️⃣ Interfaz conceptual

### Menú Facturas
- Nueva factura
- **Rectificar factura**
- (Futuro) Anulación de factura

### Ventanas
1. Selección de contrato
2. Selección de factura (por `nfactura`)
3. Ventana de edición

---

# 5️⃣ Casos especiales

### ❌ Error en `nfactura`
→ No se rectifica.
→ Se anula.
→ Se crea una nueva.
→ DRU independiente.

### ✔ Rectificación de fechas
→ Permitida.
→ Recalcula días.
→ Recalcula importes.

---

# 🏁 **DRU final listo para implementación**
Ahora sí, completamente alineado con tu nueva arquitectura sin `id_factura`, limpio, coherente y preparado para integrarse sin riesgo en el sistema.

Cuando quieras, pasamos a la fase de diseño de ventanas o al pseudocódigo de la lógica de edición.
