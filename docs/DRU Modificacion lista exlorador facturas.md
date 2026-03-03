
# 📘 **## DRU MODIFICACIÓN LISTA DE CONTRATOS MENÚ ANÁLISIS -> EXPLORADOR DE FACTURAS**

## **1. Definición**

- En este momento la lista de contratos que aparece al llamar al modulo mencionado en el titulo es incorrecta, procede del modulo consulta_contratos.py que es un modulo obsoleto y que ya no utilizamos. 

- En su momento al modificar la lista de contratos según las ultimas especificaciones se decidió crear un modulo nuevo (lista_contratos.py), de tipo generalista, que aportara los datos necesarios para las distintas listas de los módulos en los procesos desarrollados.

- Estas listas características de cada rama de menú son módulos independientes que filtran la lista generalista devuelta por lista_contratos.py adaptándola a la necesidad de cada rama.

- La modularidad y la reutilización del máximo de módulos posible característica de gestión suministros 2.0 hace necesario para continuar con la misma dinámica, crear un modulo nuevo que recoja y presente la lista para la rama que intentamos modificar (en el titulo).



## **2. Flujo de trabajo y modificaciones a realizar**

1. Desde el Menú: **Análisis → Explorador de facturas**

Modificación a realizar:

2. Lista de contratos con un solo registro por contrato (igual que lista_contratos_modificar.py) construir la tabla con los mismos campos que en todas las listas y desde lista_contratos

Fin de modificación

3. Selección de contrato → botón “Detalles" -> Detalles de contrato

4. El resto de pantallas todo igual.

