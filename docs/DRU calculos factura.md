Detalles para el calculo de la factura

La factura se estructura en 5 bloques y un total a pagar.

Este modulo es puramente un modulo de calculo

Este modulo es completamente reciclable y se utilizará (adaptandolo si es necesario) para todos aquellos procesoa que necesiten calcular el importe de la factura y/o cada uno de los apartados. Por tanto, cada bloque debe estructurarse como una clase independiente con sus metodos correspondientes si es que a lugar a alguno.

Esto quiere decir que cada bloque puede ser llamado de forma independiente cuando y desde donde sea necesario.

Hay un dato que se debe guardar para su aplicacion como corresponda llamado "bono solar cloud" que es un acumulado de los excedentes de facturas anteriores no aplicados en esta segun los calculos y premisas expresados en este DRU con lo que lo mas aconsejable es crear una tabla para tal efecto.


### 1.- ENERGIA

    En este epigrafe se totalizan los importes correspondiente a la energia consumida, la potencia contratada, los excedentes en su caso y los cargos normativos referidos al bono social y al impuesto electrico IEE. La suma de los distintos epigrafes se totaliza como "Total Energia"

    Hay cuatro apartados facturados por el concepto Energia:


## 1.1 Potencia facturada

    En este apartado se totalizan los importes correspondientes a la potencia disponible en el domicilio.

    * La potencia facturada se calcula para los periodos contrados. La formula es la misma para los dos:
    
        - tabla contratos_energia "ce" (suplemento activo del contrato relacionado con la factura)
        - tabla facturas "fa" (para la factura a totalizar)

    potencia punta: **ce.ppunta * fa.dias_factura * ce.pv_ppunta**
    potencia valle: **ce.pvalle * fa.dias_factura * ce.pv_pvalle**


    * El resultado se redondea a dos decimales y se totaliza como "Total potencia:" 

## 1.2 Energía consumida

    En este apartado se totalizan los importes correspondientes al consumo puro de energía

    * La energia consumida se calcula en tres periodos, la formula es la misma para los tres

        tabla contratos_energía ce (suplemento activo del contrato relacionado con la factura)
        tabla facturas fa (para la factura a totalizar)

    consumo punta: **fa.consumo_punta * ce.pv_conpunta**
    consumo llano: **fa.consumo_llano * ce.pv_conllano**
    consumo valle: **fa.consumo_valle * ce.pv_convalle**

    * El resultado se redondea a dos decimales y se totaliza como "Total consumo:"

## 1.3 Excedentes

    En este apartado se totalizan, en negativo, los importes correspondientes a la energía vertida a la red.

    * La compensacion por excedentes vertidos se calcula en funcion del precio por kWh en contrato multiplicado por el numero de kWh vertidos a la red capturado en el campo excedentes.

        tabla contratos_energia "ce"
        tabla facturas "fa"

      excedentes: **fa.excedentes * ce.pv_excedent**
    
    * El el resultado se redondea a dos decimales y se totaliza como "Compensacion excedentes" SIEMPRE EN NEGATIVO.

    * El importe compensado no puede ser superior (si igual) al importe de la suma de la energia consumida en todos los periodos.

    * En caso de que el calculo de los excedentes fuera superior a la suma de los importes de la energia consumida, el exceso se almacenará y sumara al saldo anterior para posteriores facturas. Se aplicará, caso de existir saldo a compensar, en el total de la factura pudiendo llegar esta a 0.

    * Iberdrola clientes ha cambiado la forma de calcular el importe de los excedentes vertidos adaptandose, a partir de la factura emitida el 10/11/2025, al precio por kWh en el contrato de forma literal, abandonando el calculo poco claro que realizaba en facturas anteriores a la mencionada. Por tanto, el calculo del punto anterior solo será exacto a partir de esta factura.

**ENERGIA**

    Todos los calculos anteriores se totalizan en el bloque:

    **energia = Total potencia + Total energía + (-Compensacion excedentes)**


