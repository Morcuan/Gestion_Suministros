
---

# 🧭 **GUÍA TÉCNICA DEFINITIVA – Módulo “Nuevo Contrato”**
### *(Versión final con estructura modular y carpetas actualizadas)*

Esta guía define **cómo debe construirse el módulo Nuevo Contrato**, su arquitectura, sus responsabilidades y la estructura del proyecto.
No se permite desviación alguna.

---

# 1. **Estructura de carpetas del proyecto**

La estructura oficial del proyecto será:

```
/Gestion_Suministros/
│
├── main.py
├── main_window.py
├── db_init.py
│
├── /utilidades/
│     ├── utilidades_bd.py        ← Funciones generales de BD
│     └── logica_negocio.py       ← Lógica común (fechas, validaciones, estado…)
│
├── /contratos/
│     ├── formulario_contrato.py  ← Vista pura (embebida en main_window)
│     ├── nuevo_contrato.py       ← Lógica y validaciones del alta
│     ├── modificar_contrato.py   ← (futuro)
│     ├── lista_contratos.py      ← (futuro)
│
├── /facturas/                    ← (futuro)
│
├── /bajas/                       ← (futuro)
│
└── /consultas/                   ← (futuro)
```

### ✔️ `/utilidades/` es un módulo transversal
- `utilidades_bd.py` → inserciones, actualizaciones, consultas auxiliares
- `logica_negocio.py` → validaciones, fechas, estado, funciones comunes

### ✔️ `/contratos/` contiene solo lo específico de contratos
- vistas
- controladores
- lógica propia del proceso

---

# 2. **Integración visual en main_window**

## 2.1. El formulario NO será una ventana independiente
Debe incrustarse en el área de trabajo central de `main_window.py`.

## 2.2. main_window debe proporcionar:
- un contenedor central (QFrame, QWidget, QStackedWidget…)
- un método para cargar formularios:

```python
def cargar_formulario(self, widget):
    self.area_trabajo_layout.addWidget(widget)
    widget.show()
```

## 2.3. nuevo_contrato.py NO crea ventanas
Solo hace:

```python
form = FormularioContrato()
main_window.cargar_formulario(form)
```

---

# 3. **Responsabilidades por módulo**

---

## 3.1. `/contratos/formulario_contrato.py`
### **Vista pura embebida**

### Obligaciones
- Ser un QWidget incrustable.
- Mostrar campos del contrato.
- No contener lógica de negocio.
- No validar.
- No acceder a BD.
- No navegar.

### Métodos obligatorios
```python
cargar_datos(datos_dict)
obtener_datos()
limpiar()
set_modo(modo)
```

### Campos NO editables en modo “nuevo”
- suplemento = 0
- fec_final
- efec_suple
- fin_suple
- fec_anulacion

---

## 3.2. `/contratos/nuevo_contrato.py`
### **Controlador del proceso de alta**

### Obligaciones
- Crear el formulario.
- Insertarlo en el área de trabajo de main_window.
- Controlar navegación entre campos.
- Validar datos.
- Convertir fechas dd/mm/aaaa → ISO.
- Calcular automáticos:
  - suplemento = 0
  - fec_final = fec_inicio + 10 años − 1 día
  - efec_suple = fec_inicio
  - fin_suple = fec_final
- Preparar diccionario final.
- Llamar a `utilidades_bd.insertar_contrato()`.
- Mostrar mensajes.

### Prohibiciones
- No abrir ventanas propias.
- No acceder a widgets internos.
- No insertar directamente en BD.
- No duplicar lógica de modificación.

---

## 3.3. `/utilidades/utilidades_bd.py`
### **Persistencia general del proyecto**

### Obligaciones
- Funciones puras de BD:
  - `insertar_contrato_identificacion()`
  - `insertar_contrato_energia()`
  - `insertar_contrato_gastos()`
  - `insertar_contrato()` (orquestadora)
- Recibir conexión desde main.py.
- Devolver id_contrato y estado de operación.

### Prohibiciones
- No mostrar mensajes.
- No validar.
- No acceder a interfaz.

---

## 3.4. `/utilidades/logica_negocio.py`
### **Lógica común reutilizable**

### Obligaciones
- Validación de fechas.
- Conversión dd/mm/aaaa ↔ ISO.
- Cálculo de fecha final (+10 años).
- Cálculo de estado del contrato:
  - futuro
  - activo
  - caducado
- Comprobación de coherencia.

### Prohibiciones
- No acceder a BD.
- No acceder a interfaz.

---

# 4. **Reglas de validación obligatorias**

### Fechas
- Formato entrada: **dd/mm/aaaa**
- Conversión obligatoria a ISO.
- `fec_inicio` ≥ hoy.
- `fec_final` = `fec_inicio` + 10 años − 1 día.
- `efec_suple` = `fec_inicio`.
- `fin_suple` = `fec_final`.

### Campos obligatorios
Todos los de las tres tablas.

### Campos automáticos
- suplemento = 0
- fec_final
- efec_suple
- fin_suple
- fec_anulacion = NULL

### Unicidad
- La combinación **ncontrato + suplemento** debe ser única.

---

# 5. **Persistencia**

### Orden obligatorio
1. Insertar en contratos_identificacion
2. Obtener id_contrato
3. Insertar en contratos_energia
4. Insertar en contratos_gastos

### Flujo
```
nuevo_contrato.py
    → utilidades_bd.insertar_contrato()
        → insertar_contrato_identificacion()
        → insertar_contrato_energia()
        → insertar_contrato_gastos()
```

---

# 6. **Flujo funcional completo**

1. Usuario selecciona “Nuevo contrato”.
2. main_window crea instancia de NuevoContrato.
3. NuevoContrato crea FormularioContrato.
4. main_window incrusta el formulario en el área de trabajo.
5. Usuario introduce datos.
6. Usuario pulsa Guardar.
7. NuevoContrato:
   - obtiene datos
   - valida
   - calcula automáticos
   - convierte fechas
   - prepara diccionario
   - llama a utilidades_bd.insertar_contrato()
8. Si éxito:
   - mensaje OK
   - limpiar o cerrar
9. Si error:
   - mensaje error

---

# 7. **Estado del contrato (no persistente)**

Siempre calculado mediante:

```
calcular_estado(fecha_inicio, fecha_final)
```

Valores:
- Futuro
- Activo
- Caducado

---

# 8. **Reglas de diseño (no negociables)**

- El formulario **siempre** se incrusta en main_window.
- No se crean ventanas flotantes.
- No se mezcla lógica con interfaz.
- No se accede a BD fuera de utilidades_bd.py.
- No se calculan fechas fuera de logica_negocio.py.
- No se accede a widgets internos desde nuevo_contrato.py.
- No se crean módulos adicionales sin actualizar esta guía.

---

Antonio, esta es la **Guía Técnica Definitiva**, con todas tus decisiones integradas.
Si estás conforme, el siguiente paso natural es:

👉 **crear el esqueleto de `formulario_contrato.py`**
(la vista pura, sin lógica, incrustada en el marco general)

Cuando tú digas, empezamos.
