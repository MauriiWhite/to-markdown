# Referencia de datos

Formatos de todo lo que el pipeline escribe. Las **claves e identificadores de esquema van
en inglés** —son contrato de datos, no prosa—; el **contenido va en español**, intacto,
tal como lo publica la Superintendencia.

`schema_version` está en `parse.py` y hoy vale **2**. Sube cuando cambia la *forma* de la
salida, no su contenido.

## Dónde vive cada cosa

```
data/
├── timings.jsonl           duración de cada etapa por corrida (alimenta los gráficos)
│                           el rendimiento en vivo NO se persiste: es del proceso actual
├── web/<libro>/            ← extraído del portal. Lo que produce el pipeline.
│   ├── cache/<pvid>.html      el subárbol de ESE Libro y nada más
│   ├── images/<sha256>.<ext>  figuras descargadas, nombradas por contenido
│   ├── markdown/NNN-<slug>.md un archivo por Título, en orden de lectura
│   ├── changelog/<stamp>.md   informe de cambios por corrida
│   ├── state/
│   │   ├── documents.json     corpus de la corrida anterior (línea base del diff)
│   │   └── runs.jsonl         una línea de métricas por corrida
│   ├── manifest.json          el árbol del Libro
│   ├── http.json              ETag / Last-Modified por página
│   ├── images.json            src -> sha256
│   ├── sections.json          los grupos de archivo (Títulos)
│   ├── documents.json         el corpus completo
│   ├── documents.jsonl        idem, una línea por documento, figuras ya resueltas
│   ├── figures.jsonl          una línea por figura, con su procedencia
│   └── changes.json           el último informe de cambios
└── pdf/<libro>/            ← el PDF oficial, alineado contra la web
    ├── markdown/NNN-<slug>.md mismos nombres que web/, para `diff` directo
    ├── images/<sha256>.png    figuras embebidas en el PDF
    ├── text.txt               salida cruda de pdftotext (caché)
    ├── documents.json         el PDF segmentado por los mismos pvid
    ├── images.json            p<página>-<n> -> sha256
    ├── visual_keys.json       huella 16x16 por figura, memoizada por SHA-256
    ├── coverage.json          la comparativa, en datos
    └── coverage.md            la comparativa, legible

assets/books/               ← entrada: el Compendio oficial en PDF
├── Book1.pdf … Book5.pdf      lo baja la etapa `pdf`, verificado por Libro
└── http.json                  ETag por Libro, para no re-bajar 130 MB por corrida

output/                     ← LO ÚNICO QUE SE ENTREGA
├── README.md
└── <libro>/
    ├── index.md
    └── NNN-<slug>.md
```

`data/` se parte primero por **fuente** y después por Libro. `web/` y `pdf/` son dos
testimonios de lo mismo y no se mezclan: juntarlos haría imposible la única pregunta que
justifica tener los dos, que es qué trae uno y el otro no.

---

## `documents.json` — el corpus

Lista de documentos, en orden de lectura del Compendio. Es la salida canónica de `parse` y
la entrada de todo lo demás.

```json
{
  "pvid": "4082",
  "url": "https://www.spensiones.cl/portal/compendio/596/w3-propertyvalue-4082.html",
  "title": "1. Afiliación de trabajadores dependientes que se encuentren cotizando…",
  "path": "Libro I, Título I, Letra A, Capítulo III",
  "citation": "Libro I, Título I, Letra A, Capítulo III, 1. Afiliación de trabajadores…",
  "breadcrumb": [{"pvid": "2536", "title": "Libro I Afiliación al Sistema…"}],
  "hierarchy": {"book": "Libro I …", "title": "Título I …", "letter": "A. …", "chapter": "Capítulo III …"},
  "topics": ["Administración de Cuentas Personales", "Afiliación a una A.F.P."],
  "amendment_notes": ["Este número fue modificado por la Norma de Carácter General Nº 31…"],
  "figures": ["<sha256>", "…"],
  "markdown": "Suscripción de Solicitud de Incorporación\n\n1.1. El trabajador…",
  "units": [ … ],
  "source_sha256": "45cb7e2dc218…",
  "content_sha256": "c5bddc91b640…",
  "schema_version": 2
}
```

