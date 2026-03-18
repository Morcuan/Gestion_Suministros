

---

# 📄 **DOCUMENTO 1 — DRU FORMAL**
*(Documento de Requisitos de Usuario — Rectificación de Facturas)*

## **DRU-FACT-004: Proceso de Rectificación de Facturas**

### **1. Objetivo**
Definir el proceso funcional y técnico para la rectificación de facturas dentro del módulo de Facturación del sistema Gestión Suministros 2.0, garantizando coherencia, trazabilidad y consistencia con el modelo de datos.

---

### **2. Alcance**
Este DRU afecta a:

- Menú Facturas → Rectificar factura
- Pantalla A: Selección de contrato
- Pantalla B: Selección de factura
- Pantalla C: Formulario de rectificación
- Tabla `facturas`
- Lógica de creación de facturas rectificadoras
- Lógica de marcado de facturas rectificadas

No afecta a:

- Captura de nueva factura (DRU independiente)
- Modificación de contrato / suplementos (DRU independiente)

---

### **3. Flujo funcional del usuario**

1. El usuario accede al menú **Facturas**.
2. Selecciona **Rectificar factura**.
3. Se abre `lista_contratos_rectificar.py` (Pantalla A).
4. Selecciona un contrato por **ncontrato**.
5. Se abre `lista_facturas_rectificar.py` (Pantalla B).
6. Selecciona una factura en estado **Emitida** o **Rectificadora**.
7. Pulsa **Rectificar**.
8. Se abre `form_factura_rectificar.py` (Pantalla C).
9. El usuario modifica los campos permitidos.
10. Pulsa **Guardar rectificación**.
11. El sistema:
    - Crea una factura rectificadora
    - Marca la original como **Rectificada**
12. El sistema vuelve al menú general.

---

### **4. Reglas de negocio**

#### **4.1 Estados de factura**
- **Emitida** → Puede rectificarse
- **Rectificadora** → Puede rectificarse
- **Rectificada** → No puede rectificarse

#### **4.2 Identificación del contrato**
- La referencia principal es **ncontrato**.
- `id_contrato` se usa solo como metadato histórico.

#### **4.3 Identificación de facturas**
- La clave operativa es:
  **(ncontrato, nfactura)**
- La clave técnica sigue siendo:
  **(id_contrato, nfactura)**
  pero no se usa para navegación.

#### **4.4 Generación del número rectificativo**
- Formato:
  `NFAC-1`, `NFAC-2`, etc.
- Se calcula buscando rectificadoras existentes.

#### **4.5 Campos no editables**
- Número de factura
- Número de contrato
- Numero de suplemento

---

### **5. Requisitos técnicos**

#### **5.1 Pantalla A**
- Lista contratos
- Selección por **ncontrato**
- Boton "Cerrar" → vuelve a menu general
- Boton "Seleccionar contrato" → abre Pantalla B

El modulo y la pantalla ya están funcionando.

#### **5.2 Pantalla B**
- Lista facturas por **ncontrato**
- Muestra solo datos de identificación (revisar que datos muestra)
- No muestra importes ni consumos
- Botón Cerrar → vuelve a Pantalla A
- Botón Rectificar → abre Pantalla C

#### **5.3 Pantalla C**
- Basada en `form_factura.py`
- Carga real de datos de la tabla facturas (no hay importes ni calculos)
- Validación de fechas y consumos (en lo posible limites por arriba y por abajo)
- Inserción de factura rectificadora
- Marcado de factura original como rectificada

---

### **6. Requisitos de datos**

La tabla `facturas` debe contener:

- `ncontrato`
- `estado`
- `rectifica_a`
- `id_contrato` (histórico)
- `suplemento`
- Resto de campos del formulario de factura

La tabla ya esta rectificada y contiene los campos descritos aqui.
---

### **7. Criterios de aceptación**

