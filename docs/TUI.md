# El panel de control

`to-markdown` se opera desde una TUI. Es la forma principal de trabajar: la CLI sigue
existiendo y hace exactamente lo mismo, pero obliga a recordar los nombres de las etapas, en
qué orden van y qué escribe cada una.

```bash
uv run python -m to_markdown tui
```

```
╭─ Etapas  (espacio marca) ─────────╮╭─ Salida ───────────────────────────────────╮
│ ▐X▌ crawl    portal -> cache/*… ││ === pdf ===                                │
│ ▐ ▌ refresh  revalida el caché… ││ book-i   Book1.pdf   8.4 MB | 453 pages |… │
│ ▐X▌ parse    HTML -> documents… ││ book-ii  Book2.pdf   9.9 MB | 415 pages |… │
│ ▐X▌ changes  diff por número n… ││ pdf en 2.4s                                │
│ ▐X▌ export   documents.jsonl +… ││ === bundle ===                             │
│ ▐X▌ pdf      baja los 5 PDF of… ││ book-i    12 .md + index | 128 normas |…   │
│ ▐X▌ compare  el PDF oficial al… ││ …                                          │
│ ▐X▌ bundle   arma output/, lo … ││                                            │
╰───────────────────────────────────╯│                                            │
╭─ Libros ──────────────────────────╮│                                            │
│ ▐X▌ book-i    Libro I. Afiliac… ││                                            │
│ ▐X▌ book-ii   Libro II. Cotiza… ││                                            │
│ …                                 ││                                            │
╰───────────────────────────────────╯│                                            │
╭───────────────────────────────────╮│                                            │
│ Corpus                            ││                                            │
│ book-i    128 normas 12 md  8 MB ││                                            │
│ …                                 ││                                            │
│ 1.220 normas · 7.200 números      ││                                            │
│ 86 archivos en output/            ││                                            │
╰───────────────────────────────────╯╰────────────────────────────────────────────╯
 terminado en 39.4s · enter correr · a todo · r actualizar · q salir
```

## Qué muestra

| Panel | Qué es |
| --- | --- |
| **Etapas** | Las siete etapas **en el orden del pipeline**, no alfabético, cada una con lo que hace y lo que escribe. `refresh` va marcada aparte porque **reemplaza** a `crawl`, no la continúa. |
| **Libros** | Los cinco Libros del Compendio. Correr uno solo es marcar uno solo. |
| **Corpus** | Qué hay hoy en disco: normas, archivos exportados, tamaño de cada PDF y de cuándo es el caché. Se relee después de cada corrida. |
| **Salida** | Lo que las etapas imprimen, en vivo, con historial. Sin ajuste de línea: la salida es tabular y ajustarla desalinea las columnas. |
| **Estado** | Abajo. Antes de correr muestra **el comando equivalente**; después, cuánto tardó. |

## Teclas

| Tecla | Qué hace |
| --- | --- |
| `Tab` / `Mayús+Tab` | **Cambiar de panel**, como en lazydocker. El panel activo se distingue por el borde azul. |
| `↑` `↓` | Moverse dentro del panel |
| `espacio` | Marcar o desmarcar lo resaltado |
| `Intro` | Correr lo marcado |
| `a` | Correr el pipeline completo |
| `r` | Actualizar: `refresh parse changes export pdf compare bundle` |
| `d` | Volver a la selección inicial |
| `m` | **Métricas** del corpus, sin gráficos (la misma tecla abre y cierra) |
| `g` | **Gráficos** de descarga, procesamiento, cobertura e historial |
| `p` | **Rendimiento** del programa en vivo: ritmo y memoria |
| `D` | **Borrar contenido descargado** (pide confirmar dos veces) |
| `x` | Parar la corrida en curso |
| `c` | Limpiar el registro |
| `?` | Ayuda completa, escrita sin dar nada por sabido |
| `q` | Salir |

## Se adapta al tamaño de la terminal

No hay ninguna medida fija. La barra lateral ocupa un 34% del ancho con un mínimo de 26 y un
máximo de 52 columnas, los paneles reparten el alto en proporciones, y los gráficos se
trazan para el ancho disponible en cada redibujo.

