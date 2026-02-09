Perfecto, Antonio. Aquí tienes la **versión 1.1 del DRU**, ya corregida e integrada con todas tus observaciones. He reescrito los puntos necesarios para que reflejen exactamente el estado real del proyecto y el flujo correcto de navegación, y he ajustado la parte del marco general para que quede claro que la integración es **desde el primer momento**.

Lo dejo limpio, cohesionado y listo para trabajar.

---

# 📘 **DRU — Módulo de Consultas Integradas (Versión 1.1)**  
*Revisado e integrado con las aclaraciones de Antonio*

---

## 🎯 **1. Objetivo del módulo**

El módulo de **Consultas Integradas** tiene como finalidad ofrecer una visión completa y coherente de la información almacenada en el sistema, unificando en un único flujo la consulta de **contratos** y **facturas**.

La premisa fundamental es que:

- Un **contrato** sin sus facturas asociadas está incompleto.  
- Una **factura** sin su contrato de origen también está incompleta.  

La navegación debe ser **escalonada y reversible**, permitiendo avanzar y retroceder entre niveles de forma ordenada:

**Lista de contratos → Detalles del contrato → Lista de facturas → Detalles de factura**,  
y viceversa, siempre regresando por los mismos peldaños.

---

## 🧱 **2. Arquitectura general del módulo**

### 2.1. Acceso al módulo
- Se añadirá una opción **“Consultas”** en el menú general.
- Se eliminarán las opciones de consulta existentes dentro de los menús de **Contratos** y **Facturas**, ya que pasan a ser redundantes.

### 2.2. Estructura conceptual
El módulo se compone de cuatro niveles:

1. **Lista de contratos**  
2. **Detalles del contrato**  
3. **Lista de facturas asociadas**  
4. **Detalles de la factura**

Cada nivel dispone de un botón **Cancelar** que devuelve al nivel inmediatamente anterior, garantizando un flujo claro y sin callejones sin salida.

---

## 🔍 **3. Flujo de trabajo detallado**

### 3.1. Lista de contratos
- Se reutilizará el módulo ya existente para la selección de contratos.  
- Diferencias respecto al flujo de captura de facturas:
  - **Aceptar** → abre la **vista de detalles del contrato**.  
  - **Cancelar** → vuelve al menú general.

### 3.2. Vista de detalles del contrato
- Esta ventana **debe reconstruirse**, ya que no existe en la versión 2.0 actual.
- Se tomará como base la ventana de **creación de contrato**, reorganizando campos y añadiendo los JOINs necesarios para mostrar nombres en lugar de IDs.
- Botones:
  - **Cancelar** → vuelve a la lista de contratos.  
  - **Ver facturas** → abre la lista de facturas asociadas.

### 3.3. Lista de facturas del contrato
- Se generará dinámicamente a partir del contrato seleccionado.
- Campos mínimos:
  - Número de factura  
  - Fecha de emisión  
  - Fecha de inicio  
  - Fecha de fin  
  - Importe total  
- Botones:
  - **Detalles factura** → abre la vista de detalles de la factura seleccionada.  
  - **Cancelar** → vuelve a la vista de detalles del contrato.

### 3.4. Vista de detalles de la factura
- Nueva ventana a crear.
- Se evaluará la recuperación de la ventana de **captura de factura** desarrollada en la versión del día 4 (rama *backup*), ya que su estructura y automatismos son adecuados para adaptarla como vista de detalles.
- Debe mostrar:
  - Datos generales  
  - Periodos y consumos  
  - Importes desglosados  
  - Totales calculados  
- Botón:
  - **Cancelar** → vuelve a la lista de facturas.

---

## 🧩 **4. Consideraciones técnicas**

### 4.1. Reutilización de módulos existentes
- La lista de contratos se reutiliza casi íntegramente.
- La vista de detalles del contrato debe reconstruirse.
- La ventana de captura de factura previa puede servir como base para la vista de detalles.

### 4.2. Nuevas ventanas necesarias
- **Lista de facturas asociadas**  
- **Detalles de factura**  

Ambas deben seguir el estilo visual del proyecto.

### 4.3. Navegación y control de ventanas
- Cada ventana debe cerrarse al abrir la siguiente.  
- El botón **Cancelar** siempre devuelve al nivel anterior.  
- No debe existir ningún flujo que deje ventanas huérfanas o inaccesibles.

### 4.4. Integración en el marco general de ventanas
Este módulo debe integrarse **desde el inicio** en el marco general de ventanas (menú lateral + zona de proceso), garantizando coherencia visual y estructural con el resto del proyecto.

---

## 🧪 **5. Pruebas previstas**

- Verificar carga correcta de la lista de contratos.  
- Confirmar que la vista de detalles del contrato no se abre sin selección.  
- Validar que la lista de facturas muestra solo las asociadas al contrato.  
- Comprobar funcionamiento de todos los botones Cancelar.  
- Revisar JOINs para mostrar nombres de compañía y población.  
- Asegurar que no se producen cierres inesperados ni ventanas huérfanas.  
- Validar cálculos y totales en la vista de detalles de factura.

---

## 📌 **6. Pendientes identificados**

- Reconstruir la vista de detalles del contrato.  
- Recuperar y adaptar la ventana de captura de factura (rama backup).  
- Crear la lista de facturas asociadas.  
- Ajustar estética general al marco visual.  
- Integrar sufijos y magnitudes desde `sufijos.py`.  
- Preparar datos de prueba para validar el flujo completo.

---

## 🗺️ **Diagrama de flujo**


┌──────────────────────────┐
│      Menú General        │
└─────────────┬────────────┘
              │
              ▼
┌──────────────────────────┐
│     Opción: Consultas    │
└─────────────┬────────────┘
              │
              ▼
┌──────────────────────────┐
│   Lista de Contratos     │
│  (selección obligatoria) │
└───────┬─────────┬────────┘
        │         │
        │         └───────────────► [Cancelar] → Vuelve al Menú General
        │
        └──────────────────────────► [Aceptar]
                                      │
                                      ▼
                    ┌────────────────────────────────┐
                    │   Detalles del Contrato        │
                    │ (Identificación / Energía /    │
                    │          Otros)                │
                    └───────────┬───────────┬────────┘
                                │           │
                                │           └────────► [Cancelar]
                                │                        Vuelve a Lista de Contratos
                                │
                                └──────────────────────► [Ver facturas]
                                                        │
                                                        ▼
                        ┌──────────────────────────────────────────┐
                        │      Lista de Facturas del Contrato      │
                        │ (número, emisión, inicio, fin, importe)  │
                        └───────────┬───────────────┬─────────────┘
                                    │               │
                                    │               └────────────► [Cancelar]
                                    │                                Vuelve a Detalles del Contrato
                                    │
                                    └──────────────────────────────► [Detalles factura]
                                                                     │
                                                                     ▼
                        ┌──────────────────────────────────────────┐
                        │        Detalles de la Factura            │
                        │ (datos generales, periodos, consumos,    │
                        │  importes, desglose, etc.)               │
                        └───────────────────────┬──────────────────┘
                                                │
                                                └───────────────► [Cancelar]
                                                                Vuelve a Lista de Facturas







