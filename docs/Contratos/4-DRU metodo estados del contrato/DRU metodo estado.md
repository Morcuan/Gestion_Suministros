# DRU Estados de contrato

## Objetivo del metodo

    -Definir que estados puede tener un contrato dentro del proyecto.

## ¿Que estados pueden tener los contratos o suplementos?

    Primero debemos definir que caracteristicas tiene el estado de un contrato entre ellas podemos distinguir las siguientes:

    - El estado de un contrato siempre se determina con el ultimo suplemento (maximo numero de suplemento) registrado en la base de datos.
    - El estado de un contrato es un dato "vivo" que puede variar durante su vida y que por esa razón se debe determina en cada ocasion que se necesite.
    - Por esta razon anterior el estado de un contrato no se almacena en BD.
    - La determinacion del estado de un contrato se hará siempre con las fechas de efecto y fin de efecto del suplemento. Nunca con las fechas de inicio y fin del contrato que son meramente administrativas.

    Los estados de un contrato pueden ser:

    - **Anulado**
        El estado "Anulado" se define como el estado de aquel contrato que habiendo tomado efecto, aunque solo haya sido por un solo dia, ha sido anulado con fecha de anulacion anterior o igual a su fecha de fin de efecto. Naturalmente debe haber una fecha de anulacion.

    - **Caducado**
        El estado "Caducado" se define como el estado de aquel contrato que no ha sido anulado durante su vida, pero cuya fecha de fin de efecto es anterior a la fecha en la que se está determinando el estado. No existe por tanto fecha de anulacion.

    - **Sin efecto**
        El estado "Sin efecto" se define como el estado de aquel contrato que ha sido anulado con efecto el mismo dia de su fecha de efecto. Este estado solo puede darse en suplementos 0 o, si existen suplementos posteriores a este, todos los suplementos tienen la misma fecha de efecto.

    - **Futuro**
        El estado "Futuro" se define como el estado de aquel contrato que aunno ha entrado en vigor. Es decir cuya fecha de efecto es posterior al dia en el que se está determinando el estado.

    - **En vigor**
        El estado "En vigor" se define como el estado de aquel contrato en el que la fecha en la que se esta determinando su estado está comprendida entre la fecha de efecto y fin de efecto. Es un contrato activo.

## Donde y como se implementa la determinacion del estado

    - La determinacion del estado de un contrato no es un módulo independiente ni cuenta a nivel visual con formulario propio.

    - La determinacion del estado se desarrollará como metodo o funcion en el modulo logica_negocio.py

    - Este metodo será importado o invocado desde cualquier modulo que lo necesite. Por ejemplo en los diferentes modulos de lista de contratos. Para mostrar el estado se modificarán los modulos de lista de contrato para añadir el estado en cada contrato

    - Los campos de BD que determinan el estado son:

        De contratos_identificacion:

            - efec_suple (fecha de efecto del suplemento)
            - fin_suple (fecha de fin de efecto del suplemento)
            - fec_anulacion (fecha de anulacion del suplemento)

        ** estos campos, con igual nombre, están incluidos en la vista vista_contratos que se utiliza en los modulos de lista de contrato.**

