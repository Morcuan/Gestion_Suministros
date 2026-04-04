Perfecto, Antonio. Con tus aclaraciones ya tenemos **todas las reglas cerradas y sin ambigüedades**, así que podemos pasar directamente al **diseño final del algoritmo** y luego a su implementación en `logica_negocio.py`.

Antes de escribir código, quiero dejarte el **pseudocódigo definitivo**, totalmente alineado con tu DRU y con tus matices adicionales. Esto nos garantiza que el método será correcto a la primera.

---

# 🧩 Algoritmo definitivo para determinar el estado del contrato

A continuación te presento el **pseudocódigo final**, ya depurado con tus aclaraciones.

---

# 🧠 1. Variables de entrada

- `efec_suple` → fecha de efecto del suplemento máximo
- `fin_suple` → fecha de fin de efecto del suplemento máximo
- `fec_anulacion` → fecha de anulación del suplemento máximo (puede ser None)
- `fecha_ref` → fecha en la que se determina el estado (por defecto hoy)
- `lista_fechas_efecto` → lista de fechas de efecto de TODOS los suplementos del contrato (para determinar “Sin efecto”)

---

# 🧠 2. Reglas del DRU aplicadas en orden lógico

```text
1. Si existe fecha de anulación:
    1.1 Si fec_anulacion == efec_suple:
            → Estado = "Sin efecto"
            (pero solo si TODOS los suplementos tienen la misma fecha de efecto)
    1.2 Si fec_anulacion <= fin_suple:
            → Estado = "Anulado"
    1.3 (No puede existir fec_anulacion > fin_suple porque ya lo validas en captura)

2. Si NO existe fecha de anulación:
    2.1 Si efec_suple > fecha_ref:
            → Estado = "Futuro"
    2.2 Si fin_suple < fecha_ref:
            → Estado = "Caducado"
    2.3 Si efec_suple <= fecha_ref <= fin_suple:
            → Estado = "En vigor"
```

---

# 🧠 3. Regla especial para “Sin efecto”

Tu aclaración es clave y la incorporo tal cual:

### Caso A — Solo existe suplemento 0
```
Si fec_anulacion == efec_suple → "Sin efecto"
```

### Caso B — Existen suplementos posteriores
```
Si TODOS los suplementos tienen la misma fecha de efecto
Y fec_anulacion == efec_suple
→ "Sin efecto"
```

### Caso C — Si algún suplemento tiene fecha de efecto distinta
```
→ El contrato tomó efecto → NO puede ser "Sin efecto"
```

---

# 🧠 4. Pseudocódigo final

```python
def determinar_estado(efec_suple, fin_suple, fec_anulacion, lista_fechas_efecto, fecha_ref=None):

    if fecha_ref is None:
        fecha_ref = date.today()

    # --- 1. CASOS CON ANULACIÓN ---
    if fec_anulacion is not None:

        # 1.1 Posible "Sin efecto"
        if fec_anulacion == efec_suple:
            if len(set(lista_fechas_efecto)) == 1:
                return "Sin efecto"
            # Si hay fechas distintas → no puede ser "Sin efecto"
            # Se evalúa como anulado normal

        # 1.2 Anulado (siempre válido porque ya validas que fec_anulacion <= fin_suple)
        return "Anulado"

    # --- 2. CASOS SIN ANULACIÓN ---
    # 2.1 Futuro
    if efec_suple > fecha_ref:
        return "Futuro"

    # 2.2 Caducado
    if fin_suple < fecha_ref:
        return "Caducado"

    # 2.3 En vigor
    if efec_suple <= fecha_ref <= fin_suple:
        return "En vigor"

    # No debería llegar aquí nunca
    return "Indeterminado"
```

---

# 🧱 5. Estamos listos para implementarlo en `logica_negocio.py`

Si quieres, ahora mismo pasamos a:

### ✔️ Crear el método real en Python
### ✔️ Integrarlo en los listados de contratos
### ✔️ Probarlo con datos reales
### ✔️ Añadirlo a facturas si procede
### ✔️ Dejarlo documentado en el DRU y en el código

Tú marcas el ritmo. ¿Quieres que empecemos ya con el código real en `logica_negocio.py`?
