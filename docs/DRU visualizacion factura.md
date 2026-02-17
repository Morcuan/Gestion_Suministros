

# 🧱 **DRU – Visualizacion de Factura (Base para trabajar)**  
*(Documento de Requisitos Unificado – Versión inicial)*

---

# 1. **Objetivo del módulo**

El módulo de visualizacion sera semejante a la estructura de una factura que esta compuesta por al menos dos paginas:

En la primera pagina, una factura muestra un resumen de los valores calculados que integran el "Total a pagar"

Estos bloque son:
 
- energía
- cargos normativos
- servicios y otros conceptos
- Iva
- Solar Cloud
- Total Factura

En la segunda pagina se muestran los calculos detallados de los bloques anteriores.

- Para estructurarlo en nuestro proceso y que sea visualmente atractivo y semejante crearemos una primera ventana "Resumen" que integrará los valores de esos bloques anteriores. 
- Esta ventana será llamada desde la ventana de detalles de la factura al pulsar el boton "totalizar factura". 
- Contara con un boton a la derecha "Cancelar" que volverá a la ventana detalles de factura a lo mejor es que al ser pulsado el boton.
- A continuacion de cada uno de los bloques anteriores habrá un boton "detalles" que desplegará una ventana independiente con los calculos detallados del apartado. Esta ventana independiente, a su vez, tendrá el boton "cerrar" que la cerrará dejando la ventana Resumen disponible nuevamente.

# 2. Calculos

 **TODOS LOS CALCULOS SE REALIZARÁN EN EL MODULO calculos.py. que devolverá los valores descritos anteriormente ya calculados.


🖥️ Diseño del módulo de visualización — Versión “Factura Iberdrola mejorada”
Ventana principal: RESUMEN DE FACTURA

Una ventana compacta, limpia, con los cinco bloques:

    Bloque 1 – Energía

    Bloque 2 – Cargos normativos

    Bloque 3 – Servicios y otros conceptos

    Bloque 4 – IVA

    Bloque 5 – Total factura (este no tiene botón de detalles)

Cada bloque mostrado así:
Código

ENERGÍA ........................................ 45,07 €     [Detalles]
CARGOS NORMATIVOS ........................ 0,40 €     [Detalles]
SERVICIOS Y OTROS .......................... 2,50 €     [Detalles]
IVA .................................................... 10,07 €     [Detalles]
TOTAL FACTURA ................................ 58,03 €

Los botones [Detalles] abren una ventana secundaria con el desglose completo.
🪟 Ventanas secundarias: Detalles del cálculo

Aquí tendremos 4 ventanas, una por cada bloque con desglose:
1. Detalles del Bloque Energía

    Potencia punta

    Potencia valle

    Consumo punta

    Consumo llano

    Consumo valle

    Excedentes

    Impuesto eléctrico

    Total bloque

2. Detalles del Bloque Cargos Normativos

    Bono social

    Otros cargos si los hubiera

    Total bloque

3. Detalles del Bloque Servicios y Otros

    Alquiler contador

    Servicios adicionales

    Descuentos

    Total bloque

4. Detalles del Bloque IVA

    Base imponible

    Tipo aplicado

    Cuota resultante

    Total IVA

🎯 Ventajas de este diseño

    El usuario ve un resumen idéntico al de Iberdrola, pero más claro.

    Puede abrir cada bloque para ver cómo se ha calculado.

    El total no necesita detalles porque es solo la suma final.

    La estructura es modular y fácil de mantener.

    Encaja perfectamente con tu flujo de cálculo actual.


