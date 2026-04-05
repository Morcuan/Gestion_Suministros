

# 📘 **DRU DEFINITIVO — HISTÓRICO DE CONTRATOS (Rama: Análisis)**





---

# 🎯 **OBJETIVO**

El módulo **Histórico de contratos** permite consultar todas las versiones que un contrato ha tenido a lo largo del tiempo, incluyendo su contrato original y todos sus suplementos asociados.

Este proceso es **exclusivamente consultivo**:
- No modifica datos
- No permite edición
- No genera nuevos contratos ni suplementos

Su finalidad es ofrecer una visión clara, ordenada y cronológica de la evolución administrativa y económica de un contrato.

---

# 🧭 **FLUJO DE TRABAJO**

El acceso se realiza desde el menú general, rama **Análisis**, opción **Histórico de contratos**.
Dentro del marco general de trabajo se desplegarán **tres pantallas**, cada una con responsabilidad única.

---

## 1️⃣ **Lista de contratos**
**Módulo:** `lista_contratos_historico.py`
**Ubicación:** `analisis_contrato/`

Pantalla inicial del proceso.
Es una copia adaptada del módulo de lista de contratos de otras ramas, aislada para evitar dependencias.

### **Botones disponibles**
- **Seleccionar contrato** → Avanza a la lista de suplementos del contrato elegido
- **Cancelar** → Vuelve al menú general

### **Validación defensiva**
- No permite continuar sin seleccionar un contrato
- Mensaje claro en caso de error

---

## 2️⃣ **Lista de suplementos del contrato seleccionado**
**Módulo:** `lista_suplementos_historico.py`
**Ubicación:** `analisis_contrato/`

Al seleccionar un contrato, se muestra una lista ordenada de sus suplementos.

### **Título**
**“Suplementos del contrato: <número de contrato>”** (en negrita)

### **Ordenación**
Los suplementos se muestran en orden ascendente por número de suplemento:
**0 → N**

### **Campos mostrados**
Todos procedentes de `contratos_identificacion` (y disponibles en `vista_contratos`):

1. **suplemento**
2. **efec_suple**
3. **fin_suple**
4. **compania**
5. **codigo_postal**
6. **fec_anulacion**

### **Mejoras aceptadas**
- Suplemento 0 puede mostrarse como **“Contrato original”**
- Suplementos anulados pueden mostrarse en gris o con marca visual discreta

### **Botones disponibles**
- **Seleccionar suplemento** → Avanza a la pantalla de detalles
- **Cancelar** → Vuelve a la lista de contratos

### **Validación defensiva**
- No permite continuar sin seleccionar un suplemento

---

## 3️⃣ **Detalles del suplemento**
**Módulo:** `formulario_contrato_historico.py`
**Ubicación:** `analisis_contrato/`

Pantalla final del proceso.
Carga los datos desde `vista_contratos` en **modo solo lectura**.

### **Título**
**“Detalles del contrato: <ncontrato> — Suplemento: <suplemento>”**
(negrita, centrado)

### **Formulario**
Basado en `formulario_contrato.py`, pero adaptado:

### ✔ Cambios aplicados
- Todos los campos en **readonly**
- Eliminados botones de guardar/modificar
- Añadido banner superior:
  **“🔍 Consulta histórica — Datos en modo solo lectura”**

### **Botones disponibles**
- **Lista de suplementos** → Vuelve a la pantalla anterior
- **Seleccionar otro contrato** → Vuelve a la lista de contratos
- **Cancelar** → Vuelve al menú general

---

# 🧠 **Lógica de negocio asociada**

## ✔ Cálculo del estado del suplemento
Aunque no existe un campo `estado` en la base de datos, se implementará un método en:

**`logica_negocio.py`**

Este método calculará el estado del suplemento en función de:

- `fec_anulacion`
- `fin_suple`
- Fecha actual
- Otros criterios que definas más adelante

El estado podrá ser, por ejemplo:

- **Vigente**
- **Finalizado**
- **Anulado**
- **Pendiente de efecto**

Este cálculo no afecta al DRU, pero sí enriquecerá la presentación futura.

---

# 🧩 **Integración con el marco general**

Las tres pantallas se abrirán dentro del área de trabajo gestionada por `main_window`, manteniendo:

- Estética unificada
- Navegación coherente
- Sin iconos adicionales (solo botones con texto, como en el resto del proyecto)

---

# 🛡 **Validaciones defensivas globales**

- No se permite avanzar sin selección previa
- No se permite modificar datos
- No se permite abrir detalles sin suplemento
- Mensajes claros y consistentes en caso de error

---

# 🏁 **Conclusión**

Este DRU final consolida:

- Arquitectura limpia
- Ramas aisladas
- Formularios reutilizados
- Navegación clara
- Seguridad total
- Preparación para futuras ramas (como histórico de facturas)

Si quieres, puedo generar ahora:

- El **esqueleto de los tres módulos**
- El **código del método calcular_estado_suplemento()**
- El **diagrama de flujo en ASCII**
- O incluso el **mockup visual** de cada pantalla

Tú decides el siguiente paso.
