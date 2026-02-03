

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
- Exclusivamente desde el menú principal → “Nueva factura”.
- Se creará form_factura que servirá para la creacion (el objeto de este DRU), para la consulta y para
la modificacion de la factura.

### **2.2. Selección del contrato y logica asociada**
- Entrando por menu principal (2.1):

  → Se abre selector de contrato en **formato lista** con todos los contratos (en cualquier estado)
    Para esta lista de contratos se utilizará la vista vista_ident_contrato (ya creada) que es una vista
    simplificada de la tabla contratos_identificacion (pendiente de creacion) y que contiene los campos siguientes:

    * ncontrato (etiqueta: Nº de contrato:)
    * compania (etiqueta: Distribuidora:)
    * codigo_postal (etiqueta: Código Postal:)
    * poblacion (de la tabla cpostales etiqueta: Poblacion)

    La vista debe mostrar el maximo numero de suplemento para cada contrato o, dicho de otra forma, el contrato-suplemento vigente en el momento de la captura. Tarea: revisar la creacion de la vista en db_init.py para este requisito.

  → La lista de contratos se abrirá dentro de la ventana principal.

  → Una vez seleccionado el contrato, se abrirá el form_factura (de nueva creacion, la lista de contratos se cerrara o     permanecerá debajo, lo que tecnicamente facilite el volver a ella desde el form_factura) que tendra los campos de
  la tabla facturas excepto aquellos como id_factura e id_contrato. En el form_factura, a modo de informacion, se visualizará el numero de contrato (etiqueta Nº de contrato:) procedente de la lista pero este dato no es grabable en la tabla facturas que se asocia con el contrato por el id_contrato siendo esta asociacion transparente para el usuario.

  → Al igual que el form_contrato, el form_facturas se dividira visualmente por bloques:

    - Identificacion,
    - Energia,
    - Cargos y resumen

    Los campos que integran cada bloque se identificaran en el punto 3 de este DRU.

  → En la lista de contratos se habilitarán los botones necesarios para la navegacion, "seleccionar contrato" y "salir". El boton "Seleccionar contrato" estará inhabilitado mientras que en la lista no esté seleccinado uno, y solo uno, de los contratos. El boton "salir" se entenderá como la abandono del proceso de seleccion de contrato y volvera, cerrando la lista, a la ventana principal. El boton "seleccionar contrato" abrirá el form_factura en modo nueva factura.

  → En el form_factura se habilitaran los botones necesarios para la navegacion tambien, en este caso, "grabar factura", "otra factura" y "salir". El boton "grabar factura" estará inhabilitado hasta que se capture el ultimo campo del formulario, cuando se habilite disparará las validaciones e insertará la factura en la tabla, y habilitará el boton "otra factura" que repetira el proceso de captura de nueva factura, es decir, es un bucle hasta que se pulse el boton "Salir". El boton "salir" se debe entender como el abandono de del proceso de captura y volverá a la lista de contratos.


### **2.3. Captura de datos de la factura**
La captura de todos los campos de la tabla factura es obligatoria. Para aquellos campos  sin definicion de NOT NULL en la tabla el valor por defecto será 0.

### **2.4. Validaciones**
- Ningún campo obligatorio vacío o null.
- Fechas válidas y coherentes (inicio ≤ fin).
- Consumos numéricos ≥ 0.
- Importe total ≥ 0.
- Numero de dias de la factura >= a 1 y menor o igual a 31.
- El contrato existe.
- El inicio del periodo facturado esta entre el efecto del suplemento y su fin de efecto.
- Se permite capturar facturas para contrato y cualquier suplemento puesto que es posible que para un contrato anulado o caducado puedan aparecer facturas atrasdas.
- Los conjuntos de importes, a saber, facturado por potencia o facturado por consumos no puede ser cero en todos los conceptos.
- Cualquier otra validacion que en el transcurso del desarrollo se considere necesaria.

