---
book: book-iii
section_pvid: 3483
level: title
order: 10
part: 3
parts: 3
title: "Título X Tablas de Mortalidad"
path: "Libro III, Título X Tablas de Mortalidad, Anexos"
documents: ["10626"]
source: web
---

# Título X Tablas de Mortalidad — Parte 3 de 3

*Parte 3 de 3 de este Título · anterior: `33-10-titulo-x-parte-2.md`*

## Anexos

### Anexo N° 10 Nota técnica construcción tablas CB-H-2020 (hombres), MI-H-2020 (hombres), RV-M-2020 (mujeres), B-M-2020 (mujeres) Y MI-M-2020 (mujeres)

**Cita:** Libro III, Título X Tablas de Mortalidad, Anexos, Anexo N° 10 Nota técnica construcción tablas CB-H-2020 (hombres), MI-H-2020 (hombres), RV-M-2020 (mujeres), B-M-2020 (mujeres) Y MI-M-2020 (mujeres)

I. INTRODUCCIÓN

Según lo dispuesto en los artículos 55 y 65 del D.L. N° 3.500 de 1980 y en el artículo 20 del DFL N° 251, de 1931, las tablas de mortalidad para efectos de (a) calcular el capital necesario de las pensiones de retiro programado, (b) computar los aportes adicionales con cargo al seguro de invalidez y sobrevivencia (SIS) y (c) determinar las reservas técnicas que deben constituir las aseguradoras por los contratos de seguro de rentas vitalicias y SIS, son fijadas conjuntamente por la Superintendencia de Pensiones (SP) y la Comisión para el Mercado Financiero (CMF).

Por otra parte, las tablas de mortalidad CB H 2014 (hombres), MI H 2014 (hombres), RV M 2014 (mujeres), B-M-2014 (mujeres) y MI M 2014 (mujeres) han estado en vigencia desde el 1 de julio de 2016.

En virtud de lo anterior, la SP y CMF han desarrollado 5 nuevas tablas de mortalidad, las que reemplazarán a las tablas señaladas en el párrafo precedente a partir del 1 de julio de 2023:

• CB-H-2020 (hombres) para pensionados por vejez y beneficiarios no inválidos de pensión de sobrevivencia.

• MI-H-2020 (hombres) para pensionados por invalidez y beneficiarios inválidos de pensión de sobrevivencia.

• RV-M-2020 (mujeres) para pensionadas por vejez.

• B-M-2020 (mujeres) para beneficiarias no inválidas de pensión de sobrevivencia.

• MI-M-2020 (mujeres) para pensionadas por invalidez y beneficiarias inválidas de pensión de sobrevivencia.

Para la construcción de las tablas de mortalidad 2020 se contó con el apoyo técnico de la Organización para la Cooperación y el Desarrollo Económicos^{1} (OCDE), que brindó recomendaciones basadas en las mejores prácticas internacionales.

El proceso de construcción de las tablas se dividió en tres etapas:

a. Obtención y depuración de datos

b. Cálculo de tasas de mortalidad

c. Cálculo de los factores de mejoramiento

En el presente informe técnico se detalla el trabajo realizado y los principales criterios técnicos que se tuvieron en consideración para la construcción de las tablas 2020. Asimismo, se discuten los efectos de la pandemia de COVID-19 en la mortalidad actual y futura.

II. DATOS PARA TASAS DE MORTALIDAD

II.1. Fuentes de información

La base de datos utilizada^{2} para la construcción de las tablas se obtuvo de dos fuentes de información que involucran al sistema previsional chileno:

Base de pólizas de renta vitalicia (CMF)

Se utilizó la información de la Circular N° 1.194 a diciembre de 2019, que incluye pólizas de renta vitalicia previsionales (RV) -ya sea como venta directa, o de traspaso o cesión de cartera- y siniestros de invalidez y sobrevivencia según la Circular N° 528. La información incluye tanto causantes de pensión como beneficiarios de pensión a pago (pensiones de sobrevivencia) y potenciales (declarados en renta vitalicia del causante).

Se incluyeron todas las pólizas de RV inmediata y RV diferida; respecto a estas últimas tanto aquellas en que se hubiera iniciado el pago de la renta vitalicia, como aquellas en que aún no comenzaran a devengarse las rentas.

Base de pensionados del actual sistema de pensiones del DL. 3.500, de 1980 (SP)

Se ocupó la información de pensionados bajo las modalidades de retiro programado (RP) y renta vitalicia proporcionada mensualmente por las Administradoras de Fondos de Pensiones, mediante la Base de Datos de Afiliados, Cotizantes, Beneficiarios, Pensionados y Fallecidos, conforme a lo establecido en el Compendio de Normas del Sistema de Pensiones, Libro V, Título XI. Se consideró la información de pensionados y sus beneficiarios, tanto efectivos como potenciales (es decir, cuando el titular de la pensión está vivo).

Adicionalmente, se obtuvo información de las calificaciones de invalidez proporcionada por las Comisiones Médicas del D.L. 3500, de 1980, y del Sistema de Consultas y Ofertas de Montos de Pensión (SCOMP), para fines de validación y completitud de datos en caso de ser necesario.

II.2. Filtros y limpieza de datos^{2}

Este proceso considera una amplia revisión de inconsistencias a nivel de registro y grupo familiar (pensionado y sus beneficiarios) de los datos de ambas fuentes (SP y CMF). Los principales análisis fueron:

- Verificación de datos tales como sexo, fecha de nacimiento y fecha de fallecimiento a través de los convenios de prestación de servicios de verificación de datos fuera de línea del Servicio de Registro Civil e Identificación (SRCEI) con la CMF y la SP.

- Revisión de inconsistencias de variables tales como el RUN, sexo y fecha de pensión; relaciones de beneficiarios de pensión de sobrevivencia; fechas inválidas y otras.

- Revisión de inconsistencias entre variables, tales como fecha de nacimiento e inicio de pensión; fecha de fallecimiento e inicio de pensión; fecha de fallecimiento y fecha de nacimiento, entre otras.

- Revisión de inconsistencias a nivel de grupo familiar, tales como sexo y edad de cónyuges; edad de pensionados e hijos; edad de pensionados y padres beneficiarios, entre otras.

- Eliminación de observaciones con fechas de pensión o nacimiento posteriores al período de construcción (31/12/2018).

Además, se aplicaron algunos filtros particulares a los datos de la SP y la CMF para obtener la población objetivo en cada base de datos. Los filtros más relevantes se resumen a continuación:

SP

• Fecha de pensión por invalidez: se consideran las fechas reportadas por las Comisiones Médicas para expedientes con fecha de solicitud posterior a 2011, asignándose la fecha de la primera resolución por invalidez total y la segunda resolución por invalidez parcial. De esta forma, no se considera el período transitorio de invalidez.

• Filtro de registros en rentas vitalicias (RRVV): se eliminan de las bases de datos de la SP los registros de pensionados y beneficiarios que corresponden a rentas vitalicias ya que están disponibles en las bases de datos de la CMF.

CMF

• Filtro de reaseguro: estos registros se eliminan porque están duplicados en las bases de datos.

• Filtro beneficiarios designados: se excluyeron los beneficiarios designados, por tratarse de registros cuya única función dentro de la póliza es asignar la reserva por la pensión no percibida por un rentista fallecido, cuando no existen beneficiarios con derecho a pensión.

Adicionalmente, se realizó un análisis de registros duplicados en cada base, donde después de detectar y corregir inconsistencias entre sexo, fecha de nacimiento, fecha de fallecimiento y fecha de invalidez, se eliminan los registros duplicados. A continuación, se muestra un resumen de los registros eliminados por los filtros para cada base de datos:

Tabla 1. Resumen de registros eliminados según fuente y filtro

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_1.jpg?ts=1691074610)

<!-- figura 0ccd10bbe488b4a56f597349f5c4b2c814ed4c8555824cc78cf1d9d58e9c6865 -->

II.3. Consolidación de datos CMF - SP

El proceso de consolidación entre ambas bases de datos también incluyó una serie de filtros para eliminar inconsistencias como:

• Inconsistencias en la edad de pensión con respecto a la fecha de primera pensión^{4}.

• Inconsistencias en las variables sexo, fecha de nacimiento y fecha de fallecimiento.

• Inconsistencias en el estado de invalidez informado.

Luego, se eliminan los registros duplicados entre ambas bases de datos, estableciendo la fecha de inicio de la exposición como la fecha más antigua para estos casos.

Tabla 2. Resumen de registros antes y después de la consolidación de datos

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_2.jpg?ts=1691074630)

<!-- figura ac54d38fda667c5056c268659676c18fc21fd634d964fde4b21bf6ab5f830e1c -->

Posteriormente, se aplican los siguientes filtros solo a la base de datos de la SP:

• Filtro de Pensión Mínima o Pensión Básica Solidaria (PBS): se eliminan los registros de causantes y su grupo familiar, cuando no son potenciales usuarios de las tablas de mortalidad. Esto se verificó comparando la pensión del causante con el valor mínimo requerido, a la fecha de solicitud, para contratar una renta vitalicia. Dicho valor se consideró equivalente a la Pensión Mínima con Garantía Estatal vigente a la fecha de solicitud, para solicitudes anteriores a julio de 2008 y equivalente a la Pensión Básica Solidaria para solicitudes posteriores. Se excluyen de esta eliminación los causantes inválidos y su grupo familiar, y los beneficiarios de sobrevivencias de causantes fallecidos no pensionados, pues algunos de estos pensionados, a pesar de no cumplir con el requisito para optar a renta vitalicia, pueden haber recibido aporte adicional del seguro de invalidez y sobrevivencia y con esto sí ser usuarios de las tablas de mortalidad.

• Filtro inconsistencia saldo-pensión: se eliminan aquellos registros en los que existe inconsistencia entre los ahorros para la jubilación y el monto de pensión (valores atípicos^{5}).

Tabla 3. Resumen de registros luego de consolidación según fuente de información

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_3.jpg?ts=1691074649)

<!-- figura 80175b5b48cdbf7025a001e82a4e910d2318da3fe4dc88718872a07315a69991 -->

A continuación, se muestran el número de registros por tipo de tabla:

Tabla 4. Resumen final de registros por tipo de tabla

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_4.jpg?ts=1691074670)

<!-- figura d4ca60418f22bfceb3a937337a264c776264dd5b9044317fb0178e5d4a1a8a44 -->

Finalmente, después de aplicar los filtros de consolidación, se juntaron las tablas de causantes y beneficiarios no inválidos para los hombres. De este modo, la base de datos consolidada se compone de los siguientes registros:

Tabla 5. Resumen final de registros por tipo de tabla luego de agrupación de causante/beneficiarios hombres

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_5.jpg?ts=1691074690)

<!-- figura 385791cdee3104d38ce2a382662abca0d2d8888551c38e2bd5e9f7ba63466c72 -->

II.4. Composición de los datos

La base de datos resultante representa a los siguientes usuarios de las tablas de mortalidad:

Pensionados

• Pensionados no inválidos que pudieron seleccionar entre retiro programado y renta vitalicia.

• Pensionado con invalidez parcial, una vez que su condición de discapacidad haya sido considerada permanente^{6}.

• Pensionados con invalidez total^{7}.

Beneficiarios

• Los familiares de los pensionados, que tienen derecho a pensiones de sobrevivencia. Es posible que ellos mismos sean calificados como inválidos.

Estos usuarios se clasifican inicialmente en seis grupos, según el sexo, tipo de prestación (pensión o sobrevivencia) y el estado de invalidez:

Tabla 6. Grupos de población

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_6.jpg?ts=1691074709)

<!-- figura f4819006b31544b817bd586ec14e23b4d099783b27b38d2cf8ab286811cc57e8 -->

III. TASAS DE MORTALIDAD

En esta sección se explica la metodología y las principales decisiones tomadas para calcular las tasas brutas de mortalidad y graduarlas.

III.1. Metodología de cálculo de las tasas brutas de mortalidad y expuestos

III.1.1. Cálculo de expuestos al riesgo

Se realizó un estudio de aniversario a aniversario para cada grupo enumerado en la Tabla 6, utilizando un período de observación desde los aniversarios de 2014 hasta los de 2019, como se muestra a continuación.

Tabla 7. Variables para el cálculo de expuestos y fallecidos

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_7.jpg?ts=1691074727)

<!-- figura 5abb0f933bb70d5eecf0cbc32b48c751b2adcc036d43e7a53ed4dfb5d5f7d59e -->

Para el cálculo de la edad asegurada "IA", el redondeo aproxima al número entero más cercano (edad actuarial). Las fechas exactas de pensión, nacimiento y fallecimiento son expresadas en términos de años decimales, donde el año es la parte entera y el mes y día son la parte decimal.

Las exposiciones y fallecimientos se calculan contando el número de personas que cumplen con los siguientes criterios, para cada edad x:

Tabla 8. Criterios para calcular expuestos y fallecidos

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_8.jpg?ts=1691074747)

<!-- figura 8d86f3ff1c6720dbbfa537e08a6cfe1bf052114cad420394a0835760a01ecbf9 -->

III.1.2. Cálculo de las tasas brutas de mortalidad

Las tasas brutas (q°_{x}) se calculan como el número de fallecidos sobre los expuestos, para cada edad y grupo:

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_9.jpg?ts=1691074772)

