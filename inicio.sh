#!/bin/bash
# inicio.sh - Activa el entorno virtual, actualiza la rama de trabajo y crea backup diario
# ⚠️ Ejecutar SIEMPRE con: source inicio.sh

echo "📁 Proyecto: Gestion_Suministros"

# ============================
#   📌 IR AL DIRECTORIO DEL PROYECTO
# ============================

PROYECTO="$HOME/Desarrollo/Gestion_Suministros"
cd "$PROYECTO" || {
    echo "❌ No se pudo acceder al directorio del proyecto."
    return
}

# ============================
#   📦 BACKUP AUTOMÁTICO
# ============================

echo "🗂️ Creando copia de seguridad diaria..."

FECHA=$(date +"%d%m%y")
NOMBRE="Gestion_Suministros_${FECHA}.tar.gz"

# Crear backup SIEMPRE fuera del proyecto para evitar errores de tar
TMP_BACKUP="/tmp/$NOMBRE"

tar --exclude="venv" \
    --exclude="*/__pycache__" \
    -czf "$TMP_BACKUP" .

if [ $? -ne 0 ]; then
    echo "❌ Error al crear el archivo TAR."
    return
fi

echo "🟢 Backup creado temporalmente en: $TMP_BACKUP"

# ============================
#   💽 COPIA AL DISCO USB
# ============================

DESTINO="/run/media/antoniom/ALMACEN/Proyecto_20"

if mount | grep -q "/run/media/antoniom/ALMACEN"; then
    echo "💽 Disco USB detectado."
else
    echo "⚠️ No se detecta el disco USB montado en /run/media/antoniom/ALMACEN"
    echo "⏳ Esperando 3 segundos..."
    sleep 3
fi

if cp "$TMP_BACKUP" "$DESTINO/" 2>/dev/null; then
    echo "🟢 Backup copiado correctamente a: $DESTINO/$NOMBRE"
else
    echo "❌ Error al copiar el backup al disco USB."
    echo "   (Puede no estar montado o no tener permisos)"
fi

echo ""
read -p "❓ ¿Quieres borrar el archivo temporal $TMP_BACKUP? (s/n): " RESP

if [[ "$RESP" =~ ^[sS]$ ]]; then
    rm "$TMP_BACKUP"
    echo "🧹 Archivo temporal eliminado."
else
    echo "📦 Archivo temporal conservado en /tmp."
fi
echo ""

# ============================
#   🔄 FLUJO GIT
# ============================

echo "🌐 Comprobando conexión a GitHub..."
if ping -c 1 github.com &> /dev/null; then
    echo "🟢 Conexión OK"
else
    echo "⚠️ No hay conexión a GitHub. Continuando en modo local."
fi

BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "desarrollo" ]; then
    echo "🔄 Cambiando de '$BRANCH' a 'desarrollo'..."
    git checkout desarrollo
fi

echo "⬇️ Actualizando rama 'desarrollo'..."
git pull origin desarrollo

echo "🧭 Últimos commits:"
git --no-pager log --oneline -5

echo "📌 Estado del repositorio:"
git status

# ============================
#   🐍 ACTIVAR ENTORNO VIRTUAL
# ============================

VENV_PATH="$PROYECTO/venv/bin/activate"

if [[ -z "$VIRTUAL_ENV" ]]; then
    if [ -f "$VENV_PATH" ]; then
        echo "🟢 Activando entorno virtual..."
        source "$VENV_PATH"
    else
        echo "❌ No se encontró el entorno virtual."
        echo "   Puedes crearlo con:"
        echo "   python3 -m venv venv"
        return
    fi
else
    echo "ℹ️ El entorno virtual ya estaba activo: $VIRTUAL_ENV"
fi

echo "🐍 Python activo: $(which python)"
echo "✔️ Entorno listo, repositorio actualizado y backup generado."
