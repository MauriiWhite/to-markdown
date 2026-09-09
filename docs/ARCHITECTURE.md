# Decisiones de diseño

Por qué el proyecto está hecho así. Cada sección es una decisión que costó algo entenderla
y que se revertiría sola si nadie la escribe.

Si venís a **cambiar** el pipeline, lee también [`../AGENTS.md`](../AGENTS.md), que es el
contrato de trabajo. Este documento explica el *porqué*; aquel dicta el *qué*.

## El problema

La Superintendencia de Pensiones publica el Compendio de Normas del Sistema de Pensiones de
dos formas: capítulo por capítulo en su portal web, y como cinco PDF únicos. Ninguna de las
dos es consumible por un agente tal cual viene.

El pipeline extrae la primera, la convierte a Markdown, y usa la segunda como **testigo** de
que la extracción quedó completa.

## Restricciones que no se negocian

### 1. Sin servicios de pago ni credenciales

El pipeline completo corre con **dos dependencias de Python** (`fake-useragent`, `pillow`) y
`poppler-utils` del sistema. No hay cliente de IA, ni claves, ni `.env`.

La corrida por defecto no usa credenciales ni servicios de pago. Si algún día una etapa
necesitara una, tendría que quedar fuera del camino por defecto — como está `refresh`, que
es la alternativa a `crawl` y nunca su continuación.

### 2. El modelo no toca nada

Jerarquía, numeración normativa, tablas HTML y notación `<sub>`/`<sup>` se extraen con
**parser**, no con un modelo. Todo el pipeline es determinista.

Lo que queda encerrado en píxeles **no se interpreta**: se enlaza a su original en el sitio
de la SP y quien lea decide. Adivinar el contenido de una imagen es peor que enlazarla,
porque produce una afirmación con la forma de un dato verificado y sin serlo.

El efecto colateral es que **todo se puede probar**: no hay una mitad del pipeline que
dependa de un servicio externo y quede fuera del alcance de la suite.

### 3. La transformación es aditiva

Ninguna etapa puede perder información. Toda figura conserva su `src`, su `sha256`, su
archivo local **y su URL en el sitio de la SP**, que es lo que la hace verificable. Si algo
no se puede resolver, se deja la referencia y se avisa — nunca un hueco en silencio.

Por eso una imagen que no se pudo descargar sigue apareciendo como
`![Figura](https://www.spensiones.cl/…)` en el entregable y no como un comentario mudo: la
URL puede funcionar perfectamente aunque nuestro `urlopen` haya fallado ese día.

### 4. Fallar cerrado, nunca abierto

El peor fallo de un scraper no es caerse: es **seguir corriendo y devolver menos**. Si la SP
cambia su CMS y `#cuerpo_documento` deja de existir, el pipeline extraería documentos vacíos
y los escribiría encima de los buenos sin decir nada.

Por eso `guard.py` valida antes de escribir y aborta conservando el corpus anterior.

Y por eso las cotas se defienden: **si una invariante estorba, la respuesta es entender por
qué se violó, no bajarle el umbral.** Una invariante mal calibrada llora lobo hasta que deja
de significar algo.

---

## Decisiones de estructura

### Dos fuentes, cinco Libros

`data/` se parte primero por **fuente** y después por Libro:

```
data/web/book-i/     lo que la SP publica en su portal — lo que el pipeline extrae
data/pdf/book-i/     el mismo Compendio que la SP exporta como documento único
```

Son dos testimonios de lo mismo y no se mezclan. Juntarlos en una carpeta haría imposible la
única pregunta que justifica tenerlos los dos: **qué trae uno que el otro no**.

### Un Libro, una carpeta

Cada Libro tiene su caché, sus imágenes, su manifiesto, su estado y su entregable bajo
`data/<fuente>/<slug>/`, y ninguna etapa mezcla dos.

La separación es exacta y está verificada: los **1.476 nodos** del árbol cuelgan de un único
Libro, y **ninguna de las 1.747 figuras** aparece en dos. Por eso cada Libro puede deduplicar
dentro de su carpeta sin coordinarse con los otros.

Que sean independientes es lo que permite que **una regresión en un Libro no arrastre a los
otros cuatro**: las invariantes se evalúan por Libro y abortan solo el suyo.

### La carpeta se nombra por el numeral romano, no por el título

La clave de partición es el **`pvid` raíz**, nunca el título. La SP ya renombró los Libros I
y V, y hoy conviven **39 documentos con el nombre anterior en su breadcrumb**. Una carpeta
nombrada por el título se habría partido en dos con ese cambio.