<!-- figura 36d280946108e3f249642cc27fc0519e6bedcd3b261b11cb376775dfa5674f41 -->

Dado que el período de observación es entre 2014 y 2019, el año central de las tasas brutas de mortalidad es el año 2016. Vale destacar que al ser el año central con que se ajustan las tasas de mortalidad el año 2016, una vez ajustadas las tasas de mortalidad suavizadas y los factores de mejoramiento, al momento de publicar las tablas de mortalidad 2020, se actualizan los qx con los factores de mejoramiento obtenidos, para que el año base sea el año 2020.

III.2.Criterios utilizados para cada tabla de mortalidad

III.2.1.Pensionados y beneficiarios no inválidos (hombres)

La tabla de mortalidad de pensionados y beneficiarios no inválidos se compone por los hombres pensionados de vejez (no inválidos) y beneficiarios no inválidos. Se decidió agrupar ambas poblaciones debido, principalmente, a que los hombres no inválidos mayores a 24 años tienen derecho a pensión de sobrevivencia solamente desde el año 2008, por lo que no se cuenta con suficiente información histórica para construir una tabla de mortalidad exclusiva para esta población. Por lo tanto, al igual que en las tablas de mortalidad 2014, se combinaron las poblaciones de pensionados no inválidos (tabla RV) y beneficiarios no inválidos (tabla B) para crear la tabla CB para hombres, dado tanto la falta de datos como los niveles similares de mortalidad observados.

El Gráfico 1 compara la mortalidad bruta de las poblaciones RV-H y B-H, a través de un intervalo de confianza (IC) del 95% para las tasas brutas B-H. El ancho del IC da cuenta de la alta variabilidad de las tasas dada la escasez de datos. La mayoría de las tasas brutas de RV-H se encuentran dentro del IC, lo que sugiere que, dada la información disponible, no se puede sostener que existen diferencias significativas en la mortalidad de ambas poblaciones en esas edades. Sin embargo, se observa mayor cercanía de las tasas brutas de RV-H al borde superior del intervalo, excediéndolo en algunos casos. Por lo tanto, en una próxima actualización de las tablas de mortalidad, cuando existan más datos disponibles, se debe reevaluar la pertinencia y factibilidad de contar con tablas individuales para ambas poblaciones.

Gráfico 1. Intervalo de confianza para tasas de hombres beneficiarios vs. pensionados

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_10.jpg?ts=1691074806)

<!-- figura d257b18de268e7fe9addf10eb24b2dff5ce2ab1812c17b2a8a3c510a27e184f6 -->

III.2.2. Pensionados y beneficiarios no inválidas (mujeres)

La tabla de pensionadas no inválidas incluye a todas las mujeres pensionadas de vejez. En este caso, se decidió mantener a las pensionadas no inválidas separadas de las beneficiarias no inválidas, ya que el análisis de las tablas de mujeres (RV-M y B-M) arroja resultados diferentes al de los hombres: el IC es más estrecho para las tasas brutas B-M y la mayoría de RV-M queda fuera del intervalo (ver Gráfico 2). Dado el alto volumen de datos de beneficiarias, fue factible y necesario construir una tabla para esa población, dado que su mortalidad difiere claramente de la mortalidad de las pensionadas.

Gráfico 2. Intervalo de confianza para tasas de mujeres beneficiarias vs. pensionadas

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_11.jpg?ts=1691074831)

<!-- figura 29523f0bd317dc8c4ebf2ce83113a9357609f1140ecc1dbd1dbdc048231eb2af -->

III.2.3. Pensionados y beneficiarios de invalidez (hombres y mujeres)

Las tablas de mortalidad de invalidez, que se componen de los pensionados y beneficiarios de pensión con dictamen de invalidez, consideran tanto las invalideces parciales como totales.

En el caso de los inválidos parciales, empiezan a exponer como pensionados una vez que tienen dictaminada de forma definitiva su condición de invalidez, a través de un segundo dictamen, después del cual pueden acceder a elegir la modalidad de su pensión (retiro programado o renta vitalicia). Esto sucede típicamente tres años después de que se dictamina por primera vez su condición de inválido parcial y tiene relación con que en ese período de tres años se espera la persona evolucione de tres formas posibles: que mejore tras realizar tratamientos, que empeore su grado de invalidez o que se confirme la invalidez parcial de forma permanente, lo que es evaluado tras transcurrir dicho período.

Por otro lado, en el caso de los inválidos totales, a partir de la reforma de pensiones del año 2008, la condición de invalidez es dictaminada de forma definitiva en la primera evaluación por parte de las Comisiones Médicas. En este caso, se observa que para los pensionados de invalidez total los niveles de mortalidad son significativamente mayores durante los primeros años (ver Gráfico 3 y Gráfico 4), esto debido a que la reforma al sistema de pensiones de 2008 eliminó el período transitorio de aquellos pensionados calificados con invalidez total, lo que provocó indirectamente registrar una mayor mortalidad en los primeros tres años de pensión, situación que en las TM2014 no fue capturada completamente debido al período de construcción entre 2008-2013.

Gráfico 3. Tasas brutas de mortalidad para hombres inválidos

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_12.jpg?ts=1691074858)

<!-- figura 46d98198754df3c6250b179223510dc0e194c6d51b7f23b999304b4bd42a27cd -->

Gráfico 4. Tasas brutas de mortalidad para mujeres inválidas

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_13.jpg?ts=1691074886)

<!-- figura 34bfe097e7c97a60ef3dabeb04a2eb49102d2c54bea4ea67e35e5b623acb6adf -->

En el Gráfico 3 y el Gráfico 4, las líneas discontinuas representan la mortalidad bruta de los pensionados por invalidez total durante el primer, segundo y tercer año desde su dictamen de invalidez. Los puntos morados representan la mortalidad bruta de los pensionados por invalidez a partir del cuarto año, es decir, las tasas últimas de mortalidad. Se observa que los primeros tres años la mortalidad es significativamente mayor y se estabiliza en un nivel más bajo a partir del cuarto año de invalidez. Con el fin de entender la causa de la mayor mortalidad inicial, se calcularon tasas brutas de mortalidad de invalidez considerando todos los años de pensión definitiva, pero excluyendo a las personas cuya invalidez fue dictaminada en base a un diagnóstico potencialmente terminal^{8}, lo que se grafica con puntos celestes. Se observa que la mortalidad última es muy similar a la mortalidad excluyendo a los enfermos terminales, lo que indica que la mayor mortalidad en los primeros tres años se debe a las personas con diagnósticos potencialmente terminales.

Producto de lo anterior y considerando los efectos de la ley N° 21.309, que establece el beneficio de retiro anticipado de los fondos de pensión en el caso de afiliados y pensionados calificados como enfermos terminales, se utilizan tasas últimas en invalidez, que son las que mejor representan la mortalidad estable de esta población. Es decir, se eliminaron los tres primeros años de pensión de los inválidos totales^{9}. Quienes se acojan a la nueva ley no utilizarán las tablas de mortalidad para determinar el desgaste de sus fondos en RP, ni tampoco tendrán derecho a contratar una pensión bajo la modalidad de renta vitalicia (es decir, la población de pensionados que usarán las tablas de mortalidad de invalidez para el cálculo del RP y la reserva de RRVV excluirá a aquellos pensionados o afiliados calificados como enfermos terminales). Cabe mencionar que se puede acceder a los beneficios de la ley siendo afiliado activo (personas que antes se hubieran pensionado por invalidez ahora se acogerán a esta ley) o pensionado (por ejemplo, personas cuya enfermedad no había entrado todavía en la etapa terminal al momento de la pensión).

III.3. Graduación de tasas de mortalidad en edades centrales

III.3.1. Whittaker Henderson tipo B

Se utilizó el modelo de Whittaker-Henderson (WH) con diferencias de cuarto orden para graduar las tasas brutas en edades centrales. Este modelo calcula un conjunto de tasas de mortalidad graduadas^{_{10}} minimizando la suma de dos términos, uno que expresa el error en la estimación y otro que expresa la suavidad de las tasas graduadas:

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_14.jpg?ts=1691074909)

<!-- figura 38d162c83864d1233d137032a157f1ac5d23ac9f912eb4266da2f773a170bca1 -->

Este método solo se puede utilizar para las edades centrales, donde hay suficientes datos disponibles. Se utilizó un intervalo de edad continuo con al menos 5 fallecidos en cada edad como entrada inicial para el modelo WH (tasas brutas de mortalidad). La siguiente tabla muestra el volumen de datos disponibles para el proceso de graduación.

Tabla 9. Datos disponibles para la graduación

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_15.jpg?ts=1691074933)

<!-- figura 65519d4610c99b05635f38acf367a8f6935874465f786a447fde81ca8ba82be6 -->

Para graduar las tasas brutas de mortalidad utilizando WH, se debe tomar una serie de decisiones: intervalo de edad, pesos y parámetros h y z. El rango de edad inicial se redujo cuando fue necesario para obtener un mejor resultado. Los pesos h se establecieron como el recíproco de la varianza de las tasas brutas (q°_{x}).

El modelo WH permite al usuario establecer el equilibrio deseado entre bondad de ajuste y suavidad. Se probaron diferentes combinaciones, concluyendo que las diferencias de cuarto orden (z=4) se ajustaban mejor a los datos observados. El coeficiente h se modificó iterativamente hasta obtener una función creciente monótona, con una forma similar a una función exponencial.

La siguiente tabla muestra los parámetros utilizados en el proceso de graduación.

Tabla 10. Parámetros usados en la graduación de las edades centrales

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_16.jpg?ts=1691075001)

<!-- figura 8083481209aa36c5bc072c53cc28afec452c93dd24e1d962f039b38abd6a6281 -->

Los siguientes gráficos muestran las tasas de mortalidad graduadas resultantes para las edades centrales:

Gráfico 5. Mortalidad bruta y graduada - CB-Hombres

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_17.jpg?ts=1691075028)

<!-- figura 86c43a7bd83cb6f1179d88822e04425880c455bff4e9625ec5f9a8a13616b86a -->

Gráfico 6. Mortalidad bruta y graduada - MI-Hombres

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_18.jpg?ts=1691075064)

<!-- figura b520c0a69afb35803838e49d760628bfb3286f2f04064400bafbd5724c6af010 -->

Gráfico 7. Mortalidad bruta y graduada - RV-Mujeres

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_19.jpg?ts=1691075161)

<!-- figura f3a59531a18331efd1f3984bcff6e29ec1d917027bd532b6dcb6975da8247d57 -->

Gráfico 8. Mortalidad bruta y graduada - B-Mujeres

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_20.jpg?ts=1691075161)

<!-- figura e63bbf3666f6bef4414620b507156c76a58ee57f53671833344e35f1b9b800eb -->

Gráfico 9. Mortalidad bruta y graduada - MI-Mujeres

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_21.jpg?ts=1691075162)

<!-- figura eac53dab0851ad2ce57e0bfb9e83fcaa48b803d904af73a4bfea90279bc93244 -->

III.3.2. Test estadísticos

Luego de ajustar las tasas brutas de mortalidad, se verificó que los resultados representan adecuadamente a la población objetivo. Para ello, se utilizaron pruebas estadísticas para mostrar la fiabilidad del ajuste en comparación con los datos observados (la descripción de los tests utilizados está en el APÉNDICE N° 2 y el detalle de sus resultados en el APÉNDICE N° 3).

Tabla 11. Resultado de test estadísticos

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_22.jpg?ts=1691075227)

<!-- figura 283a58464ba55d61bc050f3f13daa9766027e395d2c7b372f28fc7d5afd940fe -->

Como se muestra en la tabla anterior, las tasas de mortalidad graduadas pasaron todas las pruebas para todas las tablas.

III.4. Extrapolación a edades finales

Dado que no existen datos suficientes en edades avanzadas para calibrar las tasas de mortalidad utilizando el modelo WH, se utilizaron modelos paramétricos de mortalidad para extrapolar las tasas de mortalidad a esas edades. Se evaluaron varios modelos y se seleccionó uno para cada tabla, considerando la bondad del ajuste y la consistencia con otras tablas.

Los modelos considerados fueron Gompertz, Makeham, Quadratic, Heligman y Pollard (1ª y 3ª Ley) y Kannisto (ver fórmulas en APÉNDICE N° 1).

Se utilizó un subconjunto de tasas de mortalidad graduadas en las edades centrales para encontrar los parámetros de cada modelo, buscando minimizar el error de estimación. Se probaron diferentes subconjuntos de edades centrales superiores, de entre 10 y 30 edades cada uno, eligiendo el que arrojó mejores resultados para cada tabla. La selección del modelo para cada tabla se basó principalmente en el ajuste (error cuadrático medio mínimo, [(q_{x}-q°_{x} ) / q°_{x}]^{2}), pero también se tuvo en cuenta la coherencia con otras tablas (actuales y nuevas).

La Tabla 12 muestra los resultados del ajuste según el tipo de tabla y tipo de modelo de mortalidad señalados anteriormente:

Tabla 12. Error cuadrático medio según tipo de tabla y modelo de extrapolación

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_23.jpg?ts=1691075227)

<!-- figura 6b887a843cb506e01602282a57412c3cc77c59e80cd5f2af8e2c2f6cad1a951b -->

De esta forma, los criterios de selección para cada modelo de extrapolación fueron los siguientes:

