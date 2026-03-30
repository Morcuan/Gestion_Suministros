### 🟦 DRU – Módulo de Anulación / Rehabilitación de Contratos
*(versión revisada con tus aclaraciones integradas)*

> “La anulacion solo puede ser para el suplemento actual, que se distingue del futuro porque el futuro tiene fec_efecto superior al dia de hoy”
> “Es necesario comprobar y adaptar lista_contratos.py para que tenga en cuenta el caso de un contrato con un suplemento futuro.”

---

## 🟦 1. Objetivo del módulo

Permitir:

- **Anular un contrato** → asignar una fecha de anulación (`fec_anulacion`).
- **Rehabilitar un contrato** → eliminar la fecha de anulación (`fec_anulacion = NULL`).

El proceso afecta **solo a la tabla `contratos_identificacion`**, y únicamente al **suplemento vigente** del contrato.
Si existe un **suplemento futuro** (con `fec_efecto` superior a la fecha de hoy), la anulación afecta **al suplemento vigente y al suplemento futuro**, según se detalla en los casos especiales.

> “El proceso afecta solo a la tabla contratos_identificacion, y únicamente al suplemento actual (máximo) excepto si existe un suplemento futuro…”

---

## 🟦 2. Definiciones clave

- **Suplemento futuro**: suplemento de un contrato cuya `fec_efecto` es **superior a la fecha de hoy**.
- **Suplemento vigente**: suplemento del contrato tal que la fecha de hoy cumple:

  \[
  DATE('now') \text{ BETWEEN } fec\_efecto \text{ AND } fec\_final
  \]

  Es decir, hoy está dentro del rango de vigencia del suplemento.

- **No se permiten contratos abiertos**: no habrá contratos con `fec_final = NULL`. Siempre existe `fec_final`, por lo que la validación “NO puede ser posterior a `fec_final`” es siempre aplicable.

---

## 🟦 3. Flujo funcional

### 3.1 Menú principal

Ruta:

```text
Contratos → Anular / Rehabilitar
```

### 3.2 Pantalla: lista_contratos.py

Objetivo: mostrar **solo el suplemento vigente** de cada contrato, nunca el suplemento futuro.

