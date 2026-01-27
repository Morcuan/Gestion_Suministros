
# 📘 **DRU — Tabla `contratos` (Diseño, Reglas y Uso)**

## 1. **Objetivo de la tabla**
La tabla `contratos` almacena la información principal de cada contrato energético gestionado por el sistema.  
Es la entidad raíz del módulo y sirve como punto de entrada para facturas y consumos.

Su diseño debe permitir:

- Identificar un contrato de forma única.
- Registrar datos de la compañía comercializadora enlazando con la tabla compañias.
- Registrar el código postal del lugar de suministro enlazando con la tabla cpostales.
- Registrar fechas clave del contrato.
- Registrar potencias contratadas por periodo.
- Mantener trazabilidad temporal (altas, bajas, modificaciones).


## 2. **Estructura de campos**

| Campo         | Tipo                     | Obligatorio | Descripción / Regla                                                      |
|---------------|--------------------------|-------------|--------------------------------------------------------------------------|
| `id_contrato` | INTEGER PK AUTOINCREMENT | Sí          | No es el numero de contrato. Solo para indices y relaciones               |
| `ncontrato`   | TEXT                     | Sí          | Numero de contrato                                                       |
| `suplemento`  | INTEGER                  | Sí          | Numero de suplemento. 0 1er. Registro                                    |
| `id_compania` | INTEGER FK               | Sí          | Referencia a tabla `companias`                                           |
| `id_postal   `| INTEGER FK               | Sí          | Referencia a tabla `cpostales`                                           |
| `fec_inicio`  | TEXT (ISO)               | Sí          | Fecha de alta del contrato. Entrada dd/mm/yyyy → guardado yyyy-mm-dd     |
| `fec_final`   | TEXT (ISO)               | Sí          | Fecha de baja del contrato. Entrada dd/mm/yyyy → guardado yyyy-mm-dd     |
| `efec_suple`  | TEXT (ISO)               | Sí          | Fecha de efecto del suplemento. Entrada dd/mm/yyyy → guardato yyyy-mm-dd |
| `fin_suple`   | TEXT (ISO)               | Sí          | Fecha de fin de efecto del suplemento. Entrada/guardado = a anteriores   |
| `fec_anulado` | TEXT (ISO)               | No          | Fecha de anulación del contrato. Campo nulo si no está anulado           |
| `ppunta`      | REAL                     | Sí          | Potencia contratada en periodo punta, Unidad Kw/h  <10                   |
| `pv_ppunta`   | REAL                     | Sí          | Precio Kw/h. Unidad €.                                                   |
| `pvalle`      | REAL                     | Sí          | Potencia contratada en periodo valle, Unidad Kw/h. <10                   |
| `pv_pvalle`   | REAL                     | Sí          | Precio Kw/h. Unidad €.                                                   |
| `con_punta`   | REAL                     | Sí          | Consumo en periodo punta. Unidad Kw/h.                                   |
| `pv_conpunta` | REAL                     | Sí          | Precio Kw/h en periodo punta. Unidad €.                                  |
| `con_llano`   | REAL                     | Sí          | Consumo en periodo llano. Unidad Kw/h.                                   |
| `pv_conllano` | REAL                     | Sí          | Precio Kw/h en periodo llano. Unidad €.                                  |
| `con_valle`   | REAL                     | Sí          | Consumo en periodo valle. Unidad Kw/h.                                   |
| `pv_convalle` | REAL                     | Sí          | Precio Kw/h en periodo valle. Unidad €.                                  |
| `vertido`     | BOLEAN                   | Sí          | Si/No                                                                    |
| `excedentes`  | REAL                     | Sí          | Excedentes vertidos a la red. Si excedentes = No entonces 0. Unidad Kw/h.|
| `pv_excedent` | REAL                     | Sí          | Precio del Kw/h vertido a la red. Si excedentes = No entonces 0. Und = € |
| `bono_social` | REAL                     | Sí          | Imp. Bono Social.                                                        |
| `alq_contador`| REAL                     | Sí          | Imp. Alquiler contador.                                                  |
| `otros_gastos`| REAL                     | Sí          | Imp. Otros gastos del contrato                                           |
| `i_electrico` | REAL                     | Sí          | Impuesto electrico. Unidad %                                             |
| `iva`         | REAL                     | Sí          | IVA. Unidad %                                                            |
| `estado`      | TEXT                     | Sí          | Estado del contrato                                                      |
|-----------------------------------------------------------------------------------------------------------------------------------|


