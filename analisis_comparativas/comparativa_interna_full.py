#!/usr/bin/env python3
# -------------------------------------------------------------#
# Módulo: ejecutar_proceso_completo.py                         #
# Descripción: Orquesta el proceso completo de comparativa     #
# Autor: Antonio                                               #
# Fecha: 2026-04-13                                            #
# Versión: 2.0                                                 #
# -------------------------------------------------------------#

import logging

from analisis_comparativas.comparador_interno import comparar_facturacion_interna
from analisis_comparativas.crear_entorno_interno import crear_entorno_interno
from analisis_comparativas.recalculo_interno import recalcular_facturas_interno

logger = logging.getLogger(__name__)


def ejecutar_proceso_completo(conn):
    logger.info("Iniciando comparativa interna")

    crear_entorno_interno(conn)
    logger.info("Entorno interno creado")

    resultado = recalcular_facturas_interno(conn)
    logger.info(f"Recalculo completado: {resultado}")

    comparar_facturacion_interna(conn)

    print("🏁 COMPARATIVA INTERNA FINALIZADA")
