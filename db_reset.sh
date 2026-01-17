#!/bin/bash

echo "--------------------------------------------------"
echo "   Gestion_Suministros - Reinicialización de la BD"
echo "--------------------------------------------------"

DB_PATH="data/almacen.db"

# Confirmación
read -p "¿Seguro que deseas REINICIALIZAR la base de datos? (s/N): " confirm

if [[ "$confirm" != "s" && "$confirm" != "S" ]]; then
    echo "Operación cancelada."
    exit 1
fi

echo "Eliminando base de datos anterior..."
rm -f "$DB_PATH"

echo "Ejecutando db_init.py..."
python3 db_init.py

echo "---------------------------------------------"
echo "   Base de datos regenerada correctamente"
echo "---------------------------------------------"