B-M: Esta tabla tiene la edad central más alta graduada usando WH (98 años). Se eligió el modelo con mejor ajuste (Kannisto) y se tomaron en consideración estas tasas extrapoladas para definir el ajuste final de las demás tablas.

Gráfico 10. Ajuste y proyección de los modelos de extrapolación de mortalidad de tabla B-M

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_24.jpg?ts=1691075227)

<!-- figura f183bbc7b2b733e1dded437a071a4f98cacbff7c5bf16feb6feb4a5e1b21fe5c -->

RV-M: Se eligió el modelo con mejor ajuste (Kannisto) y, además, el único que no se cruza con la tabla B-M. El subconjunto de tasas graduadas utilizado se eligió para mantener la brecha entre esta tabla y la tabla B-M.

Gráfico 11. Ajuste y proyección de los modelos de extrapolación de mortalidad de tabla RV-M

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_25.jpg?ts=1691075228)

<!-- figura 745ea59e2ea473e95bda9807fbae96ad2a046c64d15e3ae8cbb1457abbd99bc5 -->

MI-M: Se eligió el modelo (Kannisto) pues es el único modelo que evita un cruce con las tablas B-M y RV-M (el modelo de H&P 3ra ley si bien no cruza a la tabla RV-M, si cruza la tabla B-M en las edades 98-108 y tiene peor ajuste que Kannisto). Asimismo, el modelo de Kannisto permite que la tabla cierre la brecha con la tabla B-M en las edades más altas, sin caer por debajo de ella.

Gráfico 12. Ajuste y proyección de los modelos de extrapolación de mortalidad de tabla MI-M

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_26.jpg?ts=1691075228)

<!-- figura 701f14bf442189f793dd028a32105bc91c16cb7d68d836d84d95c2d25b276a20 -->

CB-H: Se eligió el modelo con mejor ajuste (Makeham), el cual fue consistente con los modelos ya seleccionados (modelos para las tablas B-M y RV-M).

Gráfico 13. Ajuste y proyección de los modelos de extrapolación de mortalidad de tabla CB-H

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_27.jpg?ts=1691075229)

<!-- figura d21873dae63e5de5ef19af4b6fffc5791d33ccca6b305804d167e619e2cd12d5 -->

MI-H: Si bien el modelo de Kannisto es el de mejor ajuste, este resulta en qx´s que se cruzan con la tabla de CB-H para edades avanzadas (al igual que los modelos Gompertz y H&P 1ra ley) y, por otro lado, el modelo de H&P 3ra ley, además de cruzar la tabla CB-H, también es el de peor ajuste de los seis modelos. De esta forma, de los dos modelos restantes, se escogió el 2do con mejor ajuste (Makeham) pues este es el único que permite cerrar la brecha con la tabla CB-H en las edades más altas, sin caer por debajo de ella.

Gráfico 14. Ajuste y proyección de los modelos de extrapolación de mortalidad de tabla MI-H

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_28.jpg?ts=1691075229)

<!-- figura 3c2496572c60b5e7b058600591642e73bb37fd307c7e9b054711f9f105bdd242 -->

Finalmente, la siguiente tabla resume el modelo utilizado para cada tabla, sus parámetros y el número de años de edades centrales utilizadas para ajustarlos:

Tabla 13. Modelos y parámetros usados en la extrapolación de las edades finales

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_29.jpg?ts=1691075230)

<!-- figura c687a186191b43867ec10fe51c1693d73b3eda93051b1a3e7c72d862431ff476 -->

III.5. Extrapolación a edades tempranas

Dada la naturaleza del sistema de pensiones, los datos son insuficientes o inexistentes en edades tempranas. Hay algunos datos para el grupo de beneficiarios (tablas B-M y CB-H) hasta los 23 años, ya que los hijos pueden solicitar prestaciones de sobrevivientes hasta esa edad, pero su mortalidad es baja, por lo que no se observan suficientes muertes a esas edades. Después de esa edad, las exposiciones caen abruptamente y luego comienzan a aumentar lentamente, a medida que se alcanzan edades más frecuentes para los cónyuges con derecho a beneficios de sobrevivencia, como se muestra en los siguientes gráficos.

Gráfico 15. Expuestos en la tabla B-Mujeres

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_30.jpg?ts=1691075230)

<!-- figura b4455641f272e0cd161de761a62836da964449c0bda8fa1784507b830aee2dd8 -->

Gráfico 16. Expuestos en la tabla CB-Hombres

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_31.jpg?ts=1691076033)

<!-- figura 5e5e88f6cfc60623b3746022ec4d02ffcb1eca8017e52e9a88cb2c455bf4d002 -->

Para seleccionar un método de extrapolación desde las tasas centrales a edades tempranas, se utilizaron las tasas de mortalidad de la población en Chile del año 2016 (el año central para las tasas brutas), proporcionadas por el Instituto Nacional de Estadística (INE), las tasas brutas disponibles (de pensionados y beneficiarios de pensión usuarios de las tablas de mortalidad con al menos 5 muertes) y las tasas graduadas en las edades centrales.

III.5.1. Pensionados y beneficiarios no inválidos

Las tasas brutas para el caso de los hombres pensionados y beneficiarios no inválidos siguen de cerca la mortalidad de la población en el primer rango de datos disponibles (de 14 a 23 años). En cambio, las tasas graduadas, que empiezan a los 53 años, muestran una mortalidad menor que la de la población general. Siguiendo los datos observados, se decidió utilizar la mortalidad poblacional hasta los 23 años y luego una interpolación cúbica ad hoc entre los 24 y 52 años cuya fórmula se encuentra detallada en la Tabla 14. El Gráfico 17 muestra los resultados.

Gráfico 17. Tasas de mortalidad para edades tempranas en la tabla CB-Hombres

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_32.jpg?ts=1691076033)

<!-- figura 324eac1b7a2c12c561649a25bce3ccc5799f6c13594fe8742a36bd3f32835575 -->

III.5.2. Pensionadas no inválidas

Para las pensionadas no inválidas no hay datos para edades muy jóvenes (con al menos 5 muertes). En el caso de RV-Mujeres se decidió utilizar el mismo supuesto que para los hombres pensionados: nivel de mortalidad poblacional hasta los 23 años e interpolación cúbica ad hoc entre 24 y 61 años detallada en la Tabla 14, llegando con esto al nivel de mortalidad graduado.

III.5.3. Beneficiarias no inválidas

En el caso de las beneficiarias, los datos brutos muestran más variabilidad que en el caso de los hombres. En el primer rango de datos disponibles (de 15 a 23 años), las exposiciones son similares a las de los hombres, pero se observan muchas menos muertes (casi un tercio de las de los hombres), lo que conduce a una mayor variabilidad. Aunque la mortalidad bruta parece más alta que la de la población a edades menores, no se puede confiar en ella debido a su alta variabilidad, por lo que la mortalidad de la población se asumió para edades más jóvenes. Por otro lado, las tasas graduadas, que empiezan a los 51 años, son más bajas que las de la población (aunque la brecha es menor que para beneficiarios hombres), por lo que se utilizó la mortalidad poblacional hasta los 23 años y luego una interpolación cúbica entre los 24 y 50 detallada en Tabla 14. El Gráfico 18 muestra los resultados.

Gráfico 18. Tasas de mortalidad para edades tempranas en la B-Mujeres

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_33.jpg?ts=1691076034)

<!-- figura 24a3294b2a2a1df307441aa8c2e8df2937ac2bfca7bfc46420f59a44e6e8bf05 -->

III.5.4. Inválidos e inválidas

A diferencia de los casos anteriores, los pensionados inválidos tienen una mortalidad mucho mayor que la de la población. En este caso, el efecto predominante es el estado de invalidez y no la menor mortalidad de los pensionados en comparación con la población general. Parece razonable suponer que este efecto está presente en todas las edades, incluidos los más jóvenes. Por lo tanto, a la mortalidad de la población en edades más tempranas se le aplicó un factor proporcional que da cuenta de la mayor mortalidad de los pensionados y beneficiarios inválidos. En el caso de la edad cero se utilizó la mortalidad de la población, pues la mortalidad es mucho mayor a esa edad y el uso del factor daría lugar a una tasa excesivamente alta. La Tabla 14 presenta el detalle de la fórmula utilizada entre los 1 y 30 años para hombres y entre 1 y 28 años para mujeres.

III.5.5. Fórmulas de interpolación utilizadas

La Tabla 14 resume las fórmulas utilizadas para calcular las tasas de mortalidad en edades tempranas para cada tabla.

Tabla 14. Extrapolación en edades tempranas

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_34.jpg?ts=1691076034)

<!-- figura f2bb369e5baf63c86536ab589c649ecec63a11593aeb1ae39134d4a900b56234 -->

III.5.6. Empalmes

Para lograr una transición suave entre las tasas graduadas en las edades centrales y las tasas extrapoladas en las edades avanzadas, se modifican las últimas tres tasas de mortalidad de las edades centrales debido a que esta cantidad es suficiente para lograr este objetivo (considerando, además, el buen ajuste de los modelos de extrapolación ya vistos). La transición se logra a través de un promedio ponderado, donde el peso depende del número de edades ajustadas y de la curva de mayor importancia relativa^{11}.

Así, por ejemplo,

- El ajuste del q_{x} de la edad avanzada x corresponderá a un promedio ponderado entre el q_{x} de la edad central ajustada por Whittaker-Henderson y el q_{x} obtenido del modelo paramétrico seleccionado para la extrapolación en edades avanzadas.

- Las ponderaciones utilizadas para modificar las edades avanzadas x-1, x y x+1, son las siguientes: para la edad x-1 se utiliza un peso igual a 1⁄4 en el caso del q_{x} obtenido por el método de extrapolación en edades avanzadas, e igual a 3⁄4 en el caso del q_{x} ajustado por Whittaker-Henderson, mientras que para la edad x los pesos se igualan (1⁄2) para ambos q_{x} y para x+1, se utiliza un peso igual a 3⁄4 en el caso del q_{x} obtenido por el método de extrapolación en edades avanzadas, e igual a 1⁄4 en el caso del q_{x} ajustado por Whittaker- Henderson.

IV. FACTORES DE MEJORAMIENTO

La metodología utilizada para estimar los factores de mejoramiento (FM) corresponde a un modelo de convergencia entre factores de mejoramiento de corto y largo plazo. Este enfoque, a diferencia del adoptado en tablas anteriores, refleja la expectativa de que las mejoras en la esperanza de vida eventualmente se ralentizarán y que los altos nivees de mejoramiento observado en las últimas décadas no continuarán indefinidamente.

Los factores de mejoramiento, por lo tanto, varían no solo por edad, sino también por año calendario. Si bien este cambio complejiza la aplicación de las tablas de mortalidad, refleja de mejor forma el mejoramiento en la mortalidad esperada en el futuro y está en línea con las mejores prácticas internacionales^{12}.

A continuación, se resumen las componentes de los FM y su cálculo, tanto para hombres como para mujeres:

- FM de corto plazo (o iniciales): Se estiman a través de un suavizado bidimensional de los logaritmos de las tasas históricas de mortalidad usando Whittaker-Henderson.

- FM a largo plazo: Se estableció en 1% hasta los 90 años y luego se disminuyó linealmente hasta alcanzar cero a los 105 años.

- Método y período de convergencia: Se utilizó un polinomio cúbico y 20 años de convergencia para llegar desde los factores de mejoramiento de corto plazo hacia los de largo plazo.

IV.1 Datos utilizados

IV.1.1. Fuente de información

Para la estimación de los factores de mejoramiento se utilizan las tasas de mortalidad históricas de la población en Chile, proporcionadas por el INE. La razón para utilizar la información del INE y no del Sistema de Pensiones de Chile es que este último no cuenta con series de datos lo suficientemente largas y densas para modelar la mejora en las tasas de mortalidad. Adicionalmente, la población objetivo de las tablas de mortalidad ha cambiado durante los últimos 15 años, principalmente debido a la Reforma Previsional de 2008^{13}, por lo que calcular mejoramientos en base a información previsional no daría cuenta del mejoramiento de la mortalidad, sino del cambio poblacional del sistema.

Si bien la mortalidad de la población representada por las TM previsionales es menor a la de la población del país, la razón entre ambas mortalidades se ha mantenido relativamente estable en el tiempo, con un ligero incremento, sugiriendo que ambas poblaciones han tenido niveles similares de mejoramiento de la mortalidad. Esto se observa al calcular la razón entre las tasas de mortalidad brutas del Sistema de Pensiones y las tasas poblacionales y ver su evolución temporal (ver Gráfico 19 y Gráfico 20).

Gráfico 19. Ratio de mortalidad de pensionados sobre mortalidad poblacional, por rango de edad, hombres

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_35.jpg?ts=1691076121)

<!-- figura 1442eb1be8cae438e729f5c5bc55a1cf601ba4b1754c67046c8205d2dc948df0 -->

Gráfico 20. Ratio de mortalidad de pensionados sobre mortalidad poblacional, por rango de edad, mujeres

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_36.jpg?ts=1691076122)

<!-- figura d9aba237c798da26c94ef64c7038c0cc12d079f9fd1e2c6dd523609ede53511b -->

IV.1.2. Descripción de los datos

