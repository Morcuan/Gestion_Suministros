# DESCRIPCION DEL PROCESO HISTORICO DE FACTURAS

    Todas las facturas están asociadas, primariamente, a un contrato unico. Estas facturas, tambien, están asociadas a un suplemento y por su calculo a una version del motor de calculo.

    Esta rama del menu desarrolla una consulta de facturas partiendo de un contrato y llegando hasta el detalle de los calculos asociados a la factura lo que permite, en un primer control comprobar que los calculos de la factura física recibida coinciden con los calculos realizados.

    A continuacion se describe el proceso y el flujo de pantallas asi como las dependencias que se derivan del calculo de las factruras.

# FLUJO DEL PROCESO

- Todos los modulos estarán en la carpeta analisis_factura que está en la raiz del proyecto

    - Entrada

        - Seleccionando en el menu "Analisis" la opcion "Historico de facturas"

- Flujo del proceso

    - Pantalla Lista de contratos

        En la lista de contratos aparecen los contratos que tenemos disponibles en bd en la que hay que seleccionar uno de ellos. Visualmente la lista está correcta.

        Cuenta con los botones:

            - "Seleccionar contrato" que nos lleva a la lista de facturas asociadas a ese contrato (se valida que haya un contrato seleccionado de la lista).

            - "Cancelar" que nos lleva a menu general.

        **El modulo lista_con_his_factura.py ya está en la carpeta (analisis_factura) y se le llama desde main_window.py correctamente. Como procede de la rama facturas, aunque la funcionalidad de mostrar la lista con los datos correctos ya la tiene y funciona correctamente es necesario modificarlo para que se adapte solo para una consulta, no necesita modos ni llamar a otros modulos (nueva factura, modificar... ) salvo al que se describe a continuacion.**

    - Pantalla lista de facturas

        En la lista de facturas aparecen las facturas asociadas al contrato seleccionado en el paso anterior. Visualmente necesita unas ligeras correcciones para reducir el tamaño de los campos:

            - Fecha emision
            - Inicio periodo
            - Fin periodo
            - Importe total

        Esta reduccion permitirá que el campo Nº Factura se muestre completo que es realmente la correcion visual que hay que hacer.


        Cuenta con dos botones:

            - "Seleccionar factura" que nos lleva a la pantalla "Detalles de la factura" que se describe en el siguiente punto.

            - "Cancelar" que nos devuelve a la lista de contratos.

        **El modulo seeccionar_his_factura.py ya está en la carpeta (analisis_factura) y está enlazado con el paso anterior correctamente (se muestra la lista de facturas). Al igual que el modulo anterior procede de facturas y tambien es necesario revisarlo y modificarlo para que se adapte a la rama donde no se necesitan modos ni llamar a modulos factura rectificar o factura anular por lo que solo debe llamar al modulo "Detalles de factura" que se describe a continuacion.**

    - Pantalla "Detalles de factura"

        En esta pantalla se mostrarán los datos identificativos de la factura mediante el modulo (formulario_his_factura.py) en modo solo lectura con los datos de la factura seleccionada en el paso anterior. No se mostrarán totalizaciones de la factura que se mostrarán en un paso posterior seleccionable mediante boton al uso.

        Este formulario rectificado contará con los botones sigientes:

            - "Mostrar calculos" que nos lleva a la pantalla "Detalles calculo"

            - "Cancelar" que nos devuelve a la lista de facturas.

        **El modulo formulario_his_factura.py ya está en la carpeta analisis_factura pero al igual que los otros dos modulos anteriores hay que revisarlo y modificarlo para que se adapte a la rama actual del proceso. Tambien hay que modificarlo para que contenga los botones descritos anteriormente y la llamada al modulo descrito posteriormente en este DRU.**

    - Pantalla "Detalles calculo"

        Este modulo es de nueva construccion. Esta pantalla se mostrará despues de que en la pantalla anterior "Detalles factura" se haya pulsado el boton "Detalles calculo". Esta pentalla debe ser un detalle exaustivo de la factura. Incluidos los calculos que están en la vista factura_calculos incluidos los detalles_json descrita mas abajo en este DRU. Puesto que es un modulo nuevo habrá que ajustarlo visualmente mediante pruebas.

        Esta pantalla contará con el boton:

            - "Cancelar" que nos devolverá a la pantalla anterior "Detalles de factura"

        La idea de la pantalla Detalles de calculo es que muestre, ademas de los totales que existen en la vista mencionada, la forma de llegar a ellos, por ejemplo  para calcular el precio de la potencia punta se utiliza el numero de dias de la factura, la potencia contratada y el precio unitario por Kw/h segun contrato. La formula seria:

        "28 dias factura * 4.4 kwh/ * 0.091074 € total" = 11.22 €

        siendo 28 dias factura * 4.4 kW * 0.091074 total = una etiqueta y el resultado eso, resultado...

        De esta forma se mostrarán todos los campos de la vista y los calculos del campo detalles_json. ademas


        **La pantalla se ajustará visualmente segun las necesidades durante las pruebas de la rama**

# DEPENDENCIAS

    Esta rama tiene dependencias y modulos que son necesarios utilizar en cuanto al calculo de las facturas.

    En la actualidad, la captura de nueva factura se calcula y se inserta en la vista factura_calculos en el proceso de nueva factura. Sin embargo tenemos facturas que se capturaron antes de esta nueva arquitectura y por tanto no están incluidas ni calculadas en la vista mencionada.

    Es necesario tener un modulo de recalculo de facturas para recalcular de una sola vez las que no estén en la vista. Este recalculo se puede utilizar en otras ramas del proceso. Por ejemplo, cuando se modifica un contrato, las posibles facturas cuyo inicio de periodo sea posterior a la toma de efecto de la modificacion se marcan en el campo "recalcular" de la tabla factura con un "1" y este modulo que hay que construir sería el encargado de recalcular las facturas concernidas. Por tanto hay que construir este modulo para que desde la rama utilidades -> Recalcular de facturas se puedan recalcular dichas facturas e incluirlas en la vista factura_calculos

# ESTRUCTURA DE LAS TABLAS CONCERNIDAS

    - vista factura_calculos:

            id_calculo      INTEGER PRIMARY KEY AUTOINCREMENT,
            nfactura        TEXT NOT NULL,
            fecha_calculo   TEXT NOT NULL,          -- formato ISO yyyy-mm-dd
            version_motor   TEXT NOT NULL,          -- ej: "1.0.0"
            total_energia   REAL NOT NULL,
            total_cargos    REAL NOT NULL,
            total_servicios REAL NOT NULL,
            total_iva       REAL NOT NULL,
            cloud_aplicado  REAL NOT NULL,
            cloud_sobrante  REAL NOT NULL,
            total_final     REAL NOT NULL,
            detalles_json   TEXT NOT NULL

    - facturas

            nfactura           TEXT PRIMARY KEY,
            inicio_factura     TEXT NOT NULL,
            fin_factura        TEXT NOT NULL,
            dias_factura       INTEGER NOT NULL,
            fec_emision        TEXT NOT NULL,
            consumo_punta      REAL,
            consumo_llano      REAL,
            consumo_valle      REAL,
            excedentes         REAL,
            importe_compensado REAL,
            servicios          REAL,
            dcto_servicios     REAL,
            saldos_pendientes  REAL,
            bat_virtual        REAL,
            recalcular         INTEGER DEFAULT 0,
            estado             TEXT DEFAULT 'Emitida',
            rectifica_a        TEXT,
            ncontrato          TEXT,
            suplemento         INTEGER
