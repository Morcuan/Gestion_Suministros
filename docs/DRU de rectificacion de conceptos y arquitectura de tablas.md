

# 📘 **DRU — Rectificación de conceptos generales y estructura de tablas (Versión Definitiva)**

---

## 🎯 **1. Objetivo del DRU**

Redefinir los conceptos funcionales y la arquitectura de datos relacionados con la captura y consulta de facturas, garantizando coherencia con la estructura de contratos y eliminando duplicidades innecesarias.

---

## 🧩 **1.1 Contratos**

Los contratos contienen **todos los datos que no varían durante su vigencia**, y que son necesarios para interpretar y totalizar las facturas asociadas.

### Componentes del contrato

1. **Datos de identificación**  
2. **Datos económicos**  
3. **Gastos y cargos normativos**

Estos datos ya se capturan correctamente y **no deben duplicarse en ningún otro módulo**, especialmente en facturas.

### Suplementos del contrato

- La creación de un contrato genera automáticamente el **suplemento 0**.  
- Cualquier modificación posterior (económica, normativa o de datos generales) genera un **nuevo suplemento**, incrementando su número en 1.  
- El suplemento **vigente en la fecha de inicio del periodo de facturación** será el que aplique a cada factura.  
  - Esta asignación será **automática**, sin intervención del usuario.

> Esta regla garantiza coherencia temporal y evita errores de asignación manual.

---

## 🧾 **1.2 Captura de facturas**

El diseño actual de captura de facturas incluye datos que ya están en el contrato, lo que genera redundancia y riesgo de incoherencias.  
Este DRU redefine la factura como un documento que **solo contiene información variable**, propia del periodo facturado.

### La factura debe capturar únicamente:

### **1. Identificación**
- id_contrato (interno, no capturable)
- Número de factura  
- Fecha inicio del periodo  
- Fecha fin del periodo  
- Días facturados (capturado, pero recalculado para comprobación)  
- Fecha de emisión  

### **2. Consumos**
- Consumo punta (kWh)  
- Consumo llano (kWh)  
- Consumo valle (kWh)  
- Excedentes vertidos (kWh)

### **3. Gastos y descuentos**
- Servicios asociados (€)  
- Descuentos en servicios (€)  
- Descuentos por saldos pendientes (€)  
- Batería virtual (€)

### Reglas adicionales

- Los consumos pueden ser **0 o nulos** en cualquier combinación.  
- Los descuentos y saldos se almacenan en **negativo** cuando su valor es > 0.  
- El cálculo de días facturados debe corregirse:  
  - Actualmente se calcula un día de más.  
  - El cálculo debe ajustarse restando 1 día para coincidir con la distribuidora.

---

## 🗄️ **Nueva estructura de almacenamiento**

La captura actual utiliza tres tablas:

1. factura_identificacion  
2. factura_energia  
3. factura_asociados  

Con el nuevo diseño, estas tablas **dejan de ser necesarias**.

### Nueva tabla única: **facturas**

Campos:

1. id_contrato  
2. nfactura  
3. inicio_factura  
4. fin_factura  
5. dias_factura  
6. fec_emision  
7. consumo_punta  
8. consumo_llano  
9. consumo_valle  
10. excedentes  
11. servicios  
12. dcto_servicios  
13. saldos_pendientes  
14. bat_virtual  

### Consideraciones técnicas

- No se requiere id_factura:  
  - No hay más tablas dependientes.  
  - La clave natural será **id_contrato + nfactura**.  
- Se recomienda crear un **índice compuesto** con esos dos campos.

---

## 🖥️ **Pantalla de captura de facturas**

Se reorganiza en tres bloques:

1. **Identificación**  
2. **Energía**  
3. **Gastos y descuentos**

El id_contrato no se muestra ni se captura: se recibe desde el contrato asociado.

La pantalla conservará:

- Botón *Grabar factura*  
- Botón *Otra factura*  
- Botón *Salir*  
- Validaciones actuales adaptadas a los nuevos campos  
- Navegación ya establecida

---

## 🔍 **1.3 Consulta de facturas**

La consulta debe adaptarse a la nueva tabla, pero **sin cambios de lógica**, solo de diseño y origen de datos.

### Estructura visual

1. **Bloque Identificación**  
2. **Bloque Energía**  
3. **Bloque Gastos y descuentos**

El id_contrato no se muestra, pero sí debe aparecer el **número de contrato** en el título de la ventana.

### Tareas

- Rediseñar la pantalla  
- Actualizar campos y etiquetas  
- Mantener navegación actual  

La consulta será la **primera ventana a modificar**, ya que servirá como referencia visual para la nueva captura.

---

## 🧱 **1.4 Consideraciones futuras**

Aunque no se implementan ahora, se deja constancia de:

### Facturas rectificativas o abonos
- No se contemplan por su baja probabilidad.  
- Si en el futuro fueran necesarias, se añadirá un campo tipo_factura.

### Facturas con múltiples periodos
- No se han encontrado casos reales.  
- Si surgieran, se tratarían como **dos facturas independientes**, siguiendo el criterio de la comercializadora.

---

🧩 5. Lo dejamos anotado en el DRU (añadido oficial)

Voy a añadir esta nota al DRU definitivo, porque es importante:
1.X Totalización de factura (nota de diseño)

Aunque la totalización no forma parte de la captura ni de la consulta, la ventana de consulta debe incluir un botón “Totalizar factura” que abra un módulo independiente encargado de:

    cargar la factura

    cargar el suplemento aplicable

    cargar los precios del contrato

    calcular importes

    mostrar desglose y totales

Este módulo será reutilizable en futuras funcionalidades como comparativas y análisis.


# ✅ **Documento finalizado**

Antonio, este DRU ya está listo para convertirse en **la guía oficial del rediseño de facturas**.  
Es coherente, sólido, escalable y perfectamente alineado con la arquitectura del proyecto.

---

## 📌 Siguiente paso propuesto

Ahora que el DRU está cerrado, el orden lógico de implementación sería:

1. **Modificar la consulta de facturas**  
2. Crear la nueva tabla `facturas`  
3. Eliminar las tablas antiguas  
4. Rediseñar la captura  
5. Ajustar validaciones y cálculos  
6. Integrar con contratos y suplementos  

Si te parece bien, empezamos por el punto 1:  
**la ventana de consulta de facturas**, usando este DRU como referencia absoluta.
