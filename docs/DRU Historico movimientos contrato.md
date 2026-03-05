
# 📘 **## DRU CREACION LISTA DE CONTRATOS MENÚ ANÁLISIS -> EXPLORADOR DE CONTRATOS**

## **1. Definición y motivación**

- Con la creación del concepto suplemento para realizar una modificación en un contrato, se ha hecho necesario la creación de un acceso para ver el histórico de movimientos del contrato puesto que en las listas de contratos se ha definido que solo se presente el ultimo suplemento.

- Este histórico de movimientos presentará todos los suplementos de un contrato previamente seleccionado en una lista de contratos que partirá, como todas las demás listas de contratos del proyecto gestión suministros desde lista_contratos.py

- Esa lista previa de selección del contrato, presentará los contratos con los mismos campos que las demás listas

- La lista de contratos, puesto que se trata de un histórico de movimientos, presentará el ultimo suplemento en cualquier estado.

- La modularidad y la reutilización del máximo de módulos posible característica de gestión suministros 2.0 hace necesario para continuar con la misma dinámica, crear un modulo nuevo que recoja y presente la lista para la rama que intentamos crear.



## **2. Flujo de trabajo**

1. Desde el Menú: **Análisis → Histórico contratos**


2. Se presenta una ventana con la Lista de contratos con un solo registro por contrato (igual que lista_contratos_modificar.py). Se construirá la tabla con los mismos campos que en todas las listas y desde lista_contratos

    * Botones "Cancelar" a la derecha, "Movimientos" a la izquierda
    * Con el botón cancelar salimos al menú general

3. Seleccionando un contrato en la lista → botón “Movimientos".

4. Se presenta una ventana con la Lista de suplementos del contrato anteriormente seleccionado, en cualquier estado ordenados por numero de suplemento desde el 0 hasta el N

    * Botones "Cancelar" a la derecha, "Detalles" a la izquierda
    * Con el botón "Cancelar" volvemos a la ventana de la lista de movimientos anterior.


5. Seleccionando un movimiento de la lista → botón "Detalles"

6. Se presenta la ventana "Detalles del movimiento" (posible detalles_contrato.py filtrada por suplemento)

    * Botones "Cancelar" a la derecha
    * Con el botón "Cancelar" volvemos a la ventana de movimientos del contrato

## **3. Navegación**

La navegación entre ventanas mantendrá lo establecido para todo el proyecto en cuanto al flujo de ventanas tanto en sentido descendente por la rama como en sentido ascendente por la misma.

## **4. Posibles módulos a crear y/o modificar**

- Creación de un modulo similar a lista_contratos_modificar.py nombrado como lista_contratos_historia.py

- Modulo que recupera la lista de contratos: lista_contratos.py

- Creación de la rama del menú general: main_window.py

