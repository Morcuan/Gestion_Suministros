

# 📘 **DRU — Módulo Nuevo Contrato (versión revisada y consolidada)**

Este documento define el comportamiento, estructura y validaciones del módulo **Nuevo Contrato**, encargado de capturar un contrato energético base (suplemento 0) en la base de datos **almacen.db**.
El módulo registra los datos en las tres tablas modulares:

- `contratos_identificacion`
- `contratos_energia`
- `contratos_gastos`

---

# 🎯 **Objetivo del módulo**

Registrar un contrato nuevo desde cero, en una única operación, con:

- Validaciones defensivas
- Conversión de fechas
- Normalización de campos
- Inserción transaccional en las tres tablas
- Cálculo automático del estado
- Confirmación visual de éxito

El contrato creado es siempre **suplemento 0** y no genera suplementos.

---

# 🧱 **Estructura funcional**

El módulo consta de:

- Formulario único reutilizable (captura, consulta, modificación)
- Tres bloques de captura: Identificación, Energía, Gastos
- Validación completa antes de habilitar el botón Guardar
- Conversión de fechas `dd/mm/yyyy` → ISO `yyyy-mm-dd`
- Inserción transaccional en las tres tablas con el mismo `id_contrato`
- Cálculo automático del campo `estado`
- Cierre de la ventana tras confirmar el mensaje de éxito

---

# 🧩 **Bloques de captura**

## 🔹 **Bloque Identificación**

| Campo | Tipo | Reglas |
|-------|------|--------|
| **ncontrato** | TEXT | Introducido por el usuario. Normalización: mayúsculas, sin espacios. Debe ser único en BD. |
| **suplemento** | INTEGER | Fijo: 0 |
| **cod_compania** | TEXT | Selección desde combobox (tabla `companias`) |
| **cod_postal** | TEXT | 5 dígitos. Debe existir en `cpostales`. Si no existe → ventana auxiliar para capturar población e insertarlo. |
| **fec_inicio** | TEXT | Entrada dd/mm/yyyy → ISO |
| **fec_final** | TEXT | Entrada dd/mm/yyyy → ISO |
| **fec_anulacion** | TEXT | Null en contrato nuevo |
| **estado** | TEXT | Calculado automáticamente |
| **efec_suple** | TEXT | Igual a fec_inicio |
| **fin_suple** | TEXT | Igual a fec_final |

---

## 🔹 **Bloque Energía**

| Campo | Tipo | Reglas |
|-------|------|--------|
| ppunta / pvalle | REAL | > 0 y < 10. No ambos 0. Acepta coma o punto → convertir a punto. |
| pv_ppunta / pv_pvalle | REAL | < 1 |
| pv_conpunta / pv_conllano / pv_convalle | REAL | < 1 |
| vertido | BOOLEAN | True/False |
| excedentes | REAL | Si vertido = False → 0 |
| pv_excedent | REAL | Si vertido = False → 0 |

---

## 🔹 **Bloque Gastos**

| Campo | Tipo | Reglas |
|-------|------|--------|
| bono_social / alq_contador / otros_gastos | REAL | ≥ 0 |
| i_electrico | REAL | Porcentaje con decimales (ej. 5,12). Acepta coma o punto → convertir a punto. |
| iva | REAL | Porcentaje entero (ej. 21). |

---

# 🧮 **Reglas de validación**

### **Fechas**
- Entrada obligatoria en formato `dd/mm/yyyy`
- Conversión a ISO antes de guardar
- `fec_inicio < fec_final`
- `efec_suple = fec_inicio`
- `fin_suple = fec_final`

### **Estado**
- Si hay anulación:
  - hoy < fec_anulacion → **Activo**
  - hoy ≥ fec_anulacion → **Anulado**
- Si no hay anulación:
  - hoy ∈ [efec_suple, fin_suple] → **Activo**
  - hoy < efec_suple → **Futuro**
  - hoy > fin_suple → **Caducado**

### **Identificación**
- `ncontrato` normalizado (mayúsculas, sin espacios)
- Debe ser único en BD
- `cod_postal` debe existir en tabla `cpostales`
  - Si no existe → ventana auxiliar para capturar población e insertarlo

### **Energía**
- Potencias > 0 y < 10
- No ambas 0
- Precios variables < 1
- Si vertido = False → excedentes y pv_excedent = 0

### **Gastos**
- Todos ≥ 0
- `i_electrico` admite decimales
- `iva` es porcentaje entero

### **Botón Guardar**
- **Deshabilitado** hasta que todos los campos obligatorios estén completos y validados

---

# 🔗 **Relaciones y dependencias**

- `cod_compania` → tabla `companias`
- `cod_postal` → tabla `cpostales`
- `id_contrato` generado automáticamente
- Inserción transaccional:
  - Si falla una tabla → rollback completo
  - Se informa al usuario

---

# 🖥️ **Interfaz prevista**

- Formulario único reutilizable
- Tres bloques visuales: Identificación, Energía, Gastos
- Botón **Cancelar** → cierra sin guardar
- Botón **Guardar contrato** → habilitado solo tras validación
- Mensaje de éxito → cierra la ventana

---

# 🧪 **Pruebas previstas**

- Captura completa válida
- Vertido = False → excedentes = 0
- Fecha de anulación futura
- Fecha final anterior → error
- Potencias punta y valle = 0 → error
- `ncontrato` duplicado → error
- Inserción correcta en las tres tablas
- Verificación en vista `vw_contratos_completo`
- Alta automática de código postal inexistente

---

# 📝 **Notas adicionales**

- El suplemento 0 no se modifica desde este módulo
- No genera suplementos
- No se implementa log interno (no necesario para uso particular)

---
