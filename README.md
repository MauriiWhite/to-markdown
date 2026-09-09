# to-markdown

Convierte fuentes documentales a **Markdown verificable**: cada afirmación del corpus se
puede contrastar contra su original, y ninguna etapa pierde información.

La primera fuente —y la que define el diseño— es el **Compendio de Normas del Sistema de
Pensiones** de la Superintendencia de Pensiones de Chile.

```bash
uv sync
uv run python -m to_markdown tui
```

El corpus, medido: **1.220 documentos normativos**, 9,27 MB de texto, **1.747 figuras** y
**3.158 notas de actualización** repartidas en cinco Libros, contrastados contra el
**Compendio oficial en PDF** que publica la propia SP.

`data/` se parte primero por **fuente** y después por Libro:

- `data/web/` — lo extraído del portal de la SP, capítulo por capítulo. Es lo que produce
  el pipeline.
- `data/pdf/` — el Compendio oficial en PDF (`assets/books/`), llevado al mismo orden y a
  la misma segmentación que la web para poder contrastarlos.

| Libro | pvid | Docs | Texto | `.md` por Título | Págs. PDF | Alineados | Solo en el PDF |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `book-i` | 2536 | 128 | 1,21 MB | 12 | 414 | 125 | 0,00% |
| `book-ii` | 2748 | 166 | 0,82 MB | 15 | 361 | 166 | 0,00% |
| `book-iii` | 2815 | 508 | 3,21 MB | 19 | 1.432 | 506 | 0,02% |
| `book-iv` | 2538 | 262 | 3,09 MB | 14 | 1.327 | 261 | 0,00% |
| `book-v` | 2539 | 156 | 0,94 MB | 20 | 488 | 156 | 0,01% |

La documentación completa está en [`docs/`](docs/): [el panel](docs/TUI.md), [primeros pasos](docs/GETTING_STARTED.md), [guía práctica](docs/OPERATIONS.md), [referencia del pipeline](docs/PIPELINE.md), [esquemas de datos](docs/SCHEMAS.md) y [decisiones de diseño](docs/ARCHITECTURE.md).

## Uso

Se opera desde un panel de control:

```bash
uv sync
uv run python -m to_markdown tui
```

Marca etapas y Libros con la barra espaciadora, `enter` para correr, `a` para el pipeline
completo. La línea de estado muestra siempre **el comando equivalente**, así que lo que se
aprende marcando casillas se pega en un script sin traducir. `m` abre las métricas, `g` los
gráficos de descarga, procesamiento y cobertura, y `p` el rendimiento del programa en vivo;
`D` borra contenido descargado con doble confirmación; `?` abre la ayuda. La paleta es
Catppuccin Mocha con contraste AA. Ver [docs/TUI.md](docs/TUI.md).

Lo mismo sin interfaz, para scripts y `cron`:

```bash
uv run python -m to_markdown
```

El pipeline es idempotente: cada etapa reusa su caché, así que volver a correrlo no
re-descarga ni re-gasta en el modelo.

Toda salida se escribe bajo `data/<libro>/`, donde `<libro>` es `book-i` … `book-v`:

| Etapa | Comando | Salida (por Libro) |
| --- | --- | --- |
| 1. Crawl | `python -m to_markdown crawl` | `cache/*.html`, `images/`, `manifest.json` |
| 2. Parse | `python -m to_markdown parse` | `documents.json` |
| 3. Cambios | `python -m to_markdown changes` | `changelog/*.md`, `changes.json` |
| 4. Export | `python -m to_markdown export` | `documents.jsonl`, `figures.jsonl`, `markdown/` |
| 5. PDF oficial | `python -m to_markdown pdf` | `assets/books/Book<N>.pdf` verificado por Libro |
| 6. Comparativa | `python -m to_markdown compare` | `pdf/<book>/`: `markdown/`, `coverage.md` |
| 7. Bundle | `python -m to_markdown bundle` | `output/`: el entregable con sus índices |

Ninguna etapa necesita credenciales ni servicios de pago. El pipeline completo corre en
**33 segundos** sobre caché.

Las etapas `pdf` y `compare` necesitan `pdftotext`, `pdfimages` y `pdfinfo` (paquete
`poppler-utils`), que no son dependencias de Python.

**Los PDF oficiales se bajan solos.** La etapa `pdf` los trae del portal, los renombra a
`Book1.pdf`…`Book5.pdf` —el servidor los publica como `fo-propertyvalue-<pvid>.pdf`, que no
dice de qué Libro es— y **verifica que cada uno sea el Libro que dice ser** antes de dejarlo
en su sitio: cruza el encabezado corrido del PDF y las secciones que imprime contra el árbol
que recorrió el crawler. Medido: acepta los 5 emparejamientos correctos y rechaza los 20
incorrectos. Un PDF que no verifica no pisa al que estaba.

