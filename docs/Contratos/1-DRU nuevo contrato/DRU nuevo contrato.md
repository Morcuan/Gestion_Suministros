

# 📄 **DRU – Módulo “Nuevo Contrato” (Versión inicial)**

## 🧭 **1. Objetivo general**
El módulo **Nuevo Contrato** permitirá al usuario introducir los datos necesarios para dar de alta un contrato en la base de datos.
El proceso se basará en una arquitectura clara y modular, separando estrictamente:

- **Vista** → `formulario_contrato.py`
- **Lógica y validaciones** → `nuevo_contrato.py`
- **Persistencia** → funciones de BD ya existentes o nuevas funciones específicas
    **APORTACION**
    Se creará tambien un nuevo modulo de funciones BD que contendrá los insert y updates de las tablas segun los procesos las necesiten. Este modulo solo contendrá funciones de BD descritas.
    **FIN APORTACION**
- **Navegación** → `main_window.py`

    **APORTACION**
    - **Entrada y Conexion a BD** → `main.py`
        Todos los modulos recibiran la conexion a BD desde main.py
    **FIN APORTACION**

El objetivo es garantizar simplicidad, mantenibilidad y ausencia de duplicación de lógica o interfaz.

---

## 🧱 **2. Arquitectura del módulo**

### **2.1. formulario_contrato.py (Vista pura)**
Un formulario genérico, reutilizable, sin lógica de negocio.

#### **Responsabilidades**
- Mostrar los campos del contrato (vacíos o con datos).
- Permitir al usuario introducir o modificar valores.
- Devolver los datos introducidos cuando se le solicite.
- Cargar datos existentes cuando se le proporcionen.
- Gestionar únicamente la **presentación visual**.

#### **NO debe hacer**
- Validaciones.
- Guardado en BD.
- Acceso a ficheros.
- Emisión de señales de guardado.
- Lógica de negocio.
- Navegación entre ventanas.

#### **Funciones mínimas**
- `cargar_datos(datos_dict)`
- `obtener_datos()`
- `limpiar()`
- `set_modo(modo)` (opcional: “nuevo” / “modificar”)

---

### **2.2. nuevo_contrato.py (Lógica de alta)**
Módulo controlador responsable del proceso completo de creación de un contrato.

#### **Responsabilidades**
- Crear una instancia de `FormularioContrato`.
- Mostrar el formulario en pantalla.
- Recoger los datos introducidos por el usuario.
**APORTACION**
- Encargarse de la navegacion por los campos del formulario:
    - Suplemento no editable (automaticamente 0 en nuevo contrato)
    - Fin contrato no editable (automaticamente + 10 años de fecha inicio contrato)
    - Efecto suplemento = fecha inicio de contrato
    - Fin efecto suplemento = fecha fin contrato
    - Fec anulacion no editable
    - alguna otra a determinar.
- Validar los datos:
  - Fechas en formato dd/mm/yyyy → convertir a ISO.
  - Campos obligatorios.
  - Tipos numéricos.
  - Coherencia entre fechas.
- Preparar el diccionario final para la BD.
- Insertar el contrato en la base de datos.
- Gestionar el flujo posterior:
  - Limpiar formulario.
  - Cerrar ventana.
  - Mostrar mensajes informativos.

#### **NO debe hacer**
- Pintar campos directamente.
- Acceder a widgets internos del formulario.
- Contener código de interfaz más allá de abrir/cerrar ventanas.
- Duplicar lógica de modificación.

---

### **2.3. main_window.py (Navegación)**
Controla el menú y decide qué módulo abrir.

#### **Responsabilidades**
- Al seleccionar “➕ Nuevo contrato”, crear una instancia de `NuevoContrato`.
- No debe contener lógica de validación ni de BD.
- No debe manipular directamente el formulario.

**APORTACION**
### **2.4 main.py**
Controla la entrada al proceso y se encarga de abrir y cerrar la conexion a BD

#### **Responsabilidades**
- Las descritas
**FIN APORTACION**

---

## 🧩 **3. Flujo funcional del proceso “Nuevo Contrato”**

1. El usuario selecciona **“➕ Nuevo contrato”** en el menú principal.
2. `main_window.py` instancia `NuevoContrato`.
3. `NuevoContrato` crea y muestra `FormularioContrato`.
4. El usuario introduce los datos.
5. El usuario pulsa **Guardar**.
6. `NuevoContrato`:
   - solicita los datos al formulario (`obtener_datos()`)
   - valida los datos
   - convierte fechas a ISO
   - prepara el diccionario final
   **APORTACION**
   - inserta el contrato en la BD
   Es preferible que el modulo no haga el insert en la BD directamente sino que de eso se encarge una utiliad nueva a crear para ese menester. Por tanto:
   - llama al modulo que se encarga del insert
   - El modulo hace el insert y devuelve el resultado
   **FIN APORTACION**

