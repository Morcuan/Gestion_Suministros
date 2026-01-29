
# 📘 **DRU — Módulo Nuevo Contrato**

Este documento define el comportamiento, estructura y validaciones del módulo **Nuevo Contrato**, encargado de capturar un nuevo contrato energético en la base de datos **almacen.db**.
El contrato se registra como **suplemento 0**, con todos sus datos distribuidos en las tres tablas modulares:

- `contratos_identificacion`
- `contratos_energia`
- `contratos_gastos`

---

## 🎯 **Objetivo del módulo**

Permitir al usuario registrar un nuevo contrato desde cero, capturando todos los datos necesarios en una única operación, con validaciones defensivas y conversión de fechas.
El contrato se guarda como suplemento 0, y se considera el contrato base.

---

## 🧱 **Estructura funcional**

El módulo consta de:

- Formulario principal con campos agrupados por bloques:
  - Identificación
  - Energía
  - Gastos
- Validación de todos los campos antes de guardar
- Conversión de fechas de entrada (`dd/mm/yyyy`) a formato ISO (`yyyy-mm-dd`)
- Inserción en las tres tablas con el mismo `id_contrato`
- Cálculo automático del campo `estado`
- Confirmación visual de guardado exitoso

---

## 🧩 **Bloques de captura**

### 🔹 Bloque Identificación

| Campo | Tipo | Reglas |
|-------|------|--------|
| ncontrato | TEXT | No modificable una vez guardado |
| cod_compania | TEXT | Selección desde lista (tabla companias) |
| cod_postal | TEXT | Selección desde lista (tabla cpostales) |
| fec_inicio | TEXT | Entrada dd/mm/yyyy → ISO |
| fec_final | TEXT | Entrada dd/mm/yyyy → ISO |
| fec_anulacion | TEXT | Opcional |
| estado | TEXT | Calculado automáticamente |
| suplemento | INTEGER | Fijo: 0 |
| efec_suple | TEXT | Igual a fec_inicio |
| fin_suple | TEXT | Igual a fec_final |

---

### 🔹 Bloque Energía

| Campo | Tipo | Reglas |
|-------|------|--------|
| ppunta / pvalle | REAL | > 0 y < 10, no ambos 0 |
| pv_ppunta / pv_pvalle | REAL | < 1 |
| pv_conpunta / pv_conllano / pv_convalle | REAL | < 1 |
| vertido | BOOLEAN | True/False |
| excedentes | REAL | Si vertido = False → 0 |
| pv_excedent | REAL | Si vertido = False → 0 |

---

### 🔹 Bloque Gastos

| Campo | Tipo | Reglas |
|-------|------|--------|
| bono_social / alq_contador / otros_gastos | REAL | ≥ 0 |
| i_electrico / iva | REAL | % ≥ 0 |

---

## 🧮 **Reglas de validación**

- Todas las fechas deben introducirse en formato `dd/mm/yyyy`
- Se convierten a ISO antes de guardar
- `fec_inicio` y `fec_final` deben ser coherentes (inicio < final)
- `efec_suple = fec_inicio`, `fin_suple = fec_final`
- Si `fec_anulacion` existe:
  - hoy < fec_anulacion → estado = Activo
  - hoy ≥ fec_anulacion → estado = Anulado
- Si no hay anulación:
  - hoy ∈ [efec_suple, fin_suple] → Activo
  - hoy < efec_suple → Futuro
  - hoy > fin_suple → Caducado

---

## 🔗 **Relaciones y dependencias**

- cod_compania → companias
- cod_postal → cpostales
- id_contrato generado automáticamente
- Se usa el mismo id_contrato en las tres tablas

---

## 🖥️ **Interfaz prevista**

- Tres bloques visuales (Identificación, Energía, Gastos)
- Botón “Guardar contrato”
- Validación antes de guardar
- Mensaje de éxito
- Posibilidad de dejar la ventana abierta para capturar factura o consumo

---

## 🧪 **Pruebas previstas**

- Captura completa con todos los campos válidos
- Captura con vertido = False → excedentes = 0
- Captura con fecha de anulación futura
- Captura con fecha final anterior → error
- Captura con potencia punta y valle = 0 → error
- Confirmación de inserción en las tres tablas
- Verificación en vista `vw_contratos_completo`

---

## 📝 **Notas adicionales**

- El campo `ncontrato` debe ser único
- El suplemento 0 no puede modificarse desde este módulo
- La lógica de modificación irá en otro módulo
- Este módulo no genera suplementos, solo contratos base

---

Documento listo para revisión.
Cuando lo leas, puedes marcar correcciones, añadir campos, ajustar reglas o proponer mejoras.
Después lo discutimos y lo cerramos juntos.
