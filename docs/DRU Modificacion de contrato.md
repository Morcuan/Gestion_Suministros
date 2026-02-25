Perfecto, Antonio. Ya tengo **los dos TXT completos**, con todos los módulos que necesitaba para trabajar con precisión quirúrgica sobre tu proyecto *Gestión Suministros 2.0*.  
Ahora sí puedo darte **el DRU corregido**, **la guía técnica final**, y además **decirte exactamente qué piezas de código hay que crear y dónde encajan**, sin inventar nada y respetando tu arquitectura actual.

Voy por partes, bien ordenado.

---

# 📘 **DRU – Modificación de Contrato (versión final y corregida)**

A continuación te entrego el DRU ya depurado, coherente con tu base de datos real, tus vistas, tus módulos y tu lógica de facturación.

---

## **1. Definición**

- Una modificación de contrato consiste en la variación de uno o más **valores económicos** del contrato.
- Estas variaciones generan un **nuevo suplemento**, que será la versión vigente del contrato a partir de la fecha de efecto indicada por el usuario.
- El número de contrato es invariable; el suplemento es un número correlativo que comienza en 0 (creación del contrato) y aumenta en 1 por cada modificación económica.
- **Si no cambia ningún dato económico**, no procede crear suplemento.
- Los datos no económicos pueden actualizarse directamente en el suplemento vigente sin generar uno nuevo.

---

## **2. Qué se puede modificar**

### **No modificables por el usuario**
- id_contrato  
- ncontrato  
- suplemento  
- fec_inicio  
- fec_final  
- fec_anulacion  
- estado  
- fin_suple (fin de efecto del suplemento)

### **Modificables**
- efec_suple (fecha de efecto del suplemento nuevo)  
- Todos los valores económicos de:
  - contratos_energia  
  - contratos_gastos  
- Valores administrativos no económicos (comentarios, notas, etc.)

---

## **3. Flujo de trabajo**

1. Menú: **Contratos → Modificación**
2. Lista de contratos (vista_contratos)
3. Selección de contrato → botón “Modificación”
4. Apertura de ventana de modificación (form_modificacion.py)
5. Carga del suplemento vigente (vista_contratos, suplemento más alto)
6. Usuario modifica datos
7. Validaciones
8. Si hay cambios económicos → crear suplemento nuevo
9. Si solo hay cambios administrativos → actualizar suplemento vigente
10. Si hay suplemento nuevo → marcar facturas afectadas para recálculo

---

## **4. Lógica de creación del suplemento nuevo**

### **4.1 Datos base**
- Se parte del suplemento vigente (suplemento N).
- El nuevo suplemento será N+1.
- efec_suple lo aporta el usuario.
- fin_suple del suplemento anterior se ajusta automáticamente.

### **4.2 Fechas**
- fec_inicio y fec_final del contrato **no cambian nunca**.
- Suplemento anterior:
  - fin_suple = efec_suple_nuevo − 1 día
  - estado = “Modificado”
- Suplemento nuevo:
  - efec_suple = efec_suple_nuevo
  - fin_suple = fec_final del contrato
  - estado = “Activo”

---

## **5. Inserciones necesarias**

Un suplemento nuevo implica **tres inserts**:

1. contratos_identificacion  
2. contratos_energia  
3. contratos_gastos  

Todos replican los valores del suplemento anterior excepto los modificados.

---

## **6. Actualización del suplemento anterior**

Solo afecta a contratos_identificacion:

```sql
UPDATE contratos_identificacion
SET fin_suple = ?, estado = 'Modificado'
WHERE id_contrato = ? AND suplemento = ?;
```

---

## **7. Facturas afectadas**

Una factura debe recalcularse si:

1. Está calculada  
2. Su **inicio_factura** está dentro del rango del nuevo suplemento:

\[
efec\_suple\_nuevo \le inicio\_factura \le fec\_final\_contrato
\]

Estas facturas se marcan con:

```
recalcular = 1
```

No se recalculan automáticamente.

---

# 📗 **Guía técnica final (lista para desarrollo)**

Esta guía está adaptada **exactamente** a tu estructura real de BD, vistas y módulos.

---

## **1. SELECT inicial del contrato**

Usar vista_contratos:

```sql
SELECT *
FROM vista_contratos
WHERE ncontrato = ?
ORDER BY suplemento DESC
LIMIT 1;
```

---

## **2. Detección de cambios**

Comparar suplemento vigente vs datos modificados:

- Si no hay cambios económicos → actualizar suplemento vigente  
- Si hay cambios económicos → crear suplemento nuevo  

---

## **3. Validaciones**

- Fechas en entrada: dd/mm/yyyy  
- Conversión a ISO antes de guardar  
- efec_suple_nuevo debe cumplir:
  - ≥ fec_inicio  
  - ≤ fec_final  
  - > efec_suple_vigente  

---

## **4. Inserción del suplemento nuevo**

Tres inserts:

```sql
INSERT INTO contratos_identificacion (...)
INSERT INTO contratos_energia (...)
INSERT INTO contratos_gastos (...)
```

---

## **5. Actualización del suplemento anterior**

```sql
UPDATE contratos_identificacion
SET fin_suple = ?, estado = 'Modificado'
WHERE id_contrato = ? AND suplemento = ?;
```

---

## **6. Marcado de facturas afectadas**

```sql
UPDATE facturas
SET recalcular = 1
WHERE id_contrato = ?
  AND inicio_factura >= ?
  AND inicio_factura <= ?
  AND nfactura IN (
      SELECT nfactura
      FROM factura_calculos
  );
```

---

# 🧩 **Qué módulos hay que crear o modificar ahora**

Con todo lo que me has pasado, ya puedo decirte exactamente qué piezas faltan y dónde encajan.

---

## 🟦 **1. Crear: form_modificacion.py**
Este módulo no existe y es imprescindible.

Debe basarse en form_contrato.py, pero:

- precarga datos desde vista_contratos  
- deshabilita campos no modificables  
- permite editar efec_suple  
- detecta cambios económicos  
- ejecuta la lógica de creación de suplemento  

Lo puedo generar yo entero.

---

## 🟦 **2. Crear: db.py**
Tampoco existe.

Debe contener:

- funciones de lectura de contrato vigente  
- funciones de inserción de suplemento nuevo  
- funciones de actualización del suplemento anterior  
- funciones para marcar facturas afectadas  

También lo puedo generar completo.

---

## 🟦 **3. Modificar: calculo.py**
No requiere cambios para suplementos, pero sí para:

- detectar facturas marcadas como recalcular  
- permitir recalcularlas desde un módulo de utilidades  

---

## 🟦 **4. Crear: modulo_recalculo.py**
Un módulo nuevo que:

- liste facturas con recalcular = 1  
- permita recalcularlas en lote  
- actualice factura_calculos  
- limpie el flag recalcular  

---

## 🟦 **5. Modificar: consulta_factura.py y form_factura.py**
Solo para:

- mostrar si una factura está pendiente de recálculo  
- impedir análisis si no está actualizada  

---

# 🟩 ¿Qué hago ahora?

Puedo generar **todo el código real** de:

- form_modificacion.py  
- db.py  
- modulo_recalculo.py  

Y además:

- integrar la lógica en tu menú  
- dejarlo todo funcionando con tu BD actual  

Solo dime **por cuál módulo quieres que empiece** y lo escribo ya mismo.
