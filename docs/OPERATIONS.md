# Guía práctica

Recetas para las cosas que se hacen de verdad. Cada sección resuelve una tarea.

## Actualizar el corpus

La SP cambia ~160 páginas al año. Para traer los cambios y ver qué cambió:

```bash
uv run python -m to_markdown refresh parse changes export bundle
```

`refresh` revalida contra el servidor con `If-None-Match` / `If-Modified-Since`: las páginas
sin cambio responden `304` con cero bytes. **Reemplaza a `crawl`, no lo continúa** — por eso
se escribe en vez de él y no después.

El tiempo de pared sigue siendo de varios minutos aunque casi no se transfiera nada: está
dominado por la latencia de 1.476 peticiones a `max_workers = 3`, no por el ancho de banda.

Después, lee qué cambió:

```bash
ls -t data/web/book-iii/changelog/ | head -1     # el más reciente
```

El informe agrupa por clase (`normative`, `editorial`, `pipeline`, `cosmetic`, `new`,
`removed`) y baja a nivel de número normativo, con su diff. Lo que hay que revisar primero
es `normative`: son los cambios que la propia norma declara con una Nota de actualización.

Si aparece `pipeline`, **no cambió la norma: cambió nuestro parser**. Es la señal de que
alguien tocó `parse.py` y la salida se movió.

## Actualizar los PDF oficiales

Van con el resto del pipeline, pero se pueden pedir sueltos:

```bash
uv run python -m to_markdown pdf              # los cinco
uv run python -m to_markdown pdf -b book-iii  # uno
```

Revalida con `If-None-Match`: si el PDF de la SP no cambió, no baja nada. Para **forzar** la
descarga, borra el archivo y vuelve a correr:

```bash
rm assets/books/Book3.pdf && uv run python -m to_markdown pdf -b book-iii
```

`assets/` está en `.gitignore`: los 130 MB de PDF no se versionan porque el pipeline los
reconstruye solo y verificados. Un clon limpio corre `uv run python -m to_markdown` y los
tiene.

`assets/books/http.json` guarda el `ETag` de cada Libro. Borrarlo hace que la etapa vuelva a
decidir por tamaño, que es lo que hace en la primera corrida.

## Trabajar sobre un solo Libro

`--book` / `-b` es repetible y acepta los slugs de `[[books]]`:

```bash
uv run python -m to_markdown -b book-iii                    # las 6 etapas, un Libro
uv run python -m to_markdown parse export -b book-i -b book-v
```

Útil para reprocesar sin repasar los otros cuatro. Como cada Libro es un corpus
independiente —su caché, su manifiesto, su estado y su entregable—, no hay coordinación que
mantener.

> `bundle` escribe `output/README.md` **solo si corrieron los cinco Libros**. Con `-b` se
> regeneran las carpetas pedidas y el README del paquete queda como estaba.

## Correr etapas sueltas

Las etapas se ejecutan en el orden en que se escriben:

```bash
uv run python -m to_markdown parse                  # solo re-parsear el caché
uv run python -m to_markdown export bundle          # solo rearmar el entregable
uv run python -m to_markdown compare -b book-iv     # solo la comparativa de un Libro
```

Ninguna vuelve a descargar nada mientras el caché esté en pie.

## Verificar el estado del proyecto

### Lo rápido

```bash
uv run ruff check src tests    # esperado: All checks passed!
uv run pytest -q               # esperado: 109 passed, 5 deselected
uv run pytest -m network -q    # esperado: 5 passed (golpea spensiones.cl)
```

### Las invariantes contra el corpus real

```bash
uv run python - <<'PY'
import json
from to_markdown import BOOKS
from to_markdown.guard import check, metrics
for b in BOOKS:
    docs = json.loads(b.file("documents.json").read_text(encoding="utf-8"))
    man = json.loads(b.file("manifest.json").read_text(encoding="utf-8"))
    m, problems = metrics(docs), check(b, docs, man)
    print(f"{b.slug:9} docs={m['documents']:4} units={m['units']:5} figs={m['figures']:4} "
          f"notes={m['notes']:4} empty={m['empty']} -> {problems or 'OK'}")
PY
```

### Los PDF oficiales

```bash
uv run python -m to_markdown pdf
```

Verifica los cinco contra el árbol del crawler sin bajar nada si están vigentes. Esperado:

```
book-i     Book1.pdf     8.4 MB |   453 pages | cached    | Libro I, 22 sections match the crawl
```

`N sections match the crawl` es el número de secciones que el PDF imprime y que el crawler
también extrajo. Cualquier número ≥ 2 confirma la correspondencia; el veredicto duro es que
no haya errores.

### El entregable

```bash
find output -name '*.md' | wc -l              # 86 = 80 Títulos + 5 índices + README
grep -rl '\[\[FIG' output/ | wc -l            # 0 — ningún marcador sin resolver
grep -rho '!\[Figura\](\S*)' output/ | grep -vc spensiones.cl   # 0 — todo apunta a la SP
du -sh output                                 # ~9.8M
```

### La cobertura contra el PDF oficial