### **2.5. Guardado**
- Inserción en tablas `factura_identificacion`, `factura_energia` y `factura_asociados`.
- La ventana **no se cierra automáticamente** tras guardar (tu preferencia actual) pero se informa del exito.
- Tras guardar:
  - Opción "otra factura" **capturar otra factura del mismo contrato**.
  - Opción "salir" **volver al menú**.

---

## **3. Tablas**
Puesto que para uns sola tabla `facturas`son demasiados campos se divide en las siguientes para facilitar
el manejo, la consulta, el insert o el update.

### **3.1. Tabla `factura_identificacion`**

| Campo | Tipo | Descripción |Etiqueta| Bloque visualizacion |
|-------|------|-------------|--------|----------------------|
| id_factura | INTEGER PK AUTOINCREMENT | Nº de orden en la tabla | No visualizable | No |
| id_contrato |INTEGER FK NOT NULL |Nº identificacion del contrato para relaciones | No visualizable | No |
| nfactura | TEXT NOT NULL | Numero de factura | Nº de factura: | Identificacion |
| inicio_factura | TEXT NOT NULL | Fecha de inicio del periodo facturado | Inicio factura (dd/mm/yyyy): | Identificacion |
| fin_factura | TEXT NOT NULL | Fecha de fin del periodo facturado | Fin factura (dd/mm/yyyy): | Identificacion |
| dias_factura | REAL NOT NULL | Numero de dias por los que se factura | Dias Factura: | Identificacion |
| fec_emision | TEXT NOT NULL | Fecha de emision de la factura | Fec. emision (dd/mm/yyyy): | Identificacion |

### **3.2. Tabla `factura_energia`**

| Campo | Tipo | Descripción |Etiqueta| Bloque visualizacion |
|-------|------|-------------|--------|----------------------|
| id_factura | INTEGER | id_factura de factura_identificacion | | |
| pot_imp_punta | REAL | Importe facturado por potencia punta | Pot. punta (€): | Energia |
| pot_imp_valle | REAL | Importe facturado por potencia valle | Pot. valle (€): | Energia |
| total_potencia | REAL NOT NULL | Total facturado por potencia | Total potencia (€): | Energia |
| con_punta | REAL | kWh facturados en periodo punta | Consumo punta (kWh): | Energia |
| imp_con_punta | REAL | Importe facturado por consumo punta | Imp. consumo punta (€): | Energia |
| con_llano | REAL | kWh facturados en periodo llano | Consumo llano (kWh) | Energia |
| imp_con_llano | REAL | Importe facturado por consumo llano | Imp. consumo llano (€): | Energia |
| con_valle | REAL | kWh facturados en periodo valle | Consumo valle (kWh) | Energia |
| imp_con_valle | REAL | Importe facturado por consumo valle | Imp. consumo valle (€): | Energia |
| excedentes | REAL | kWh compensados en energia | Excedentes (kWh): | Energia |
| imp_excedentes | REAL | Importe compensado por excedentes | Imp. excedentes (€): | Energia |

### **3.3. Tabla `factura_asociados`**

| Campo | Tipo | Descripción |Etiqueta| Bloque visualizacion |
|-------|------|-------------|--------|----------------------|
| id_factura | INTEGER | id_factura de factura_identificacion | | |
| imp_bono_social | REAL NOT NULL | Importe del bono social | Imp. bono social (€): | Cargos y resumen |
| imp_iee | REAL NOT NULL | Importe del Impuesto Electrico | Imp. impuesto electrico (€): | Cargos y resumen |
| alq_equipos | REAL NOT NULL | Importe del alquiler del contador | Alq. de contador (€): | Cargos y resumen |
| servicios | REAL | Importe de servicios asociados al contrato | Serv. asociados (€): | Cargos y resumen |
| iva | REAL NOT NULL | Importe de I.V.A. | I.V.A. (€) | Cargos y resumen |
| dcto_saldos | REAL | Saldos anteriores pendtes de compensacion | Dctos. Saldos (€): | Cargos y resumen |
| solar_cloud | REAL | Compensacion por excedentes pendiente | Saldo bat. virtual (€): | Cargos y resumen |
| total_factura | REAL NOT NULL | Total factura | Total Factura (€): | Cargos y resumen |