Los insumos entregados por el INE corresponden a tablas de mortalidad por sexo y edad (donde la última edad que se muestra es la del grupo abierto de 100 años y más), que fueron elaboradas durante el proceso de la Estimación y Proyección de Población base 2017^{14}. El horizonte oficial de ese proceso es 1992-2050, pero el INE, a petición de la SP y CMF, añadió el período 1982-1991, elaborado mediante la misma metodología y concordante con la historia demográfica condensada en las tablas de vida del período oficial.

De acuerdo a la documentación del INE y a lo discutido con el equipo responsable de las estimaciones y proyecciones, las principales diferencias metodológicas de este proceso, comparado con los anteriores, son:

a. El uso de la población residente en lugar de la población registrada.

b. El uso de edades simples hasta el grupo abierto de 100 años y más, en lugar de grupos de edad de 5 años hasta el grupo abierto de 80 años y más.

c. El uso de años calendario en lugar de períodos de cinco años.

IV.1.3. Período de calibración

Las estimaciones del INE se basan, en términos simples, en los censos 1982, 1992, 2002 y 2017, en estadísticas vitales alrededor de los años censales y en interpolaciones para los años intermedios. Por lo tanto, al calcular factores de mejoramiento anuales para cada edad x y año t (FM_{x,t} = 1 - (q_{x,t} / q_{x,t-1}) ) se observan patrones distintos de mejoramiento, que representan los mejoramientos observados entre cada censo (ver Gráfico 21 y Gráfico 22).

Gráfico 21. Mejoramientos observados 1982-2016, hombres

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_37.jpg?ts=1691076122)

<!-- figura bb5b6ed2ca61914b0ec8a30d24343297437d7c14f4f9a889572a9d7bcef8c638 -->

Gráfico 22. Mejoramientos observados 1982-2016, mujeres

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_38.jpg?ts=1691076123)

<!-- figura 29bdff6482be1af4d8811c8f3919fff6a18357dbb954af8bda40314c48956600 -->

En los gráficos se observa que los mejoramientos de la década de los 80 son particularmente altos para las edades medias, sobre todo en los hombres. En efecto, la expectativa de vida (EV) aumentó aceleradamente en esa década y en las anteriores, hasta alcanzar un nivel cercano al de los países de ingresos altos. Desde la década de los 90, en cambio, Chile ha experimentado menores mejoramientos, similares a los de otros países con altas EV, como se observa en el Gráfico 23.

Gráfico 23. Evolución de expectativa de vida al nacer, ambos sexos combinados

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_39.jpg?ts=1691076123)

<!-- figura c32e509b089c1ae883ca4611512f97de1d973230910303a589586c86c85734f8 -->

*Fuente: United Nations, Department of Economic and Social Affairs, Population Division (2019). World Population Prospects 2019, Online Edition. Rev. 1.*

Por lo anterior, se excluyó la década de los 80 del cálculo de los FM de corto plazo, pues es improbable que esos mejoramientos se repitan en el futuro. Por lo tanto, los FM de corto plazo se calcularon con información del censo 1992 en adelante, es decir, 25 años de información (1992-2016).

Cabe mencionar que no se observan efectos de cohorte en los mejoramientos históricos en el período considerado, lo que se aprecia en los mapas de calor de la sección IV.4, dada la ausencia de patrones diagonales en los mejoramientos.

IV.2. Factores de mejoramiento de corto plazo

Para calcular los FM de corto plazo se evaluaron diversos modelos unidimensionales^{15} y luego se decidió realizar un suavizamiento, del logaritmo de las tasas de mortalidad, en dos dimensiones (edades y años) usando el método de Whittaker-Henderson. Este método es fácil de explicar, conocido por un gran número de profesionales y usado por otros países con este mismo propósito (Ej: Canadá y Estados Unidos). El método minimiza la siguiente suma:

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_40.jpg?ts=1691076124)

<!-- figura f119dda0aa5825d63fe1059be93a9a5a390adf4f59a61a33722308904c29c89a -->

Donde:

grad = tasas graduadas

brutas = tasas antes de graduación

W_{t} = Matriz de pesos

h = factor de suavidad en dirección horizontal, i.e. a través de los años calendarios

v = factor de suavidad en dirección vertical, i.e. a través de las edades

m = orden de diferencia finita en dirección horizontal

n = orden de diferencia finita en dirección vertical

El primer término considera las diferencias entre los valores brutos de mortalidad y los valores suavizados, ponderadas por los pesos W_{t}. El segundo término es la suma de la m-ésima diferencia finita al cuadrado tomada en una dirección horizontal (a través de años dentro de cada edad) y el tercero es la suma de la n-ésima diferencia finita al cuadrado tomada en una dirección vertical (a lo largo de las edades dentro de cada año). Hay cuatro parámetros que deben elegirse para la graduación: los órdenes de diferencia m y n y los factores de equilibrio (o suavizado), h y v.

En vez de suavizar directamente las tasas históricas de mortalidad, se gradúa el logaritmo de dichas tasas, pues esto conduce a FM suaves. Se utilizan diferencias de orden 2 en ambos casos (m y n) y factores de equilibrio igual a 300 para las edades (v) y 800 para los años (h). Estos parámetros son similares a los usados por Canadá en su escala MI-2017^{16}, pero en este caso se utilizó un mayor suavizamiento a través de los años calendarios, dadas las diferencias en los patrones de mejoramiento entre censos, discutidas anteriormente. Los FM resultantes para el año 2016 tienen un nivel similar al mejoramiento observado durante los últimos 15 años en los datos del INE (2002-2016). Las ponderaciones W_{t} se consideran iguales a 1 para todas las edades, debido a que no se cuenta con el número de expuestos y fallecidos subyacentes en las estimaciones del INE.

Si bien las tasas históricas de mortalidad están disponibles hasta el grupo abierto de 100 años y más, la documentación del INE indica que, dada las irregularidades observadas en las tasas en edades avanzadas, a partir de la edad 90 se realizó un ajuste adicional para suavizarlas. Por lo tanto, se evaluó utilizar el rango etario completo o acortarlo hasta los 90 años, cuando el volumen de los datos originales era suficiente para no requerir ajustes adicionales. Como se puede observar en el Gráfico 24 y el Gráfico 25, usar datos hasta la edad 90 para el suavizamiento produce FM más consistentes en las edades avanzadas, con un decrecimiento casi lineal a cero (lo que no sucede con un decaimiento lineal desde los 100 años). Además, utilizar un decaimiento lineal a cero más allá de un límite es una práctica común, como por ejemplo en los factores de mejoramiento canadienses. Por lo tanto, el cálculo de los FM de corto plazo se hizo considerando las edades de 0 a 90 años.

Gráfico 24. FM de hombres al año 2016, según tramo edad usado

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_41.jpg?ts=1691076124)

<!-- figura f78653919db551438daee1666c452e2184b75479173d209ce12cc0cda6396b48 -->

Gráfico 25. FM de mujeres al año 2016, según tramo edad usado

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_42.jpg?ts=1691076125)

<!-- figura b4d096edb56c223aa234c78e31d53140f40aa6ef7035e1040ce5c484aeebc227 -->

Típicamente la aplicación del método de WH requiere desechar algunas edades o años dado que la calidad del suavizamiento en los bordes de la ventana de suavizamiento es peor, pues se suaviza con menos datos. En este caso, no se observó ese efecto, dado que los datos del INE ya están suavizados en ambas direcciones^{17}, por lo que no se descartaron datos suavizados. La estimación de los FM de corto plazo, por lo tanto, corresponde al último año suavizado (mejoramiento de las tasas de mortalidad el año 2016, con respecto al año anterior).

Los FM iniciales para edades superiores a los 90 años se calcularon con un decaimiento lineal a cero hasta los 105 años. Esto se debe a que, aunque hay evidencia de mejoras en las edades más avanzadas, la literatura no es del todo clara y proporciona evidencia en ambas direcciones. Un descenso a cero hasta 105 años está más en línea con la práctica internacional^{18} que el límite de 100 años de las tablas 2014. Adicionalmente, este descenso a cero de 90 a 105 años está en línea con el suavizamiento para edades menores a 90 años (donde los mejoramientos ya tienen un decaimiento lineal por si solos), como se ve en el Gráfico 26.

Gráfico 26. Factores de Mejoramiento de corto plazo

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_43.jpg?ts=1691076125)

<!-- figura 67eb0f3c539474b1f97630702cf77f49c5c888f589da149d75ea5c6f27664614 -->

IV.3. Factores de largo plazo

El nivel de los factores de mejoramiento de largo plazo es un parámetro muy relevante en las proyecciones futuras de longevidad. Además, es un insumo que contiene cierto grado de subjetividad y juicio experto.

Varios avances médicos han elevado la esperanza de vida durante el último siglo y han permitido alcanzar una longevidad nunca antes vista. Sin embargo, existe evidencia contradictoria sobre cómo evolucionarán las mejoras a largo plazo. Algunos expertos creen que aún queda un margen considerable para seguir aumentando la longevidad a través de eventuales avances médicos; por otro lado, se argumenta que las tasas actuales de mejora de la mortalidad difícilmente se seguirán produciendo y que ya estamos cerca de los límites del mejoramiento.

La evolución de las mejoras históricas en la mortalidad también puede ayudar a determinar la tasa a largo plazo. Como se ve en la siguiente tabla, se observa que las mejoras en la mortalidad han ido disminuyendo a lo largo de los años.

Tabla 15. Evolución de los FM observados en Chile

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_44.jpg?ts=1691076126)

<!-- figura b86ef3f297beeaf47d1c08ebdf72ef851dbe093a9dd4d764033e93e110d36712 -->

*Fuente: Elaboración propia en base a información proporcionada por el INE*

Por otro lado, se puede observar^{19} que los países que tienen mayores expectativas de vida suelen ser aquellos que tienen un PIB mayor. En el caso de Chile, si bien se observa que este se encuentra con niveles de expectativa de vida similares a países desarrollados, el PIB es sustancialmente menor, lo que indica que Chile aún podría continuar experimentando mejoramientos al nivel actual por unos años más. A continuación, se muestra una comparación de la esperanza de vida al nacer para países que tienen una esperanza de vida similar a Chile y el PIB per cápita de cada uno de estos países.

Tabla 16. Expectativa de vida al nacer para países con alta longevidad

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_45.jpg?ts=1691076126)

<!-- figura b3e2e98be8e274ffbcf275665656b0f47fbfe5eb9591c6466269dba5e0e2a68c -->

Tabla 17. PIB per cápita medido en dólares internacionales 2011

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_46.jpg?ts=1691076126)

<!-- figura 4d42bdf4a03e16bac0ae5c2b2414b54b7a9e3a272dc7a8bad65a697339964687 -->

*Nota: PIB corregido por inflación y diferencias de precios entre países.*

*Fuente: https://ourworldindata.org/grapher/life-expectancy-vs-gdp-per-capita?tab=chart&stackMode=absolute&country=CHL~CAN~JPN~NZL~KOR~ESP~GBR~USA&region=World*

En la siguiente tabla se muestran los factores de mejoramiento de largo plazo que han considerado distintas tablas de mortalidad de Canadá, Estados Unidos y Reino Unido.

Tabla 18. FM de largo plazo en distintos países

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_47.jpg?ts=1691076127)

<!-- figura 06a2e7ed29acc2e7f63d2272acdef22acc7c40e27813a36cb9fb31549870041d -->

*Fuente: Task Force Report on Mortality Improvement, Canadian Institute of Actuaries, April 2017*

*¹ The 2015 Statistics Canada Population Projections for Canada medium assumption for the period 2031/2032.*

*² The 27th Actuarial Report on the Canada Pension Plan as at 31 December 2015.*

*3 The 2016 Trustees ultimate intermediate assumptions are for the period 2040-2090.*

*4 The 2015 Technical Panel ultimate assumptions are for the period 2039-2089.*

*5 The QPP mortality improvement rates are shown by decades. For ages over 50, mortality-to-incidence ratios (MIRs) in the decade 2036-2045 are slightly higher than shown, and for the decade 2056-2065 are slightly lower than shown (especially for males).*

*6 The 2014 Office for National Statistics in the UK principal projection assumptions are for the period 2038+.*

Como ya se ha mencionado, la evidencia sobre la evolución futura de la mortalidad no es concluyente. La tasa de largo plazo para las tablas de mortalidad previsionales de Chile, se fijó en el 1% porque permite situarse en un escenario intermedio respecto a lo observado a nivel internacional. Además, se analizaron los impactos en EV, para edades relevantes según los diferentes tipos de pensionados, de modificar el FM de largo plazo desde 1% a 0,8% y 1,2%, sin observar cambios importantes, como se muestra en la tabla a continuación:

Tabla 19. Cambios en EV para diferentes valores de las tasas de largo plazo

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_48.jpg?ts=1691076127)

<!-- figura 98634182411322bef2335e64de3aa3dd2eeb241a7300d8e62da3e44e94f7cb63 -->

Se observa que aumentar la tasa de largo plazo de 1% a 1,2%, aumenta la expectativa de vida de un pensionado hombre de 65 años en aproximadamente 2 meses, y en caso contrario, al disminuirla a 0,8%, se observa un cambio similar, pero en sentido contrario, es decir, una baja en la expectativa de vida de casi 2 meses. En el caso de una mujer pensionada de 60 años, los cambios son similares a los observados en hombres, pero esta vez alcanzan valores cercanos a 3 meses. Las mayores diferencias se observan para pensionadas por invalidez de 50 años, para quienes un cambio en la tasa de largo plazo conlleva a 4,5 meses de diferencia en expectativa de vida según se aumente o disminuya la tasa de largo plazo.

