# Referencia del pipeline

Siete etapas en orden, más una alternativa. Cada una lee lo que dejó la anterior y escribe
en la carpeta de su Libro. Todas son idempotentes y ninguna necesita credenciales.

```
spensiones.cl ──▶ crawl ──▶ parse ──▶ changes
                    │         │         │
                    ▼         ▼         ▼
              cache/*.html  documents  changelog/
              images/       .json      changes.json
                    │         │
                    └────────▶ export ──▶ markdown/ + *.jsonl ──┐
                              │                                 │
                              ▼                                 ▼
spensiones.cl ──▶ pdf ──▶ assets/books/Book<N>.pdf ──▶ compare  bundle ──▶ output/
                              (verificado contra ──┘      │
                               el árbol del crawl)        ▼
                                                  data/pdf/<libro>/
```

## Invocación

Desde el panel de control, que muestra las mismas etapas con lo que hace cada una:

```bash
uv run python -m to_markdown tui        # ver TUI.md
```

O directamente:

```bash
uv run python -m to_markdown                       # las 6 etapas, los 5 Libros
uv run python -m to_markdown parse export          # solo esas etapas, en ese orden
uv run python -m to_markdown -b book-iii           # solo ese Libro
uv run python -m to_markdown export -b book-i -b book-v
```

| Argumento | Qué hace |
| --- | --- |
| `ETAPA…` | Etapas a correr, **en el orden en que se escriben**. Por defecto, las seis. |
| `--book SLUG`, `-b SLUG` | Restringe a ese Libro. Repetible. Por defecto, los cinco. |

Etapas válidas: `crawl`, `refresh`, `parse`, `changes`, `export`, `pdf`, `compare`, `bundle`.
Un nombre desconocido aborta antes de correr nada, y lo mismo un slug desconocido.

Los Libros se devuelven siempre en el orden de `config.toml` (I…V), no en el orden en que
se escribieron en la línea de comandos: el Compendio se lee y se informa de I a V.

## Resumen de entradas y salidas

Rutas relativas a `data/web/<libro>/` salvo donde se indique.

| # | Etapa | Lee | Escribe |
| ---: | --- | --- | --- |
| 1 | `crawl` | `spensiones.cl` | `cache/*.html`, `images/<sha>.<ext>`, `manifest.json`, `images.json`, `http.json` |
| — | `refresh` | `spensiones.cl` + caché | lo mismo que `crawl`, revalidando |
| 2 | `parse` | `cache/`, `images.json`, `manifest.json` | `documents.json`, `state/runs.jsonl` |
| 3 | `changes` | `documents.json`, `state/documents.json` | `changelog/<stamp>.md`, `changes.json`, `state/documents.json` |
| 4 | `export` | `documents.json`, `manifest.json`, `images.json` | `documents.jsonl`, `figures.jsonl`, `markdown/*.md`, `sections.json` |
| 5 | `pdf` | `spensiones.cl`, `documents.json` | `assets/books/Book<N>.pdf`, `assets/books/http.json` |
| 6 | `compare` | `assets/books/Book<N>.pdf`, `manifest.json`, `documents.json` | `data/pdf/<libro>/`: `text.txt`, `images/`, `images.json`, `documents.json`, `markdown/*.md`, `coverage.json`, `coverage.md` |
| 7 | `bundle` | `sections.json`, `documents.json`, `manifest.json`, `markdown/` | `output/<libro>/*.md`, `output/<libro>/index.md`, `output/README.md` |

---

## 1. `crawl` — el portal a disco

`src/to_markdown/crawl.py`

Recorre en anchura el árbol de cada Libro desde su `pvid` raíz. Cada página lista sus hijos
en el bloque `SP_pa_menuSubvalores_compendio`; una página con `cuerpo_documento` tiene texto
normativo.

- **Transporte**: una conexión HTTPS **viva por hilo**, reutilizada, y `Accept-Encoding:
  gzip`. Las dos cosas juntas son **2,25x** sobre el transporte anterior (244 → 108 ms por
  página con los mismos 3 hilos) y 4,7x menos bytes en la red. El ETag se normaliza al
  guardarlo: Apache le agrega `-gzip` al servir comprimido y ese ETag nunca vuelve a calzar.
- **Concurrencia**: `crawl.max_workers = 3`. Es un número **medido**, no elegido: con 8
  hilos `spensiones.cl` responde `502`. No lo subas — el keep-alive da la velocidad sin
  tocarlo, y de hecho baja la carga del servidor en vez de subirla.
- **Reintento**: exponencial, hasta `max_retries = 6`, con conexión nueva en cada intento
  —una conexión que dio error queda en estado indefinido—. Un `304` no es error: significa
  "no cambió".
