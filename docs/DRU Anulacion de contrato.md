

# 📘 **DRU – Anulacion de Contrato**


## **1. Definición**

- Los contratos de suministro se pueden anular por diversas circunstancias.

- La anulacion de contrato es sencillamente la inclusion de una fecha de anulacion a partir de la cual las condiciones economicas o administrativas del contrato no tienen vigencia en el suplemento vigente en el momento de la anulacion.

- La anulacion de contrato no implica que no se puedan capturar mas facturas, pero si que esas facturas aunque pudieran ser emitidas despues de la anulacion deben corresponder al periodo de vigencia del contrato, es decir el periodo facturado no debe superar la fecha de anulacion de la factura.

- Una vez anulado el contrato no se puede volver a modificar ni volver a rehabilitar.


## **2. Qué se puede modificar**

### **No modificables por el usuario**

- En este suplemento no se puede modificar ningun dato del contrato excepto los mencionados en el siguiente apartado

### **Modificables**

**de contratos_identificacion**

- fec_anulacion

---

## **3. Flujo de trabajo**

1. Menú: **Contratos → Anulacion**
2. Lista de contratos (vista_contratos)
3. Selección de contrato → botón “Anulacion”
4. Apertura de ventana de modificación (form_modificacion.py)
5. Carga del suplemento vigente (vista_contratos, suplemento más alto)
6. Todos los datos no editables excepto fec_anulacion
6. Usuario introduce fecha de anulacion
7. Se valida que la fecha de anulacion sea <= a la fecha de fin de efecto del suplemento vigente
8. Se guarda la modificacion sin generar un nuevo suplemento.


---

## **4. Lógica de creación del suplemento nuevo**

### **4.1 Datos base**
- Se parte del suplemento vigente (suplemento N).
- El nuevo suplemento de anulacion será N+1.
- efec_suple lo aporta el usuario.
- fin_suple del suplemento anterior se ajusta automáticamente.

### **4.2 Fechas**
- fec_inicio y fec_final del contrato **no cambian nunca**.
- Suplemento anterior:
  - No se modifica

- Suplemento actual:

  - fec_anulacion = la introducida por el usuario
  - fin_suple = fec_anulacion
  - estado = “Anulado”

---

## **5. Tratamiento de BD**


1. UPDATE en contratos_identificacion segun el punto anterior.

  - fec_anulacion,
  - fin_suple
  - estado