Por debajo de **92 columnas** el diseño cambia: los paneles dejan de ir al costado y se
apilan, porque una barra lateral y un registro no caben juntos sin que los dos queden
ilegibles. En ese modo se oculta el panel de estado del corpus, que es lo único que también
está en los gráficos (`g`) y por lo tanto lo que menos cuesta sacar.

| Terminal | Diseño | Barra | Estado | Registro | Gráficos |
| --- | --- | ---: | --- | ---: | ---: |
| 200×60 | lado a lado | 52 | 48×13 | 146×55 | 146×40 |
| 120×40 | lado a lado | 40 | 36×8 | 78×35 | 78×25 |
| 92×30 | lado a lado | 31 | 27×5 | 59×25 | 59×18 |
| 85×28 | apilado | oculta con apartado | oculto | 83×12 | 83×14 |
| 70×24 | apilado | oculta con apartado | oculto | 68×10 | 68×12 |
| 60×20 | apilado | oculta con apartado | oculto | 58×8 | 58×9 |

Con un apartado abierto en pantalla angosta, la barra lateral **se aparta del todo**: quien
abrió los gráficos está mirando los gráficos, no las casillas.

### El panel de estado elige sus columnas

Era de ancho fijo —unas 45 columnas— contra una barra que baja hasta 26, así que las filas
se partían. Ahora decide cuántas caben antes de escribirlas:

```
48 col   book-i     128 normas  12 títulos  13 md
36 col   book-i     128 nor  12 tít  13 md
30 col   book-i     128  12
18 col   i     128
```

Comprobado en cada ancho de 16 a 59 columnas: ninguna fila se pasa.

## Paleta Catppuccin Mocha

Los 26 tonos oficiales de Mocha, aplicados por papel y no por gusto. Las reglas están
escritas en `tui/theme.py` y comprobadas por la suite:

**Elevación.** Mocha ordena sus fondos de más hondo a más alto. El panel lo usa así:

| Tono | Dónde |
| --- | --- |
| `crust` `#11111b` | el fondo de la pantalla, debajo de todo |
| `mantle` `#181825` | la barra lateral: etapas, Libros, estado |
| `base` `#1e1e2e` | el área de trabajo: la salida y los tres apartados |
| `surface0` `#313244` | las barras que flotan encima: encabezado, estado y pie |

Los controles van hundidos y lo que se está mirando, un escalón más arriba.

**Un acento interactivo, y uno solo.** `blue` `#89b4fa` marca el panel que tiene el foco, y
nada más. Si apareciera en dos sitios a la vez dejaría de responder «dónde estoy». Los
modales se distinguen con `lavender` `#b4befe`, porque son otra capa y no otro foco.

**Los acentos semánticos no decoran.** `green` es lo que entra en la corrida, `yellow` avisa,
`red` es un error. Ninguno se usa para otra cosa.

**El color nunca es el único canal.** En los gráficos, las categorías se siguen distinguiendo
por **densidad de trama**:

```
█ igual   ▓ reformateado   ▒ sin alinear   ░ solo en el PDF
```

El color queda como refuerzo redundante, que es lo que hace que el panel se siga leyendo en
una terminal sin color, en blanco y negro, y para quien no distingue un matiz de otro. Y el
orden de las tramas **es** la escala —más lleno es mejor calce— así que se entiende sin
consultar la leyenda. Donde hace falta énfasis sin color (la deriva del historial) lo da el
peso: lo normal va atenuado y lo que se sale de rango va en negrita.

**Contraste comprobado.** Los 19 pares de texto y fondo que el panel dibuja cumplen el
umbral AA de la WCAG —4,5:1 en texto, 3:1 en bordes— y la suite falla si un retoque los baja.
Mocha es una paleta bonita, no accesible por decreto: `overlay0` sobre `mantle` no llega a
4,5:1, así que qué tono va en qué papel es lo que hace legible el panel.

## Tres apartados, tres preguntas