## 3. **Reglas de validación**

### ✔ Fechas
- Entrada obligatoria en formato `dd/mm/yyyy`  
- Conversión automática a ISO `yyyy-mm-dd` antes de guardar
- En la creacion del contrato suplemento = 0
- `fec_inicio` y `fec_final`son inamovibles en todos los suplementos
- Si suplemento = 0 `fec_final` > `fec_inicio
- Si suplemento = 0 `efec_suple` =`fec_inicio`, `fin_suple` = `fec_final`
- Si suplemento = 1 `fec_final` de suplemento 0 = `efec_suple`-1 `fin_suple` = `fec_final`
- Los suplementos sucesivos se comportan como el 1 respecto al 0.

### ✔ Estado del contrato
- El estado del contrato se refiere siempre al maximo numero de suplemento existente.
- Calculado para cada suplemento insertado en la tabla en funcion de la fecha del sistema (o consulta)
- Si sysdate >= `efec_suple` y <= `fin_suple` contrato "Activo"
- Si sysdate < `efec_suple` contrato "Futuro"
- Si `fec_anulado` not null contrato "Anulado" salvo que sysdate < `fec_anulado` en cuyo caso es "Activo"
- Si `fin_suple` < sysdate y `fec_anulado` = null entonces contrato = "Caducado"
- No se estima necesario con la Estructura contrato/suplemento el estado "Modificado"

### ✔ Potencias
- Valores numéricos positivos siempre < 10
- Permitir decimales
- No permitir 0 en los dos periodos simultáneamente

### ✔ Consumos
- Valores numéricos positivos < 1000 en todos los periodos
- Permitir decimales
- Se permite 0 en cualquier periodo pero no en los tres simultáneamente

### ✔ Excedentes
- Si `vertido`(Bolean) = False no se admiten valores en excedentes y en pv_excedent
- `excedentes` < 1000
- `pv_excedent` < 1

### ✔ Estado
Valores permitidos:
- `Activo`
- `Anulado`
- `Futuro`
- `Caducado`


## 4. **Relaciones previstas**

### 🔗 `contratos` → `companias`
- FK: `id_compania`
- Muestra nombre de compañía en consultas y detalles

### 🔗 `contratos` → `poblaciones`
- FK: `id_poblacion`
- Muestra población en consultas y detalles

### 🔗 `contratos` → `facturas`
- Relación 1:N
- Un contrato puede tener muchas facturas

### 🔗 `contratos` → `consumos`
- Los consumos se capturarán junto con las facturas y se almacenaran en la tabla facturas en cada factura 


## 5. **Reglas de negocio**

- Un contrato **activo** no puede tener `fec_anulado`
- Un contrato **de baja** debe tener `fec_anulado`
- Un contrato está **Activo** hasta que sysdate = `fec_anulado`
- Un contrato está **Caducado** cuando no está anulado y fin_suple < sysdate
- No se permite modificar `ncontrato`
- No se permite modificar `suplemento`
- Las potencias deben mantenerse en orden: punta → llano


---

## 6. **Notas de implementación**

- La tabla debe crearse en `db_init.py` con SQL limpio y comentado  
- La ventana de captura debe validar antes de guardar
- La ventana de consulta debe mostrar:
  - compañía (JOIN)
  - población (JOIN)
  - estado visual (color opcional)
- La ventana de detalles debe mostrar:
  - valores agupados por conceptos (datos, potencias, consumos, excedentes, gastos...)
  - potencias ordenadas
  - fechas en formato humano, siendo el humano español de españa
  

## 7. **Pendientes para la siguiente fase**

- Crear tabla `facturas`  
- Definir índices recomendados  
- Preparar DRU de facturas
- Diseñar la ventana de captura de contratos
- Diseñar la ventana de consulta con subformularios (tu idea tipo Access) con contratos / facturas

---

# ⭐ Observaciones

- El diseño, relaciones, indices y logica de estados puede cambiar mientras estamos en desarrollo de la captura del contrato.