| Clave | Tipo | Qué es |
| --- | --- | --- |
| `pvid` | `str` | Identificador de la página en el CMS de la SP. **La clave estable**: los títulos cambian, los pvid no. |
| `url` | `str` | La página en el portal. Toda afirmación del corpus se contrasta aquí. |
| `title` | `str` | Título propio de la página |
| `path` | `str` | Ruta canónica según la propia SP, o el breadcrumb como respaldo |
| `citation` | `str` | `path` + `title`, como se cita la norma |
| `breadcrumb` | `list[{pvid, title}]` | La cadena de ancestros tal como la publica el sitio |
| `hierarchy` | `dict` | `book` / `title` / `letter` / `chapter`, asignados por prefijo. Va **anidado** porque el nivel Título y el título propio de la página son cosas distintas y en plano colisionarían. |
| `topics` | `list[str]` | Las "Materias asociadas" que etiqueta la SP |
| `amendment_notes` | `list[str]` | Notas de actualización: qué NCG modificó qué |
| `figures` | `list[str]` | SHA-256 de las figuras del cuerpo, sin repetir |
| `markdown` | `str` | El cuerpo normativo. En `documents.json` con marcadores `[[FIG:…]]`; en `documents.jsonl` ya resueltos a `![Figura](url)` |
| `units` | `list[dict]` | Ver abajo |
| `source_sha256` | `str` | Hash del **cuerpo HTML de origen**. Responde *¿cambió la norma?* |
| `content_sha256` | `str` | Hash de **nuestro Markdown**. Responde *¿cambió nuestra salida?* |
| `schema_version` | `int` | Forma de esta estructura |

### `units[]` — números normativos direccionables

```json
{
  "unit_id": "4082#4",
  "number": "4",
  "citation": "Libro I, Título I, Letra A, Capítulo III, …, N° 4",
  "text": "4. El trabajador deberá…",
  "sha256": "c5bddc91b640…"
}
```

| Clave | Tipo | Qué es |
| --- | --- | --- |
| `unit_id` | `str` | `<pvid>#<número>`. El texto anterior al primer número usa `#preamble`. |
| `number` | `str \| null` | El número tal como lo escribe la norma. `null` en el preámbulo. |
| `citation` | `str` | Cita completa, lista para copiar |
| `text` | `str` | El texto de la unidad |
| `sha256` | `str` | Hash del texto. Es lo que permite detectar renumeración. |

> `unit_id` usa el número porque es como la norma se cita a sí misma. La renumeración se
> detecta emparejando por `sha256`, no por posición.

## `documents.jsonl` — el corpus, línea por línea

Mismo esquema que `documents.json`, un objeto JSON por línea, con **las figuras ya
resueltas** en `markdown`. Es el formato para consumir el corpus en streaming.

## `figures.jsonl` — procedencia de cada figura

```json
{
  "sha256": "03025d80dac8…",
  "src": "articles-17104_recurso_1.jpg?ts=1787241414",
  "url": "https://www.spensiones.cl/portal/compendio/596/articles-17104_recurso_1.jpg?ts=…",
  "file": "03025d80dac8….jpg",
  "documents": ["4305", "4321"]
}
```

`url` es lo que hace verificable el corpus; `file` es el respaldo local por si la SP cambia
el archivo. `documents` lista las normas que la citan — una figura reutilizada en cinco
normas es un dato, no una repetición.

## `manifest.json` — el árbol del Libro

```json
{
  "book":      {"slug": "book-i", "pvid": "2536", "title": "Libro I …"},
  "order":     ["2536", "2541", "2586", …],
  "documents": ["4073", "4074", …],
  "nodes":     { "2586": { … } },
  "leaves":    ["3605", "3606", …]
}
```

| Clave | Qué es |
| --- | --- |
| `book` | El Libro se identifica en su propio manifiesto: una carpeta suelta tiene que poder decir de qué Libro es sin volver a `config.toml`. |
| `order` | Todos los nodos en profundidad, en el orden en que el CMS lista sus hijos — que es el orden en que la SP los imprime. **No** es orden de `pvid`: los pvid se asignan por fecha de creación. |
| `documents` | **La lista autoritativa** de páginas con texto normativo, ya ordenada. Ninguna etapa vuelve a derivarla. |
| `nodes` | El árbol completo, indexado por `pvid` |
| `leaves` | Nodos sin hijos. **No es lo mismo que `documents`** — ver abajo. |