**Transporte**: una conexión HTTPS viva por hilo (keep-alive) y `Accept-Encoding: gzip`.
Medido con los mismos 3 hilos: **244 → 108 ms por página, 2,25x**, y 4,7x menos bytes en la
red. El handshake TLS repetido 1.476 veces era dos tercios del tiempo del crawl. El ETag se
normaliza al guardarlo porque Apache le agrega `-gzip` al servir comprimido y ese ETag nunca
vuelve a calzar — sin eso, `refresh` habría re-descargado todo en cada corrida.

Las peticiones al sitio van con un **User-Agent de escritorio distinto en cada una**
(`fake-useragent`, catálogo empaquetado: no toca la red al inicializarse). Si el catálogo no
cargara se sigue con un UA propio en vez de abortar el crawl.

## Entregable legible: un archivo por Título

`data/<fuente>/<libro>/markdown/` trae un `.md` por **Título**, numerado en orden de lectura
del Compendio:

```
data/web/book-i/markdown/
├── 1-titulo-i-afiliacion-e-incorporacion-a-una-administradora-...md
├── 2-titulo-ii-desafiliacion.md
└── 12-titulo-xii-de-la-informacion-sobre-la-cotizacion-...md
```

Un Libro son sus Títulos, y cada Título va entero en un archivo con sus Letras, Capítulos y
Anexos dentro, anidados como encabezados:

```markdown
# Título III Administración de Cuentas Personales
## A. Administración de Cuentas Personales
### Capítulo I. Introducción
### Capítulo II. Definiciones preliminares
…
### Anexos
#### Anexo Nº 1 Formulario Orden de Traspaso Irrevocable
```

Los 1.220 documentos del CMS se agrupan así en **80 archivos**. El nivel se ajusta con
`export.group_by` (`"title"`, `"letter"` o `"chapter"`). La agrupación se resuelve por el
árbol y no por el texto del título: "Capítulo I. Introducción" aparece 11 veces solo en el
Libro III, y agrupar por nombre los fundiría en uno.

`data/pdf/<libro>/markdown/` usa **exactamente los mismos nombres de archivo**, así que
contrastar una sección es `diff`:

```bash
diff data/web/book-i/markdown/002-*.md data/pdf/book-i/markdown/002-*.md
```

Las figuras embebidas en el PDF se extraen con `pdfimages` a `data/pdf/<libro>/images/`,
nombradas por SHA-256 como en el lado web, y quedan referenciadas desde el Markdown de la
sección cuyo rango de páginas las contiene.

## Figuras: enlazadas a su original

El Markdown sirve cada imagen **desde el sitio de la Superintendencia**:

```markdown
![Figura](https://www.spensiones.cl/portal/compendio/596/articles-6965_recurso_1.jpg)
```

Lo único que este corpus promete sobre una figura es su **procedencia**. Una ruta local
obligaría a confiar en que alguien copió bien el archivo; la URL se abre y se contrasta
contra la fuente en un clic. La copia local bajo `images/<sha256>` es respaldo por si la SP
cambia o retira el archivo, no la fuente de verdad.

`figures.jsonl` lleva una entrada por figura con su `url`, su `sha256`, el archivo local y
**qué normas la citan** — una figura reutilizada en cinco normas es un dato, no una
repetición.

Las imágenes no se interpretan: adivinar qué dice una figura es peor que enlazarla.

## El entregable: `output/`

`data/` es el área de trabajo del pipeline —caché, estado, comparativas—; `output/` es lo
único que se le manda a alguien. Son **86 archivos y 9,8 MB**, sin imágenes locales porque
las figuras enlazan a `spensiones.cl`.

```
output/
├── README.md                 qué es, de dónde salió, cómo navegarlo
├── book-i/
│   ├── index.md              ← 12 Títulos, sus Capítulos y sus materias
│   ├── 1-titulo-i-....md
│   └── … 12 archivos
└── book-ii … book-v/
```

Cada Libro lleva su propio `index.md` con tres cosas: la tabla de sus Títulos (archivo,
normas, palabras), el desglose de Letras y Capítulos de cada uno, y un índice de **materias**
—las etiquetas que la propia SP asocia a cada norma— con los Títulos donde aparece cada una.

Eso es lo que hace el corpus navegable para un modelo: ubicar "el Capítulo XXIV del Título
III" es una consulta al índice y la lectura de un archivo, en vez de abrir los doce.

| Libro | Títulos | Normas | Palabras |
| --- | ---: | ---: | ---: |
| `book-i` | 12 | 128 | 194.818 |
| `book-ii` | 15 | 166 | 135.952 |
| `book-iii` | 19 | 508 | 534.000 |
| `book-iv` | 14 | 262 | 489.291 |
| `book-v` | 20 | 156 | 151.961 |