El `pvid`, en cambio, no ha cambiado nunca: es la única clave estable del árbol.

### Las invariantes van por Libro, no sobre el total

Sobre el total, perder entero el Libro I deja 1.092 documentos — por encima de cualquier
cota global razonable— y el fallo pasa inadvertido. Por Libro, salta de inmediato.

---

## Decisiones de extracción

### `is_leaf` no es "tiene texto"

Un nodo puede tener hijos **y** cuerpo normativo propio: un Título que además imparte
instrucciones, un Capítulo con preámbulo antes de sus números.

Son **24 en el corpus** y valen **189.686 caracteres** que el PDF de la SP sí imprime. El
pipeline los descartaba en silencio por no ser hojas.

El manifiesto lleva `has_body` por nodo y `documents` con la lista autoritativa ya en orden
de lectura. **Ninguna etapa vuelve a derivarla de `is_leaf`** — que la calcule el crawl y no
cada etapa es lo que impide que vuelvan a discrepar.

### El orden es el de lectura, no el del `pvid`

El árbol se recorre en profundidad, con los hijos en el orden en que el CMS los lista. Es el
orden en que el Compendio se lee y en que la SP lo imprime.

Ordenar por `pvid` daría otra cosa: los pvid se asignan por fecha de creación, así que un
capítulo agregado después queda al final aunque normativamente vaya al medio.

### Una conexión viva por hilo, no una por petición

Es la diferencia más grande del crawl y la que nada delataba. `urllib.urlopen` abre una
conexión TCP nueva —con su handshake TLS— en **cada una** de las 1.476 páginas. Sobre este
sitio eso cuesta 917 ms por página; reutilizando la conexión, 310 ms.

Lo importante es que **no toca la concurrencia**: siguen siendo `max_workers` conexiones
simultáneas, solo que no se tiran y se rehacen. El límite medido de 3 hilos se respeta
entero, y de hecho el servidor hace *menos* trabajo, no más.

Va por hilo y no en un pool compartido porque una conexión HTTP/1.1 sirve una petición a la
vez, y `ThreadPoolExecutor` ya da exactamente `max_workers` hilos: `threading.local()` es
toda la coordinación que hace falta.

El corolario es que el pool tiene que ser **uno para toda la corrida**. Antes se creaba un
`ThreadPoolExecutor` por nivel del árbol, así que cada nivel levantaba hilos nuevos y con
ellos conexiones nuevas — que es justo lo que el keep-alive evita.

### Se pide gzip, que el servidor ya servía

`urllib` nunca mandaba `Accept-Encoding`, así que el sitio devolvía HTML sin comprimir.
Pedirlo son 0,19 MB en la red por cada 0,89 MB de HTML: **4,7x menos transferencia**, que
además es menos trabajo para el servidor del organismo.

### Y el ETag se normaliza, o el gzip habría roto la actualización

Ésta es la trampa, y es silenciosa. Apache le agrega `-gzip` al ETag cuando sirve comprimido
(`mod_deflate`), y **ese ETag no vuelve a calzar**: devolverlo en `If-None-Match` responde
200, no 304. El ETag plano, en cambio, da 304 aunque la petición pida gzip.

Sin normalizarlo, activar el gzip habría hecho que `refresh` re-descargara las 1.476 páginas
en cada corrida en vez de recibirlas como 304 de cero bytes. El corpus habría seguido
saliendo correcto — solo que tardando veinte veces más, sin que nada lo avisara. Es
exactamente el tipo de fallo abierto que el resto del proyecto evita.

Medido después del arreglo: **156 de 156 páginas responden 304, cero bytes transferidos.**

### Las redirecciones se siguen a mano

`urllib.urlopen` las seguía solo; `http.client` no. Este sitio responde **302 a cualquier
pvid inexistente**, y sin seguir la redirección se cachearía el stub de 267 bytes del 302
como si fuera la norma: HTML válido, sin cuerpo normativo, que el parser habría dado por
página vacía.

Siguiéndola se llega al 404 real y la petición falla ruidosamente, que es lo correcto.

### El cuerpo se compara contra `Content-Length`

Una respuesta cortada a la mitad es el fallo que más caro sale: se cachearía como HTML
válido y el parser extraería un documento truncado sin que ninguna invariante se queje,
porque un documento corto sigue siendo un documento. Se compara **antes** de descomprimir,
que es lo que mide `Content-Length`.

### `max_workers = 3` está medido, no elegido

Con 8 hilos `spensiones.cl` responde `502`. Con 3 completa el árbol sin fallos. **No se
sube.**

