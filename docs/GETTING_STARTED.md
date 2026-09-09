# Primeros pasos

De un clon limpio a `output/` listo para entregar. Al terminar vas a tener 86 archivos
Markdown con el Compendio completo, contrastados contra el PDF oficial de la SP.

Tiempo: **~40 segundos** con caché, **~4 minutos** en limpio (1.476 páginas del portal en
~2,7 min más 130 MB de PDF oficiales en ~18 s).

## 1. Requisitos

| Requisito | Para qué | Cómo verificar |
| --- | --- | --- |
| Python ≥ 3.12 | Todo | `python3 --version` |
| [`uv`](https://docs.astral.sh/uv/) | Gestor de paquetes y ejecutor | `uv --version` |
| `poppler-utils` | Las etapas `pdf` y `compare` | `which pdftotext pdfimages pdfinfo` |

`poppler-utils` trae `pdftotext`, `pdfimages` y `pdfinfo`, que son binarios del sistema y
no dependencias de Python:

```bash
sudo pacman -S poppler          # Arch
sudo apt install poppler-utils  # Debian / Ubuntu
brew install poppler            # macOS
```

**No hay `.env`, ni claves de API, ni servicios de pago.** Si algún paso te pide una
credencial, es un error: reportalo.

## 2. Instalar

```bash
uv sync
```

Instala `fake-useragent` y `pillow` (más `pytest` y `ruff` del grupo `dev`) en `.venv/`.

> Usa siempre `uv run …`. No invoques el Python global ni actives el virtualenv a mano:
> `uv` resuelve el entorno correcto y mantiene `uv.lock` consistente.

## 3. Verificar que el código está sano

Antes de descargar nada, comprobá que el pipeline funciona. Las pruebas offline corren
contra páginas HTML reales congeladas en `tests/fixtures/`, así que no tocan la red:

```bash
uv run ruff check src tests   # esperado: All checks passed!
uv run pytest -q              # esperado: 109 passed, 5 deselected
```

Los 5 deseleccionados son los canarios de red. Se piden aparte:

```bash
uv run pytest -m network -q   # esperado: 5 passed
```

Estos cinco golpean `spensiones.cl` y confirman que el sitio sigue teniendo la estructura
que el parser espera. Si fallan, el portal cambió: lee
[operations.md → El canario falló](OPERATIONS.md#el-canario-de-red-falló).

## 4. Correr el pipeline

La forma recomendada es el panel de control:

```bash
uv run python -m to_markdown tui
```

Marca etapas y Libros con la barra espaciadora y `enter` para correr; `a` corre el pipeline
completo. La salida va en vivo al panel derecho y el estado del corpus se actualiza solo.
Detalle completo en [TUI.md](TUI.md).

Lo mismo sin interfaz, para scripts y `cron`:

```bash
uv run python -m to_markdown
```

Eso es todo. Corre las siete etapas por defecto, en orden, sobre los cinco Libros:

```
crawl → parse → changes → export → pdf → compare → bundle
```

**No hay que descargar nada a mano.** La etapa `pdf` baja los cinco PDF oficiales del portal
a `assets/books/`, los renombra a `Book1.pdf`…`Book5.pdf` y verifica que cada uno sea el
Libro que dice ser antes de dejarlo en su sitio. `assets/` está en `.gitignore` junto a
`data/` y `output/`: son 130 MB que el pipeline reconstruye solo.

Es **idempotente**: cada etapa reusa su caché, así que volver a correrlo no re-descarga el
portal ni rehace trabajo. Sobre caché completo tarda **61 segundos**.

### Qué vas a ver

```
=== crawl ===

--- Libro I. Afiliación al Sistema de Pensiones (book-i) ---
  level 1: 1 nodes -> 12 children
  level 2: 12 nodes -> 38 children
  ...
  nodes: 156 | leaves: 124 | with normative text: 128
  images: 72 references -> 72 unique files

=== parse ===
book-i     documents:  128 | 1,213,526 chars | units: 1,582 | figures:   72 | notes:  492
...
TOTAL      documents: 1220 | 9,272,279 chars | units: 7,200 | figures: 1747 | notes: 3158

=== pdf ===
book-i     Book1.pdf     8.4 MB |   453 pages | downloaded | Libro I, 22 sections match the crawl
...

=== bundle ===
book-i     12 .md + index |  128 normas |  194,818 palabras
...
TOTAL      80 .md + 5 índices -> .../output
```

En la **primera corrida**, `changes` dice `first run: nothing to compare against` en los
cinco Libros: no hay corrida anterior contra la cual comparar. Es lo normal.

### La primera corrida sí baja el portal

Sin caché, `crawl` descarga 1.476 páginas HTML y 1.747 imágenes, y `pdf` los 130 MB de los
cinco Libros oficiales. Va con `max_workers = 3`
—medido: con 8 hilos el sitio responde `502`— así que toma varios minutos. **No subas ese
número.**

## 5. Ver el resultado

```
output/
├── README.md          ← qué es esto, generado
├── book-i/
│   ├── index.md       ← empezar aquí: Títulos, Capítulos y materias del Libro
│   ├── 1-titulo-i-afiliacion-e-incorporacion-....md
│   └── … 12 archivos
├── book-ii/  … 15 archivos
├── book-iii/ … 19 archivos
├── book-iv/  … 14 archivos
└── book-v/   … 20 archivos
```

Un archivo por **Título**, que es la unidad con la que la norma se cita y se modifica
entera. Dentro de cada archivo, las Letras y Capítulos van anidados como encabezados
`##`/`###`/`####`, con front matter YAML arriba:

```markdown
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

# Título I Afiliación e Incorporación a una Administradora de Fondos de Pensiones

## A. Afiliación e Incorporación a una Administradora

### Capítulo I. Introducción
```

Comprobación rápida de que salió bien:

```bash
find output -name '*.md' | wc -l       # 86
grep -rl '\[\[FIG' output/ | wc -l     # 0 — ningún marcador sin resolver
du -sh output                          # ~9.8M
```

## 6. Contrastar contra el PDF oficial

Las etapas `pdf` y `compare` ya corrieron como parte del pipeline. Su informe legible queda en
`data/pdf/<libro>/coverage.md`:

```bash
head -40 data/pdf/book-i/coverage.md
```

Dice, capítulo por capítulo, qué trae el PDF que no está en la web. Sobre 4.022 páginas la
respuesta actual son **104 palabras** — es decir, la extracción del portal está completa.

---

## Qué sigue

- Actualizar el corpus cuando la SP publique cambios → [operations.md](OPERATIONS.md#actualizar-el-corpus)
- Entender qué hace cada etapa → [pipeline.md](PIPELINE.md)
- Consumir los JSON/JSONL desde otro programa → [schemas.md](SCHEMAS.md)