Por otro lado, como ya se mencionó, Chile está por debajo del PIB per cápita en comparación con países con expectativas de vida similares, por lo que esto puede compensarse con un período más largo de convergencia entre una tasa de corto y una de largo plazo, que el usado por otros países.

Para los FM de largo plazo en edades superiores a los 90 años se asumió el mismo criterio que en los FM de corto plazo, es decir, un decaimiento lineal a 0 hasta los 105 años.

IV.4. Convergencia al largo plazo

La elección del período de convergencia para el modelo bidimensional requiere de juicio experto. El análisis de mapas de calor puede ayudar a comprender las variaciones en las tasas de mejora para edades tempranas, centrales y avanzadas (ver Gráfico 27). Se observa que en edades tempranas las volatilidades de las mejoras han sido mayores (así como en jurisdicciones como Canadá o Inglaterra), lo que podría justificar un período de convergencia más corto en estas edades. Sin embargo, se decidió utilizar un período de convergencia más largo para las edades tempranas (modelos como CMI o MI-2017 usan 10 años de convergencia), para permitir un margen más conservador porque Chile, aunque tiene EV similares a las de esos países, aún mantiene diferencias significativas en el PIB per cápita. Por lo anterior, se definió un período de convergencia de 20 años para todas las edades.

Gráfico 27. Mapa de calor de los FM suavizados, para hombres (izq.) y mujeres (der.)^{20}

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_49.jpg?ts=1691076128)

<!-- figura 803c221a419ae495fbf6daa234037562e3addcea1ac9ac47dbdc1e4fd0395260 -->

Para la definición y determinación de un método de convergencia se revisó la literatura observándose que la práctica común es el uso de polinomios cúbicos. Este tipo de convergencia tiende a producir una convergencia suave desde los FM históricos más recientes a los FM de largo plazo.

Dado que no se observaron efectos de cohorte significativos en los datos de la población chilena (pues no hay presencia de patrones diagonales en los mejoramientos históricos como puede verse en los mapas de calor), se adoptó un único polinomio de convergencia, como el usado en la escala MI-2017 de Canadá, entre el año 2016 (último año suavizado) y la tasa de largo plazo. Se asume que la pendiente es cero en el último año y la pendiente al inicio se toma como la pendiente de 2015 a 2016 hasta un valor absoluto máximo de 0,003, utilizando una ecuación separada para cada edad.

La fórmula de la ecuación cúbica es:

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_50.jpg?ts=1691076128)

<!-- figura 2092e1f3eedf31e0d0d0e009563b9bb9adec67546bd757cab19061684390d0b3 -->

Donde, t es el año de mejora, x es la edad, m es la pendiente en 2016 y t_{ult} es el primer año en el que se aplica la tasa de largo plazo, en este caso, el año 2036, ya que hay 20 años de convergencia.

Los siguientes gráficos muestran la convergencia de los FM:

Gráfico 28. Convergencia de los FM de mujeres al largo plazo

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_51.jpg?ts=1691076194)

<!-- figura d9bc5d57906e27f10889cb87914cdc8f40d282aedcd50918664874ef9142212b -->

Gráfico 29. Convergencia de los FM de hombres al largo plazo

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_52.jpg?ts=1691076194)

<!-- figura 866d91f591fe9d44127c994ee55f1dbd48fd45556fca5b40a2475d8cd1b596e9 -->

V. EFECTOS DEL COVID-19 EN LOS SUPUESTOS DE MORTALIDAD

A lo largo de las últimas décadas, Chile ha experimentado una disminución continua de los niveles generales de mortalidad, lo que se ha traducido en mejores expectativas de vida de la población. Esta mayor longevidad puede atribuirse principalmente a avances sustanciales en las condiciones de vida y de la urbanización, en el aumento del nivel educativo y en los avances verificados en materia de salud. Sin embargo, en este contexto de disminución de la mortalidad, el primer semestre de 2020 la Organización Mundial de la Salud (OMS) declaró la emergencia sanitaria internacional por el COVID-19 y, tras una evolución exponencial del número de infectados, la OMS declaró el brote de una pandemia. En Chile, el primer fallecimiento por COVID-19 fue reportado el 16 de marzo de 2020 y, desde ese momento, se han experimentado diversas olas de contagios y fallecimientos, afectando de esta forma la mortalidad de la población desde 2020 a la fecha y, en particular, la mortalidad de la población en edad de pensionarse^{21} (ver Gráfico 30).

Gráfico 30. N° fallecimientos semanales por COVID-19 (mujeres mayores a 60 años y hombres mayores a 65 años)

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_53.jpg?ts=1691076194)

<!-- figura ede202640ed08e4bfb4488421bf51801da0a71e9340d0c644ba083f9ef31a166 -->

*Fuente: Elaboración propia para hombres y mujeres en edad de pensión, con información del Departamento de Estadísticas e Información de Salud (DEIS) con cierre 02/06/2022.*

Por lo anterior, el efecto que tendrá el COVID-19 en la población usuaria de las tablas de mortalidad previsionales debe ser estudiado con detención, de modo de determinar, si los efectos de la pandemia tendrán impacto en la sobrevida futura de la población pensionada y, con ello, determinar los ajustes a realizar a las tablas de mortalidad propuestas en caso de ser necesario.

V.1. Aumento de mortalidad experimentados durante la pandemia

En Chile, la mortalidad de la población general ha aumentado desde el inicio de la pandemia observándose un aumento en 2020-2022 en comparación al periodo 2016-2019 (ver Gráfico 31).

Gráfico 31. Tasa promedio de mortalidad (por cien mil habitantes)

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_54.jpg?ts=1691076227)

<!-- figura b915b250aa96c98de3b0e8fbc3034dd072962a70e501249dcff93542970ddee0 -->

*Fuente: Informe semanal de defunciones por COVID-19 N°99, Ministerio de Salud.*

Al comparar la mortalidad del periodo 2016-2019 con la mortalidad en el periodo 2020-2022, se observa que hay un aumento de la mortalidad en todos los meses observados, donde el mayor cambio en la tasa de mortalidad se registró en junio 2020. Estas variaciones pueden ser explicadas por los efectos directos del COVID-19 (fallecimientos debido al contagio por COVID-19), como también aquellos provocados de forma indirecta (fallecimiento debido al menor acceso a la atención médica por parte de las personas). Sin embargo, también se esperaría algunos cambios de comportamiento que fuesen positivos en pos de disminuir la mortalidad, como son una menor exposición a otros virus respiratorios y una mejor higiene.

Este efecto de mayor mortalidad observada durante 2020-2022 también puede apreciarse si comparamos el número de fallecimientos totales desde 2016 a la fecha para la población en edad de pensión (ver Gráfico 32).

Gráfico 32. N° fallecimientos totales para hombres y mujeres en edad de pensión

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_55.jpg?ts=1691076257)

<!-- figura a92fb8a14a81a8b4443a0a182b68755ea22abb8441f755549d1e0d54d478743c -->

*Fuente: Elaboración propia para hombres y mujeres en edad de pensión, con información del Departamento de Estadísticas e Información de Salud (DEIS) con cierre 02/06/2022.*

En el gráfico, se puede ver la mayor mortalidad en 2020-2022, observándose al igual que para la población general, la mayor desviación en junio 2020. Adicionalmente, a mayo de 2022 se observa que estas desviaciones han ido disminuyendo^{22}.

V.1.1. Diferencias en la mortalidad por rango etario

El aumento en mortalidad ha variado también por rango etario, donde de acuerdo con la información disponible por el MINSAL (ver Tabla 20), el rango etario menos afectado corresponde a 0-29 años y los rangos etarios más afectados corresponden a 50-59 y 60-69. En el rango de 0-29 años, se observó en su mayoría variaciones negativas de la mortalidad (es decir, hubo una menor mortalidad en 2020, 2021 y 2022 (parcial) respecto a las tasas de mortalidad promedio de 2016-2019). Por otro lado, los rangos etarios 50-59 y 60-69, alcanzaron hasta un 64% de mayor mortalidad (abril-21) y 70% (junio-20), respectivamente.

Excluyendo el periodo mayo-22, el cual muestra información parcial, en abril-22 se puede ver que la variación en la mortalidad (respecto a 2016-2019) ha disminuido en comparación a lo ocurrido en el mismo mes de 2021 en todos los rangos etarios excepto el rango 0-29 donde ha aumentado de -12% a -8%.

Tabla 20. Variación porcentual de la mortalidad en base a mortalidad promedio 2016-2019 por rango etario

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_56.jpg?ts=1691076289)

<!-- figura 5e399aaa9774c02b4fbc9345085f58e33275c2ad98f45a2032fc527e836d72d8 -->




![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_57.jpg?ts=1691076290)

<!-- figura 912182ba4c4af0bb101a842896ef46e525f7c10ef056940a79459b07d3715323 -->

*Fuente: Informe semanal de defunciones por COVID-19 N°99, Ministerio de Salud.*

Por otro lado, si observamos el número de fallecimientos totales por rango etario durante el periodo de pandemia (ver Gráfico 33), vemos que el mayor número de fallecimientos corresponde a edades entre 75-79 años para hombres y 85-89 años para mujeres.

Gráfico 33. N° fallecimientos por COVID por tramo etario (virus identificado o no)^{23}

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_58.jpg?ts=1691076330)

<!-- figura 18c967b0fef855170eec1a2b68a943635e20a5f3562d8ea08b188c6c34ee032d -->

V.1.2.Exceso de mortalidad durante la pandemia

Una de las formas más comunes de medir los efectos del COVID-19 en la mortalidad es determinar el exceso de mortalidad^{24}, es decir, la desviación de fallecimientos respecto a lo que se hubiese esperado de no haber ocurrido la pandemia. El exceso de mortalidad puede explicarse tanto por las muertes por COVID-19, como por el cambio en otras causas de muerte. Dado que la mortalidad es mayor entre las personas con enfermedades preexistentes, algunas personas que hubieran muerto por otras causas, murieron en cambio por COVID-19 (muertes aceleradas). Por ejemplo, 12.361 personas por encima de la edad de jubilación murieron en 2019 por "Enfermedades del sistema respiratorio", pero sólo 8.794 en 2020 y 9.421 el año 2021. Este descenso podría explicarse por las muertes aceleradas y por los efectos indirectos de la pandemia, ya que hubo menos circulación de otros virus respiratorios.

Los siguientes gráficos muestran a nivel poblacional en Chile, la evolución del exceso de mortalidad entre las personas en edad de pensión, desagregándolo en dos causas. La curva azul muestra el exceso de mortalidad y las barras muestran cómo esta mortalidad puede explicarse por las muertes por COVID-19 y por el cambio en las muertes por otras causas. El primer gráfico considera tanto los casos de virus identificado como no identificado y el segundo gráfico considera solo los casos de virus identificado:

Gráfico 34. Exceso de mortalidad debido a COVID-19 (virus identificado o no) y cambios en otras causas de muertes

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_59.jpg?ts=1691076366)

<!-- figura ffc91723cc9e167bc7b0353d34849b71b3e0df31084cf5f73badf6bcb527bfc9 -->

*Fuente: Elaboración propia para hombres y mujeres en edad de pensión, con información del Departamento de Estadísticas e Información de Salud (DEIS) con cierre 02/06/2022.*

Gráfico 35. Exceso de mortalidad debido a COVID-19 (sólo virus identificado) y cambios en otras causas de muertes

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_60.jpg?ts=1691076366)

<!-- figura c26dd50a429945d48117942cedc495355992314866466a0c06b1bc0fcde8eca9 -->

*Fuente: Elaboración propia para hombres y mujeres en edad de pensión, con información del Departamento de Estadísticas e Información de Salud (DEIS) con cierre 02/06/2022.*

V.2. Efectos de enfermedades subyacentes en la mortalidad por COVID-19 y población sobreviviente

El impacto del COVID-19 en la mortalidad varía significativamente según las enfermedades de salud subyacentes. La OCDE en el Working Party de diciembre de 2021, observó que tener una comorbilidad subyacente aumenta significativamente el riesgo de mortalidad por COVID-19, siendo la enfermedad renal la que se encuentra entre las más mortales y aumenta el riesgo de muerte en casi cinco veces (~5x). Otras comorbilidades señaladas en el documento como factores de riesgo relevantes incluyen, en orden descendente, enfermedad cardiovascular (~3x), enfermedad respiratoria (2-3x), diabetes (~2x), hipertensión (~2x), demencia (~2x), cáncer (~2x) y enfermedad hepática (1,5x).

De acuerdo con los análisis señalados por la OCDE, la gran mayoría de las personas que mueren a causa del COVID-19 tienen al menos una comorbilidad y son comunes las comorbilidades múltiples. Asimismo, el hecho de que las poblaciones más frágiles estén en mayor riesgo respalda la hipótesis de que muchas de las muertes por COVID-19 son muertes aceleradas que podrían haber ocurrido igualmente en el corto plazo.

V.3. Efectos a largo plazo del COVID-19 en la mortalidad

