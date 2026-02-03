#!/bin/bash
# nivelacion.sh - Guarda automáticamente todos los cambios en la rama 'desarrollo'
# ⚠️ Ejecutar SIEMPRE con: source nivelacion.sh

echo "📁 Nivelando proyecto Gestion_Suministros"

# Ir al proyecto
cd ~/Desarrollo/Gestion_Suministros || {
    echo "❌ No se pudo acceder al directorio del proyecto."
    return
}

# --- Verificar identidad Git ---
if ! git config user.name >/dev/null 2>&1 || ! git config user.email >/dev/null 2>&1; then
    echo "⚠️ Git no tiene configurado nombre o correo."
    echo "🛠️ Configurando identidad global..."
    git config --global user.name "Antonio"
    git config --global user.email "antonio@pepino.local"
    echo "✅ Identidad configurada: Antonio <antonio@pepino.local>"
else
    echo "🧾 Identidad Git detectada:"
    echo "   Nombre: $(git config user.name)"
    echo "   Correo: $(git config user.email)"
fi
# --- Fin verificación identidad Git ---

# Asegurar que estamos en la rama correcta
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "desarrollo" ]; then
    echo "⚠️ Estabas en la rama '$BRANCH'. Cambiando a 'desarrollo'..."
    git checkout desarrollo
fi

echo "🔍 Estado actual:"
git status

# Comprobar si hay cambios
if git diff --quiet && git diff --cached --quiet; then
    echo "✔️ No hay cambios que guardar."
    return
fi

echo "📝 Añadiendo todos los cambios..."
git add -A

# Crear mensaje de commit limpio
COMMIT_MSG="Nivelaccion manual, Modificacion de inicio.sh para controlar mejor las copias a SD y
borrar comprimido despues. Modificacion de db_init.py para crear 3 tablas de facturas separadas
para mas claridad y manejo. Creacion de facturas.py con la estructura de SQL conforme a las tres tablas.
DRU facturas completado y renombrado. Modificacion de la BD almacen para la creacion de las tres tablas
de facturas, la vista segun estas y borrado de la tabla unica de facturas.
 $(date '+%Y-%m-%d %H:%M')"

echo "💾 Realizando commit: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

# Comprobar remoto
if ! git remote | grep -q origin; then
    echo "❌ No existe el remoto 'origin'. No se puede hacer push."
    return
fi

echo "⬆️ Enviando cambios a la rama 'desarrollo'..."
git push origin desarrollo

echo "✔️ Nivelación completada."

# Cerrar entorno virtual si está activo
if [ -n "$VIRTUAL_ENV" ]; then
    echo "🔻 Cerrando entorno virtual..."
    deactivate || true
    echo "🟤 Entorno virtual desactivado. Sesión finalizada."
else
    echo "ℹ️ No había entorno virtual activo."
fi