7. Si todo es correcto:
   - muestra mensaje de éxito
   - decide si limpia el formulario o cierra la ventana
8. Si hay errores:
   - muestra mensaje de error
   - no guarda nada

---

## 📦 **4. Datos mínimos del contrato**
**APORTACION**
Los datos minimos del nuevo contrato son aquellos que tenemos definidos en tres tablas:
- Contratos_identificacion:
            - id_contrato     INTEGER PRIMARY KEY AUTOINCREMENT,
            - ncontrato       TEXT NOT NULL,
            - suplemento      INTEGER NOT NULL,
            - compania        TEXT NOT NULL,
            - codigo_postal   TEXT NOT NULL,
            - fec_inicio      TEXT NOT NULL,
            - fec_final       TEXT NOT NULL,
            - efec_suple      TEXT NOT NULL,
            - fin_suple       TEXT NOT NULL,
            - fec_anulacion   TEXT,
            FOREIGN KEY (codigo_postal)   REFERENCES cpostales(codigo_postal)

- Contratos_energia:
            - id_contrato     INTEGER PRIMARY KEY,
            - ppunta          REAL NOT NULL,
            - pv_ppunta       REAL NOT NULL,
            - pvalle          REAL NOT NULL,
            - pv_pvalle       REAL NOT NULL,
            - pv_conpunta     REAL NOT NULL,
            - pv_conllano     REAL NOT NULL,
            - pv_convalle     REAL NOT NULL,
            - vertido         INTEGER NOT NULL,
            - pv_excedent     REAL NOT NULL,
            FOREIGN KEY (id_contrato) REFERENCES contratos_identificacion(id_contrato)

- Contratos_gastos:
            - id_contrato     INTEGER PRIMARY KEY,
            - bono_social     REAL NOT NULL,
            - alq_contador    REAL NOT NULL,
            - otros_gastos    REAL NOT NULL,
            - i_electrico     REAL NOT NULL,
            - iva             REAL NOT NULL,
            FOREIGN KEY (id_contrato) REFERENCES contratos_identificacion(id_contrato)

Todos los campos son obligatorios para un nuevo contrato pero con matices ya que como se ha mencionado existen campos que en un nuevo contrato son "automaticos" como son :
        - suplemento (numero de suplemento, 0 para un nuevo contrato)
        - fec_final (10 años a partir de fec_inicio ej: inicio 01/01/2026 final 31/12/2036, ej: inicio 15/05/2026 final 14/05/2036)
        - efec_suple en la creacion = a fec_inicio
        - fin_suple en la creacion = fec_final
        - fec_anulacion no editable
Por estos campos anteriores, en la creacion, no se permitirá acceder a ellos en el formulario. Se grabarán automaticamente con los valores descritos.

El campo id_contrato de la tabla de contratos solo es util para referencia interna de las tablas de contrato. El campo principal de relacion con facturas y con cualquier otra tabla o proceso es el numero de contrato (ncontrato)

**FIN APORTACION**

---

## 🔒 **5. Reglas de validación**
- Las fechas deben introducirse en formato **dd/mm/yyyy**.
    **APORTACION**
    Denominar el formato **dd/mm/yyyy** es incorrecto. dd en formato español es el acronimo de dia, mm el acronimo del mes y yyyy no tiene traduccion al español por lo tanto tomemos la convencion para etiquetas de que el formato a mostrar sea **dd/mm/aaaa**
    **FIN APORTACION**
- Se convertirán a formato ISO **yyyy-mm-dd** antes de guardar.
- Campos obligatorios no pueden estar vacíos.
- Campos numéricos deben ser válidos.
- La fecha fin no puede ser anterior a la fecha inicio.
- La fecha inicio no puede ser anterior al dia de hoy.
**APORTACION**
- El numero de contrato puede estar N veces en la tabla, pero la conbinacion ncontrato+suplemento SI ES UNICA EN LA TABLA. La relacion exacta entre ellos es que a un contrato le corresponden N suplementos y a un suplemento le corresponde un ncontrato.
**FIN APORTACION**

---

## 🗃️ **6. Persistencia**
**APORTACION**
- Se usarán la tablas  `contratos_identificacion, contratos_energía y contratos_gastos` en la BD.
- El módulo `nuevo_contrato.py` será el único responsable de llamar al modulo de utilidades para las funciones de inserción.
**FIN APORTACION**
- El formulario no interactúa con la BD.

---

## 🧼 **7. Objetivo de esta arquitectura**
- Evitar módulos gigantes.
- Evitar duplicación de lógica.
- Evitar formularios con lógica interna.
- Facilitar mantenimiento.
- Permitir reutilizar el formulario en:
  - nuevo contrato
  - modificación de contrato
  - futuras ampliaciones

