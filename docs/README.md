

# 📘 GESTION_SUMINIESTROS 

Aplicación de escritorio desarrollada en **Python + PySide6** para la gestión integral de contratos, consumos, facturación y comparativas de suministros.  
El proyecto está diseñado con un flujo de trabajo profesional, un entorno virtual aislado y scripts automatizados que facilitan el desarrollo diario.

---

# 🧱 Estructura del proyecto

```
Gestion_Suministros/
│
├── docs/
│   └── README.md
│
├── modules/
│   ├── consumos.py
│   ├── contratos.py
│   ├── facturas.py
│   ├── menus.py
│   ├── utilidades_bd.py
│   ├── utilidades_fc.py
│   ├── paletas.py
│   └── ...
│
├── tests/
│   ├── test_db.py
│   ├── test_ui.py
│   └── test_utils.py
│
├── inicio.sh
├── nivelacion.sh
├── lanzador.sh
├── requirements.txt
└── main.py
```

---

# 🧩 Arquitectura general

La aplicación sigue una arquitectura modular:

- **main.py** → punto de entrada  
- **menus.py** → menú principal y navegación  
- **contratos.py** → lógica de contratos (nuevo, modificación, consulta, baja)  
- **consumos.py** → gestión de consumos  
- **facturas.py** → gestión de facturación  
- **comparativas.py** → análisis comparativo  
- **utilidades_bd.py** → funciones de base de datos  
- **utilidades_fc.py** → funciones auxiliares  
- **paletas.py** → estilos y colores  

---

# 🧩 Diagrama conceptual de módulos

```
main.py
 ├── menus.py
 │     ├── contratos.py
 │     │      ├── contrato_nuevo
 │     │      ├── contrato_modificacion
 │     │      └── contrato_consulta
 │     ├── consumos.py
 │     ├── facturas.py
 │     └── comparativas.py
 │
 ├── utilidades_bd.py
 ├── utilidades_fc.py
 └── paletas.py
```

---

# ⚙️ Instalación

## 1. Clonar el repositorio

```
git clone https://github.com/kwrn6v27qg-max/Gestion_Suministros.git
cd Gestion_Suministros
```

## 2. Crear entorno virtual

```
python3 -m venv venv
```

## 3. Activar entorno virtual

Linux/macOS:

```
source venv/bin/activate
```

Windows:

```
venv\Scripts\activate
```

## 4. Instalar dependencias

```
pip install -r requirements.txt
```

---

# 🖥️ Ejecución de la aplicación

Con el entorno virtual activado:

```
python3 main.py
```

O usando el script dedicado:

```
./lanzador.sh
```

---

# ⚙️ Scripts del proyecto

## **inicio.sh**
Prepara el entorno de trabajo:

- Cambia al directorio del proyecto  
- Cambia a la rama `desarrollo`  
- Hace `git pull`  
- Activa el entorno virtual  
- Muestra la versión de Python activa  

**Uso:**

```
source inicio.sh
```

---

## **nivelacion.sh**
Guarda y sube los cambios al repositorio:

- Muestra `git status`  
- Añade todos los cambios  
- Crea un commit automático  
- Sube a la rama `desarrollo`  
- **Desactiva el entorno virtual al finalizar**  

**Uso:**

```
source nivelacion.sh
```

---

## **lanzador.sh**
Ejecuta la aplicación:

- Activa el entorno virtual  
- Lanza `main.py`  
- Muestra la versión de Python activa  

**Uso:**

```
./lanzador.sh
```

---

# 🧪 Entorno virtual

El proyecto utiliza un entorno virtual dedicado:

```
Gestion_Suministros/venv/
```

El archivo `requirements.txt` contiene únicamente las dependencias reales necesarias para ejecutar la aplicación.

---

# 🧹 Archivos ignorados

El proyecto incluye un `.gitignore` que evita subir:

- `__pycache__/`
- `*.pyc`
- entornos virtuales (`venv/`, `.env/`)

---

# 🛠️ Estado actual del desarrollo

- Scripts de automatización corregidos y alineados  
- Entorno virtual limpio y regenerado  
- Dependencias actualizadas  
- Repositorio libre de archivos generados  
- Preparado para retomar el desarrollo funcional (ej. módulo “Contrato nuevo”)  

---

# 🗺️ Roadmap

## **Corto plazo**
- Revisar y corregir el flujo de “Contrato nuevo”
- Unificar estilos visuales en PySide6 (paletas, fuentes, tamaños)
- Añadir validaciones más robustas en formularios

## **Medio plazo**
- Implementar exportación de informes (PDF/Excel)
- Añadir gráficos de consumos y comparativas
- Mejorar la estructura de la base de datos

## **Largo plazo**
- Crear un instalador multiplataforma  
- Añadir soporte para plugins o módulos externos  
- Integrar API para datos externos de suministros  

---

# 📝 Changelog (resumen reciente)

### **2026-01-13**
- Regenerado `requirements.txt`  
- Creado `.gitignore`  
- Eliminados todos los `__pycache__` del repositorio  
- Corregidos `inicio.sh`, `nivelacion.sh` y `lanzador.sh`  
- Añadido cierre automático del entorno en `nivelacion.sh`  
- Limpieza general del proyecto  

---