```bash
head -40 data/pdf/book-iii/coverage.md
```

O el resumen de los cinco:

```bash
uv run python -m to_markdown compare
```

## Cambiar la agrupación del entregable

Por defecto un archivo por **Título**. Se cambia en `config.toml`:

```toml
[export]
group_by = "title"    # "title" | "letter" | "chapter"
```

Después hay que rehacer el entregable:

```bash
uv run python -m to_markdown export bundle
```

`"letter"` queda en medio (33 archivos en el Libro I). `"chapter"` produce muchos más archivos y más chicos: 84 en el Libro I en vez de 12. Sirve
si aguas abajo se va a hacer chunking fino; para lectura humana o para que un modelo lea una
norma entera, el Título es la unidad correcta.

## Agregar un Libro

Si la SP publica un Libro VI, es agregar una tabla a `config.toml`:

```toml
[[books]]
slug = "book-vi"
pdf_file = "Book6.pdf"
pvid = "…"                # el pvid raíz, que se lee del portal
name = "Libro VI. …"
min_documents = 0         # medir primero, después ajustar con ~12% de holgura
min_units = 0
```

Corre `crawl parse` con `min_documents = 0` para medir, y recién entonces fijá las cotas al
número medido menos ~12%. El PDF va a `assets/books/Book6.pdf`.

El canario de red avisa si la SP publica un Libro que no está listado.

---

# Resolución de problemas

## `DEGRADED CORPUS in … — nothing was written`

El guard detectó una regresión y **abortó antes de escribir**. La salida anterior está
intacta. El mensaje dice exactamente qué invariante se violó:

```
DEGRADED CORPUS in Libro III. Beneficios Previsionales (book-iii) — nothing was written:
  - only 312 documents, expected >=450
  - only 41% have hierarchy, expected >=95%
```

**Qué hacer, en este orden:**

1. **Entender por qué se violó.** Si cayó la cantidad de documentos o la jerarquía, lo más
   probable es que la SP cambió su CMS y los selectores de `parse.py` dejaron de calzar.
2. Corre el canario: `uv run pytest -m network -q`. Es el diagnóstico directo.
3. Abre una página real y comparala contra los regex de `parse.py`
   (`BODY_OPEN`, `CRUMB_BLOCK`, `TITLE`, `CANONICAL`, `TOPICS`).
4. **Solo si el cambio es legítimo** —la SP de verdad reorganizó el Libro— forzá:

   ```bash
   TO_MARKDOWN_FORCE=1 uv run python -m to_markdown parse -b book-iii
   ```

   y **ajusta la cota en `config.toml` al número nuevo medido**.

> Si una invariante estorba, la respuesta es entender por qué se violó, no bajarle el
> umbral. Una invariante mal calibrada llora lobo hasta que deja de significar algo.

## `WRONG PDF for … — nothing was written`

La etapa `pdf` bajó un archivo que no es el Libro que dice el nombre con que iba a guardarlo,
y **no lo escribió**: el PDF que ya estaba sigue intacto.

```
WRONG PDF for Libro I. Afiliación al Sistema de Pensiones (book-i) — nothing was written:
  - header says ['Libro III'] but Book1.pdf must be Libro I

  downloaded: https://www.spensiones.cl/portal/compendio/596/fo-propertyvalue-2815.pdf
  would be:   .../assets/books/Book1.pdf
```

Significa que el `pvid` de ese Libro en `config.toml` ya no apunta a ese Libro en el portal.
Abre la raíz del Libro y mira a dónde va su enlace `AccesoPDF`:

```bash
uv run python -c "from to_markdown import BY_SLUG; b=BY_SLUG['book-i']; \
  print(f'https://www.spensiones.cl/portal/compendio/596/w3-propertyvalue-{b.pvid}.html')"
```

Si la SP reorganizó los Libros, corrige el `pvid` en `config.toml` — es la clave de
partición de todo el proyecto, así que el crawl también estaría recorriendo el árbol
equivocado.

El otro mensaje posible es el del cruce contra el crawler:

```
  - 9/11 sampled sections are not in the crawled book-iii tree, e.g. 'Libro IV, Título I…'
```

Ese dice que el PDF **se declara** como el Libro correcto pero sus secciones no son las que
el crawler extrajo. Suele ser el caso contrario: el caché del crawl quedó viejo. Corre
`refresh parse` y vuelve a intentar.

## `WRONG PDF on disk for …`

Lo mismo, pero sobre un archivo que ya estaba en `assets/books/`. Bórralo y vuelve a bajarlo:

```bash
rm assets/books/Book3.pdf && uv run python -m to_markdown pdf -b book-iii
```

## `note: only N sections sampled, cross-check inconclusive`

**No es un fallo.** El muestreo encontró menos de dos secciones reconocibles, así que el
cruce contra el crawler no concluye — pero el encabezado corrido sí se verificó, que es la
comprobación que decide de qué Libro es el archivo.

Pasa con PDF chicos o con secciones muy largas. Si te importa cerrar el cruce, `compare` hace
la comparación completa capítulo por capítulo.

## `note: no crawl to cross-check against; run parse first`