Si bien los impactos de la pandemia en la mortalidad aún persisten, es razonable esperar que estos solo tengan un efecto en la mortalidad de corto plazo y que la mayoría de estos impactos sean temporales en la medida que disminuyan los impulsores del exceso de mortalidad. Sin embargo, no existe certidumbre acerca de los impactos a más largo plazo, debido a los efectos que podría tener la pandemia en el estado de salud. Lo anterior, aumenta el riesgo de que la mortalidad observada se desvíe de los supuestos utilizados en su construcción, por lo que se requiere un seguimiento continuo de la suficiencia de las tablas de mortalidad.

En cualquier caso, una vez que los efectos de la pandemia disminuyan, lo más razonable es que las tasas de mortalidad debieran volver a sus niveles de referencia. Este fue el caso después de la pandemia de gripe española de 1918-1919. El Gráfico 36, muestra que la esperanza de vida volvió a su tendencia anterior en 1920, superando incluso el nivel observado antes de la pandemia.

Gráfico 36. Evolución de la esperanza de vida, WP OCDE 2021.

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_61.jpg?ts=1691076392)

<!-- figura 4d5123356cb32873cabdcbe2875dd54074be6e150b9391da99d7d758b4b464e8 -->

Asimismo, es probable que los más frágiles de la población hayan fallecido durante la pandemia de COVID-19, por lo tanto, es esperable que los sobrevivientes sean relativamente más longevos, lo que resultará en una menor mortalidad en los años posteriores a la pandemia. Lo anterior, está respaldado por la evidencia de que los grupos específicos que experimentaron una mayor mortalidad también fueron los que tenían tasas más altas de comorbilidades. Sin embargo, es probable que este efecto de selección sea de corta duración, ya que los niveles de mortalidad volverían a su trayectoria anterior en unos pocos años, como ocurrió después de la pandemia de gripe española de 1918-1919.

V.4. Conclusiones respecto a los efectos del COVID-19 en la construcción de tablas de mortalidad

Para determinar el tratamiento más adecuado del COVID-19 en la construcción de las tablas previsionales, es necesario recordar que el objetivo de estas tablas es garantizar que, en el caso de rentas vitalicias, habrá un adecuado nivel de reservas para el pago de todas las pensiones comprometidas hasta el fallecimiento del pensionado y sus beneficiarios. En el caso de retiro programado, el objetivo es garantizar que los fondos acumulados por el pensionado no se agotarán antes del fallecimiento del pensionado y sus beneficiarios. Las tablas de mortalidad debiesen basarse en el supuesto de mejor estimación de la mortalidad y, por lo tanto, es relevante que reflejen las tasas de mortalidad actuales y futuras que se esperan de la población sobreviviente de la pandemia.

Al considerar el periodo de construcción de las tasas de mortalidad, es importante evaluar si la experiencia de mortalidad observada en este periodo es adecuada para reflejar la mortalidad actual y futura de la población a la cual se le aplicarán posteriormente. En el caso del COVID-19, la mayor mortalidad experimentada durante la pandemia corresponde a un periodo anómalo que ha cambiado la tendencia observada hasta antes de 2020. Por lo anterior, este periodo no debiese incluirse en la construcción de las tablas de mortalidad, debido a que incluirlo aumentaría significativamente el nivel de mortalidad base, lo que no sería consistente con los efectos temporales que se espera tenga la pandemia en la mortalidad.

Asimismo, actualmente no existe información suficiente que indique un efecto permanente en la mortalidad por causa del COVID-19. Por ello, cualquier ajuste de la mortalidad esperada a largo plazo no se justifica dada la falta de información al respecto. Sin embargo, y debido a la incertidumbre en la mortalidad de largo plazo, es fundamental realizar una revisión continua de la suficiencia de las tablas previsionales, de modo de corregir oportunamente cualquier desviación en la mortalidad.

Por lo tanto, las tablas de mortalidad construidas con información hasta diciembre de 2019 entregan la mejor información de la tendencia esperada para la mortalidad post-pandemia, esto es, cuando pasen los efectos temporales de la crisis sanitaria en curso.

APÉNDICE N° 1. MÉTODOS DE EXTRAPOLACIÓN

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_62.jpg?ts=1691091488)

<!-- figura fc5b2309bf0b586cb23afb13291bc87edfcb65bb919b360191cb53c46f263b36 -->

APÉNDICE N° 2. DETALLES METODOLÓGICOS

I. MÉTODO DE AJUSTE WHITTAKER HENDERSON TIPO B

El método de ajuste de Whittaker Henderson Tipo B (WH) consiste en una combinación de regresión lineal y el método Bayesiano de ajuste.

Podemos definir la fórmula de WH de la siguiente manera:

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_63.jpg?ts=1691091488)

<!-- figura 1e2bf703149f7176da54fe63ecc83cf1fabd2007107dec8c7c774c82f81894e3 -->

Donde,

F(fit): es la medida de ajuste

S (smooth): es una medida de suavidad de la curva

h: es el parámetro de suavidad de la curva

q_{x} : tasa de mortalidad obtenida luego de la graduación para la edad x

q°_{x} : tasa de mortalidad bruta (antes de la graduación) para la edad x

Descripción de F

Esta es la parte asociada a la minimización de los residuos cuadrados ponderados por el peso (W_{x}) de la muestra en cada edad, de tal forma que los residuos que tienen una muestra grande deben ser más pequeños para mantener F lo más cerca de cero. Mientras F tiende a cero el ajuste es mejor.

El ponderador W_{x} toma en cuenta la varianza de la variable aleatoria U_{x} asumiendo una distribución normal. U_{x} es una variable aleatoria binomial, pero puede ser aproximada por una variable aleatoria normal siempre que el número de observaciones n_{x} sea lo suficientemente grande.

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_64.jpg?ts=1691091489)

<!-- figura 37511c0dc40843276ce09479a77daa0015de2c6ddf9c7fc67a522f9df386b46e -->

Sabemos que la varianza es inversamente proporcional al número de observaciones. A mayores observaciones la varianza disminuye:

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_65.jpg?ts=1691091489)

<!-- figura 22f2e474feebe58a262b2cc508bb4d4954441cfad297bf97493c6d4103841a6a -->

Entonces,

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_66.jpg?ts=1691091489)

<!-- figura bff6ff43512093df81113a945d7154e48cca5117a54a7d8f9cc928dca52ea83c -->

El ponderador da más importancia al q_{x} bruto cuya varianza es menor (el ponderador va a ser más grande).

Descripción de S

Para definir la suavidad de la curva generalmente se utilizan las diferencias finitas de diferente orden sobre los valores de q_{x} brutos. S se obtiene de la suma cuadrada de las diferencias finitas. Si, por ejemplo, z=4 estamos considerando que la secuencia q_{x} se asemeja a un polinomio de grado 3. Debemos recordar que las diferencias finitas se asemejan a una derivada y, por lo tanto, el orden de diferencia condiciona el grado del polinomio.

Para encontrar los valores de q_{x} ajustados es necesario minimizar M, que es una función con n incógnitas de los valores q_{x}. Entonces, los q_{x} que minimizan M corresponden a la solución para las n ecuaciones como resultado de la derivada parcial de M con respecto a q_{x}.

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_67.jpg?ts=1691091490)

<!-- figura 145a1deaa40a6a58df90331d36b9e05cc2a1a302f26c8845da2832936e83ae91 -->

Es posible encontrar este resultado representando el problema en forma matricial.

II. DESCRIPCIÓN DE TEST ESTADISTICOS

a. El test de Chi Cuadrado.

Es un test completo que sólo se utiliza como referencia para verificar si las tasas brutas de mortalidad representan a la población. Mide las desviaciones estándar de la estimación respecto de las tasas brutas de mortalidad. Una de las limitaciones de este test es que puede haber grandes desviaciones en ciertas edades y pequeñas en otras, por lo que el resultado final es aceptable según el test. Deseablemente estas desviaciones deben ser constantes para obtener un buen resultado.

b. Test de Desviaciones Estandarizadas.

Este test verifica que la desviación estandarizada de las muertes observadas con respecto a las muertes esperadas tenga una distribución similar a una normal estandarizada, para detectar si hay desviaciones que crecen más allá de lo esperado, o su media se aleja de cero.

c. Test de Desviaciones Absolutas.

Este test refleja que las desviaciones absolutas no sean mayores a un cierto número (generalmente se utiliza que éstas no sean mayores a una unidad de la variable normal, o sea de alrededor de 2/3.)

d. Test de Desviaciones Acumuladas.

Los fallecimientos en las distintas edades deben ser independientes y se deben representar en una variable aleatoria normal. Por esta razón las desviaciones estándar deben ser relativamente homogéneas para todos los tramos. La hipótesis nula a testear es que las desviaciones acumuladas no deben ser mayores al doble de la raíz cuadrada de la varianza de la distribución.

e. Test de Signos.

Considerando que la hipótesis nula es que las desviaciones observadas de las muertes respecto de las muertes esperadas son una variable normal independiente, lo mismo debe ocurrir con los signos, encontrándose un número similar de éstos, tanto positivo como negativo.

f. Test de Stevens.

Es similar al test de signos. Estos signos pueden ser todos positivos al principio y luego todos negativos al final del ajuste, por lo que el test de Stevens observa subgrupos de signos a través de la tabla y computa el signo de cada subgrupo. Luego, en estos subgrupos deben estar distribuidos de manera similar tanto los signos positivos como negativos.

g. Test de Cambio de Signo.

La probabilidad de cada signo es independiente y está representada en una variable normal, por lo que se puede aplicar una variable binomial donde el signo positivo o negativo tiene la misma probabilidad, ½. Con esto se verifica que los cambios de signo sean homogéneos y no presenten anomalías.

APÉNDICE N° 3. RESULTADOS TEST ESTADÍSTICOS

Mujeres causantes:

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_68.jpg?ts=1691091490)

<!-- figura 4647f66564513d6010f02da3d605ed8023d3dd44e3ccf15a0bfcde27da00e15a -->

Mujeres beneficiarias:

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_69.jpg?ts=1691091490)

<!-- figura 50b24d7b40108c7f5e3959f5c3e9654c181acaeca6b198211e6effa8712fa7c5 -->

Mujeres inválidas:

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_70.jpg?ts=1691091491)

<!-- figura a53a563e2f0013df3071d680cf061f6c8f5f52bed67861862017939423c9c6bf -->

Hombres causantes y beneficiarios no inválidos:

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_71.jpg?ts=1691091491)

<!-- figura bae98b27464508d136ef74c7c235de7a153d56ddd7c115a8482346ce6467ed20 -->

Hombres inválidos:

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_72.jpg?ts=1691091492)

<!-- figura 0458421cd5114a2c838d43f4bb7099b523773d0fb97f24fdc5e165906e6676ea -->

APÉNDICE N° 4. FILTROS UTILIZADOS EN LAS BASES DE DATOS

1. LA BASE DE DATOS

Se obtuvieron las siguientes bases de datos:

- CMF: Se genera a partir de la información de la Circular N° 1.194, que incluye pólizas de renta vitalicia previsionales (ya sea como venta directa, o de traspaso o cesión de cartera) y siniestros de invalidez y sobrevivencia según la Circular N° 528. La información incluye tanto causantes de pensión como beneficiarios de pensión a pago y potenciales.

- SP: Contiene información entregada por las AFP, de pensionados bajo la modalidad de retiro programado y de renta vitalicia. Esta incluye tanto a causantes de pensión como a beneficiarios de pensión efectivos y potenciales. Contiene además información de las calificaciones de invalidez proporcionada por las Comisiones Médicas del D.L. 3500, del Sistema de Consultas y Ofertas de Montos de Pensión (SCOMP) y de pensiones asistenciales (ex PASIS), para fines de completitud de datos no validados.

Para la obtención del sexo, fecha de nacimiento y fecha de defunción, datos claves para la construcción de las tablas de mortalidad, se enviaron a parear al Servicio de Registro Civil e Identificación (SRCEI) las bases de datos de la CMF y SP, a través de los convenios de prestación de servicios de verificación de datos de registro civil fuera de línea entre la SP/CMF y el SRCEI. Este pareo se realizó en marzo de 2020.

2. CRITERIOS UTILIZADOS EN LA GENERACIÓN DE LAS BASES DE DATOS DE PENSIONADOS DE LA SP Y LA CMF

2.1 Definiciones Previas

A continuación, se definen algunos de los términos que se utilizarán a lo largo de este anexo:

- Sobrevivencia pura: Se refiere a las pensiones generadas producto del fallecimiento del afiliado antes de haberse pensionado y que generó pensión de sobrevivencia.

- Causante: Se refiere a un pensionado(a) por vejez o invalidez, que puede o no tener beneficiarios legales de pensión de sobrevivencia. Se incluyen también afiliados(as) que fallecieron antes de haberse pensionado y que generan pensión de sobrevivencia pura.

- Beneficiario efectivo: Se refiere a un beneficiario legal de pensión de sobrevivencia, que recibe o ha recibido pagos por esta pensión, pues el causante de la pensión ha fallecido. No se considera los beneficiarios designados de renta vitalicia.

- Beneficiario potencial: Se refiere a un beneficiario legal de pensión de sobrevivencia, que no ha recibido pagos por esta pensión, pues el pensionado causante no ha fallecido. No se consideran los beneficiarios designados de renta vitalicia.