El recorrido por Libro no cuesta nada frente al recorrido único: son las mismas 1.476
peticiones repartidas en cinco tandas. Lo que se gana es que el caché queda particionado en
origen, no reordenado después.

### Las cabeceras HTTP se normalizan a minúsculas

`dict(response.headers)` pierde la insensibilidad a mayúsculas de `HTTPMessage`, y este
servidor manda `Etag` — ni `ETag` ni `etag`. Sin normalizar, el ETag no se guardaba nunca y
la revalidación caía en silencio al `Last-Modified`, que es una señal más débil.

### `<sub>`/`<sup>` son notación matemática, no notas al pie

Verificado sobre las **837 ocurrencias** del corpus: son `VC_{i}`, `l_{x}`, `BH_{m}`. Se
convierten a `_{…}` / `^{…}`.

### Las tablas sin `<th>` no promueven su primera fila

Solo **4 de las 371 tablas** del corpus traen `<th>`. En las otras 367, promover la primera
fila a encabezado convertiría un dato en un rótulo y un agente leería mal la tabla.

Las celdas vacías se conservan: en normativa una celda vacía puede ser información —un campo
que no aplica—, no ruido.

### Los `<h6>` se separan en dos

**3.076** son "Nota de actualización" y dicen qué NCG modificó el número anterior: van como
cita (`>`), pegados a su número. Los otros **71** son pies de figura y fuentes: quedan en el
cuerpo, junto a lo que describen.

El Manual de Cuentas mete sus notas dentro de celdas de tabla y a mitad del texto de la
celda, así que la detección es independiente del contexto — un regex posicional nunca
calzaría ahí.

---

## Decisiones de detección de cambios

### Dos hashes, no uno

| Hash | De qué | Responde |
| --- | --- | --- |
| `source_sha256` | El cuerpo HTML de origen | ¿cambió la norma? |
| `content_sha256` | Nuestro Markdown | ¿cambió nuestra salida? |

Son distintos **a propósito**. Con uno solo, cada mejora al parser se vería como si 1.220
normas hubieran cambiado, y el changelog dejaría de valer.

Cruzarlos es lo que da la clase `pipeline`: *cambió nuestra salida, no la norma*.

### Tres señales, no un booleano

| Señal | Origen | Responde | Falla sola porque |
| --- | --- | --- | --- |
| `ETag` / `Last-Modified` | HTTP | ¿el servidor tocó la página? | un re-guardado del CMS parece un cambio |
| `source_sha256` | cuerpo HTML | ¿cambió el contenido de origen? | exige descargar todo |
| Nota de actualización nueva | la norma | ¿es un cambio normativo? | una corrección de tipeo no lleva nota |

Cruzarlas da una **clasificación** —`normative`, `editorial`, `cosmetic`, `pipeline`, `new`,
`removed`— que es mucho más útil que un booleano: un retoque del CMS, una corrección de
tipeo y una modificación por Norma de Carácter General no se accionan igual.

### El diff es por número normativo

"El N° 4 del Capítulo II cambió, por NCG 370" es accionable. "Este documento de 12 KB
cambió" no lo es. El corpus tiene **7.200 unidades direccionables** (`4074#4`).

### La renumeración se empareja por hash, no por número

**93 notas** del corpus documentan cosas como *"pasando los actuales números 3 al 12 a ser 5
al 14"*. Emparejando solo por número, cada una produciría decenas de cambios falsos.

Las unidades se emparejan primero por hash de contenido: misma unidad con otro número es una
**renumeración**, no una modificación.

### El estado avanza en `changes`, no en `parse`

Si avanzara en `parse`, el diff se compararía contra sí mismo y siempre diría "sin cambios".

---

## Decisiones del entregable

### Un archivo Markdown por Título

Un Título es la unidad con la que la norma **se cita y se modifica entera**, y con la que la
SP encabeza cada página de su PDF. Sus Letras, Capítulos y Anexos no se leen sueltos: van
dentro del mismo archivo, anidados como encabezados.

Repartido por Capítulo, el Libro I serían 84 archivos que hay que recomponer a mano para
leer una sola norma.

### La agrupación se resuelve por el árbol, no por el texto del título

Los nombres se repiten: *"Capítulo I. Introducción"* aparece **11 veces solo en el Libro
III**, bajo Letras distintas. Agrupar por nombre los fundiría en un archivo.

### El ordinal sale del árbol completo