## El PDF oficial contra el portal

La SP publica lo mismo dos veces. `pdf` baja el segundo y comprueba de qué Libro es; `compare` lo lleva al orden y la segmentación de la
web —recorriendo el árbol en profundidad y anclando cada capítulo por su encabezado— y
responde qué trae uno que el otro no.

| | |
| --- | --- |
| Documentos alineados | **1.214 de 1.220** (99,5%) |
| Texto del PDF que no está en el portal | **0,007%** (104 palabras de 1,45 M) |
| Texto del portal que no está en el PDF | **0** una vez descontado el reformateo |
| Sin anclar | 2 documentos — su texto **sí** está en el PDF (88-100% del vocabulario), lo que difiere es el encabezado |

**Volumen comparado:** 1.450.300 palabras en el PDF contra 1.426.041 en el portal, +1,70% a
favor del PDF. No es contenido nuevo: solo el 0,007% del texto del PDF no existe en el
portal. La diferencia son los encabezados corridos que un documento impreso repite en cada
sección y una web no.

**Figuras:** se comparan por contenido visual (16×16 en gris) y no por archivo. Por archivo
el PDF parecía traer 122 de más; en realidad embebe la misma figura varias veces con
compresión distinta, y el portal la sirve en JPG donde `pdfimages` devuelve PNG.

| | |
| --- | ---: |
| Archivos — portal / PDF | 1.747 / 1.866 |
| Figuras distintas — portal / PDF | 1.747 / 1.741 |
| Presentes en ambos | **1.733** |
| Solo en el portal | 14 |
| Solo en el PDF | 8 |

Cada capítulo recibe un veredicto: `match` (n-gramas ≥95%), `reformatted` (los n-gramas no
calzan pero las palabras sí están: el PDF aplana las tablas HTML y cambia el orden de las
celdas), `unaligned` (el corte absorbió texto vecino y no se puede juzgar) o `extra_in_pdf`.
Sin separar `reformatted`, el Manual de Cuentas del Libro IV reportaba 9.901 palabras de
"contenido nuevo" cuyas 21 palabras distintivas estaban las 21 en el portal.

La misma cautela vale para lo que no ancla: el informe dice `unanchored`, no "ausente", y
mide qué porcentaje del vocabulario de esa sección aparece igual en el PDF. Declarar una
ausencia que en realidad es un encabezado distinto sería el mismo error en espejo.

### Un Libro suelto

```bash
uv run python -m to_markdown parse -b book-i -b book-v
```

`--book` es repetible y acepta los slugs de `[[books]]`. Útil para reprocesar un solo Libro
sin repasar los otros cuatro.

### Actualización

```bash
uv run python -m to_markdown refresh parse changes export
```

`refresh` revalida contra el servidor con `If-None-Match` / `If-Modified-Since` en vez de
confiar en el caché. Medido sobre el Libro I: **156 de 156 páginas responden `304` con cero
bytes**, en 16,6 s — unos 2,6 min para los cinco Libros.

## Detección de cambios

Tres señales independientes, porque ninguna basta sola:

| Señal | Origen | Responde | Falla sola porque |
| --- | --- | --- | --- |
| `ETag` / `Last-Modified` | HTTP | ¿el servidor tocó la página? | un re-guardado del CMS parece un cambio |
| `source_sha256` | cuerpo HTML | ¿cambió el contenido de origen? | exige descargar todo |
| Nota de actualización nueva | la norma | ¿es un cambio normativo? | una corrección de tipeo no lleva nota |

Cruzarlas da una **clasificación** en vez de un booleano: `normative`, `editorial`,
`cosmetic`, `pipeline` (cambió nuestro parser, no la norma), `new`, `removed`.

El diff es **por número normativo**, no por documento: "el N° 4 del Capítulo II cambió, por
NCG 370" es accionable; "este documento de 12 KB cambió" no lo es. El corpus tiene 7.200
unidades direccionables (`4074#4`).

La renumeración se detecta y se reporta como tal: 93 notas del corpus documentan cosas como
*"pasando los actuales números 3 al 12 a ser 5 al 14"*. Emparejando solo por número, cada una
produciría decenas de cambios falsos; las unidades se emparejan primero por hash de contenido.

## Robustez

- **`is_leaf` no es "tiene texto".** Un nodo puede tener hijos y cuerpo normativo propio:
  un Título que además imparte instrucciones, un Capítulo con preámbulo. Son 24 en el corpus
  y valen 189.686 caracteres que el PDF de la SP sí imprime y que el pipeline descartaba en
  silencio. El manifiesto lleva `has_body` por nodo y la lista autoritativa en `documents`.