### 2 CARGOS NORMATIVOS

    Los "Cargos normativos" son en realidad obligaciones que el gobierno ha impuesto a cada uno de los contratos de suministro de los consumidores en aras de una pretendida solidaridad para con los mas desfavorecidos. Como comentario personal indicar que la solidaridad impuesta deja de ser solidaridad para pasar a ser obligacion y por tanto imposicion.



    Los "cargos normativos" son dos:

# 2.1 financiacion del bono social

        tabla contratos_gastos "cg"
        tabla facturas "fa"

    * El resultado se redondea a dos decimales y se totaliza como "bono_social"

    financiacion bono social: **fa.dias_factura * cg.bono_social**

# 2.2 impuesto sobre electricidad

        tabla contratos_gastos "cg"
        tabla facturas "fa"

    impuesto sobre electricidad: **(1+(cg.i_electrico/100) * ENERGIA**

    Nota, el campo cg.i_electrico es, en realidad, un porcentaje por lo que la forma de calcular ese porcentaje de un valor x es la forma que se describe aqui.

    * El resultado se redondea a dos decimales y se totaliza como "IEE"

**CARGOS NORMATIVOS**

    Los calculos anteriores se totalizan en el bloque:

    **cargos_normativos = bono_social + IEE**



### 3 SERVICIOS Y OTROS CONCEPTOS

    En este apartado se facturan tres conceptos

## 3.1 Alquiler equipos de medida

    * Se trata de lo que cobra la distribuidora por el alquiler del contador que mide la energía consumida en base a

        tabla contratos_gastos "cg"
        tabla facturas "fa"

    equipos: **fa_dias_factura * cg.alq_contador**

    * El resultado se redondea a dos decimales y se totaliza como "Equipos"

## 3.2 Servicios

    * Se trata de costes (servicios asociados al contrato obligatorios) fijos por servicios asociados - los descuentos aplicados (en el campo factura.dcto_servicios) que se captura en negativo.

        tabla facturas "fa"

    servicios asociados: **fa.servicios + (-fa.dcto_servicios)**

    * El resultado se redondea a dos decicmales y se totaliza como "Servicios"


**SERVICIOS Y OTROS CONCEPTOS**

    Los calculos anteriores se totalizan como serv_otros:

    Serv_otros: **equipos +  Servicios**


###  4 IVA

    El IVA se calcula en base a la suma de todos los apartados anteriores:

        tabla contratos_gastos cg

    IVA: **energia + cargos_normativos + serv_otros * (1+(cg.iva))**


### TOTAL FACTURA

    TOTAL FACTURA = **energia + cargos normativos + servicios y otros conceptos + iva**


## 5 BONO SOLAR CLOUD

    Se trata del saldo de los excedentes no compensados en anteriores facturas. Se calcula en el apartado "1.3 Excedenes" y se aplica a la totalidad de la factura hasta el limite de la misma, incluido el iva.

   energia - (excedentes * pv_excedentes) + valor anterior

    * Ejemplo: supongamos que el bloque energía tiene un valor de 20 €, que hemos vertido a la red un total de 259 kWh, que el precio de compensacion de excedentes es de 0.07 €/kWh, que el total de la factura por a suma de los cuatro bloques anteriores es de 19€ y que teniamos un saldo en solar cloud pendiente de compensacion de 25€, el calculo sería:

    sobrante de compensar en el bloque energia = (energia - (259*0.07)) --> 20 - 18.13 = 1.87 €

    Bono social anterior = 25

    total factura 19€ bono solar cloud 25 factura = 19-25= 0 

    Resto de bono social a compensar 6€ + 1.87 € generados en esta factura Total para el siguientes facturas 7.87€



    
### TOTAL A PAGAR

    El total de la factura se calcula en base a:

    **TOTAL A PAGAR = TOTAL FACTURA + (-SOLAR CLOUD*)**

    *El "SOLAR CLOUD" que se compensa en esta factura es el pendiente anterior no el pendiente mas el sobrante de esta factura.