- Fecha de pensión: Se refiere indistintamente a fecha de solicitud de pensión suscrita en la AFP o a la fecha de inicio de vigencia de la póliza de RV.

- Inválidos: Pensionados por invalidez o beneficiarios inválidos. No se consideran los beneficiarios designados de renta vitalicia.

2.2 Consideraciones adicionales

- Modalidad de pensión: Se clasifica como Renta Vitalicia (RV) a todos los registros que provengan de la base de datos de la CMF. El resto de los casos son clasificados como Retiro Programado (RP). Puede existir beneficiarios clasificados como RV y otros como RP dentro de un mismo grupo familiar, debido a que alguno de los beneficiarios puede haber dejado de serlo (por ejemplo, hijos que se casan o cumplen 24 años) o fallecido antes de la compra de la póliza de RV.

- Composición de las tablas RV, B, MI, CB: A continuación, se describe la población utilizada para el cálculo de cada tabla de mortalidad 2020:

- RV: Contiene información de causantes de pensión no inválidas (mujeres), de las bases de datos de la SP y CMF.

- B: Contiene información de beneficiarias de pensión de sobrevivencia no inválidas (mujeres), tanto potenciales como efectivos, de las bases de datos de la SP y CMF.

- CB: Contiene información de causantes y beneficiarios no inválidos (hombres), de las bases de datos de la SP y CMF.

- MI: Contiene información tanto de causantes como beneficiarios inválidos, de las bases de datos de la SP y la CMF.

- Edad: Para la aplicación de los filtros, se utilizan las siguientes definiciones de edad:

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_73.jpg?ts=1691091492)

<!-- figura dab51a0dc14e701d7aa54740be60132b41442d0859d3599a7a9275184e8f1358 -->

Sea, fnac la fecha de nacimiento y feval la fecha de cálculo de la edad:

- Definición de fecha no válida (FNV): Se considera que una fecha es no válida cuando no corresponde a una fecha. Para ello, se verifica lo siguiente:

- Año no puede ser menor a 1861.

- Mes debe estar dentro de los valores 1 a 12

- El día debe estar dentro de los valores correspondientes a cada mes: 1 a 31 para enero, marzo, mayo, julio, agosto, octubre y diciembre; 1 a 30 para abril, junio, septiembre y noviembre; 1 a 28 para febrero o de 1 a 29 si el año es bisiesto.

- Además, se ha observado que el SRCEI tiene información de días 29 de febrero para años no bisiestos. En este caso, se toma como fecha válida, pero se modifica la fecha al día 28, con el objeto de que las herramientas de cálculo no generen error en la lectura de la fecha.

3. FILTROS DE CONTENIDO Y LIMPIEZA DE DATOS

Exclusivos para la base de datos de la SP:

Criterios fecha solicitud SP:

- Con la reforma previsional del año 2008 se traspasaron a las AFP las pensiones asistenciales (ex PASIS) con afiliación a las AFP sin saldo. Dado que las AFP reportan la fecha de traspaso a la AFP como fecha de pensión, se reemplaza este dato por la fecha de inicio de pago de la pensión asistencial.

- Cuando no fue posible validar la información de las fechas de invalidez, se utilizó la fecha de las Comisiones Médicas o SCOMP o CMF (según ese orden de prelación). Si en ninguna de las tres fuentes alternativas de información hubo información disponible, se dejaron esas fechas de invalidez como sin información.

- Para pensiones de invalidez, se consideró la fecha reportada por las Comisiones Médicas para casos con fecha de solicitud posterior a 2011, asignándose la fecha del primer dictamen por invalidez total y la del segundo dictamen por invalidez parcial. De esta forma, no se considera ni el período del proceso de calificación de invalidez, ni el período transitorio para inválidos parciales.

- Finalmente se deja la fecha de solicitud de pensión más antigua para cada causante de pensión.

Criterios y filtro de monto de pensión:

Se obtiene la información de monto y saldo de pensión de las siguientes fuentes y siguiente orden SCOMP, CMF e información de las AFP. Ambos datos se obtienen de forma conjunta de la misma fuente y en caso de no estar alguno de ellos, se dejan como sin información ambos.

Posteriormente, se eliminan todos aquellos causantes cuya pensión es inferior a la "Pensión Mínima para afiliados hombres y mujeres menores de 70 años" si la fecha de solicitud es anterior a julio 2008 y todos aquellos causantes cuya pensión es inferior a la "Pensión Básica Solidaria" (PBS) si la fecha de solicitud es posterior a julio 2008; se elimina además su grupo familiar. Este filtro se utiliza debido a que la población que tiene una pensión bajo la PBS no utiliza la tabla de mortalidad para el desgaste de sus fondos en RP y no puede acceder a la modalidad de Rentas Vitalicias, por lo cual no es usuaria de las tablas de mortalidad publicadas.

Se excluyen del filtro (no se eliminan) los siguientes:

- Causantes inválidos y su grupo familiar (se utilizan tablas vigentes para el cálculo aportes adicionales).

- Beneficiarios de sobrevivencias puras (se utilizan tablas vigentes para el cálculo aportes adicionales).

- Causantes que hayan jubilado anticipadamente y su grupo familiar (necesariamente cumplen el requisito para escoger modalidad de pensión y por tanto son usuarios de la tabla).

- Causantes que hayan entrado a SCOMP y su grupo familiar (necesariamente cumplen requisito pensión).

- Causantes pensionados en RV y su grupo familiar (necesariamente cumplen requisito pensión).

Las dos primeras excepciones se deben a que en esos casos se utilizan las tablas de mortalidad para el cálculo del aporte adicional, mientras que las tres últimas se deben a que en esos casos necesariamente se cumplen los requisitos para seleccionar modalidad de pensión.

Filtro inconsistencia entre monto y saldo de pensión para causantes de vejez: Se eliminan los registros con saldo_pensión/monto_pensión menores a 100 y mayores a 350. Se excluyen de este filtro aquellos con saldo_pensión menor a 3,5 y monto_pensión igual a 0,01. El monto de pensión se redondea a 2 decimales.

Estos dos últimos filtros, se aplican al final del proceso de construcción de la base de datos, así se puede contar con una base sin filtro de monto de pensión, para análisis adicionales.

Filtro modalidad de pensión

Se eliminan los registros correspondientes a rentas vitalicias, pues esa información es reportada por la CMF, pero se guarda la fecha de solicitud de dichos registros eliminados, para ser considerados como fecha de pensión en los datos de la CMF, quedando solo datos de retiros programados en la base de la SP.

Exclusivos para la base de datos de la CMF:

Filtro aceptaciones de reaseguro: Se eliminan las aceptaciones de reaseguro (por ser un registro que duplica al registro de la compañía cedente).

Filtro inconsistencia entre situación de invalidez y tipo de pensión16F^{25}: Se eliminan los causantes reportados como inválidos en la variable situación de invalidez y el tipo de pensión relacionado a vejez.

Filtros de inconsistencia de datos:

Filtro SRCEI: Se eliminan los registros que no tienen información certera del SRCEI.

Filtro inconsistencia fechas de nacimiento original versus resultado SRCEI: Este filtro elimina beneficiarios que no están recibiendo pensión que probablemente su RUN fue mal informado. Para encontrar los casos, se comparan las fechas de nacimiento originalmente informadas por las AFP o CSV, con las del SRCEI y se eliminan los casos donde se encuentran 3 o más dígitos distintos entre ambas fechas. Se exceptúan de este filtro a los beneficiarios fallecidos, donde coinciden los datos originales con los resultados del pareo, tanto en la fecha de fallecimiento como en el sexo.

Filtro datos vacíos, codificación errónea o fecha no valida (FNV): Se eliminan los registros sin información, con codificación errónea o con fecha no valida en las siguientes variables: RUN, fecha de pensión, fecha de nacimiento, fecha fallecimiento, sexo, código de parentesco y monto de pensión. En el caso de código de parentesco se consideró como código erróneo el de beneficiario designado de renta vitalicia.

Filtro inconsistencias entre fechas: Se eliminan los registros con inconsistencias entre fechas: fecha nacimiento>fecha fallecimiento, fecha pensión>fecha fallecimiento y fecha nacimiento>fecha pensión (exceptuando hijos)

Filtro error fecha de pensión: Se eliminan los registros con fecha de inicio de pensión anterior al 01/01/1981.

Filtro error edad pensión: Se eliminan los registros donde la edad a la fecha de inicio de la pensión es mayor a 120 años.

Filtro fecha de corte: Se eliminan los registros cuya fecha de pensión o de nacimiento es mayor a 31/12/2018, para alinearse a la fecha de corte de las bases de datos.

Filtro mismo RUN beneficiario y causante: Se eliminan los beneficiarios que tienen asociado el mismo RUN del causante de su pensión.

Filtro causantes de sobrevivencia pura: Se eliminan los causantes de pensión de sobrevivencia que fallecieron antes de pensionarse por vejez o invalidez.

Filtro tipo de pensión invalidez inconsistente: Se eliminan los registros de los causantes con "tipo de pensión" igual a invalidez y "situación de invalidez" igual a "no". Esto porque corresponde a una inconsistencia entre el tipo de pensión y la situación de invalidez del rentista, no pudiendo inferir la real situación de invalidez del pensionado.

Filtros de inconsistencia con el grupo familiar:

Filtro inconsistencia sexo entre cónyuges: Se eliminan los registros de cónyuges o madre/padre de hijo de filiación no matrimonial, que tengan el mismo sexo que el causante.

Filtro inconsistencia edad cónyuge: Se eliminan los registros de cónyuges que tengan a la fecha de fallecimiento del causante menos de 16 años de edad.

Filtro inconsistencia edad madre/padre de hijo de filiación no matrimonial: Se eliminan los registros de madres/padres de hijo de filiación no matrimonial, que tengan a la fecha de fallecimiento del causante menos de 12 años de edad.

Filtro inconsistencia entre edad causante e hijo beneficiario: Se eliminan los registros de beneficiarios, en que la edad del causante sea menor a 12 años a la fecha de nacimiento del hijo beneficiario.

Filtro inconsistencia entre edad de madre/padre del causante y causante: Se eliminan los registros de padres o madres de causantes, en que la edad de padre o madre del causante sea inferior a 12 años a la fecha de nacimiento del causante.

Filtro inconsistencia sexo del padre o madre de causante: Se eliminan los registros de los padres de causante con sexo femenino y las madres de causante con sexo masculino.

4. TRATAMIENTO DE DUPLICADOS EN CADA BASE

Cada individuo debe exponer dentro de un mismo grupo una sola vez (ver composición de las tablas en sección 2.2). Los individuos son identificados a través de su RUN y se tratan de la misma forma en cada base de datos (SP, CMF) por separado previo a la consolidación. Estos criterios o filtros se realizan de forma posterior a la eliminación de registros por inconsistencia de datos y se aplican secuencialmente.

Filtro duplicados beneficiarios potenciales base SP: Se eliminan los beneficiarios potenciales si ya existe un registro como beneficiario efectivo para un mismo grupo familiar, por tener el beneficiario efectivo información más actualizada que cuando era un beneficiario potencial. Sólo base SP.

Filtro duplicados beneficiarios asociados a causantes: Se eliminan todos los registros de beneficiarios que aparecen asociados a más de 2 causantes, por entenderse como RUN erróneamente asignados y no poder identificar al causante del que efectivamente es beneficiario. Sólo base SP (CMF aplica filtro de flags^{26}).

Filtro duplicados beneficiarios asociados a cada tabla: Se eliminan los registros duplicados de beneficiarios que aparecen más de una vez en una misma tabla. Para ello, se deja el registro con fecha de inicio de vigencia más antiguo.

Filtro inconsistencia situación invalidez, causante-beneficiario-inválidos: En caso de encontrarse un RUN en los 3 grupos (causante, beneficiario no inválidos e inválidos), se eliminan todos los registros, a excepción del causante inválido si corresponde a la primera pensión.

Filtro inconsistencia situación invalidez misma fecha vigencia: Si un individuo (RUN) aparece en varios registros con una misma fecha de inicio de pensión, calificado en unos como inválido y en otros como no inválido (causantes o beneficiarios), se eliminan todos los registros asociados al RUN. En el caso que el RUN en algunos de los registros duplicados corresponda a un causante calificado como inválido, este registro se mantiene eliminando sus duplicaciones en las que difiere de esta calificación.

Filtro inconsistencia en situación de invalidez del causante: Este filtro considera dos situaciones:

a) Los registros asociados a un RUN de causante que aparece calificado como no inválido en una pensión inicial y que en un registro posterior aparece calificados como inválido (ya sea en la condición de causante o beneficiario) se eliminan. Esto porque un causante que ya se pensionó como no inválido, no podrá pensionarse por invalidez posteriormente. En el caso de que en el registro posterior aparezca como beneficiario inválido, se asume que correspondería a un cónyuge y que debiera estar clasificado como no inválido en la base de datos.

b) Los registros asociados a un RUN de causante que aparece calificado como inválido en una pensión inicial y que en un registro posterior aparece calificado como no inválido (ya sea como causante o beneficiario), se eliminan todos los registros en que el RUN se califica como no inválido y se mantiene el registro de la primera pensión correspondiente al causante inválido. En este caso, si el causante inválido contrata una segunda pensión, por norma, no podrá ser clasificado como inválido, por lo que el registro válido corresponderá al causante inválido.