- **Integridad**: el cuerpo se compara contra `Content-Length` antes de descomprimir. Una
  respuesta cortada se reintenta en vez de cachearse como HTML válido.
- **Redirecciones**: se siguen hasta 5 saltos. El sitio responde `302` a cualquier pvid
  inexistente y el destino es un `404`; sin seguirlo se cachearía el stub de 267 bytes.
- **User-Agent**: uno de escritorio distinto por petición (`fake-useragent`, catálogo
  empaquetado que no toca la red al inicializarse). Si el catálogo no carga, sigue con un UA
  propio en vez de abortar — es la única excepción al "fallar cerrado" del proyecto, y lo es
  porque aquí no hay riesgo de escribir datos degradados, solo de no descargarlos.
- **Imágenes**: se nombran por `sha256` del contenido. Deduplica la misma figura citada en
  varias normas y hace idempotentes las etapas siguientes.

Deja en `manifest.json` la lista **autoritativa** `documents`, ya en orden de lectura: son
las páginas con cuerpo normativo. Ninguna etapa posterior vuelve a derivarla.

### `refresh` — la alternativa a `crawl`

```bash
uv run python -m to_markdown refresh parse changes export
```

Revalida contra el servidor con `If-None-Match` / `If-Modified-Since` en vez de confiar en
el caché. Las páginas sin cambio responden `304` con cero bytes.

**No es la continuación de `crawl`, es su reemplazo.** Por eso `refresh` está fuera de la
corrida por defecto: encadenar ambos revalidaría contra el servidor 1.476 páginas recién
descargadas, para nada.

## 2. `parse` — HTML a Markdown, determinista

`src/to_markdown/parse.py`

Sin modelo de lenguaje. Jerarquía, numeración normativa, tablas y notación matemática se
extraen con parser.

| Elemento HTML | Se convierte en | Por qué |
| --- | --- | --- |
| `<h1>`…`<h5>` | `#`…`#####` | Jerarquía del documento |
| `<sub>` / `<sup>` | `_{…}` / `^{…}` | En este corpus son notación matemática (`VC_{i}`, `l_{x}`), verificado sobre 837 ocurrencias — no notas al pie |
| `<h6>` con "Nota de actualización" | `> **Nota de actualización:** …` | Dicen qué NCG modificó el número anterior |
| Otros `<h6>` | `*texto*` | Son pies de figura y fuentes |
| `<img>` | `[[FIG:<sha256>]]` | Marcador que resuelve `export` |
| `<table>` | Tabla Markdown | Ver abajo |

**Tablas**: solo 4 de las 371 del corpus traen `<th>`. En las otras 367, promover la primera
fila a encabezado convertiría un dato en un rótulo. Sin `<th>` se emite encabezado vacío y
todas las filas quedan como datos. Las celdas vacías se conservan: en normativa una celda
vacía puede ser información.

**Unidades numeradas**: el cuerpo se parte por número normativo (`1.`, `2.-`, `3)`), que es
la unidad con la que la norma se cita y se modifica. El texto anterior al primer número
queda como `preamble`.