Si el número de archivo se calculara sobre el subconjunto que se exporta, cada capítulo que
el lado PDF no logra alinear correría todos los siguientes, y los dos árboles dejarían de
poder compararse con un `diff`.

### Las figuras apuntan a la SP, no a la copia local

Lo que este corpus garantiza sobre una figura es su **procedencia**. Quien lea el documento
tiene que poder abrir la imagen tal como la publica la Superintendencia, sin intermediarios
y sin depender de que alguien haya copiado bien el archivo.

La copia local sigue existiendo bajo `images/<sha256>` y su hash va en el comentario de
traza. Es el respaldo por si la SP cambia o retira el archivo, no la fuente de verdad.

El costo es explícito: **las figuras requieren conexión para verse.**

### Los encabezados del cuerpo se bajan dos niveles

El cuerpo trae `#`…`#####` heredados del HTML de la SP. Pegados tal cual bajo el `#` del
Título, un `#` interno competiría con el título del archivo y el índice del Markdown saldría
plano. Bajarlos conserva la jerarquía en vez de aplanarla.

### `bundle` va aparte de `export`

`data/` es el área de trabajo del pipeline, con su caché, su estado y sus artefactos
intermedios. `output/` es lo único que se le manda a alguien. Son dos cosas distintas y por
eso son dos etapas.

### El índice de cada Libro no es decorativo

Cuando el destinatario es un modelo, sin índice encontrar "el Capítulo XXIV del Título III"
obliga a leer los 12 archivos del Libro; con índice, es una consulta y después **un solo
archivo**.

Por eso el `index.md` lleva las Letras y Capítulos de cada Título, y las **materias** — las
etiquetas que pone la propia SP, que valen más que cualquier clasificación que
inventáramos nosotros.

### El paquete se fecha por el crawl, no por hoy

El bundle puede rearmarse mil veces sobre un corpus de la semana pasada. Fechar el paquete
en vez del contenido haría creer que la norma está más al día de lo que está.

---

## Decisiones de la descarga del PDF

### El enlace sale del pvid, no de una lista

El portal enlaza el Libro completo desde su propia raíz como `fo-propertyvalue-<pvid>.pdf`.
Derivarlo del `pvid` significa no tener una segunda fuente de verdad que mantener al día: es
la misma clave con la que se particiona `data/`, y la única que la SP no ha cambiado nunca.

El costo es que si la SP cambia el esquema de la URL, nada lo notaría hasta que la descarga
fallara. Por eso hay un canario de red que lo comprueba contra la raíz de cada Libro.

### Se renombra porque el nombre del servidor no dice nada

`fo-propertyvalue-2536.pdf` no dice de qué Libro es, y el nombre del archivo es lo único que
ve `compare` cuando lo abre. `Book1.pdf` sí lo dice.

### Y se verifica **antes** de renombrar

Ésta es la decisión que justifica toda la etapa. Renombrar sin verificar sería peor que bajar
los PDF a mano: un `Book3.pdf` que en realidad fuera el Libro IV se compararía contra el
árbol equivocado, y `coverage.md` saldría lleno de "contenido solo en el PDF" sin que ninguna
invariante se quejara — el mismo fallo silencioso que `guard.py` existe para evitar.

Por eso el archivo se descarga a un temporal y solo se mueve si verifica. Es el mismo
**fallar cerrado** del resto del proyecto: un PDF que no corresponde no puede pisar al que ya
estaba.

### Dos comprobaciones, porque el encabezado solo dice la mitad

1. **El PDF se declara a sí mismo.** Cada página lleva
   `Compendio de Normas del Sistema de Pensiones - Libro III` como encabezado corrido.
2. **Corresponde a lo que extrajo el crawler.** Las páginas repiten el `path` de la norma con
   el mismo texto que `parse` guardó en `documents.json`.

La primera dice "este archivo es el Libro III". La segunda dice "y es el mismo Libro III que
recorrió el crawler". Sin la segunda, un PDF vigente contra un caché viejo pasaría inadvertido.

Medido: cada PDF verifica contra el suyo con 11 a 22 secciones cruzadas y **rechaza los 20
emparejamientos incorrectos**.

### Se muestrea en bloques contiguos, no en páginas sueltas

El encabezado está en todas las páginas, pero el breadcrumb solo aparece donde arranca una
sección, y esos arranques van agrupados. Muestrear equiespaciado cae sistemáticamente entre
ellos: con 32 páginas sueltas el Libro IV daba 10 secciones en 34 s.

