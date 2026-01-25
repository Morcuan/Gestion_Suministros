#!/bin/bash
# nivelacion.sh - Guarda automáticamente todos los cambios en la rama 'desarrollo'
# ⚠️ Ejecutar SIEMPRE con: source nivelacion.sh

echo "📁 Nivelando proyecto Gestion_Suministros"

# Ir al proyecto
cd ~/Desarrollo/Gestion_Suministros || {
    echo "❌ No se pudo acceder al directorio del proyecto."
    return
}

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
COMMIT_MSG="Nivelaccion manual, Finalizacion del modulo main_window.
Solucionado el problema del menu lateral, integradas tres paletas de colores,
integrado la opcion >acerca de...< integrados iconos en las opciones
generales y opciones secundarias. $(date '+%Y-%m-%d %H:%M')"

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