La etapa `pdf` corrió antes que `parse`, así que no hay `documents.json` contra el cual
cruzar. El encabezado se verificó igual. En la corrida por defecto no pasa: `pdf` va después
de `parse` justamente por esto.

## `could not download … (truncated: N of M bytes)`

La respuesta llegó cortada y el transporte la rechazó en vez de cachearla. Se reintenta solo
hasta `max_retries`; si persiste, el sitio o la red están inestables. Vuelve a correr: el
caché conserva lo ya descargado.

Es deliberado que falle: una página truncada se habría cacheado como HTML válido y el parser
habría extraído un documento incompleto sin que ninguna invariante se quejara.

## `could not download … (HTTP 404 …)` en una página que existía

El sitio responde `302` a cualquier pvid inexistente y el destino es un `404`. Si aparece
sobre un pvid que antes funcionaba, la SP movió o retiró esa página. Corre el canario:

```bash
uv run pytest -m network -q
```

## El canario de red falló

Los cinco canarios verifican que el sitio sigue publicando lo que el parser espera:

| Prueba | Qué protege |
| --- | --- |
| `test_marcadores_de_estructura_siguen_existiendo` | `cuerpo_documento`, el bloque de hijos |
| `test_la_jerarquia_sigue_en_los_atributos` | El breadcrumb y sus `pvid-NNNN` |
| `test_el_documento_canario_parsea_igual_que_siempre` | Una página conocida, extremo a extremo |
| `test_el_servidor_sigue_honrando_peticiones_condicionales` | Que `refresh` siga sirviendo |
| `test_el_sitio_sigue_publicando_los_cinco_libros` | Que no haya un Libro nuevo sin listar |
| `test_cada_libro_sigue_enlazando_su_pdf_completo` | Que la URL `fo-propertyvalue-<pvid>.pdf` siga siendo el esquema |
| `test_el_pdf_de_cada_libro_sigue_sirviendose` | Que el PDF responda y traiga `ETag` |
| `test_el_servidor_sigue_comprimiendo` | Que el gzip siga activo (4,7x menos transferencia) |
| `test_el_etag_sigue_calzando_con_gzip_activo` | Que el 304 siga funcionando **pidiendo gzip** |
| `test_una_pagina_inexistente_no_se_confunde_con_una_vacia` | Que el `302` siga llevando a un `404` |

Un fallo aquí **no** es un fallo del pipeline: es el sitio que cambió. Arreglá los selectores
en `parse.py` / `crawl.py`, agrega la página que falló a `tests/fixtures/` y recién entonces
vuelve a correr el corpus.

## `missing pdftotext` / `missing pdfinfo` (poppler-utils)

Afecta a `pdf` y a `compare`. Las otras cinco etapas corren sin ellos:

```bash
sudo pacman -S poppler          # Arch
sudo apt install poppler-utils  # Debian / Ubuntu
brew install poppler            # macOS
```

## `could not download …` durante el crawl

El sitio responde `502` bajo carga. `max_workers = 3` está **medido** para no provocarlo, y
`max_retries = 6` con espera exponencial es la red de seguridad.

Si igual falla, el sitio está caído o hay un problema de red. Vuelve a correr: el caché
conserva lo ya descargado y el crawl retoma donde quedó.

**No subas `max_workers`.** Con 8 hilos el sitio responde `502` de forma reproducible.

## `WARNING: fake_useragent failed to load`

El catálogo de User-Agents no abrió. El crawl **sigue** con un UA propio. Es la única
excepción deliberada al "fallar cerrado" del proyecto: aquí no hay riesgo de escribir datos
degradados, solo de no descargarlos.

## `WARNING: N images not downloaded (marked FIG-MISSING, not lost)`

Alguna imagen no se pudo descargar. **No se perdió la referencia**: queda como
`[[FIG-MISSING:<src>]]` y `export` la resuelve igual a `![Figura](url)`, porque la URL puede
funcionar perfectamente aunque nuestro `urlopen` haya fallado ese día.

Vuelve a correr `crawl` para reintentar la descarga de la copia local.

## `WARNING: N figures without a source URL`

Una figura perdió su procedencia, que es lo único que este corpus promete sobre ella.
Revisa `images.json` del Libro: la entrada `src -> sha256` debería existir para cada hash
referenciado en `documents.json`.

## Las pruebas se saltan solas

```
SKIPPED [1] book-iii no construido: `uv run python -m to_markdown crawl parse`
```

Las pruebas que validan el corpus real se saltan si `data/` no está construido. Las 109
offline corren siempre porque leen `tests/fixtures/`, que sí está versionado.

## El changelog dice `pipeline` en cientos de documentos

Cambió `parse.py` y la salida se movió. **No es un cambio normativo.** Es exactamente lo que
la clase `pipeline` existe para distinguir: si el proyecto llevara un solo hash, cada mejora
al parser se vería como si 1.220 normas hubieran cambiado.

Revisa el diff: si el cambio es el que buscabas, subí `SCHEMA_VERSION` en `parse.py` cuando
haya cambiado la *forma* de la salida, no solo su contenido.
