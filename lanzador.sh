# ------------------------------------------              #
# Modulo: lanzador.sh                                     #
# Descripción: Lanzador del proyecto Gestion_Suministros  #
# Autor: Antonio Morales                                  #
# Fecha: 2026-02-09                                       #
# --------------------------------------------------------#

#!/usr/bin/env bash
# Lanzador del proyecto Gestion_Suministros
# Ejecutar desde la terminal integrada de VS Code dentro del proyecto

set -euo pipefail

# Ruta del entorno virtual (CORREGIDO)
VENV_DIR="$HOME/Desarrollo/Gestion_Suministros/venv"

# Comprobación: ¿estamos en el proyecto correcto?
if [[ ! -f "main.py" ]]; then
  echo "ERROR: No se encuentra main.py en el directorio actual."
  echo "Asegúrate de estar en ~/Desarrollo/Gestion_Suministros"
  exit 1
fi

# Comprobación del entorno virtual
if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
  echo "ERROR: No se encuentra el entorno virtual en:"
  echo "       $VENV_DIR"
  echo "       Crea uno con: python3 -m venv venv"
  exit 1
fi

echo "🟢 Activando entorno virtual..."
source "$VENV_DIR/bin/activate"

echo "🐍 Python activo: $(which python)"

echo "🚀 Lanzando Gestion_Suministros..."
exec python3 main.py