Cuatro bloques de 16 páginas —las mismas 64, pero en 4 llamadas a `pdftotext` en vez de 32—
dan 23 en 4,7 s. Un bloque contiguo cae dentro de una sección entera, y leer un rango cuesta
una sola apertura del archivo en lugar de una por página.

### El cruce es por prefijo

El PDF corta los breadcrumbs largos con el salto de línea
(`…Estadísticas de afiliados pensionados y de Bonos de`). Exigir el string entero declararía
huérfanas dos de cada tres secciones legítimas.

Como `path` empieza por el Libro, un breadcrumb del Libro equivocado no puede calzar por
prefijo con este conjunto ni por casualidad.

### El encabezado se ancla a la línea completa

El cuerpo normativo también cita al Compendio: *"…del Título IV del Libro I del Compendio de
Normas del Sistema de Pensiones. Información"*. Tomar cualquier línea que lo mencione
rechazaba el Libro I, que es correcto.

### El ETag evita re-bajar 130 MB

Los cinco Libros pesan 130 MB y la etapa está en la corrida por defecto. Sin revalidación
condicional, cada `uv run python -m to_markdown` los bajaría de nuevo.

La primera corrida después de tenerlos a mano no tiene `ETag` guardado; ahí decide el
`Content-Length`, para no re-descargarlos solo para descubrir que ya estaban.

---

## Decisiones de la comparativa

### Se alinea antes de comparar

Comparar sin alinear daría un diff de 9 MB contra 10 MB: ilegible e inaccionable. Alineado,
la pregunta se contesta por capítulo: *"el N° 3 del Capítulo II está en el PDF y no en la
web"*.

El PDF se lleva al mismo orden y a la misma segmentación que la web, y cada documento se
ancla avanzando siempre hacia adelante.

### Dos métricas, porque una sola confunde dos cosas

El Manual de Cuentas del Libro IV lo muestra: la web lo publica como tabla HTML y sale
`| nivel | cuenta de mayor |`; el PDF imprime esas mismas celdas seguidas y en otro orden de
columnas. Los n-gramas no calzan y **parece contenido nuevo**, pero las 21 palabras
distintivas del pasaje están las 21 en la web.

- **n-gramas** (`shingle = 8` palabras): ¿está el mismo texto, en el mismo orden?
- **léxico**: ¿está el mismo vocabulario, sin importar el orden?

Con las dos juntas la lectura es inequívoca: **n-gramas bajos y léxico alto es reformateo;
los dos bajos es contenido que de verdad solo está de un lado.**

Sin separar `reformatted`, esa sección reportaba **9.901 palabras de "contenido nuevo"** que
no lo eran.

### El n-grama es una tupla de palabras, no una cadena

El n-grama solo se usa como **miembro de un conjunto**: nadie lee nunca su contenido, y
`runs()` agrupa los pasajes por la posición, no por el texto. Construir 2 millones de
cadenas unidas para eso era el mayor costo de la etapa.

Una tupla de palabras es **exactamente la misma identidad** —dos tuplas son iguales si y
solo si sus palabras lo son— sin construir ninguna cadena. Las palabras se internan porque
el corpus repite muchísimo ("de", "la", "pensión"): con `sys.intern` todas las apariciones
comparten un objeto, y con él su hash ya calculado.

Un **hash rodante** habría sido más rápido todavía, y se descartó: una colisión daría por
presente un pasaje que no está, que es justo lo que la etapa mide. La velocidad no vale
convertir una medición exacta en una probable.

Medido: la etapa baja de 29,2 s a 23,7 s, y los **1.214 veredictos salen idénticos campo a
campo** — veredicto, las cuatro coberturas, y los pasajes concretos de cada lado.

### `unaligned` existe para no mentir

Cuando el corte absorbió texto vecino, el capítulo trae párrafos que pertenecen a otro y la
pregunta "¿esto sobra?" no tiene respuesta a ese nivel. Meterlo en `extra_in_pdf` inflaba el
hallazgo con texto que sí está en la web, dos capítulos más allá.

La misma cautela vale al revés: el informe dice `unanchored`, no *"ausente"*. Declarar una
ausencia que en realidad es un encabezado distinto sería el mismo error en espejo.

### El texto del PDF conserva las mayúsculas

La caja se baja **aparte y solo para comparar**. Un compendio normativo en minúsculas no es
una transcripción fiel: es un subproducto de la herramienta de comparación filtrándose al
entregable.

Se usa `lower` y no `casefold` porque `casefold` no conserva la longitud (ß → ss), y aquí los
desplazamientos del texto en caja original y en minúsculas tienen que coincidir carácter a
carácter.