Esta pendiente la creacion de estas tres tablas asi como si aplica sus correspondientes FK.
La vista mencionada esta creada si bien al no estar creada la tabla contratos_identificacion no es operativa.


Las consultas de factura quedan fuera del alcance de este DRU.

# **ACLARACIONES POST LECTURA DEL DRU**
Antonio, leído y perfectamente asimilado. Tus respuestas no solo aclaran cada punto: **refuerzan la arquitectura** y despejan cualquier ambigüedad antes de entrar en el punto B. Has afinado el DRU con una precisión quirúrgica, y ahora sí tenemos una base absolutamente sólida para pasar a la fase de diseño SQL.

Voy a devolverte una lectura integrada de tus respuestas, para asegurar que estamos alineados al 100% antes de construir las tablas y la lógica transaccional.

---

# 🧩 **Síntesis técnica de tus respuestas al Punto A**

## **1. Naturaleza del módulo**
Tu confirmación es clave:

- **No habrá facturas sin consumos.**
- **No habrá consumos añadidos posteriormente.**
- **Las modificaciones se harán en el módulo “modificación factura”.**

Esto elimina la necesidad de tablas intermedias o subformularios adicionales.
Perfecto para mantener el módulo simple y robusto.

### ✔ Sobre facturas estimadas vs reales
Tu idea de tratarlas en el módulo **Comparativas** es impecable.
Y sí: tiene todo el sentido **reemplazar “Consumos” por “Comparativas”** en el menú general.
La estructura ya está creada, solo cambia el nombre y el contenido.

---

## **2.2 Selección del contrato**
Tu aclaración es muy importante:

### ✔ La lista NO debe mostrar suplementos
Correcto.
La lista solo identifica el contrato, no el suplemento.

### ✔ La asociación factura → suplemento se hará por fecha de emisión
Esto es exactamente lo que hacen las comercializadoras reales.
Y evita confusiones al usuario.

### ✔ Solo un suplemento está activo, pero no necesariamente el de mayor número
Perfecto.
Esto implica que la vista debe filtrar por `estado = 'Activo'`, no por `MAX(n_suplemento)`.

---

## **2.2.2 y 2.2.3 Marco general de ventanas**
Confirmado:

- **Navegación tipo pantallas.**
- **Solo una visible.**
- **Nada de ventanas flotantes.**

Esto encaja perfectamente con tu marco general ya implementado para contratos.

---

## **2.2.4 Botón “Grabar factura”**
Aceptas la lógica mejorada:
→ habilitar solo cuando **todos los campos obligatorios** estén completos y válidos.

Perfecto.

---

## **2.4 Validaciones**

### ✔ Rango de días: 1 a 62
Correcto.
Hay meses consecutivos de 31 días (julio–agosto), así que 62 es el límite real.

### ✔ JOIN con suplementos
Sin problema: todos los suplementos tienen fecha fin.
Esto simplifica la validación.

### ✔ Importes y facturas de regularización
Aquí has hecho una reflexión muy buena:

- Potencias nunca serán cero.
- Impuestos nunca serán cero.
- Consumos pueden ser cero en tarifa plana.
- Facturas de regularización pueden tener total cero.

Esto nos lleva a una conclusión:

### **La validación debe ser flexible según el tipo de factura.**

Pero como aún no existe el campo “tipo de factura”, lo dejaremos así:

- **No permitir que TODOS los importes de potencia y consumo sean cero simultáneamente.**
- **Permitir total cero.**

Esto cubre el 99% de los casos reales.

---

## **2.5 Guardado**
Confirmas que usarás el mismo sistema que en contratos:

- Transacción
- Insert en tabla principal
- Recuperar id
- Insert en tablas secundarias
- Commit o rollback

Perfecto.

---

## **3. Tablas**

### ✔ `dias_factura` → INTEGER
Aceptado.

### ✔ `id_factura` como PK y FK en tablas secundarias
Aceptado.

### ✔ `total_potencia` capturado, no calculado
Perfectamente razonable.
Ya habrá tiempo de calcular en Comparativas.

---

