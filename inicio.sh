#!/bin/bash
# inicio.sh - Activa el entorno virtual y actualiza la rama de trabajo
# ⚠️ Ejecutar SIEMPRE con: source inicio.sh

# Ir al proyecto
cd ~/Desarrollo/Gestion_Suministros || return

echo "📁 Proyecto: Gestion_Suministros"
echo "🔄 Actualizando rama de trabajo 'desarrollo'..."

# Cambiar a la rama de desarrollo
git checkout desarrollo
git pull origin desarrollo
git status

echo "🟢 Activando entorno virtual..."
source ~/entornos/Gestion_Suministros/bin/activate

echo "🐍 Python activo: $(which python)"
echo "✔️ Entorno activado y repositorio actualizado. Listo para trabajar."
