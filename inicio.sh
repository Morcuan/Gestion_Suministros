#!/bin/bash
# inicio.sh - Activa el entorno virtual y actualiza la rama de trabajo
# ⚠️ Ejecutar SIEMPRE con: source inicio.sh

echo "📁 Proyecto: Gestion_Suministros"

# Ir al proyecto
cd ~/Desarrollo/Gestion_Suministros || {
    echo "❌ No se pudo acceder al directorio del proyecto."
    return
}

# Comprobar si hay conexión a GitHub
echo "🌐 Comprobando conexión a GitHub..."
if ping -c 1 github.com &> /dev/null; then
    echo "🟢 Conexión OK"
else
    echo "⚠️ No hay conexión a GitHub. Continuando en modo local."
fi

# Asegurar que estamos en la rama correcta
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "desarrollo" ]; then
    echo "🔄 Cambiando de '$BRANCH' a 'desarrollo'..."
    git checkout desarrollo
fi

# Actualizar repositorio
echo "⬇️ Actualizando rama 'desarrollo'..."
git pull origin desarrollo

# Mostrar resumen de commits recientes
echo "🧭 Últimos commits:"
git --no-pager log --oneline -5

# Mostrar estado
echo "📌 Estado del repositorio:"
git status

# Activar entorno virtual
VENV_PATH="~/Desarrollo/Gestion_Suministros/venv/bin/activate"

if [ -f ~/Desarrollo/Gestion_Suministros/venv/bin/activate ]; then
    echo "🟢 Activando entorno virtual..."
    source ~/Desarrollo/Gestion_Suministros/venv/bin/activate
else
    echo "❌ No se encontró el entorno virtual."
    echo "   Puedes crearlo con:"
    echo "   python3 -m venv venv"
    return
fi

echo "🐍 Python activo: $(which python)"
echo "✔️ Entorno activado y repositorio actualizado. Listo para trabajar."