### Las figuras del PDF se comparan por huella visual

El PDF re-comprime las imágenes, así que el `sha256` del archivo nunca coincidiría. La
comparación va por huella de 16×16 en gris.

Esa huella se memoiza en `visual_keys.json`, y la memoización es **exacta y no una
aproximación**: el nombre del archivo *es* el SHA-256 de su contenido, así que su huella no
puede cambiar. Medido sobre el Libro III, que tiene 1.683 figuras entre los dos lados:
decodificarlas con Pillow en cada corrida costaba 11,9 s de los 37,5 s de la etapa.

### `heading_gap` y `body_anchor` están medidos

Entre el `path` y el título real, el PDF mete un encabezado corrido que a veces difiere: sin
el punto tras el numeral, y en un caso con la errata *"traspado"* por *"traspaso"*.
`heading_gap = 300` los cubre.

`body_anchor = 120` son las letras del cuerpo que sirven de ancla cuando el encabezado no
calza: **16 capítulos** del corpus dependen de ese respaldo para no salir como ausentes.

---

## Decisiones de la interfaz

### La TUI llama a las mismas funciones, no a un subproceso

No hay dos implementaciones del pipeline que puedan divergir: el panel importa `STAGES` del
propio `__main__` y lo invoca. Un cambio en una etapa se ve igual en las dos interfaces sin
que nadie tenga que acordarse de actualizar la segunda.

### Las etapas siguen usando `print`

Es lo correcto para una herramienta de línea de comandos, y la TUI lo captura redirigiendo
`stdout`. La alternativa —reescribir las etapas para que emitan eventos que la TUI consuma y
la CLI imprima— crea dos caminos que pueden desincronizarse. Un `print` no puede.

### Un aborto se muestra, no cierra el panel

`guard` y la verificación del PDF paran con `SystemExit`, que es una parada **deliberada** y
no un fallo del programa. Si la TUI no la atrapara, el caso que el proyecto entero está
construido para detectar —un corpus degradado— cerraría la interfaz en vez de explicarse.

### El comando equivalente, siempre a la vista

La línea de estado muestra `python -m to_markdown parse export -b book-iii` para lo que esté
marcado. La TUI no esconde la CLI: lo que se aprende marcando casillas se pega en un script
sin traducir nada.

### La paleta es Catppuccin Mocha, y las categorías van por trama

Los 26 tonos oficiales, aplicados por papel y no por gusto: `crust`→`mantle`→`base`→
`surface0` es la escala de elevación —controles hundidos, área de trabajo un escalón más
arriba, barras flotando encima—, `blue` marca el foco y **solo** el foco, `lavender` la capa
modal, y `green`/`yellow`/`red` son lo que dicen ser. Un acento que cumple dos papeles no
responde ninguna pregunta.

Donde hacían falta cuatro categorías distinguibles —el veredicto por capítulo— se siguen
usando **densidades de trama** (`█▓▒░`) en vez de cuatro colores. El color es refuerzo
redundante, no el canal: se lee en una terminal sin color, en blanco y negro, y para quien
no distingue un color de otro. Y el orden de las tramas **es** la escala —más lleno es mejor
calce—, así que la leyenda confirma lo que ya se entendió.

Los 19 pares de texto y fondo que el panel dibuja cumplen el umbral AA de la WCAG (4,5:1 en
texto, 3:1 en bordes), comprobado en la suite. Mocha es una paleta bonita, no accesible por
decreto: qué tono va en qué papel es lo que la hace legible.

Para el énfasis sin color se usa el peso: en el historial, una deriva normal va atenuada y
una fuera de rango va en negrita, así que la vista se va sola a lo que importa.

### Nada tiene medida fija

La barra lateral es un porcentaje con mínimo y máximo, los paneles reparten el alto en
proporciones, y **los gráficos reciben el ancho disponible y se dibujan para ese ancho**.
Ese último punto es el que hace que el panel sirva igual en 80 columnas y en 200: no hay
ninguna constante de ancho en el módulo de analítica.

Por debajo de 92 columnas el diseño se apila en vez de encogerse. Encoger dos paneles hasta
que ninguno se lea no es adaptarse, es fallar en dos lugares a la vez.

Se descubrió midiendo: la leyenda del gráfico de cobertura ocupaba 59 columnas de una sola
línea, y el gráfico de historial reservaba un margen fijo de 24 que no alcanzaba para su
propio sufijo. Los dos se pasaban del ancho en una terminal angosta.

### Los textos suponen poca familiaridad con la terminal

