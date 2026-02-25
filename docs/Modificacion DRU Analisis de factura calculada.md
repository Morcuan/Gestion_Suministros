
---

# 🧱 Base del DRU (Documento de Requisitos de Usuario)  


## 1. Flujo general de navegación  
Todas las ventanas nuevas y existentes deben:

- Abrirse **en el contenedor principal** (como el resto de la aplicación).
- Tener navegación **hacia abajo** (abrir la siguiente ventana) y **hacia arriba** (volver a la anterior).
- Mantener el estilo visual ya establecido en Gestion_suministros 2.0.
- No usar subformularios ni paneles secundarios flotantes.

---

## 2. Flujo completo de facturas

### **A) Lista de facturas**
- Botón “Detalle” → abre **DetalleFactura**.
- Cierra la lista.

### **B) Ventana DetalleFactura**
- Botón “Totalizar factura” pasa a llamarse **“Analizar factura”**.
- Al pulsarlo:
  - Se abre **Detalles del cálculo (JSON)**.
  - Se cierra DetalleFactura.

### **C) Ventana Detalle del Cálculo (JSON)**
- Se abre **como ventana independiente**
- DetalleFactura se cierra al abrirla.
- Se muestran TODOS los detalles de los calculos con el siguiente esquema:

    Potencia: xx.xx €
    Punta--> kW: xx Precio Unitario: x.xxxxxx Importe: xx.xx €
    Llano--> kW: xx Precio Unitario: x.xxxxxx Importe: xx.xx €
    Valle--> kW: xx Precio Unitario: x.xxxxxx Importe: xx.xx €

    Consumo: xx.xx €
    Punta xxxxxx
    Llano xxxxxx
    Valle xxxxxx

    Excedentes: xx.xxx  €
    Generados: xx.xx Precio Unitario: x.xxxxxx Importe compensado: x.xxx Sobrante: xxxxxx

    y asi los demas bloques de calculo.
  
- Solo tiene un botón **“Cerrar”** abajo a la derecha.
- Ese botón:
  - Cierra la ventana JSON.
  - Reabre ResumenFactura.

---

## 3. Eliminaciones definitivas
- Venetana Resumen Factura
- Subformularios.
- Scrolls automáticos no deseados.
- Layouts híbridos o experimentales.
- Jerarquías de `parent().parent()` y similares.
- Cualquier intento de dividir la pantalla en dos paneles simultáneos.

---

## 4. Objetivo final
Volver a un flujo:

- **Lineal**
- **Predecible**
- **Robusto**
- **Visualmente coherente**
- **Fácil de mantener**