- El usuario puede rectificar cualquier factura Emitida o Rectificadora.
- La factura original queda marcada como Rectificada.
- La nueva factura aparece correctamente en la lista.
- El proceso no depende de `id_contrato`.
- No se muestran importes en Pantalla B.
- Pantalla C carga datos reales y válidos.

---

---

# 📘 **DOCUMENTO 2 — README TÉCNICO DE LA RAMA**

# **README — Rama `facturas/rectificar_factura`**

## **Descripción**
Esta rama implementa el proceso completo de rectificación de facturas en el menu de Facturas del proyecto Gestión Suministros 2.0.

---

## **Arquitectura del flujo**

```
Hacia adelante:

Menú → Pantalla A → Pantalla B → Pantalla C → Guardado → Menú

Hacia atras:

Pantalla C → Pantalla B → Pantalla A → Menú
```

### **Pantalla A — lista_contratos_rectificar.py**
- Lista contratos
- Selección por **ncontrato**
- Navegación hacia Pantalla B

### **Pantalla B — lista_facturas_rectificar.py**
- Lista facturas del contrato
- Muestra solo datos de identificación
- No muestra importes ni consumos
- Valida estado
- Navega a Pantalla C

### **Pantalla C — form_factura_rectificar.py**
- Basada en `form_factura.py`
- Carga real de datos
- Bloquea campos no editables
- Guarda rectificadora
- Marca original como rectificada

---

## **Decisiones de diseño clave**

### **1. `ncontrato` es la referencia principal**
- Se usa para todas las consultas
- Evita problemas con suplementos
- `id_contrato` queda como metadato histórico

### **2. Pantalla B no muestra importes**
- Solo identificación
- Evita duplicar lógica de cálculo
- Mantiene separación de responsabilidades

### **3. Pantalla C se basa en `form_factura.py`**
- Evita divergencias
- Mantiene consistencia visual y funcional
- Reutiliza validaciones

---

## **Tareas pendientes (DRUs independientes)**

- Ajustar captura de facturas para nuevos campos
- Ajustar modificación de contrato para actualizar `id_contrato`y suplemento en facturas afectadas

---

---

# 🛠️ **DOCUMENTO 3 — PLAN DE TRABAJO PASO A PASO**

# **Plan de Trabajo — Rectificación de Facturas**

## **Objetivo**
Reconducir la rama y completar el proceso de rectificación de forma estable y coherente.

---

## **FASE 1 — Reescritura de Pantalla C (CRÍTICA)**

1. Crear nuevo módulo basado en `form_factura.py`
2. Reescribir `cargar_factura()` usando **ncontrato + nfactura**
3. Ajustar SELECT al esquema real
4. Bloquear campos no editables
5. Implementar validaciones
6. Implementar guardado:
   - Insertar rectificadora
   - Marcar original como rectificada
7. Probar flujo completo desde Pantalla B

---

## **FASE 2 — Ajustes en Pantalla B**

1. Eliminar importes y placeholders, si es que se muestran
2. Mostrar solo datos de identificación
3. Asegurar navegación correcta
4. Validar estados
5. Probar con varios contratos.

Nota: A pesar de que en la tabla facturas existe el numero de suplemento solo se utiliza a titulo informativo y por si puediera ser necesario para el futuro.

---

## **FASE 3 — Verificación de Pantalla A**

1. Confirmar que pasa `ncontrato` (ya es correcto)
2. Confirmar navegación correcta
3. Revisar coherencia con el menú principal

---

## **FASE 4 — Ajustes en tabla `facturas`**

1. Verificar campos nuevos
2. Verificar índices
3. Verificar integridad referencial
4. Probar inserción de facturas nuevas

---

## **FASE 5 — Pruebas completas**

1. Rectificar factura Emitida
2. Rectificar factura Rectificadora
3. Intentar rectificar factura Rectificada
4. Verificar que la lista se refresca
5. Verificar que el menú vuelve correctamente
6. Verificar que no se usa `id_contrato` en navegación

---

## **FASE 6 — DRUs independientes**

- DRU: Captura de facturas
- DRU: Modificación de contrato / suplementos

---


