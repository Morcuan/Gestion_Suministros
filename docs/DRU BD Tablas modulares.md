
# **DRU — BD Almacen.db (Versión Modularizada)**

Documento de referencia que define la estructura, reglas, relaciones y vistas del módulo **Contratos**, reorganizado en bloques modulares para mejorar mantenibilidad, claridad y escalabilidad.

Incluye:

- Tablas del módulo Contratos (modularizadas)
- Tablas auxiliares
- Tablas futuras (Facturas y Consumos)
- Relaciones globales
- Reglas de validación
- Vista(s) unificadas para uso operativo

---

# **1. Objetivo general del módulo**

Representar contratos energéticos mediante **suplementos**.  
Cada suplemento es una fotografía completa del contrato en un periodo de vigencia.  
La modularización divide la información en **tres bloques funcionales**, cada uno con su propia tabla, todos vinculados por `id_contrato`.

---

# **2. Tablas del módulo Contratos**

La tabla original `contratos` se divide en tres tablas:

- `contratos_identificacion`
- `contratos_energia`
- `contratos_gastos`

Cada suplemento tendrá exactamente **una fila en cada tabla** (relación 1:1).

---

## **2.1. Tabla `contratos_identificacion`**

### Objetivo  
Contener los datos estructurales y de vigencia del contrato y sus suplementos.

### Estructura

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| id_contrato | INTEGER PK AUTOINCREMENT | Sí | Identificador interno del suplemento |
| ncontrato | TEXT | Sí | Número de contrato (no modificable) |
| suplemento | INTEGER | Sí | 0 = inicial, 1..N = modificaciones |
| cod_compania | TEXT FK | Sí | Comercializadora |
| cod_postal | TEXT FK | Sí | Código postal del suministro |
| fec_inicio | TEXT ISO | Sí | Fecha de alta del contrato |
| fec_final | TEXT ISO | Sí | Fecha de caducidad del contrato |
| efec_suple | TEXT ISO | Sí | Inicio de vigencia del suplemento |
| fin_suple | TEXT ISO | Sí | Fin de vigencia del suplemento |
| fec_anulacion | TEXT ISO | No | Fecha de anulación |
| estado | TEXT | Sí | Estado calculado y guardado |

---

## **2.2. Tabla `contratos_energia`**

### Objetivo  
Contener los parámetros energéticos y económicos del suplemento.

### Estructura

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| id_contrato | INTEGER PK FK | Sí | Suplemento asociado |
| ppunta | REAL | Sí | Potencia punta (kW) |
| pv_ppunta | REAL | Sí | Precio potencia punta |
| pvalle | REAL | Sí | Potencia valle (kW) |
| pv_pvalle | REAL | Sí | Precio potencia valle |
| pv_conpunta | REAL | Sí | Precio energía punta |
| pv_conllano | REAL | Sí | Precio energía llano |
| pv_convalle | REAL | Sí | Precio energía valle |
| vertido | BOOLEAN | Sí | Si hay excedentes |
| excedentes | REAL | Sí | Cantidad vertida (kWh) |
| pv_excedent | REAL | Sí | Precio excedente |

---

## **2.3. Tabla `contratos_gastos`**

### Objetivo  
Contener los gastos adicionales e impuestos aplicables al suplemento.

### Estructura

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| id_contrato | INTEGER PK FK | Sí | Suplemento asociado |
| bono_social | REAL | Sí | Importe |
| alq_contador | REAL | Sí | Importe |
| otros_gastos | REAL | Sí | Importe |
| i_electrico | REAL | Sí | % impuesto eléctrico |
| iva | REAL | Sí | % IVA |

---

# **3. Tablas auxiliares**

## **3.1. Tabla `companias`**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| cod_compania | TEXT PK | Código |
| nombre | TEXT | Nombre comercial |

---

## **3.2. Tabla `cpostales`**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| cod_postal | TEXT PK | Código postal |
| poblacion | TEXT | Nombre de la población |

---

# **4. Tablas futuras (en suspenso)**

## **4.1. Tabla `facturas`**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_factura | INTEGER PK |  |
| id_contrato | INTEGER FK | Suplemento asociado |
| fecha_factura | TEXT ISO | Fecha |
| periodo_inicio | TEXT ISO | Inicio periodo facturado |
| periodo_fin | TEXT ISO | Fin periodo facturado |
| importe_total | REAL | Total factura |

---

## **4.2. Tabla `consumos`**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_consumo | INTEGER PK |  |
| id_factura | INTEGER FK | Factura asociada |
| con_punta | REAL | kWh |
| con_llano | REAL | kWh |
| con_valle | REAL | kWh |

---

# **5. Reglas de validación**

## Fechas
- Entrada: dd/mm/yyyy  
- Guardado: yyyy-mm-dd  
- fec_inicio y fec_final son inamovibles en todos los suplementos.  
- Suplemento 0:
  - efec_suple = fec_inicio  
  - fin_suple = fec_final  
- Suplementos >0:
  - efec_suple = día siguiente al fin_suple anterior  
  - fin_suple = fec_final del contrato  
- fec_anulacion opcional  
- Si existe fec_anulacion:
  - hoy < fec_anulacion → Activo  
  - hoy ≥ fec_anulacion → Anulado  

---

## Estado del contrato
Aplicado al suplemento actual:

- Si hoy ∈ [efec_suple, fin_suple] → Activo  
- Si hoy < efec_suple → Futuro  
- Si fin_suple < hoy → Caducado  
- Si fec_anulacion existe:
  - hoy < fec_anulacion → Activo  
  - hoy ≥ fec_anulacion → Anulado  

---

## Potencias
- Valores > 0 y < 10  
- Punta y valle no pueden ser ambos 0  
- Precios potencia < 1  

---

## Precios energía
- Valores > 0  
- Precios < 1  

---

## Excedentes
- Si vertido = False → excedentes = 0 y pv_excedent = 0  
- excedentes < 1000  
- pv_excedent < 1  

---

## Gastos
- Todos positivos  
- i_electrico e iva en %  

---

# **6. Relaciones globales**

```
companias (1) ─── (N) contratos_identificacion
cpostales (1) ─── (N) contratos_identificacion

contratos_identificacion (1) ─── (1) contratos_energia
contratos_identificacion (1) ─── (1) contratos_gastos

contratos_identificacion (1) ─── (N) facturas
facturas (1) ─── (1) consumos
```

---

# **7. Vista unificada del contrato**

## Nombre sugerido  
`vw_contratos_completo`

## Contenido  
Unión de:

- contratos_identificacion  
- contratos_energia  
- contratos_gastos  
- companias  
- cpostales  

## Objetivo  
Proveer una vista operativa completa para:

- consultas  
- ventanas de detalle  
- informes  
- exportaciones  

---

# **8. Notas de implementación**

- La modularización no altera la lógica de suplementos.  
- El módulo Contratos deberá adaptarse para leer/escribir en las tres tablas.  
- La vista unificada permitirá mantener la simplicidad en las consultas.  
- La migración desde la tabla antigua requerirá un script de separación por bloques.  

---

Documento completado.  
Cuando quieras, pasamos a la siguiente fase: **definir los esquemas SQL y las vistas**, o si lo prefieres, revisamos este DRU para pulirlo aún más.