Cada etapa dice qué hace en palabras ("Descarga las páginas del sitio de la
Superintendencia") y no por su efecto técnico. La línea inferior explica lo que está
resaltado, incluido si necesita internet y qué archivo escribe. `?` abre una ayuda que
empieza por qué es la herramienta y sigue con un paso a paso.

La línea de estado, además, muestra siempre el comando equivalente: la TUI no esconde la
CLI, la enseña.

### Borrar pide dos confirmaciones distintas, no dos veces la misma

La primera se contesta con una tecla, y una tecla se aprieta por reflejo. La segunda obliga
a **escribir una palabra**, que solo se puede escribir después de leer qué se va a borrar.

La palabra cambia con el riesgo: `borrar` para lo que se repone, **`no se repone`** para el
historial de corridas y la línea base del changelog, que no vuelven de ninguna fuente.

Cada objetivo declara cómo reponerse, y la lista va de lo más barato a lo más caro. Es lo
que convierte "borrar 371 MB" en una decisión informada: el entregable se rehace en un
segundo y el caché del portal cuesta tres minutos de red.

### La única serie temporal real del corpus son las notas de actualización

El `Last-Modified` del servidor parece la fuente obvia y no sirve: el CMS reguardó las 1.476
páginas el mismo día, así que las 1.476 dicen el mismo año. Es el mismo motivo por el que el
proyecto lleva dos hashes — un re-guardado del CMS parece un cambio y no lo es.

Las notas de actualización sí fechan: `…por la Norma de Carácter General Nº 31, de fecha 29
de diciembre de 2011`. De ahí sale una serie de 16 años, 2.948 modificaciones fechadas sobre
3.158 notas (93%), que responde algo que ninguna otra métrica del proyecto responde: **cuánto
cambia la norma, y cuándo.**

Las erratas de tipeo del original (`1012` por `2012`, dos casos) quedan fuera por rango. Un
año imposible no es actividad normativa, es un dedo que se resbaló.

### Los gráficos son de tendencia, y en un solo desplazamiento

Una foto dice cuánto hay; una tendencia dice hacia dónde va. Las secciones temporales van
primero por eso, y las estructurales después.

El apartado se abre y se cierra con la misma tecla dentro del panel, en vez de ser una
pantalla con pestañas: consultarlo no hace perder el sitio, y no hay que recorrer pestañas
para encontrar el gráfico que se buscaba.

### El tiempo por etapa solo se compara dentro del mismo alcance

Una etapa sobre un Libro y la misma sobre los cinco tardan cosas distintas por definición.
Se toma el alcance más frecuente y no el de la última corrida: una prueba o una reejecución
suelta no puede redefinir contra qué se compara todo.

La medición la anotan la CLI y la TUI por el mismo camino, o las dos mitades de la serie no
serían comparables. Y se anota en `finally`, para que un `SystemExit` de `guard` no se lleve
la medición consigo: una corrida detenida es un dato de la serie, no un hueco.

### La paleta se impone con un tema, no con CSS

Los colores que los widgets eligen solos —las teclas del pie, los avisos, el cursor de los
campos— salen de `accent`, `success`, `warning` y `error` **del tema** de textual, que se
leen de ahí y no del CSS de la app. Ningún override de CSS los alcanza: hay que registrar un
tema propio.

Y lo mismo, con más filo, para `$text`: textual la define como `auto 87%` —un blanco de
contraste rebajado— y ese `auto` **gana sobre cualquier `$text:` declarado en la hoja de la
app**. Con ella sin fijar, el registro y las listas salían en un gris de croma 2 ajeno a la
paleta mientras el resto del panel ya era Mocha. Fijar `text` en las variables del tema es
lo único que alcanza al CSS interno de los widgets.

Está comprobado sobre los códigos ANSI que salen por la terminal, no a ojo: Mocha no tiene
un solo gris neutro —hasta `crust`, el más apagado, va tintado de azul, croma 10— así que
**cualquier color acromático en pantalla es, por definición, de fuera**. La prueba mide el
croma de todo lo emitido y falla por debajo de ese piso.

Es el mismo contrato que antes con el signo invertido: la interfaz era monocromática y la
prueba exigía que NO emitiera matiz; ahora es Catppuccin y exige que no emita gris.

### Métricas, tendencias y rendimiento son tres preguntas, no tres pestañas

*Cuánto hay*, *cómo cambia el Compendio* y *cómo va el programa* se responden con datos
distintos y se miran en momentos distintos. Cada una tiene su apartado y su tecla.

La última es la que faltaba y la que más se confundía: `g` habla de **la norma**, `p` habla
del **programa**. Un gráfico de actividad normativa y uno de memoria residente no comparten
nada más que el hecho de ser gráficos.

### El rendimiento se mide muestreando, no contando al final

Un resumen al terminar dice cuánto tardó; no dice dónde estuvo el cuello de botella. La
serie sí: el pico de peticiones por segundo cae exactamente en `crawl`, y la memoria trepa
de 100 a 384 MB dentro de `compare`, que es donde están los n-gramas.

Tres decisiones que hacen que la serie signifique algo:

- **El ritmo se deriva entre muestras**, no del acumulado. Una curva acumulada siempre sube,
  y sube igual de bonito cuando el ritmo se derrumbó.
- **El muestreo corre siempre**, no solo con el apartado abierto. Si empezara al abrirlo, la
  curva arrancaría a mitad de la corrida y el pico ya habría pasado.
- **Los contadores se ponen a cero por corrida.** Un ritmo acumulado desde que se abrió el
  panel mezcla la corrida de hace media hora con la de ahora.

Los contadores son globales de módulo a propósito: instrumentar el pipeline no puede obligar
a cambiar la firma de cada función, o la instrumentación termina donde termina la paciencia.

Todo es de la biblioteca estándar —`/proc/self/statm` con `getrusage` de respaldo—. Un
medidor de rendimiento que necesita instalar algo es un medidor que no se usa.

### Líneas, no barras, para lo que evoluciona

La pregunta del rendimiento es *"¿cómo viene evolucionando?"*, y una serie temporal de
decenas de puntos en barras no se lee. `textual-plotext` da líneas braille reales y se
redimensiona solo; los colores se le fijan a mano desde la paleta, porque plotext trae los
suyos y son de colores.

### Ninguna medida es fija, tampoco el texto

Los gráficos ya recibían el ancho. Faltaba el panel de estado, que era una tabla de ancho
fijo —unas 45 columnas— contra una barra que baja hasta 26: las filas se partían y dejaba de
leerse. Ahora **decide cuántas columnas caben antes de escribirlas**, que es la única forma
de que una tabla de ancho fijo sea responsive.

Y en pantalla angosta hacía falta una cota: sin ella, a 85×28 la barra apilada se comía todo
y el registro quedaba con **cero filas** — presente en el layout, inútil en la práctica. Con
un apartado abierto, la barra se aparta del todo.

### La analítica es un módulo aparte, sin textual

Son funciones puras sobre lo que ya está en disco, así que se prueban sin levantar una
interfaz y se pueden reusar desde un informe. Y todo sale de JSON ya escrito: abrir los
gráficos no recalcula nada, o abrir la TUI costaría lo que cuesta `parse`.

El gráfico de historial existe por una razón concreta: **ninguna invariante puede ver la
deriva lenta.** Cada una compara una corrida contra la anterior, así que un descenso
gradual nunca la dispara. La serie sí lo muestra.

### `textual` es una dependencia de la interfaz, no del pipeline

Se importa de forma perezosa dentro de `build_app()`. El pipeline completo sigue corriendo
con las dos dependencias de siempre, que es la restricción que importa: la herramienta tiene
que poder correr en un `cron` sin terminal.

---

## Convenciones de estilo

| Qué | Idioma | Por qué |
| --- | --- | --- |
| Código: identificadores, funciones, clases | Inglés | Convención del lenguaje |
| Claves de JSON/JSONL, front matter, enumeraciones (`category`, `verdict`, `type`) | **Inglés** | Son **contrato de datos**, no prosa |
| Texto normativo, notas de actualización, materias | **Español, intacto** | Se transcriben tal como los publica la SP |
| Salida de comandos: consola, `--help`, errores | **Inglés** | Es la superficie con la que se opera la herramienta, y va en el mismo idioma que el código |
| Documentación, docstrings, comentarios, prosa de los informes (`coverage.md`, changelog) | **Español** | Es para quien mantiene el proyecto |

Type hints modernos (`dict[str, Any]`, `list[str] | None`) en todas las firmas.

`schema_version` se sube cuando cambia la **forma** de la salida, no solo su contenido.

---

## Lo que no está aquí

Esta fase cubre **solo extracción y transformación**. Chunking, embeddings, búsqueda,
el agente y el despliegue son fases posteriores.

El entregable está pensado para que esas fases sean posibles sin volver a la fuente: un
archivo por Título con jerarquía explícita, unidades numeradas direccionables, materias
etiquetadas por la SP y la URL de origen en cada norma y en cada figura.
