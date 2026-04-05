Perfecto, Antonio. Con el DRU ya consolidado, aquí tienes **la Guía Técnica completa del proceso Histórico de Contratos**, escrita con tu estilo habitual: clara, modular, defensiva y perfectamente alineada con la arquitectura de *Gestion Suministros 2.0*.

Incluyo un único bloque visual para ayudarte a visualizar el flujo general:





---

# 📘 **GUÍA TÉCNICA — HISTÓRICO DE CONTRATOS (Rama: Análisis)**

Esta guía describe la **implementación técnica**, la **estructura de módulos**, las **consultas SQL**, la **navegación**, las **validaciones**, y la **interacción con el marco general** del proceso *Histórico de contratos*.

---

# 🧱 1. **Arquitectura del módulo**

## 📂 Estructura de carpetas
```
analisis_contrato/
    lista_contratos_historico.py
    lista_suplementos_historico.py
    formulario_contrato_historico.py
```

### ✔ Principios aplicados
- **Aislamiento total** respecto a otras ramas
- **Reutilización controlada** de formularios
- **Ningún riesgo de modificar datos**
- **Integración limpia** con `main_window`

---

# 🖥 2. **Pantalla 1 — lista_contratos_historico.py**

## 🧩 Función
Mostrar todos los contratos disponibles para iniciar la consulta histórica.

## 🔌 Origen de datos
Consulta a la tabla `contratos` o a la vista `vista_contratos` (recomendado para coherencia).

### SQL sugerido
```sql
SELECT ncontrato, titular, compania, codigo_postal, efecto, fin_efecto
FROM vista_contratos
GROUP BY ncontrato
ORDER BY ncontrato ASC;
```

## 🎛 Componentes
- Treeview con columnas básicas de identificación
- Botones:
  - **Seleccionar contrato**
  - **Cancelar**

## 🛡 Validaciones
- Si no hay selección → `messagebox.showwarning(...)`
- Si hay selección → abrir `lista_suplementos_historico.py`

---

# 🖥 3. **Pantalla 2 — lista_suplementos_historico.py**

## 🧩 Función
Mostrar todos los suplementos del contrato seleccionado.

## 🔌 Origen de datos
Consulta a `vista_contratos` filtrando por `ncontrato`.

### SQL sugerido
```sql
SELECT suplemento, efec_suple, fin_suple, compania, codigo_postal, fec_anulacion
FROM vista_contratos
WHERE ncontrato = ?
ORDER BY suplemento ASC;
```

## 🎛 Componentes
- Título:
  **“Suplementos del contrato: <ncontrato>”**
- Treeview con columnas:
  - suplemento
  - efec_suple
  - fin_suple
  - compania
  - codigo_postal
  - fec_anulacion

## 🎨 Mejoras visuales
- Suplemento 0 → “Contrato original”
- Suplementos anulados → texto gris o estilo diferenciado

## 🛡 Validaciones
- No permitir avanzar sin selección
- Botones:
  - **Seleccionar suplemento**
  - **Cancelar** (volver a lista de contratos)

---

# 🖥 4. **Pantalla 3 — formulario_contrato_historico.py**

## 🧩 Función
Mostrar todos los datos del contrato + suplemento en modo **solo lectura**.

## 🔌 Origen de datos
Consulta a `vista_contratos` con filtro doble:

```sql
SELECT *
FROM vista_contratos
WHERE ncontrato = ? AND suplemento = ?;
```

## 🎛 Componentes
- Copia del formulario original de contratos
- Todos los widgets en modo **readonly**
- Banner superior:
  **“🔍 Consulta histórica — Datos en modo solo lectura”**

## 🛡 Validaciones
- No abrir si no hay suplemento seleccionado
- Botones:
  - **Lista de suplementos**
  - **Seleccionar otro contrato**
  - **Cancelar** (volver al menú general)

---

# 🧠 5. **Lógica de negocio**

## 📌 Método recomendado: `calcular_estado_suplemento()`

Se implementará en:

```
logica_negocio.py
```

### Entradas:
- efec_suple
- fin_suple
- fec_anulacion
- fecha actual

### Salidas posibles:
- “Vigente”
- “Finalizado”
- “Anulado”
- “Pendiente de efecto”

### Uso:
- Puede mostrarse en la lista de suplementos
- Puede mostrarse en el formulario histórico
- Puede integrarse en futuras ramas (ej. histórico de facturas)

*(Esperamos tu DRU para implementarlo con precisión.)*

---

# 🔗 6. **Integración con main_window**

Las tres pantallas se abren dentro del marco general mediante:

```python
self.main_window.cargar_widget(ClasePantalla)
```

### Reglas:
- Nunca se abren ventanas flotantes
- Siempre se reemplaza el área de trabajo
- Navegación lineal y reversible

---

# 🛡 7. **Validaciones defensivas globales**

- No permitir avanzar sin selección
- No permitir abrir detalles sin suplemento
- No permitir edición en ningún campo
- Mensajes claros y consistentes
- Cierre limpio y retorno al menú general

---

# 🧩 8. **Dependencias internas**

- `vista_contratos`
- `logica_negocio.py`
- `main_window.py`
- `conexion.py`
- Formularios reutilizados adaptados a readonly

---

# 🏁 **Guía técnica completada**

Este documento ya está listo para integrarlo en tu documentación técnica del proyecto.
Cuando tengas el DRU del cálculo del estado del suplemento, lo leemos juntos y lo implementamos con precisión quirúrgica.

Hoy toca descansar un poco, que también forma parte del método.