> “Mostrar solo el suplemento máximo (por contrato (vista_contratos).
> Es necesario comprobar y adaptar lista_contratos.py para que tenga en cuenta el caso de un contrato con un suplemento futuro.”

Reglas:

- Si un contrato **no tiene suplemento futuro**:
  - El suplemento vigente será el de mayor `suplemento` cuyo rango de fechas incluya la fecha de hoy.
- Si un contrato **tiene suplemento futuro**:
  - El suplemento futuro tiene `fec_efecto > DATE('now')` y **no es vigente**.
  - El suplemento vigente es el inmediatamente anterior, aquel cuyo rango de fechas incluye la fecha de hoy.

Selección del suplemento vigente (por contrato):

```sql
SELECT *
FROM contratos_identificacion
WHERE ncontrato = ?
  AND DATE('now') BETWEEN fec_efecto AND fec_final
ORDER BY suplemento DESC
LIMIT 1;
```

Con esto se garantiza:

- No se selecciona el suplemento futuro (`fec_efecto > DATE('now')`).
- No se devuelven todos los suplementos anteriores, solo el **vigente** (el que cubre la fecha actual).

El usuario:

- Selecciona un contrato (suplemento vigente).
- Pulsa **Seleccionar contrato** → continúa el proceso.
- Pulsa **Cancelar** → vuelve al menú general.

### 3.3 Pantalla: anular_rehabilitar.py

Controlador que:

1. Recibe `ncontrato`.
2. Determina el **suplemento vigente** (según la lógica anterior).
3. Comprueba si existe **suplemento futuro** para ese contrato.
4. Carga los datos del suplemento vigente.
5. Abre el formulario correspondiente.

---

## 🟦 4. Formulario

> “Todos los campos bloqueados excepto `fec_anulacion`
> Título: ‘Anular / Rehabilitar contrato’”

Se puede implementar de dos formas (A o B). Funcionalmente son equivalentes.

### Opción A: Reutilizar `FormularioContrato` en modo especial

- Todos los campos **bloqueados** excepto `fec_anulacion`.
- Título: **“Anular / Rehabilitar contrato”**.

### Opción B: Crear `formulario_contrato_anulacion.py`

Campos visibles:

- Todos los campos de `contratos_identificacion`.
- **No editables**, excepto:

  - **`fec_anulacion`** → editable.

Botones:

- **Guardar** → guarda la anulación / rehabilitación.
- **Cancelar** → vuelve a la lista de contratos.

---

## 🟦 5. Reglas de validación

### 5.1 Formato de fecha

- Formato: `dd/mm/yyyy`.
- Se permite vacío (NULL).

> “Se permite vacío (NULL)”

### 5.2 Rango permitido

Si la fecha NO es NULL:

- Puede ser **anterior a hoy** (anulación retroactiva permitida).
- **NO puede ser anterior a `fec_inicio` del contrato**.
- **NO puede ser posterior a `fec_final`** (no hay contratos con `fec_final = NULL`).

### 5.3 Rehabilitación

- Si el usuario borra la fecha → `fec_anulacion = NULL`.

> “Si el usuario borra la fecha → `fec_anulacion = NULL`”

---

## 🟦 6. Lógica de guardado

Se implementa en `guardar_anulacion.py` (o dentro del controlador).

### 6.1 Obtener datos del formulario

- `fec_anulacion_str`.

### 6.2 Validar

- Si vacío → `fec_anulacion = NULL`.
- Si no vacío → convertir a formato ISO.

### 6.3 Determinar contexto de suplementos

Para el `ncontrato` seleccionado:

1. **Obtener suplemento vigente** (ya determinado en la pantalla anterior).
2. **Comprobar si existe suplemento futuro**:

```sql
SELECT suplemento, fec_efecto
FROM contratos_identificacion
WHERE ncontrato = ?
  AND fec_efecto > DATE('now')
ORDER BY suplemento DESC
LIMIT 1;
```

- Si devuelve fila → existe suplemento futuro.
- Si no devuelve filas → no existe suplemento futuro.

### 6.4 Actualización en BD

#### Caso A: contrato SIN suplemento futuro

Solo se actualiza el **suplemento vigente**:

```sql
UPDATE contratos_identificacion
SET fec_anulacion = ?
WHERE ncontrato = ?
  AND suplemento = ?;  -- suplemento vigente
```

Parámetros:

- `fec_anulacion_iso` o `NULL`.
- `ncontrato`.
- `suplemento_vigente`.

#### Caso B: contrato CON suplemento futuro

Se actualizan **dos suplementos**:

1. **Suplemento vigente**
   - Se anula con la fecha introducida por el usuario (`fec_anulacion_iso` o `NULL`).

   ```sql
   UPDATE contratos_identificacion
   SET fec_anulacion = ?
   WHERE ncontrato = ?
     AND suplemento = ?;  -- suplemento vigente
   ```

2. **Suplemento futuro**
   - Se anula automáticamente, asignando como `fec_anulacion` su propia `fec_efecto`.

   ```sql
   UPDATE contratos_identificacion
   SET fec_anulacion = fec_efecto
   WHERE ncontrato = ?
     AND suplemento = ?;  -- suplemento futuro
   ```

> “Fecha de anulación del suplemento futuro = efecto suplemento futuro”

### 6.5 Mensaje final

- Si se asigna fecha de anulación → “Contrato anulado correctamente.”
- Si se elimina la fecha (`fec_anulacion = NULL`) → “Contrato rehabilitado correctamente.”

### 6.6 Navegación

- Volver a la lista de contratos tras el guardado.

---

## 🟦 7. Casos especiales

> “Contrato ya anulado
> Contrato no anulado
> Contrato con suplemento futuro”

### 7.1 Contrato ya anulado

- Mostrar la fecha de anulación actual.
- Permitir borrarla (rehabilitar).
- Si existe suplemento futuro:
  - El suplemento futuro también está anulado (con `fec_anulacion = fec_efecto`).
  - Si se rehabilita el contrato (borrando `fec_anulacion` del vigente), se debe definir si el suplemento futuro:
    - Permanece anulado, o
    - Se rehabilita también.
  *(Este comportamiento puede definirse según negocio; si se requiere, se añade aquí.)*

### 7.2 Contrato no anulado

- Campo `fec_anulacion` vacío.
- Permitir introducir fecha.

### 7.3 Contrato con suplemento futuro

- La anulación del contrato afecta:
  - Al **suplemento vigente** (según la fecha introducida).
  - Al **suplemento futuro**, cuya `fec_anulacion` se fija automáticamente a su `fec_efecto`.

---

## 🟦 8. Resumen del DRU

| Etapa      | Acción                                                                 |
|-----------|-------------------------------------------------------------------------|
| Menú      | Contratos → Anular/Rehabilitar                                          |
| Lista     | Mostrar solo el suplemento vigente (no el futuro)                       |
| Formulario| Mostrar datos, solo `fec_anulacion` editable                            |
| Validación| Formato, rango, permitir NULL, sin contratos con `fec_final = NULL`     |
| Guardado  | UPDATE sobre suplemento vigente; si hay futuro, también sobre el futuro |
| Resultado | Anulación o rehabilitación completada                                   |

---

Si quieres, en el siguiente paso podemos bajar aún más al detalle técnico (pseudocódigo del controlador, nombres de variables, manejo de errores) o revisar solo la parte de rehabilitación cuando hay suplemento futuro, que es donde más decisiones de negocio pueden aparecer.