### `nodes[pvid]`

```json
{
  "pvid": "2586",
  "title": "A. Afiliación e Incorporación a una Administradora",
  "parent": "2541",
  "depth": 3,
  "is_leaf": false,
  "has_body": false,
  "url": "https://www.spensiones.cl/portal/compendio/596/w3-propertyvalue-2586.html",
  "last_modified": "Mon, 07 Sep 2026 16:05:49 GMT"
}
```

> **`is_leaf` no es "tiene texto".** Un nodo puede tener hijos **y** cuerpo normativo
> propio: un Título que además imparte instrucciones, un Capítulo con preámbulo antes de sus
> números. Son **24 en el corpus** y valen **189.686 caracteres** que el PDF de la SP sí
> imprime. Usa `has_body` y `documents`, nunca `is_leaf`, para saber qué tiene texto.

## `sections.json` — los grupos de archivo

```json
{
  "pvid": "2541",
  "title": "Título I Afiliación e Incorporación a una Administradora de Fondos de Pensiones",
  "path": "Libro I, Título I, Letra A Afiliación e Incorporación a una Administradora",
  "level": "title",
  "index": 1,
  "filename": "1-titulo-i-afiliacion-e-incorporacion-a-una-administradora….md",
  "documents": ["4073", "4074", "4075", "4082", …]
}
```

`index` sale del árbol **completo**, no del subconjunto que se exporta: es lo que hace que
el lado web y el lado PDF produzcan los mismos nombres de archivo.

## `http.json` — la señal de cambio más barata

```json
{ "2536": {
    "etag": "\"15502-65ae6caa43140\"",
    "last_modified": "Mon, 07 Sep 2026 16:05:49 GMT",
    "fetched_at": "2026-09-07T23:53:51+00:00"
} }
```

Las cabeceras se guardan **en minúsculas**: este servidor manda `Etag` — ni `ETag` ni
`etag` — y sin normalizar el ETag no se guardaría nunca.

`fetched_at` es lo que fecha el paquete en `output/`.

## `assets/books/http.json` — el índice de los PDF oficiales

```json
{ "book-i": {
    "url": "https://www.spensiones.cl/portal/compendio/596/fo-propertyvalue-2536.pdf",
    "etag": "\"802d15-65ae761adf6c0\"",
    "last_modified": "Mon, 07 Sep 2026 16:48:03 GMT",
    "bytes": 8400149
} }
```

Va junto a los archivos y no bajo `data/` porque describe a `assets/books/` y tiene que
viajar con él: sin `ETag`, cada corrida re-descargaría los 130 MB de los cinco Libros.

Se indexa por `slug` y no por `pvid` como `data/web/<libro>/http.json`, porque aquí la clave
que importa es a qué archivo local corresponde la entrada.

## `images.json`

Lado web, `src -> sha256`:

```json
{ "articles-17104_recurso_1.jpg?ts=1787241414": "03025d80dac8…" }
```

Lado PDF, `p<página>-<n> -> sha256`:

```json
{ "p0007-000": "a1b2c3…" }
```

El índice del PDF va por página y no por orden de aparición: es lo que permite devolverle
cada figura a la sección que la contiene.

## `changes.json` — el informe de cambios

```json
{
  "book": {"slug": "book-i", "name": "Libro I. Afiliación al Sistema de Pensiones"},
  "generated_at": "2026-09-08T13:01:09+00:00",
  "schema_version": 2,
  "documents_before": 128,
  "documents_after": 128,
  "summary": {"new": 0, "normative": 0, "editorial": 0, "removed": 0, "pipeline": 0, "cosmetic": 0},
  "changes": [ … ]
}
```

Cada entrada de `changes[]`:

| Clave | Qué es |
| --- | --- |
| `category` | `new` · `normative` · `editorial` · `removed` · `pipeline` · `cosmetic` |
| `document` | `{pvid, citation, url}` |
| `new_notes` | Notas de actualización que aparecieron en esta corrida |
| `units` | Eventos por número normativo |

Eventos de `units[]`, por `type`:

| `type` | Campos | Significa |
| --- | --- | --- |
| `renumbered` | `from`, `to`, `unit_id` | Mismo texto, otro número |
| `modified` | `number`, `unit_id`, `diff` | Texto cambiado, con su diff unificado |
| `added` | `number`, `unit_id`, `text` | Número nuevo (primeros 400 caracteres) |
| `removed` | `number`, `unit_id`, `text` | Número eliminado |

El changelog legible equivalente queda en `changelog/<stamp>.md`.

## `coverage.json` — PDF contra portal

```json
{
  "book": {"slug": "book-i", "name": "…", "pdf": "Book1.pdf"},
  "verdicts": {"match": 102, "reformatted": 17, "extra_in_pdf": 6},
  "extra_words_in_pdf": 6,
  "generated_at": "2026-09-08T13:01:15+00:00",
  "pdf_pages": 414, "pdf_chars": 1231767,
  "toc_lines_skipped": 153, "front_matter_chars": 8057,
  "aligned": 125, "section_files": 12, "web_documents": 128,
  "anchored_by_heading": 124, "anchored_by_body": 1,
  "unanchored": [], "uncovered_chars": 15991,
  "figures": {"web_files": 72, "pdf_files": 72, "shared": 72, "only_in_web": 0, "only_in_pdf": 0},
  "documents": [ … ]
}
```

Cada entrada de `documents[]`:

| Clave | Qué es |
| --- | --- |
| `pvid`, `citation` | Qué capítulo es |
| `pdf_page` | Dónde ancló en el PDF |
| `anchored_by` | `heading` o `body` (respaldo cuando el encabezado no calza) |
| `pdf_words`, `web_words` | Volumen de cada lado |
| `coverage_pdf`, `coverage_web` | Cobertura por n-gramas de `shingle = 8` palabras |
| `lexical_pdf`, `lexical_web` | Cobertura léxica, **sin importar el orden** |
| `verdict` | `match` · `reformatted` · `unaligned` · `extra_in_pdf` |
| `alignment_suspect` | El corte absorbió texto vecino |
| `extra_in_pdf`, `extra_in_web` | Los pasajes concretos que faltan de cada lado |

> Las dos métricas juntas son la lectura inequívoca: n-gramas bajos con léxico alto es
> **reformateo**; los dos bajos es contenido que de verdad solo está de un lado.

## `state/runs.jsonl` — la serie histórica

Una línea por corrida y por Libro:

```json
{"book": "book-i", "at": "2026-09-08T13:01:05+00:00", "documents": 128,
 "chars": 1213526, "units": 1582, "figures": 72, "notes": 492, "empty": 0}
```

Es lo que hace visible la deriva lenta: un descenso gradual de figuras no dispara ninguna
invariante, pero en la serie se ve.

---

## `output/` — el entregable

### Front matter de cada `.md`

```yaml
---
book: book-i
section_pvid: 2541
level: title
order: 1
title: "Título I Afiliación e Incorporación a una Administradora de Fondos de Pensiones"
path: "Libro I, Título I, Letra A Afiliación e Incorporación a una Administradora"
documents: ["4073", "4074", "4075", "4082", …]
source: web
---
```

`source` es `web` o `pdf`, según de qué testimonio salió el archivo.

### Convenciones dentro del cuerpo

| Marca | Significa |
| --- | --- |
| `# Título` / `## Letra` / `### Capítulo` | La jerarquía del Compendio |
| `*Materias: …*` | Las etiquetas que la SP asocia a esa norma |
| `> **Nota de actualización:** …` | Qué NCG modificó el número anterior |
| `![Figura](https://www.spensiones.cl/…)` | La imagen **servida desde el sitio de la SP** |
| `<!-- figura <sha256> -->` | Hash para encontrar la copia local en `images/` |
| `<!-- pvid 4082 · https://… -->` | Cierra cada norma con su origen verificable |
| `_{i}` / `^{2}` | Subíndice y superíndice: notación matemática |

Los encabezados heredados del HTML se **bajan** para que quepan bajo los de la sección; sin
eso, un `#` interno competiría con el título del archivo y el índice saldría plano.

### `index.md` de cada Libro

Tres secciones: la tabla de Títulos con su archivo y tamaño; el desglose de Letras y
Capítulos de cada uno; y el índice de **materias** con los Títulos donde aparece cada una.

Para ubicar una norma: leer el `index.md`, encontrar su Título, abrir ese archivo.
