# DRU – Interfaz General del Proyecto  
**Proyecto:** Gestion_suministros 2.0.A  
**Documento:** DRU-Interfaz_general  
**Versión:** 1.0  
**Fecha:** [23/01/2026]  
**Autor:** Antonio  

---

## 1. Objetivo del módulo  
Definir la estructura visual, el estilo, la navegación y el comportamiento general de la interfaz gráfica de Gestion_suministros 2.0
Este DRU establece el marco común para todas las ventanas y procesos del sistema, garantizando coherencia, claridad y facilidad de uso.

---

## 2. Alcance  

### 2.1 Funcionalidades incluidas  
- Diseño del **marco general** de la aplicación.  
- Definición del **menú lateral** y su comportamiento.  
- Definición de la **zona de contenido** donde se cargarán los módulos.  
- Estilo visual general: colores, botones, tipografías, tamaños.  
- Reglas de navegación entre módulos.  
- Comportamiento de apertura y cierre de ventanas internas.  
- Comportamiento de mensajes, diálogos y avisos.

### 2.2 Funcionalidades excluidas  
- Lógica interna de cada módulo (contratos, facturas, consumos…).  
- Validaciones específicas de cada proceso.  
- Diseño detallado de ventanas particulares (se definirán en sus DRU propios).  
- Modelos de datos o estructura de base de datos.

---

## 3. Descripción funcional detallada  

### 3.1 Estructura general  
La aplicación tendrá una **ventana principal única**, que actuará como contenedor de todos los procesos.

La ventana principal se divide en dos áreas:

#### A) Menú lateral (panel izquierdo)  
- Ancho fijo.  
- Contendrá los menús principales del sistema, que a su vez contendrán las opciones operativas:  
  - Inicio  
  - Contratos
     - Nuevo contrato 
     - Operaciones en contratos
        - Consulta
        - Modificación 
        - Anulacion
  - Facturas  
    - misma estructura
  - Consumos  
  - Utilidades  
  - Configuración  
  - Salir  
- Cada opción abrirá su módulo correspondiente **dentro de la zona de contenido**, nunca en ventanas flotantes externas.

#### B) Zona de contenido (panel derecho)  
- Área donde se cargarán las pantallas de cada módulo.  
- Solo habrá **una pantalla visible a la vez**.  
- Los módulos podrán tener subpantallas internas, pero siempre dentro de esta zona.

---

### 3.2 Comportamiento del menú lateral  
- El menú permanece siempre visible.  
- Al seleccionar una opción, se resalta visualmente.
- Una vez seleccionada la opción se despliegan, si las hay, sus opciones.
- No se permiten múltiples módulos abiertos simultáneamente.  
- Si un módulo tiene cambios sin guardar, se mostrará un aviso antes de cambiar de sección.

---

### 3.3 Comportamiento de las ventanas internas  
- Cada módulo se carga como un **widget** dentro de la zona de contenido.  
- No se abrirán ventanas independientes salvo:  
  - diálogos de confirmación  
  - mensajes de error  
  - selectores de fecha  
  - selectores de archivo  
- Los botones de navegación interna (Guardar, Cancelar, Volver) actuarán **solo dentro del módulo**, sin afectar al marco general.

---

## 4. Diseño visual  

### 4.1 Paleta de colores  
Se define una paleta base para toda la aplicación:

- **Color primario:** azul suave (para botones principales y encabezados)  
- **Color secundario:** gris claro (fondos y paneles)  
- **Color de acento:** verde o naranja (acciones importantes)  
- **Color de error:** rojo suave  
- **Color de texto:** negro/gris oscuro  

La paleta exacta se definirá en el módulo `estilo.py`.

---

### 4.2 Tipografías  
- Fuente principal: Sans Serif (DejaVu Sans, Noto Sans o similar).  
- Tamaños estándar:  
  - Títulos: 16  
  - Texto normal: 13
  - Botones: 12  

---

### 4.3 Botones  
Todos los botones del sistema seguirán un estilo uniforme:

- Bordes redondeados suaves.  
- Color primario para acciones principales (Guardar, Aceptar).  
- Color neutro para acciones secundarias (Cancelar, Volver).  
- Iconos opcionales, pero consistentes.  
- Tamaño mínimo estándar para evitar botones diminutos.

El estilo se centralizará en `estilo.py`.

---

## 5. Reglas de navegación  

- El usuario siempre debe saber **dónde está** y **qué está haciendo**.  
- Cada módulo tendrá un título visible en la zona de contenido.  
- No se permiten ventanas flotantes salvo diálogos.  
- El botón “Salir” del menú lateral cerrará la aplicación previa confirmación.  
- Los módulos deben poder volver a su estado inicial sin cerrar la aplicación.

---

## 6. Flujos de proceso  

### 6.1 Flujo principal  
1. El usuario abre la aplicación.  
2. Se muestra la ventana principal con el menú lateral y la pantalla de Inicio.  
3. El usuario selecciona una opción de menú o una opción de submenú, que llama un módulo.  
4. El módulo se carga en la zona de contenido.  
5. El usuario interactúa con el módulo.  
6. Puede volver al menú lateral en cualquier momento.  
7. Puede cerrar la aplicación desde el menú lateral.

---

### 6.2 Flujos alternativos  
- Si un módulo tiene cambios sin guardar, se mostrará un diálogo:  
  - Guardar  
  - Descartar  
  - Cancelar navegación  

- Si ocurre un error, se mostrará un mensaje modal con estilo uniforme.

---

## 7. Requisitos no funcionales  

- **Coherencia visual:** todas las ventanas deben seguir el mismo estilo
- **Mantenibilidad:** el estilo debe estar centralizado en un único módulo.  
- **Escalabilidad:** el marco debe permitir añadir nuevos módulos sin romper nada.  
- **Usabilidad:** navegación clara, botones visibles, mensajes comprensibles.  
- **Robustez:** evitar ventanas duplicadas o procesos paralelos no controlados.

---

## 8. Casos de uso  

### CU-01: Navegar entre módulos  
- El usuario selecciona “Contratos”.  
   - Se despliegan, si las tienen, sus opciones
- El usuario elige la opcion
- Se carga la pantalla de contratos en la zona de contenido.  

### CU-02: Intentar salir con cambios sin guardar  
- El usuario está modificando un contrato.  
- Intenta ir a “Facturas”.  
- Aparece un diálogo de confirmación.  

### CU-03: Cerrar la aplicación  
- El usuario pulsa “Salir”.  
- Se muestra un diálogo de confirmación.  

---

## 9. Batería de pruebas  

- Verificar que el menú lateral funciona correctamente.  
- Verificar que solo se muestra un módulo a la vez.  
- Verificar que los estilos se aplican de forma uniforme.  
- Verificar que los diálogos aparecen cuando deben.  
- Verificar que no se abren ventanas flotantes no permitidas.  

---

## 10. Criterios de cierre  

El DRU se considera implementado cuando:

- El marco general está construido.  
- El menú lateral funciona.  
- La zona de contenido carga módulos correctamente.  
- El estilo visual está centralizado.  
- La navegación es estable y coherente.  
- Todas las pruebas pasan.  

---