Filtro inconsistencia en situación de invalidez del beneficiario: Este filtro considera dos situaciones:

a) Los registros asociados a un RUN de beneficiario que aparecen en una primera pensión como no inválidos y luego en un registro posterior (segunda pensión) como inválidos (ya sea causante o beneficiario), se dejan ambos registros, pero el registro del beneficiario no inválido se deja con fecha final de exposición la fecha de inicio de vigencia de la invalidez. Esto debido a que se considera que es factible que alguien que no era causante se haya invalidado con posterioridad a la primera aparición en el sistema de pensiones ya sea como beneficiario o causante.

b) Los registros asociados a un RUN de beneficiarios inválidos y que en un registro posterior (segunda pensión) aparecen como causantes o beneficiarios no inválidos se eliminan. Esto porque se considera que un inválido no cambiará su situación de invalidez una vez que fue calificado como tal.

5. CRITERIOS PARA LA CONSOLIDACIÓN DE LAS BASES DE DATOS

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_74.jpg?ts=1691091493)

<!-- figura eb87b8ddcee2e64c5e62579b657e8b74469c35582ea6359547956ca06a20454c -->

Una vez depurada cada base de datos individual, se procede a consolidar éstas.

Filtro inconsistencia edad de pensión - Filtro de seguridad:

Este filtro corresponde a un filtro de seguridad, que tiene el objeto de revisar casos que puedan tener error en el RUN pareado con el SRCEI, por lo que se realiza para todos los casos donde hubo cambio de fecha de nacimiento.

Para este filtro, se debe rescatar antes el mínimo de las fechas de inicio de vigencia de pensión de cada causante de pensión para cada una de las bases de datos (SP, CMF), además de su situación de invalidez. La fecha de inicio de vigencia a considerar corresponde a la fecha de inicio de pensión original de cada BD, la cual debe ser válida (no nula, distinta de cero o sin error).

Luego, se analiza la edad del causante a la fecha de la primera pensión (considerando fecha de nacimiento post pareo de los registros en análisis). Se considera que hay inconsistencia de la edad de pensión cuando ocurra lo siguiente:

a) Causantes no inválidos, donde la edad al inicio de vigencia de la pensión es menor a 35 años.

b) Causantes no inválidos, donde la edad al inicio de vigencia de la pensión es mayor a 85 años.

c) Causantes inválidos, donde la edad al inicio de vigencia de la pensión es menor a 18 años.

d) Causantes inválidos, donde la edad al inicio de vigencia de la pensión es mayor a 70 años.

Identificadas estas inconsistencias, se eliminan los registros del causante en cada una de las bases de datos en que aparece.

En este filtro la edad se considera entera (redondeada).

Duplicados con error: Los registros asociados a RUN con diferencias entre la base de la SP y CMF, en los campos de sexo, fecha de nacimiento y/o fecha de fallecimiento se eliminan.

Filtro duplicados, inicio de exposición consolidación: En el caso de los RUN que se dupliquen en cada tabla de mortalidad y entre las bases de la SP y la CMF, se deja como fecha de inicio de exposición a la menor registrada entre ambas y se elimina el registro de la SP. Luego se buscan nuevamente RUN duplicados en cada tabla, pero entre las 2 bases de datos (CMF, SP).

Filtro inconsistencia situación invalidez misma fecha vigencia: Si un individuo (RUN) aparece en varios registros con una misma fecha de inicio de pensión, calificado en unos como inválido y en otros como no inválido (causantes o beneficiarios), se eliminan todos los registros asociados al RUN. En el caso que el RUN en algunos de los registros duplicados corresponda a un causante calificado como inválido, este registro se mantiene, eliminando sus duplicaciones en las que difiere de esta calificación.

Filtro inconsistencia en situación de invalidez del causante: Este filtro considera dos situaciones:

a) Los registros asociados a RUN de causantes no inválidos que en un registro posterior aparecen en el grupo de inválidos (ya sea como causante o beneficiario) se eliminan.

b) Los registros asociados a RUN de causantes inválidos que en registros posteriores aparecen calificados como no inválidos, ya sea como causante o beneficiario, se mantiene la calificación del primer registro correspondiente a inválido. En el caso que las fechas de inicio de vigencia son iguales, se eliminan los 2 registros.

Filtro inconsistencia en situación de invalidez del beneficiario: Este filtro considera dos situaciones:

a) Los registros asociados a RUN de beneficiario no inválido que aparecen en un registro posterior calificado como inválido (ya sea causante o beneficiario), se tratarán como registros independientes en la base fusionada, asignando al registro del beneficiario no inválido como fecha fin de vigencia la fecha de inicio vigencia del registro donde se califica al RUN como inválido.

b) Duplicados entre grupos beneficiarios e inválidos: Se eliminan los registros que aparecen en el grupo de inválidos (ya sea como causante o beneficiario) donde la fecha de inicio de vigencia del beneficiario no inválido es posterior o igual al inicio de vigencia en que aparece como inválido (se considera que una persona declarada inválida no cambia su situación de invalidez). En el caso de que el beneficiario no inválido tiene fecha de vigencia anterior al del grupo de inválidos, se dejan ambos registros, pero en la primera pensión se coloca como fecha final de exposición la fecha de inicio de vigencia de la invalidez (se considera que la persona se invalidó en la fecha de inicio de vigencia de la segunda póliza o pensión). En el caso que las fechas de inicio de vigencia sean iguales, se eliminan los 2 registros.

Filtro inconsistencia situación invalidez, causante-beneficiario-inválidos: Los registros asociados a un mismo RUN que se encuentre en los 3 grupos de calificación, (causante, beneficiario no inválidos e inválidos), se eliminan, a excepción del registro asociado al causante inválido si este corresponde a la primera pensión. Esto porque se asume que un causante inválido, por norma, no aparecerá en la BD como inválido en pólizas posteriores.

6. NÚMERO DE REGISTROS RESULTANTES

A continuación, se muestra el número de registros resultantes de la depuración de cada base de datos por separado y luego de la consolidación. Notar que los datos de causantes y beneficiarios no inválidos hombres se juntan después de la consolidación de las bases de datos.

6.1 Base de datos de la SP

Registros antes de filtros de limpieza y duplicados

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_75.jpg?ts=1691091493)

<!-- figura 27b78576bd621fdcbe13f68300bcdaadb22492b12908d9f5289f3a54d076c43b -->

Registros después de filtros de limpieza y duplicados

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_76.jpg?ts=1691091494)

<!-- figura 91bbf41197b4dc67526d949077824b630332f88f5c3184eb87ce2a234655748f -->

6.2 Base de datos de la CMF

Registros antes de filtros de limpieza y duplicados

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_77.jpg?ts=1691091494)

<!-- figura 74b4aaa64cda3fa557487abc8dd928d7091b616a84051e8385f2c8eefd30732d -->

Registros después de filtros de limpieza y duplicados

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_78.jpg?ts=1691091494)

<!-- figura 655f9bf43a0b56cdcc5b0ae13410940b26ca62e1e25661454a94e128150900c0 -->

6.3 Consolidación

Registros antes y después de la consolidación, por fuente de datos

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_79.jpg?ts=1691091495)

<!-- figura 1d2701d883f5768c752ef4696947eda51c5163e49ce6ed81b3d23f4f09e58074 -->

Registros antes y después de filtro de monto de pensión, por fuente de datos

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_80.jpg?ts=1691091495)

<!-- figura 848840067248cad6287c3211a056ea1b56e9d377b653b45d8f6e4cf235c8c535 -->

Después de la consolidación y filtro de monto de pensión, por tipo de beneficiario

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_81.jpg?ts=1691091496)

<!-- figura a6dd471601a0078d95269c47da32e2a5eb52c7671143638feada4c33145cbd83 -->

Finalmente, después de aplicar los filtros de consolidación se juntan las tablas de causantes y beneficiarios no inválidos para los hombres, así la base de datos consolidada se compone de los siguientes registros.

![Figura](https://www.spensiones.cl/portal/compendio/596/articles-15660_recurso_82.jpg?ts=1691091496)

<!-- figura 293520e18c4202846e38e6e8613d14357e780fcc284328a07f5ef1eb0d0d98b4 -->

> **Nota de actualización:** Este Anexo fue agregado por la Norma de Carácter General N° 306, de fecha 24 de febrero de 2023.

*1Organización para la Cooperación y el Desarrollo Económicos (OCDE) agrupa a 38 países miembros. Chile es miembro desde el 2010. Su misión es promover políticas que mejoren el bienestar económico y social de las personas alrededor del mundo.*

*2La base de datos se encuentra disponible tanto en el sitio web de la CMF como el de la SP.*

*3Para un mayor detalle de los filtros aplicados a la base de datos del sistema previsional, véase el APÉNDICE N° 4.*

*4Corresponde al mínimo de las fechas de inicio de vigencia de pensión de cada causante de pensión para cada una de las bases de datos (SP, CMF).*

*5Para mayor detalle ver APÉNDICE N° 4.*

*6Tres años después de la calificación de invalidez parcial, se realiza una segunda calificación, que puede confirmar la pensión de invalidez o revocarla.*

*7Después de la reforma de pensiones del año 2008, todas las pensiones por invalidez total se consideran permanentes, sin necesidad de reevaluación.*

*8Los diagnósticos potencialmente terminales fueron identificados por la División de Comisiones Médicas de la Superintendencia de Pensiones.*

*9Esto se implementó sumándole 3 años a la fecha de pensión de las personas con invalidez total, al momento de realizar el cálculo de las tasas brutas de mortalidad de invalidez.*

*10La descripción de esta metodología se detalla en el punto I. del APÉNDICE N° 2.*

*11El ajuste de WH tiene mayor ponderación para las edades más distantes del punto de unión y, por el contrario, se otorga mayor ponderación al ajuste del modelo de extrapolación para las edades más cercanas al punto de unión. En función de este criterio, y considerando la definición de tres puntos de unión, se utilizó 3/4 para el más lejano, 1/4 para el más cercano al punto de unión y 1/2 para el punto central.*

*12El uso de factores de mejoramiento en dos dimensiones (edad y año) ha sido ampliamente adoptado en el ámbito previsional, por ejemplo, en Canadá, Estados Unidos y Reino Unido.*

*13Los principales cambios fueron la disminución del umbral de pensión para elegir modalidad de pensión, que pasó del monto de la Pensión Mínima al monto de la Pensión Básica Solidaria, y la eliminación del período transitorio para las pensiones de invalidez total.*

*14Estimaciones y Proyecciones de la Población de Chile 1992-2050. Total País. Metodología y Principales Resultados. INE, diciembre 2018.*

*15Lee-Carter, P-Spline, Booth-Maindonald-Smith, Hyndman-Ullah, Robust Hyndman-Ullah, Weighted Hyndman-Ullah y Hyndman, Booth & Yasmeen (2012).*

*16Escala de mejora de la mortalidad bidimensional, por el Instituto Canadiense de Actuarios.*

*17En los datos del INE, la transición en los años censales no es suave, pero esos años no están en el borde de la ventana usada.*

*18En sus últimas tablas Canadá usó 105 años; el Reino Unido, 110 años y Estados Unidos, 115 años.*

*19Our World in Data: Life Expectancy vs GDP per capita, 2015.*

*https://ourworldindata.org/grapher/life-expectancy-vs-gdp-per-capita?tab=chart&stackMode=absolute&country=CHL~CAN~JPN~NZL~KOR~ESP~GBR~USA&region=World*

*20La escala en el mapa de calor presentado muestra los mejoramientos más elevados asociados al color rojo y va disminuyendo en intensidad de acuerdo a los cambios en los datos.*

*2160 años o más para mujeres y 65 años o más para hombres.*

*22Durante el proceso de consulta pública, se observó un aumento en el número de fallecidos para el periodo junio-octubre 2022. Sin embargo, este fue menor respecto al periodo 2020-2021. Este aspecto también es discutido en el apartado Covid-19 de la sección VII. Proceso de Consulta Pública del informe normativo de las TM2020 publicado por la CMF.*

*23Considera los códigos CIE U07.1 (COVID-19, virus identificado) y U07.2 COVID-19 (virus no identificado).*

*24Para determinar el exceso de mortalidad se extrapoló la tendencia lineal observada entre 2016-2019 para determinar el crecimiento en el número de fallecimientos y aplicó este crecimiento semanalmente al promedio 2016-2019.*

*25Este filtro se aplica al final del proceso de construcción de la base de datos.*

*26El SRCEI en conjunto con los resultados del pareo entrega un flag para cada registro, según la siguiente codificación: 1 "Apellidos y nombres coinciden 100%", 2 "Apellidos coinciden 100% y nombres coinciden ≥60%", 3 "Apellidos coinciden 100% y nombres coinciden ≤60%", 4 "Búsqueda por nombre: los apellidos y nombres coinciden en un 100%, coincidiendo también la fecha de nacimiento, 5 "No existe el registro" y 6 "Formato inválido en registro de entrada".*

**Fuente oficial:** Libro III, Título X Tablas de Mortalidad, Anexos, Anexo N° 10 Nota técnica construcción tablas CB-H-2020 (hombres), MI-H-2020 (hombres), RV-M-2020 (mujeres), B-M-2020 (mujeres) Y MI-M-2020 (mujeres) · https://www.spensiones.cl/portal/compendio/596/w3-propertyvalue-10626.html