**Dos hashes**: `source_sha256` (cuerpo HTML de origen) y `content_sha256` (nuestro
Markdown). Son distintos a propósito — ver [architecture.md](ARCHITECTURE.md#dos-hashes-no-uno).

Antes de escribir corre `guard.enforce()`. Si el Libro salió degradado, **aborta sin tocar
la salida anterior** y los otros cuatro Libros siguen intactos.

## 3. `changes` — qué cambió y de qué tipo

`src/to_markdown/changes.py`

Compara contra `state/documents.json`, el estado de la corrida anterior. En la primera
corrida guarda la línea base y no reporta nada.

Cruza tres señales independientes para clasificar cada cambio:

| Clase | Significa |
| --- | --- |
| `new` | Normas que no existían en la corrida anterior |
| `normative` | El contenido cambió **y** la norma lo declara con una Nota de actualización |
| `editorial` | El contenido cambió sin nota que lo declare (tipeo, formato) |
| `removed` | Normas que ya no están en el árbol |
| `pipeline` | Cambió **nuestra** salida, no la norma: es una modificación del parser |
| `cosmetic` | El CMS tocó la página pero el contenido es idéntico |

El diff es **por número normativo**, no por documento: "el N° 4 del Capítulo II cambió" es
accionable; "este documento de 12 KB cambió" no lo es.

La **renumeración** se detecta y se reporta como tal. Las unidades se emparejan primero por
hash de contenido: misma unidad con otro número es una renumeración, no una modificación.
Sin eso, las 93 notas del corpus que dicen *"pasando los actuales números 3 al 12 a ser 5 al
14"* producirían decenas de cambios falsos cada una.

El estado avanza **aquí y no en `parse`**: si avanzara antes, el diff se compararía contra sí
mismo y siempre diría "sin cambios".

## 4. `export` — resuelve figuras y escribe el entregable

`src/to_markdown/export.py`

Cada `[[FIG:<sha>]]` se reemplaza por `![Figura](<URL en spensiones.cl>)` más un comentario
con el hash. El Markdown apunta a la **URL original y no a la copia local** a propósito: lo
que este corpus garantiza sobre una figura es su procedencia. La copia local sigue en
`images/<sha>` como respaldo por si la SP cambia el archivo.

Una imagen que no se pudo descargar (`[[FIG-MISSING:…]]`) igual conserva su enlace: la URL
puede funcionar perfectamente aunque nuestro `urlopen` haya fallado ese día.

**Agrupación**: un archivo por Título (`export.group_by`, alternativas `"letter"` y
`"chapter"`). Se resuelve subiendo por el árbol, no por el texto del título: "Capítulo I.
Introducción" aparece 11 veces solo en el Libro III y agrupar por nombre los fundiría.

El ordinal del archivo sale del árbol **completo**, no de los documentos que se pasen. Es lo
que hace que el lado web y el lado PDF produzcan los mismos nombres y se puedan comparar con
un `diff`.

## 5. `pdf` — baja los Libros oficiales y verifica cuál es cuál

`src/to_markdown/pdf.py` · **requiere `pdfinfo` y `pdftotext`** · toca la red

Baja los cinco PDF que la SP publica y los deja en `assets/books/Book<N>.pdf`. Antes había
que descargarlos a mano.

**La URL sale del pvid.** El portal enlaza el Libro completo desde su propia raíz como
`fo-propertyvalue-<pvid>.pdf`, así que no hay una lista de URLs que mantener: es la misma
clave estable con la que `crawl` particiona el corpus.

**El nombre del servidor no sirve.** `fo-propertyvalue-2536.pdf` no dice de qué Libro es, y
el nombre es lo único que ve `compare` cuando abre el archivo. Por eso se renombra a
`Book1.pdf`…`Book5.pdf`, según `pdf_file` de `config.toml`.

**Y renombrar sin verificar sería peor que bajarlos a mano.** Un `Book3.pdf` que en realidad
fuera el Libro IV se compararía contra el árbol equivocado, y `coverage.md` saldría lleno de
"contenido solo en el PDF" sin que nada avisara. El PDF se descarga a un temporal, se
verifica, y **solo entonces** se mueve a su nombre final.

### Las dos comprobaciones

| # | Qué comprueba | Contra qué |
| --- | --- | --- |
| 1 | El PDF se declara a sí mismo | Su encabezado corrido: `Compendio de Normas del Sistema de Pensiones - Libro III`, presente en todas sus páginas |
| 2 | **Corresponde a lo que extrajo el crawler** | Las secciones que el PDF imprime (`Libro III, Título I Pensiones, Letra B…`) contra los `path` de `documents.json` |

La segunda es la que el nombre del archivo no puede dar: comprueba que este PDF y el subárbol
que recorrió el crawler son **el mismo Libro**, no solo que ambos digan "Libro III".

Medido sobre los cinco Libros: cada PDF verifica contra el suyo con 11 a 22 secciones
cruzadas, y **rechaza los 20 emparejamientos incorrectos**.

Detalles, todos medidos:

- **Se muestrea en bloques contiguos, no en páginas sueltas.** El encabezado está en todas
  las páginas, pero el breadcrumb solo aparece donde arranca una sección, y esos arranques
  van agrupados. Con 32 páginas sueltas el Libro IV daba 10 secciones en 34 s; con 4 bloques
  de 16 —las mismas 64 páginas, pero en 4 llamadas a `pdftotext` en vez de 32— da 23 en 4,7 s.
- **El cruce es por prefijo.** El PDF corta los breadcrumbs largos con el salto de línea
  (`…Estadísticas de afiliados pensionados y de Bonos de`); exigir el string entero
  declararía huérfanas dos de cada tres secciones legítimas.
- **El espaciado se uniforma.** Algunas páginas escriben `Libro III,Título V` sin el espacio
  tras la coma.
- **El encabezado se ancla a la línea completa.** El cuerpo normativo también cita al
  Compendio (`…del Libro I del Compendio de Normas del Sistema de Pensiones. Información`);
  tomar cualquier mención rechazaba un PDF correcto.

### Idempotencia

Los cinco Libros pesan 130 MB. La etapa guarda el `ETag` de cada uno en
`assets/books/http.json` y revalida con `If-None-Match`: una corrida sobre PDF vigentes
cuesta cinco peticiones condicionales y cero bytes.

La primera corrida después de haberlos bajado a mano no tiene `ETag` guardado; ahí decide el
`Content-Length`, para no re-descargar 130 MB solo para descubrir que el archivo ya estaba.

## 6. `compare` — el PDF oficial contra el portal

`src/to_markdown/compare/` · **requiere `pdftotext` y `pdfimages`**

Lleva el PDF al mismo orden y a la misma segmentación que la web, y contrasta capítulo por
capítulo. Comparar sin alinear daría un diff de 9 MB contra 10 MB, ilegible.

- **Texto**: `pdftotext`, cacheado en `data/pdf/<libro>/text.txt`.
- **Figuras**: `pdfimages`, indexadas por página (`p0007-000`) y comparadas por huella
  visual de 16×16 en gris, no por byte: el PDF re-comprime.
- **Anclaje**: por encabezado, con respaldo por las primeras `body_anchor = 120` letras del
  cuerpo. 16 capítulos del corpus dependen de ese respaldo.

Cada capítulo recibe un veredicto:

| Veredicto | Significa |
| --- | --- |
| `match` | n-gramas ≥ 95%: el mismo contenido de los dos lados |
| `reformatted` | n-gramas bajos pero léxico ≥ 95%: mismo contenido, otra maquetación (típicamente una tabla HTML que el PDF imprime en otro orden de columnas) |
| `unaligned` | El corte absorbió texto vecino; la pregunta "¿esto sobra?" no tiene respuesta a ese nivel |
| `extra_in_pdf` | Los dos bajos: contenido que de verdad solo está en el PDF |

`unaligned` existe para no mentir. Sin separarlo, el Manual de Cuentas del Libro IV
reportaba 9.901 palabras de "contenido nuevo" cuyas 21 palabras distintivas estaban las 21
en el portal.

## 7. `bundle` — arma `output/`

`src/to_markdown/bundle.py`

No transforma nada: toma los Markdown que produjo `export` y los empaqueta con los índices
que un lector —persona o modelo— necesita para orientarse.

Va aparte de `export` porque son dos cosas distintas: `data/` es el área de trabajo, con
caché, estado y artefactos intermedios; `output/` es lo único que se le manda a alguien.

Genera por Libro un `index.md` con:

- La tabla de Títulos, su archivo y su tamaño en palabras.
- El desglose de Letras y Capítulos de cada Título.
- El índice de **materias**, las etiquetas que la propia SP asocia a cada norma.

El índice importa más de lo que parece cuando el destinatario es un modelo: sin él,
encontrar "el Capítulo XXIV del Título III" obliga a leer los 12 archivos del Libro; con
él, es una consulta al índice y después un solo archivo.

`output/README.md` se escribe **solo cuando corrieron los cinco Libros**: un README que
describe cinco Libros cuando la corrida procesó uno mentiría sobre el paquete.

La fecha del paquete sale de `http.json` —cuándo se descargó realmente el Libro— y no de
hoy: el bundle puede rearmarse mil veces sobre un corpus de la semana pasada, y fecharlo hoy
haría creer que la norma está más al día de lo que está.

---

## `guard.py` — no es una etapa, es la red

`src/to_markdown/guard.py`

Se invoca desde `parse`, antes de escribir. Valida **por Libro**, no sobre el total: perder
entero el Libro I deja 1.092 documentos, por encima de cualquier cota global razonable, y el
fallo pasaría inadvertido.

| Invariante | Cota | Dónde se configura |
| --- | --- | --- |
| Documentos del Libro | `>= min_documents` | `config.toml`, por Libro |
| Números normativos del Libro | `>= min_units` | `config.toml`, por Libro |
| Raíz única en el manifiesto | `== [book.pvid]` | `guard.py` |
| Documentos con jerarquía | `>= 95%` | `MIN_WITH_PATH` |
| Documentos con contenido (texto **o** figura) | `>= 98%` | `MIN_WITH_CONTENT` |
| Documentos vacíos | `<= 10` | `MAX_EMPTY` |
| Variación de volumen entre corridas | `<= ±25%` | `MAX_TEXT_DRIFT` |

Ante una violación, `SystemExit` con el detalle y **nada se escribe**. Para forzar
—solo cuando ya entendiste por qué se violó—:

```bash
TO_MARKDOWN_FORCE=1 uv run python -m to_markdown parse
```

Cada corrida deja además una línea en `state/runs.jsonl` con las métricas del Libro. Un
descenso lento de figuras o unidades no dispara ninguna invariante, pero en la serie se ve.
