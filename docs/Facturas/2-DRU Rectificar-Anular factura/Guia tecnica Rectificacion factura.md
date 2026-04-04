Perfecto, Antonio.
Entramos **directamente en modo implementación** de la rama *Rectificación de factura*, siguiendo el DRU que ya has validado.

Voy a darte ahora **la arquitectura técnica exacta**, paso a paso, para que puedas implementarlo sin riesgo, sin tocar la rama de “Nueva factura” y manteniendo tu entorno limpio y modular.

---

# 🧱 1. Estructura general de la nueva rama
La rama se llamará, por ejemplo:

```
facturas_rectificar/
```

Y contendrá:

- `rectificar_factura.py` → flujo principal
- `seleccionar_factura.py` → listado de facturas por contrato
- Reutilización de `facturas.py` → ventana de captura, pero en modo edición
- Ajustes menores en `db_facturas.py` → añadir UPDATE por `nfactura`
- Ajustes en `factura_calculos.py` → recalcular y actualizar por `nfactura`

---

# 🪟 2. Ventana 1: Selección de contrato
**Reutilizas exactamente la misma ventana** que en “Nueva factura”.

La única diferencia es que, al pulsar “Aceptar”, en vez de abrir la ventana de captura, abrirá:

```
seleccionar_factura.py
```

---

# 🧾 3. Ventana 2: Selección de factura
Nueva ventana, muy simple:

### Campos:
- Tabla/listado con las facturas del contrato seleccionado
- Columnas:
  - `nfactura`
  - `fecha_emision`
  - `inicio_factura`
  - `fin_factura`
  - `importe_total`

### Botones:
- **Editar factura seleccionada**
- Cancelar / Volver

### Lógica:
- Al seleccionar una fila → obtienes `nfactura`
- Llamas a la ventana de edición:

```
facturas.py(modo="edicion", nfactura=valor)
```

---

# 🛠 4. Ventana 3: Edición de factura (reutilizando facturas.py)

Aquí está la clave:
**NO duplicas la ventana. NO creas otra. NO tocas la lógica de nueva factura.**

Solo añades:

### ✔ Parámetro nuevo en el constructor:
```
def __init__(self, modo="nuevo", nfactura=None):
```

### ✔ Si modo == "edicion":
1. Cargar datos de la factura desde BD usando `nfactura`
2. Rellenar los campos
3. Deshabilitar los campos protegidos:
   - nfactura
   - ncontrato
   - suplemento
   - estado
   - rectifica_a
   - recalcular
4. Cambiar el texto del botón:
   - “Guardar cambios”
5. Cambiar la función asociada al botón:
   - En vez de `insertar_factura()`
   - Llamar a `actualizar_factura()`

---

# 🧮 5. Lógica de actualización en BD

En `db_facturas.py` añades:

```
def actualizar_factura(datos):
    UPDATE facturas SET
        fecha_emision = ?,
        inicio_factura = ?,
        fin_factura = ?,
        consumo = ?,
        excedentes = ?,
        importe_compensado = ?,
        servicios = ?,
        descuento_servicios = ?,
        saldos_pendientes = ?,
        bateria_virtual = ?
    WHERE nfactura = ?
```

### ✔ `dias_facturados`
No se edita → se recalcula automáticamente antes del UPDATE.

---

# 🔄 6. Recalcular factura_calculos

En `factura_calculos.py`:

- Reutilizas el motor de cálculo actual.
- En vez de insertar una fila nueva, haces:

```
DELETE FROM factura_calculos WHERE nfactura = ?
INSERT INTO factura_calculos (...)
```

O bien:

```
UPDATE factura_calculos SET ...
```

Lo que prefieras, pero DELETE+INSERT es más limpio y coherente con tu filosofía.

---

# 🧪 7. Validaciones

### ✔ Fechas
- dd/mm/yyyy → convertir a ISO antes de guardar
- Recalcular días facturados

### ✔ Campos numéricos
- Igual que en nueva factura

### ✔ Coherencia con contrato
- Fechas dentro del periodo del contrato

---

# 🧩 8. Resultado final del flujo

1. Seleccionas contrato
2. Seleccionas factura
3. Entras en ventana de edición
4. Modificas lo permitido
5. Guardas
6. Se recalcula todo
7. Se actualiza factura y factura_calculos
8. Vuelves al menú principal o a la ventana anterior

---

# 🎯 Antonio, ya puedes empezar a picar código
Este diseño está:

- Limpio
- Modular
- Sin duplicar ventanas
- Sin tocar la rama de nueva factura
- Basado en `nfactura` como clave
- Con cálculo y BD perfectamente alineados

Si quieres, ahora pasamos a:

- Generar el pseudocódigo completo
- Generar el esqueleto de los módulos
- O empezar por la ventana de selección de factura

Tú decides el siguiente paso.
