

# **DRU – Módulo de Facturas (versión inicial)**

## **1. Naturaleza del módulo**
- Una factura **pertenece siempre a un único contrato**.  
- No existe factura sin contrato asociado.
- La captura de una factura **incluye también la captura de sus consumos** (punta, llano, valle), en el mismo acto.
- La tabla `facturas` **incluye los campos de consumos**, evitando tablas intermedias y simplificando consultas.
- La factura es un elemento **de alta frecuencia**: se espera que haya muchas por contrato.

---

## **2. Flujo funcional**
### **2.1. Entrada al módulo**
- Desde el menú principal → “Nueva factura”.
- Desde la ventana de contratos → botón “Añadir factura a este contrato”.

### **2.2. Selección del contrato**
- Si se entra desde el menú principal:  
  → Se abre selector de contrato (lista o buscador).
- Si se entra desde un contrato abierto:  
  → El contrato ya viene fijado.

### **2.3. Captura de datos de la factura**
Campos obligatorios:
- **ID del contrato** (FK)
- **Fecha de factura**  
  - Entrada: `dd/mm/yyyy`  
  - Validación estricta  
  - Conversión a ISO antes de guardar
- **Periodo facturado**  
  - Fecha inicio (dd/mm/yyyy → ISO)  
  - Fecha fin (dd/mm/yyyy → ISO)
- **Importe total**  
  - Numérico, validación de coma/punto
- **Consumos**  
  - Punta (kWh)  
  - Llano (kWh)  
  - Valle (kWh)
- **Potencia contratada** (si procede)
- **Otros importes** (impuestos, alquiler contador, etc.)  
  → Campos opcionales pero previstos en la tabla.

### **2.4. Validaciones**
- Ningún campo obligatorio vacío.
- Fechas válidas y coherentes (inicio ≤ fin).
- Consumos numéricos ≥ 0.
- Importe total ≥ 0.
- El contrato existe y está activo.

### **2.5. Guardado**
- Inserción en tabla `facturas`.
- La ventana **no se cierra automáticamente** tras guardar (tu preferencia actual).
- Tras guardar:
  - Opción de **capturar otra factura del mismo contrato**.
  - Opción de **volver al menú**.
  - Opción de **abrir consumos** (si más adelante decides separarlos visualmente).

---

## **3. Tabla `facturas` (propuesta inicial)**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_factura | INTEGER PK | Autonumérico |
| id_contrato | INTEGER FK | Contrato asociado |
| fecha_factura | TEXT ISO | Fecha de emisión |
| periodo_inicio | TEXT ISO | Inicio periodo facturado |
| periodo_fin | TEXT ISO | Fin periodo facturado |
| consumo_punta | REAL | kWh |
| consumo_llano | REAL | kWh |
| consumo_valle | REAL | kWh |
| importe_total | REAL | Importe final factura |
| alquiler_contador | REAL | Opcional |
| impuestos | REAL | Opcional |
| notas | TEXT | Opcional |

*(Esto es ampliable cuando revises el DRU provisional.)*

---

## **4. Comportamiento en consultas**
- Desde un contrato se listan sus facturas.
- Al seleccionar una factura:
  - Se muestran todos los datos, incluidos consumos.
  - Botón “Modificar factura” (cuando implementemos modificaciones).
  - Botón “Volver al contrato”.

---

## **5. Pendientes para completar el DRU**
- Confirmar si quieres **más campos económicos** (peajes, energía, servicios…).
- Decidir si los consumos se capturan **en la misma ventana** o en una ventana hija.
- Confirmar si quieres almacenar **importe por periodo** (punta/llano/valle) además del total.
- Revisar si la factura debe tener **estado** (por ejemplo, “validada”, “estimada”, etc.).

---

Si quieres, puedo preparar ahora mismo la **versión final del DRU en Markdown**, lista para pegar en tu documentación diaria, o podemos seguir afinando los campos antes de cerrarlo. ¿Cómo prefieres avanzar?
