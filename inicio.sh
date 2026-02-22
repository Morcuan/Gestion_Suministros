#                                                         #
# Modulo: inicio.sh                                       #
# Descripción: Inicialización del entorno de trabajo      #
# Autor: Antonio Morales                                  #
# Fecha: 2026-02-09                                       #
# ------------------------------------            --------#

#!/bin/bash
# inicio.sh - Activa el entorno virtual, actualiza la rama de trabajo y crea backup diario
# ⚠️ Ejecutar SIEMPRE con: source inicio.sh

echo "📁 Proyecto: Gestion_Suministros"

# Ir al proyecto
cd ~/Desarrollo/Gestion_Suministros || {
    echo "❌ No se pudo acceder al directorio del proyecto."
    return
}

# ============================
#   📦 BACKUP AUTOMÁTICO
# ============================
echo "🗂️ Creando copia de seguridad diaria..."

FECHA=$(date +"%d%m%y")
NOMBRE="Gestion_Suministros_${FECHA}.tar.gz"

# Ruta de la tarjeta SD (AJUSTA si es necesario)
DESTINO="/media/antonio/ALMACEN/Proyecto_20"

# Detectar si la SD está montada
#if mount | grep -q "$DESTINO"; then
#    SD_MONTADA=true
#    echo "💽 SD detectada en: $DESTINO"
#else
#    SD_MONTADA=false
#    echo "⚠️ No se detecta la SD montada en $DESTINO"
#fi

# Crear backup excluyendo venv y __pycache__
tar --exclude="venv" \
    --exclude="*/__pycache__" \
    -czf "$NOMBRE" .


    cp "$NOMBRE" "$DESTINO/"
    echo "🟢 Backup copiado a la ALMACEN: $DESTINO/$NOMBRE"

# Preguntar si borrar el archivo .tar.gz para evitar que Git lo detecte
echo ""
read -p "❓ ¿Quieres borrar el archivo temporal $NOMBRE para evitar que Git lo detecte? (s/n): " RESP

if [ "$RESP" = "s" ] || [ "$RESP" = "S" ]; then
    rm "$NOMBRE"
    echo "🧹 Archivo temporal eliminado: $NOMBRE"
else
    echo "📦 Archivo conservado en el directorio del proyecto."
    echo "⚠️ Recuerda borrarlo manualmente antes de hacer commits."
fi
echo ""

# ============================
#   🔄 FLUJO ORIGINAL
# ============================

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
echo "✔️ Entorno activado, repositorio actualizado y backup generado. Listo para trabajar."
