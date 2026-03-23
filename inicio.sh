#!/bin/bash
# inicio.sh - Activa el entorno virtual, actualiza la rama de trabajo y crea backup diario
# ⚠️ Ejecutar SIEMPRE con: source inicio.sh

echo "📁 Proyecto: Gestion_Suministros"

# ============================
#   📌 IR SIEMPRE AL DIRECTORIO DEL PROYECTO
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

DESTINO="/media/antoniom/ALMACEN/Proyecto_20"

# Crear backup SIEMPRE en el directorio del proyecto
tar --exclude="venv" \
    --exclude="*/__pycache__" \
    -czf "$NOMBRE" .

# Comprobar si la SD está montada
if mount | grep -q "$DESTINO"; then
    echo "💽 SD detectada en: $DESTINO"
else
    echo "⚠️ No se detecta la SD montada en $DESTINO"
    echo "⏳ Esperando 3 segundos por si acaba de montarse..."
    sleep 6
fi

# Intentar copiar a la SD
if cp "$NOMBRE" "$DESTINO/" 2>/dev/null; then
    echo "🟢 Backup copiado a la SD: $DESTINO/$NOMBRE"
else
    echo "❌ Error al copiar el backup a la SD"
    echo "   (Puede no estar montada o no tener permisos)"
fi

echo ""
read -p "❓ ¿Quieres borrar el archivo temporal $NOMBRE para evitar que Git lo detecte? (s/n): " RESP

if [[ "$RESP" =~ ^[sS]$ ]]; then
    rm "$NOMBRE"
    echo "🧹 Archivo temporal eliminado: $NOMBRE"
else
    echo "📦 Archivo conservado en el directorio del proyecto."
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