Cada uno se abre y se cierra **con su propia tecla**, dentro del panel. Abrir uno cierra los
otros: tres a la vez dejan a cada uno con un tercio del alto. Mientras está abierto entra en
la rotación de `Tab`.

| Tecla | Apartado | Responde |
| --- | --- | --- |
| `m` | **Métricas** | *Cuánto hay.* Los números del corpus, sin gráficos |
| `g` | **Gráficos** | *Cómo cambia el Compendio.* Tendencias del corpus en el tiempo |
| `p` | **Rendimiento** | *Cómo va el programa ahora mismo.* En vivo, mientras corre |

La distinción entre los dos últimos importa: `g` habla de **la norma**, `p` habla del
**programa**. Son cosas distintas y estaban mezcladas.

## Métricas (`m`)

Una tabla y tres bloques de cifras: el corpus por Libro, el contraste contra el PDF oficial,
lo que hay en disco y la actividad normativa. Sin barras — es el apartado para cuando se
quiere el número, no la forma.

```
Libro      Normas  Números  Figuras  Notas  Títulos   md     Texto
──────────────────────────────────────────────────────────────────
book-i        128    1.582       72    492       12   13    1.21 MB
…
TOTAL        1220    7.200    1.747  3.158       80   85    9.27 MB
```

## Gráficos (`g`) — cómo cambia el Compendio

Todos de tendencia, en un solo desplazamiento, temporales primero.

| Sección | Responde |
| --- | --- |
| **Actividad normativa por año** | Cuánto cambió la norma cada año, con desglose por Libro |
| **Duración de las etapas** | Cuánto tarda cada una y si está tardando más que antes |
| **Historial de corridas** | Cuánto texto se extrajo en cada corrida |
| **Cobertura** | El PDF oficial contra el portal, capítulo por capítulo |
| **Procesamiento** | Qué salió: normas, números, figuras, notas |
| **Descarga** | Qué hay en caché y cuánto pesa |

### Actividad normativa: la tendencia que el corpus tiene de verdad

No mide nuestro trabajo sino el del organismo. Sale de las **fechas que la propia SP escribe
en sus notas de actualización** (`…por la Norma de Carácter General Nº 31, de fecha 29 de
diciembre de 2011`).

```
2011   ████████████████████████████████████████████████████████████████ 567
2012   ████████████████████████████████████████████▊                    396
…
2026   ████████████████▋                                                147

2.948 modificaciones fechadas en 16 años (2011–2026) · promedio 184 al año
```

El `Last-Modified` del servidor **no sirve**: el CMS reguardó las 1.476 páginas el mismo día
y las 1.476 dicen 2026. La norma sí declara cuándo la cambiaron.

### Duración: solo compara corridas del mismo alcance

Una etapa sobre un Libro y la misma sobre los cinco tardan cosas distintas por definición.
Se toma el alcance **más frecuente**, no el de la última corrida, y se informa lo que queda
fuera.

## Rendimiento (`p`) — cómo va el programa, en vivo