- **Invariantes con fallo cerrado, por Libro.** Antes de escribir, cada Libro se valida
  contra sus propias cotas medidas (`[[books]]` en `config.toml`): documentos y unidades
  mínimos, una sola raíz en su manifiesto, ≥98% con contenido, y variación de volumen ≤25%
  respecto de la corrida anterior. Si algo no cuadra, **aborta ese Libro sin tocar su
  salida anterior**; los otros cuatro siguen. Evaluar por Libro y no sobre el total no es
  cosmético: perder entero el Libro I deja 1.074 documentos, por encima de cualquier cota
  global razonable, y el fallo pasaría inadvertido. Escape: `TO_MARKDOWN_FORCE=1`.
- **Fixtures congelados.** `tests/fixtures/` tiene 5 páginas HTML reales versionadas. Las
  pruebas de parseo no dependen de `data/`, que está en .gitignore: una prueba que se salta
  sola en un clon limpio no protege de nada.
- **Canario contra el sitio en vivo.** `uv run pytest -m network` verifica que los
  selectores siguen vigentes, que el servidor sigue honrando peticiones condicionales y que
  el índice del Compendio sigue publicando exactamente los cinco Libros configurados —un
  Libro VI no listado en `config.toml` no lo recorrería nadie, y ninguna invariante se
  quejaría, porque los cinco conocidos seguirían sanos. Las invariantes avisan cuando ya corriste el pipeline; el canario avisa el
  día que la SP cambia el CMS. Va en un cron diario.
- **Historial de métricas.** Cada corrida agrega una línea a `data/<libro>/state/runs.jsonl`
  (documentos, chars, unidades, figuras, notas, vacíos). Un descenso lento no dispara
  ninguna invariante, pero en la serie se ve.

## Formato de salida

Todas las claves e identificadores de esquema van en **inglés**; el contenido normativo
queda en español, intacto. `schema_version` acompaña cada registro para que un consumidor
aguas abajo pueda notar un cambio de formato en vez de descubrirlo por un campo ausente.

```json
{"pvid": "4074", "url": "…", "title": "Capítulo II. …", "path": "Libro I, Título I, …",
 "citation": "…", "breadcrumb": [...],
 "hierarchy": {"book": "…", "title": "…", "letter": "…", "chapter": "…"},
 "topics": ["Afiliación a una A.F.P."], "amendment_notes": ["…"],
 "figures": ["<sha256>"], "markdown": "…",
 "units": [{"unit_id": "4074#4", "number": "4", "citation": "…, N° 4",
            "text": "…", "sha256": "…"}],
 "source_sha256": "…", "content_sha256": "…", "schema_version": 2}
```

El nivel *Título* de la jerarquía va anidado bajo `hierarchy` porque en plano chocaría con
el `title` propio de la página: son cosas distintas.

## Entregable

Cinco entregables, uno por Libro, con la misma forma:

- `data/<libro>/documents.jsonl` — un registro por norma: jerarquía (Libro / Título / Letra /
  Capítulo), materias, notas de actualización, y el cuerpo en Markdown con las tablas
  convertidas y las figuras enlazadas a su original en el sitio de la SP.
- `data/web/<book>/figures.jsonl` — un registro por figura: su URL en el sitio de la SP, su
  `sha256`, el archivo local y qué normas la citan.
- `data/<libro>/markdown/<pvid>.md` — el mismo contenido, legible. Es como se revisa la
  calidad de verdad: abriendo un archivo.

Un consumidor que quiera el corpus entero concatena los cinco; uno que solo atienda
beneficios previsionales carga `book-iii` y nada más.

## Confiabilidad

Cuatro compromisos, en orden de importancia:

1. **Aditivo, nunca destructivo.** Cada figura conserva su URL de origen, su hash y su
   archivo local. El Markdown enlaza al original en el sitio de la SP: la procedencia se
   verifica en un clic, no se toma por buena.
2. **Determinista de punta a punta.** Jerarquía, numeración, tablas HTML y las 837
   conversiones `<sub>`/`<sup>` salen por parser. No hay modelo, no hay heurística que
   adivine: lo que queda encerrado en píxeles se enlaza, no se interpreta.
3. **Contrastado contra el PDF oficial.** El mismo Compendio que la SP exporta como
   documento único se alinea capítulo por capítulo contra lo extraído del portal. El texto
   coincide: 0,007% del PDF no existe en la web, y 0% al revés descontando reformateo.
4. **Fallo cerrado, por Libro.** Las invariantes se evalúan por Libro contra cotas medidas.
   Un Libro degradado aborta el suyo y conserva su salida anterior; los otros cuatro siguen.
