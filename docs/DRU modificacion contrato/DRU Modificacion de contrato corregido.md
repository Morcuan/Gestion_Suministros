

---

# 📘 **DRU DEFINITIVO – MODIFICACIÓN DE CONTRATOS**
**Proyecto:** Gestión_Suministros
**Módulo:** Contratos
**Proceso:** Modificación de contrato existente
**Versión:** 1.4 (definitiva)

---

# 1. 🎯 Objetivo del proceso

El objetivo de este proceso es permitir la modificación de las condiciones administrativas y/o económicas vigentes de un contrato. Estas modificaciones **no alteran el registro original**, sino que generan un **nuevo suplemento**, con:

- Número de suplemento incrementado
- Nueva fecha de efecto
- Ajuste automático del suplemento anterior

> “Estas nuevas condiciones generan un nuevo registro en la BD que se diferencia del anterior por el numero de suplemento que se incrementa secuencialmente…”
> “La modificacion de un contrato no genera la actualizacion del registro origen del contrato, excepto en el campo… fecha de fin de efecto del suplemento anterior.”

**Premisas clave:**

- **No se aceptan suplementos retroactivos.**
- **La fecha de anulación no se gestiona aquí** (módulo independiente).
- **Todos los contratos**, incluso anulados, pueden modificarse.
- La modificación puede afectar a facturas posteriores → se marcan para recalcular.

---

# 2. 🧭 Flujo general del proceso

## 2.1. Entrada al módulo

Ruta:
**Menú → Contratos → Modificar contrato**

Se abre `lista_contratos.py` mostrando:

- ncontrato
- compañía
- código postal
- efec_suple
- fin_suple
- fec_anulacion
- estado

Filtros:

- Todos los contratos
- Solo último suplemento

Botones:

- **Buscar** → vuelve al menú
- **Elegir contrato** → activo solo con selección

---

## 2.2. Selección del contrato

Al seleccionar un contrato:

- Se obtiene `ncontrato`
- Se consulta `vista_contratos`
- Se abre `formulario_contrato.py` en modo edición
- Se cargan todos los campos del contrato y su suplemento actual

---

## 2.3. Estado inicial del formulario

### Campos NO editables

- Número de contrato
- Fecha de inicio
- Fecha final
- Fin suplemento
- **Fecha de anulación (si existe o no existe)**

### Campos editables

- Todos los demás campos del formulario

---

# 3. 🧪 Validaciones del proceso

## 3.1. Validaciones específicas

- No se permite cambiar:
  - Número de contrato
  - Fecha de inicio
  - Fecha final
  - Fecha de anulación
- **No se aceptan fechas de efecto retroactivas**
  - La fecha de efecto del nuevo suplemento debe ser ≥ fecha actual
- Cambio de CP:
  - Validación igual que en alta
  - Se permite crear CP nuevo
- Cambio de compañía:
  - Permitido sin restricciones

---

## 3.2. Validaciones heredadas del alta

- Fechas en formato `dd/mm/yyyy`
- Conversión a ISO antes de guardar
- Validación de CP
- Creación de CP si no existe
- Validación numérica
- **Campos económicos no pueden quedar vacíos**
- Regla de vertido:
  - Si `vertido = N` → `pv_excedent = 0`

---

# 4. 💾 Guardado de la modificación

Al pulsar **Guardar**:

1. Se recuperan todos los datos del formulario
2. Se detectan cambios:
   - Si no hay → mensaje y no se guarda
3. Se validan todos los campos
4. Se convierten fechas a ISO
5. Se aplica regla de vertido
6. **Se buscan facturas afectadas**
7. Se actualiza suplemento anterior
8. Se inserta nuevo suplemento
9. Se muestra mensaje de éxito
10. Se vuelve a la lista

---

## 4.1. Suplemento anterior

- `fin_efecto = fecha_efecto_nuevo_suplemento − 1 día`
- No se modifican otros campos

---

## 4.2. Nuevo suplemento

- `num_suplemento_nuevo = num_suplemento_anterior + 1`
- Se insertan registros en:
  - `contratos_identificacion`
  - `contratos_energia`
  - `contratos_gastos`

---

# 5. 🔐 Reglas de negocio adicionales

## 5.1. Fecha final

> “fecha_final = fecha_inicio + 10 años − 1 día”

No se recalcula en modificación.

---

## 5.2. Suplemento

- Efecto suplemento = el indicado en el formulario
- Fin suplemento = fecha final del contrato
- No se recalculan en modificación

---

## 5.3. Integridad

- Los campos no editables no aceptan foco ni cambios

---

# 6. 🖥️ Interfaz

## 6.1. Botones

- **Guardar** → valida, marca facturas, crea suplemento
- **Volver** → regresa a lista
- **Cancelar** → cierra sin guardar

---

## 6.2. Limpieza

Tras guardar:

- Se limpia formulario
- Se cierra ventana
- Se vuelve a lista

---

# 7. 📌 Mensajes al usuario

- **Guardado correcto**
  > “Suplemento guardado correctamente.”

- **Error de validación**
  > “El campo X no es válido.”

- **CP no encontrado**
  > “El código postal no existe. ¿Desea crearlo?”

- **Fecha de efecto retroactiva**
  > “La fecha de efecto no puede ser anterior a la fecha actual.”

- **Facturas afectadas**
  > “Existen facturas para recalcular.”

---

# 8. 🧱 Estructura técnica

- Ventanas:
  - `listaContratos`
  - `ModificarContrato`
  - `FormularioContrato`
- Controladores:
  - `lista_contratos.py`
  - `modificar_contrato.py`
- BD:
  - `actualizar_contrato_identificacion`
  - `actualizar_contrato_energia`
  - `actualizar_contrato_gastos`

---

# 9. 🚩 Dependencias con facturas

- Se buscan facturas con `periodo_inicio >= fecha_efecto_nuevo_suplemento`
- Para cada una:
  - `recalcular = 1`
  - `suplemento = num_suplemento_nuevo`
- Si existen → mensaje al usuario
- No se recalculan automáticamente
- Facturas anteriores → no se tocan

---

# 10. 🧩 Flujo resumido

1. Abrir módulo
2. Seleccionar contrato
3. Cargar formulario
4. Modificar campos permitidos
5. Validar
6. Buscar facturas afectadas
7. Crear suplemento
8. Mensaje de éxito
9. Volver a lista

---

---