**Gráficos de línea reales** ([`textual-plotext`](https://github.com/Textualize/textual-plotext)),
redibujados cada medio segundo mientras el pipeline corre.

```
Rendimiento del programa · en reposo · 39 s
peticiones 1.476 · 3.2/s (pico 6.0) · red 28 MB
memoria 259 MB (pico 384) · CPU 96% · normas 1.220 · figuras 1.747

                         Peticiones por segundo
6.0┤                      ⢰⡇
4.0┤                      ⡇⡇
0.0┤⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣸       ⠸⡇ ⠸⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀
                         Memoria del proceso
384┤                                          ⡰⠉⠉⠉⠉⠉⠉⠉⢹
150┤   ⣀⣀⠤⠤⠤⠊⠉⠁       ⠈⠉
```

Son **líneas** y no barras porque la pregunta es *"¿cómo viene evolucionando?"*, y una serie
temporal de decenas de puntos en barras no se lee.

| Qué mide | De dónde sale |
| --- | --- |
| Peticiones y peticiones/s | Contador en `_request`, la única puerta de salida a la red |
| Bytes en la red / entregados | Comprimido y descomprimido: juntos dicen cuánto ahorra el gzip |
| Memoria residente | `/proc/self/statm`, con `getrusage` de respaldo |
| CPU | `getrusage`, derivado entre muestras |
| Normas y figuras | Contadores en `parse` y `crawl` |

Notas de diseño:

- **El ritmo se deriva entre muestras**, no del acumulado. Una curva acumulada siempre sube,
  y sube igual de bonito cuando el ritmo se derrumbó.
- **El muestreo corre siempre**, no solo con el apartado abierto: si empezara al abrirlo, la
  curva arrancaría a mitad de la corrida.
- **Los contadores se ponen a cero por corrida**, o un ritmo acumulado mezclaría la corrida
  de hace media hora con la de ahora.
- Todo es de la biblioteca estándar. Un medidor de rendimiento que necesita instalar algo es
  un medidor que no se usa.

## Borrar contenido descargado (`D`)

Es la única operación de la herramienta que destruye trabajo, así que pide **dos
confirmaciones distintas**:

1. **Elegir qué borrar.** La lista muestra cada objetivo con su peso, cuántos archivos y
   **cómo se repone**. Va ordenada de lo más barato de reponer a lo más caro, así que quien
   la recorre de arriba abajo se encuentra primero con lo que se rehace solo.
2. **Escribir una palabra.** La primera pregunta se contesta con una tecla, y una tecla se
   aprieta por reflejo. Escribir obliga a leer qué se está por borrar. La palabra es
   `borrar` para lo reponible y **`no se repone`** para lo que no vuelve.

| Objetivo | Cómo se repone |
| --- | --- |
| Entregable (`output/`) | `bundle` · ~1 s, sin red |
| Comparativa del PDF (`data/pdf/`) | `compare` · ~24 s, sin red |
| PDF oficiales (`assets/books/`) | `pdf` · ~18 s, 130 MB de red |
| Figuras (`data/web/*/images/`) | `crawl` · vuelve a bajar las 1.747 |
| Caché del portal (`data/web/*/cache/`) | `crawl` · ~3 min, 1.476 páginas |
| **Historial y línea base** (`state/`, `changelog/`) | **NO SE REPONE** |
| **TODO** | El pipeline entero, menos el historial |

La lista esconde los objetivos que no existen, así que sin nada descargado —un checkout
recién clonado, o justo después de borrar todo— `D` no abre el menú: responde **«No hay nada
descargado que borrar»** en el registro. Un modal que pregunta «elige qué borrar» con la
lista vacía es una pregunta sin respuestas posibles.

Tampoco se puede borrar con una corrida en curso: `D` avisa y pide pararla con `x` primero.

Después de borrar, el panel informa cuántos archivos y cuántos bytes había, y repite el
comando exacto para reponerlo.

## El comando equivalente, siempre a la vista

La línea de estado muestra el comando que corresponde a lo marcado:

```
listo · python -m to_markdown parse export -b book-iii
```

Es deliberado: la TUI no esconde la CLI, la enseña. Lo que se aprende marcando casillas se
puede pegar después en un script o en `cron` sin traducir nada.

## Qué NO hace distinto

La TUI llama a **las mismas funciones** que la CLI, no a un subproceso ni a una segunda
implementación. Las consecuencias importan:

- No hay dos pipelines que puedan divergir. Un cambio en una etapa se ve igual en las dos.
- Las etapas siguen usando `print`, que es lo correcto para una herramienta de línea de
  comandos; la TUI lo captura. Un `print` no puede quedar desincronizado de lo que la CLI
  enseña, y un sistema de eventos paralelo sí.
- **Un aborto se muestra, no cierra el panel.** `guard` y la verificación del PDF paran con
  `SystemExit`, que es una parada deliberada, no un fallo del programa. La TUI la atrapa y
  muestra el motivo completo — el caso que el proyecto entero está construido para detectar
  no puede terminar en una pantalla en blanco.

## Si `textual` no está

El pipeline entero corre sin ella; la TUI se importa de forma perezosa:

```
the TUI needs `textual`. It ships with the project:  uv sync
The pipeline itself runs without it:  uv run python -m to_markdown
```
