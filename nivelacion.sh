#!/bin/bash
# ---------------------------------------------#
# Modulo: nivelacion.sh                        #
# Descripción: Nivelación completa y segura     #
# Autor: Antonio Morales                       #
# Fecha: 2026-03-04                            #
# ---------------------------------------------#

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

# ============================
#   🔎 DETECCIÓN DE CAMBIOS
# ============================

HAY_CAMBIOS_SIN_ADD=0
HAY_CAMBIOS_STAGING=0
HAY_COMMITS_PENDIENTES=0

# Cambios sin añadir
if ! git diff --quiet; then
    HAY_CAMBIOS_SIN_ADD=1
fi

# Cambios en staging
if ! git diff --cached --quiet; then
    HAY_CAMBIOS_STAGING=1
fi

# Commits locales pendientes de subir
if [ -n "$(git log origin/desarrollo..desarrollo)" ]; then
    HAY_COMMITS_PENDIENTES=1
fi

# ============================
#   📝 PROCESO DE NIVELACIÓN
# ============================

# 1) Añadir cambios sin añadir
if [ $HAY_CAMBIOS_SIN_ADD -eq 1 ]; then
    echo "📝 Hay cambios sin añadir. Añadiendo..."
    git add -A
    HAY_CAMBIOS_STAGING=1
fi

# 2) Commit si hay algo en staging
if [ $HAY_CAMBIOS_STAGING -eq 1 ]; then
    COMMIT_MSG="Nivelaccion manual: Terminada la rama analisis oferta externa. $(date '+%Y-%m-%d %H:%M')"
    echo "💾 Realizando commit: $COMMIT_MSG"
    git commit -m "$COMMIT_MSG"
    HAY_COMMITS_PENDIENTES=1
fi

# 3) Push si hay commits locales pendientes
if [ $HAY_COMMITS_PENDIENTES -eq 1 ]; then
    echo "⬆️ Subiendo commits pendientes a GitHub..."
    git push origin desarrollo
    echo "🟢 Nivelación completada correctamente."
else
    echo "✔️ No hay nada que subir. Todo está sincronizado."
fi

echo "🏁 Proceso de nivelación finalizado."
