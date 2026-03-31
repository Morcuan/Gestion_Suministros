
# 🛠️ **GUÍA TÉCNICA DEFINITIVA – MODIFICACIÓN DE CONTRATOS**
**Proyecto:** Gestión_Suministros
**Versión:** 1.4

---

# 1. Premisas técnicas

- No hay suplementos retroactivos
- La fecha de anulación no se gestiona aquí
- Todos los contratos son modificables
- Cada modificación genera un nuevo suplemento
- Campos económicos no pueden quedar vacíos
- La búsqueda de facturas se ejecuta **solo al pulsar Guardar**
- Si hay facturas afectadas → mensaje informativo

---

# 2. Arquitectura

Ventanas:

- `lista_contratos.py`
- `modificar_contrato.py`
- `formulario_contrato.py`

Tablas:

- `contratos_identificacion`
- `contratos_energia`
- `contratos_gastos`
- `facturas`

---

# 3. Flujo técnico

## 3.1. Lista de contratos

- Cargar datos
- Mostrar columnas
- Filtros
- Botón “Elegir contrato” → abre formulario

---

## 3.2. Carga del formulario

- Consultar `vista_contratos`
- Rellenar campos
- Marcar como NO editables:
  - ncontrato
  - fecha_inicio
  - fecha_final
  - fin_suple
  - fecha_anulacion

---

# 4. Validación

## 4.1. En edición

- Validación básica
- No permitir campos económicos vacíos

## 4.2. Al guardar

1. Detectar cambios
2. Validar:
   - Fechas
   - No retroactividad
   - CP
   - Números
3. Convertir fechas a ISO
4. Aplicar regla de vertido
5. **Buscar facturas afectadas**
6. Mostrar mensaje si existen

---

# 5. Suplementos y BD

## 5.1. Suplemento anterior

- Actualizar `fin_efecto`

## 5.2. Nuevo suplemento

- Insertar en las tres tablas
- Incrementar número de suplemento

---

# 6. Facturas

- Buscar facturas con `periodo_inicio >= efecto_nuevo`
- Marcar:
  - `recalcular = 1`
  - `suplemento = num_suplemento_nuevo`
- Mostrar mensaje
- No recalcular automáticamente

---

# 7. Interfaz

- Guardar → valida + marca facturas + crea suplemento
- Volver → lista
- Cancelar → menú
- Tras guardar → limpiar + cerrar + volver a lista

---

# 8. Checklist de desarrollo

- Carga correcta
- Bloqueo de campos
- Detección de cambios
- Validación completa
- No retroactividad
- Conversión ISO
- Actualización suplemento anterior
- Inserción suplemento nuevo
- Marcado de facturas
- Mensajes correctos
- Flujo de retorno correcto

---
