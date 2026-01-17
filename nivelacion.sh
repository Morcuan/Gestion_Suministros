#!/bin/bash
# nivelacion.sh - Guarda automáticamente todos los cambios en la rama 'desarrollo'
# ⚠️ Ejecutar con: source nivelacion.sh

# Ir al proyecto
cd ~/Desarrollo/Gestion_Suministros || return

echo "📁 Nivelando proyecto Gestion_Suministros"
echo "🔍 Estado actual:"
git status

# Comprobar si hay cambios
if git diff --quiet && git diff --cached --quiet; then
    echo "✔️ No hay cambios que guardar."
    return
fi

echo "📝 Añadiendo todos los cambios..."
git add -A

# Crear mensaje de commit limpio y en una sola línea
COMMIT_MSG="Elininacion de cualquier referencia a OCU_SOLAR en los modulos" \
        #-m "Hacer que nivelacion.sh cierre el entorno" \
        #-m "Prueba de commit multilinea" \
        -m "$(date '+%Y-%m-%d %H:%M')"

echo "💾 Realizando commit: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

echo "⬆️ Enviando cambios a la rama 'desarrollo'..."
git push origin desarrollo

echo "✔️ Nivelación completada."

echo "🔻 Cerrando entorno virtual..."
deactivate || true
echo "🟤 Entorno virtual desactivado. Sesión finalizada."

