# AGENTS.md

## Qué es esto

**to-markdown**: convierte fuentes documentales a Markdown verificable. La primera fuente
—y la que define el diseño— es el **Compendio de Normas del Sistema de Pensiones** de la
Superintendencia de Pensiones de Chile.

El nombre es genérico a propósito: la forma del pipeline (recorrer, parsear determinista,
diffear, exportar, contrastar contra un original) no es específica del Compendio.

Esta fase cubre **solo extracción y transformación**. Chunking, embeddings, búsqueda, agente
y despliegue son fases posteriores y no están aquí.

## Stack

| Capa | Tecnología |
| --- | --- |
| Lenguaje | Python ≥3.12 (`src`-layout) |
| Gestor de paquetes | `uv` |
| Dependencias | `fake-useragent`, `pillow` (pipeline) · `textual`, `textual-plotext` (solo la TUI) |
| Externo | `poppler-utils`: `pdftotext`, `pdfimages`, `pdfinfo` (etapas `pdf` y `compare`) |

Todo el código va en `src/to_markdown/`. Los archivos de configuración van en la raíz.

**Cuatro capas, y la dependencia va en un solo sentido:**

    core  ←  infra  ←  stages  ←  analytics  ←  tui

`core` no importa nada del proyecto; `infra` solo importa `core`; las etapas importan
`core` e `infra`, nunca al revés. Si una capa necesita algo de la de arriba, está mal
puesta.

**Un archivo, una responsabilidad.** Cada paquete tiene una fachada en su `__init__.py` que
expone lo que se usa desde fuera y esconde en qué archivo está cada cosa. El registro de
etapas vive en `stages/__init__.py` y no en el CLI: cuáles son las etapas y en qué orden van
es del pipeline, y el CLI y la TUI son dos formas de invocarlo.

Importar `to_markdown.tui` no puede exigir `textual`: el pipeline entero tiene que poder
correr en un `cron` sin terminal, así que la fachada difiere ese import hasta `build_app()`
—y solo enmascara el `ImportError` de `textual`, nunca uno del propio panel.

## Comandos

```bash
uv sync
uv run python -m to_markdown                 # pipeline completo, idempotente
uv run python -m to_markdown parse export    # solo etapas sueltas
uv run python -m to_markdown -b book-iii    # solo un Libro (repetible)
uv run python -m to_markdown pdf             # baja los 5 PDF oficiales y verifica cuál es cuál
uv run python -m to_markdown compare         # PDF oficial contra lo extraído del portal
uv run pytest -q                            # suite offline (usa tests/fixtures/)
uv run pytest -m network                    # canario contra el sitio en vivo
uv run ruff check src tests
```

Usar siempre `uv`. No invocar el binario global de Python ni activar el virtualenv a mano.

## Restricciones

### 1. Sin servicios de pago ni credenciales
El pipeline completo corre con dos dependencias de Python y `poppler-utils` del sistema. No
hay cliente de IA, ni claves, ni `.env`.

`textual` es la tercera dependencia y es **solo de la interfaz**: se importa de forma
perezosa dentro de `build_app()`, así que el pipeline sigue corriendo en un `cron` sin
terminal. Esa propiedad no se pierde por agregar una TUI.

### 2. Nada por defecto cuesta dinero
La corrida por defecto (`crawl parse changes export compare`) no usa credenciales ni
servicios de pago. `refresh` es la alternativa a `crawl`, nunca su continuación.

### 3. El modelo solo toca píxeles
Jerarquía, numeración normativa, tablas HTML y notación `<sub>`/`<sup>` se extraen con
parser. Lo que queda encerrado en píxeles **no se interpreta**: se enlaza a su original en
el sitio de la SP y quien lea decide. Adivinar el contenido de una imagen es peor que
enlazarla.

### 4. La transformación es aditiva
Ninguna etapa puede perder información. Toda figura conserva `src`, `sha256` y su archivo
local **y su URL en el sitio de la SP**, que es lo que la hace verificable. Si algo no se
puede resolver, se deja la referencia y se avisa — nunca un hueco en silencio.

### 5. Estilo
- Código Python (identificadores, funciones, clases) en **inglés**.
- **Claves e identificadores de esquema en inglés**, siempre: claves de JSON/JSONL, front
  matter YAML, y valores que actúan como enumeración (`category`, `type`, `status`, `kind`).
  Son contrato de datos, no prosa.
- **Contenido en español**, intacto: el texto normativo, las notas de actualización y las
  materias se transcriben tal como los publica la Superintendencia.
- **Toda la salida de los comandos, en inglés**: mensajes de consola, ayuda de `--help`,
  errores y avisos, y los textos de la interfaz del revisor. Es la superficie con la que se
  opera la herramienta y va en el mismo idioma que el código.
- Documentación, docstrings, comentarios y la prosa de los informes generados
  (`coverage.md`, changelog), en **español**.
- Type hints modernos (`dict[str, Any]`, `list[str] | None`) en todas las firmas.
- `schema_version` se sube cuando cambia la forma de la salida, no solo su contenido.

### 6. Fallar cerrado, nunca abierto
`guard.py` valida el corpus antes de escribirlo. Ninguna etapa puede sobrescribir una salida
buena con una degradada. Si una invariante estorba, la respuesta es entender por qué se violó
—no bajarle el umbral. Una invariante mal calibrada llora lobo hasta que deja de significar
algo.

### 7. Dos hashes, no uno
`source_sha256` (cuerpo HTML) y `content_sha256` (nuestro Markdown) son distintos a
propósito. Con uno solo, cada mejora al parser se vería como si 1.198 normas hubieran
cambiado y el changelog dejaría de valer.

### 8. Concurrencia contra el sitio
`crawl.max_workers = 3` está medido, no elegido: con 8 hilos `spensiones.cl` responde 502.
No subirlo.

La velocidad se gana en el **transporte**, no en la concurrencia: una conexión HTTPS viva por
hilo (keep-alive) y `Accept-Encoding: gzip` dan 2,25x con los mismos 3 hilos —244 a 108 ms
por página— y 4,7x menos bytes. El handshake TLS repetido 1.476 veces era dos tercios del
tiempo. El pool de hilos es **uno para toda la corrida**: uno por nivel del árbol levantaba
conexiones nuevas en cada nivel y anulaba el keep-alive.

Tres cosas que el transporte tiene que seguir haciendo, y que ninguna invariante detectaría:

- **Normalizar el ETag.** Apache le agrega `-gzip` al servir comprimido y ese ETag nunca
  vuelve a calzar. Sin normalizarlo, `refresh` re-descarga las 1.476 páginas en cada corrida
  y el corpus sigue saliendo correcto, solo que veinte veces más lento.
- **Seguir las redirecciones.** El sitio responde 302 a cualquier pvid inexistente; sin
  seguirla se cachea el stub de 267 bytes como si fuera la norma.
- **Comparar contra `Content-Length`.** Una respuesta cortada se cachearía como HTML válido
  y el parser extraería un documento truncado en silencio.

### 9. Dos fuentes, cinco Libros
`data/` se parte primero por FUENTE y después por Libro. `web/` es lo que la SP publica en
su portal, capítulo por capítulo, y es lo que el pipeline extrae; `pdf/` es el mismo
Compendio que la SP exporta como documento único, alineado contra el anterior. Son dos
testimonios de lo mismo y no se mezclan: juntarlos en una carpeta haría imposible la única
pregunta que justifica tenerlos los dos, que es qué trae uno y el otro no.

### 10. Un Libro, una carpeta
El Compendio se publica en cinco Libros y `data/` los refleja uno a uno: cada Libro tiene
su caché, sus imágenes, su manifiesto, su estado y su entregable bajo `data/<slug>/`, y
ninguna etapa mezcla dos. La separación es exacta y está verificada — los 1.478 nodos del
árbol cuelgan de un único Libro y ninguna de las 1.743 figuras aparece en dos.

La carpeta se nombra por el **numeral romano**, y la clave de partición es el **pvid raíz**,
nunca el título: la SP ya renombró los Libros I y V, y hoy conviven 39 documentos con el
nombre anterior en su breadcrumb. Una carpeta nombrada por el título se habría partido en
dos con ese cambio.

Las invariantes también van por Libro. Sobre el total, perder entero el Libro I deja 1.094
documentos —por encima de cualquier cota global razonable— y el fallo pasa inadvertido.

### 11. `is_leaf` no es "tiene texto"
Un nodo puede tener hijos **y** cuerpo normativo propio: un Título que además imparte
instrucciones, un Capítulo con preámbulo antes de sus números. Son 24 en el corpus y valen
190.502 caracteres que el PDF de la SP sí imprime. El manifiesto lleva `has_body` por nodo y
`documents` con la lista autoritativa ya en orden de lectura; ninguna etapa vuelve a
derivarla de `is_leaf`.

### 12. Un archivo Markdown por Título
El entregable legible se agrupa por **Título** (`export.group_by`, por defecto `"title"`):
un Libro son sus Títulos, y cada Título es un solo `.md` con sus Letras, Capítulos y Anexos
dentro, anidados como encabezados `##`/`###`/`####`. Es la unidad con la que la norma se
cita y se modifica entera, y con la que la SP encabeza cada página de su PDF.

La agrupación se resuelve por el árbol y no por el texto del título, porque los nombres se
repiten —"Capítulo I. Introducción" aparece 11 veces solo en el Libro III— y agrupar por
nombre los fundiría. El ordinal del archivo sale del árbol **completo**, no de los
documentos que se pasen: si se calculara sobre el subconjunto, cada capítulo que el lado PDF
no logra alinear correría todos los siguientes y los dos árboles dejarían de compararse con
un `diff`.

### 13. El PDF se verifica antes de renombrarlo

La etapa `pdf` baja los cinco Libros del portal y los guarda como `Book<N>.pdf`. El servidor
los publica bajo `fo-propertyvalue-<pvid>.pdf`, un nombre que no dice de qué Libro es, así
que renombrar es obligatorio — y renombrar sin verificar sería peor que bajarlos a mano: un
`Book3.pdf` que en realidad fuera el Libro IV se compararía contra el árbol equivocado y
`coverage.md` saldría lleno de "contenido solo en el PDF" sin que nada avisara.

Por eso se descarga a un temporal, se verifica, y **solo entonces** se mueve. Dos
comprobaciones, y la segunda es la que el nombre no puede dar:

1. El PDF se encabeza a sí mismo en cada página ("Compendio de Normas del Sistema de
   Pensiones - Libro III"). Se ancla a la línea completa: el cuerpo normativo también cita
   al Compendio, y tomar cualquier mención daba un falso positivo.
2. Las páginas repiten el `path` de la norma con el mismo texto que `parse` guarda en
   `documents.json`. Cruzarlos comprueba que este PDF y el subárbol que recorrió el crawler
   son el mismo Libro, no solo que ambos digan "Libro III".

El enlace sale del **pvid**, no de una lista de URLs: es la misma clave estable con que se
particiona todo lo demás. El canario de red avisa si la SP cambia el esquema.

### 14. La interfaz es Catppuccin Mocha, y el color nunca es el único canal

Los 26 tonos oficiales de Mocha, aplicados por papel: `crust`→`mantle`→`base`→`surface0` es
la escala de elevación, `blue` marca el foco y nada más, `lavender` marca la capa modal, y
`green`/`yellow`/`red` son lo que dicen ser. Ningún acento cumple dos papeles.

Las categorías de los gráficos se siguen distinguiendo por **densidad de trama** (`█▓▒░`) y
no por matiz: el color es refuerzo redundante, así que el panel se lee igual en una terminal
sin color y para quien no distingue un color de otro. El énfasis sin color lo da el peso.

Los 19 pares de texto y fondo cumplen el contraste AA de la WCAG, y la suite lo comprueba.

Ningún ancho es constante: los gráficos reciben el ancho disponible y se dibujan para ese
ancho. Por debajo de 92 columnas el diseño se apila en vez de encogerse — encoger dos
paneles hasta que ninguno se lea no es adaptarse.

La prosa de la interfaz supone **poca familiaridad con la terminal**: las etapas se
describen por lo que hacen, no por su efecto técnico, y la línea de estado muestra siempre
el comando equivalente. La TUI no esconde la CLI, la enseña.

### 15. El rendimiento se mide muestreando, no al final

`monitor.py` lleva contadores de proceso que las etapas incrementan, y la TUI los muestrea
cada medio segundo para trazar líneas. Es lo que distingue "tardó 32 s" de "el pico de red
fue en `crawl` y la memoria trepó a 384 MB en `compare`".

El ritmo se deriva **entre muestras** y no del acumulado: una curva acumulada siempre sube, y
sube igual cuando el ritmo se derrumbó. El muestreo corre siempre, no solo con el apartado
abierto, o la curva arrancaría a mitad de la corrida.

Los contadores son globales de módulo a propósito: instrumentar el pipeline no puede obligar
a cambiar la firma de cada función. Y todo es stdlib — un medidor que hay que instalar es un
medidor que no se usa.

### 16. Borrar pide dos validaciones distintas

Es la única operación que destruye trabajo. La primera se contesta con una tecla; la segunda
obliga a escribir una palabra, que solo se puede escribir después de leer qué se va a
borrar. La palabra cambia con el riesgo: `no se repone` para el historial de corridas y la
línea base del changelog.

Todo objetivo declara **cómo se repone**, y la lista va de lo más barato a lo más caro.

## Estructura

```
├── pyproject.toml · config.toml · AGENTS.md · README.md
├── src/to_markdown/
│   ├── __init__.py       fachada del paquete: reexporta el modelo y las rutas
│   ├── __main__.py       CLI: analiza los argumentos y despacha
│   │
│   ├── core/             EL DOMINIO · no depende de nada del proyecto hacia fuera
│   │   ├── config.py         config.toml y las rutas
│   │   ├── books.py          el modelo `Book`: qué es un Libro y dónde vive lo suyo
│   │   └── guard.py          las invariantes del corpus
│   │
│   ├── infra/            EL MUNDO EXTERIOR · red, proceso y disco de trabajo
│   │   ├── net.py            transporte HTTP: keep-alive, gzip, redirecciones, reintentos
│   │   ├── monitor.py        contadores del proceso en vivo · solo stdlib
│   │   └── cleanup.py        qué se puede borrar y cómo se repone
│   │
│   ├── stages/           EL PIPELINE · `__init__.py` es el registro y el orden
│   │   ├── crawl.py      1. sitio -> data/web/<libro>/cache/*.html + images/
│   │   ├── parse/        2. documentos jerarquizados (determinista, sin modelo)
│   │   │   ├── __init__.py   el documento: metadatos, jerarquía, hashes
│   │   │   └── html.py       el conversor HTML -> Markdown y las unidades numeradas
│   │   ├── changes.py    3. diff por número normativo, clasificado
│   │   ├── export.py     4. entregable: JSONL + un Markdown por Título
│   │   ├── pdf.py        5. baja assets/books/Book<N>.pdf y verifica que sea ESE Libro
│   │   ├── compare/      6. PDF oficial alineado contra el portal
│   │   │   ├── __init__.py   la alineación y la fachada de la etapa
│   │   │   ├── extract.py    pdftotext / pdfimages y la forma canónica
│   │   │   ├── coverage.py   n-gramas, cobertura léxica y el veredicto
│   │   │   └── render.py     el Markdown del lado PDF y el informe
│   │   └── bundle.py     7. empaqueta output/: los .md y sus índices
│   │
│   ├── analytics/        MÉTRICAS Y GRÁFICOS · sin textual, funciones puras
│   │   ├── format.py         primitivas: barras, líneas de tendencia, números
│   │   ├── sources.py        las series con fecha: duraciones y actividad normativa
│   │   ├── metrics.py        lo que hay en disco, leído sin recalcular nada
│   │   ├── charts_state.py   gráficos del estado actual (una foto)
│   │   ├── charts_trend.py   gráficos de tendencia (cómo cambia en el tiempo)
│   │   └── charts.py         el informe: qué secciones y en qué orden
│   │
│   └── tui/              LA INTERFAZ · mismas etapas, misma salida, otra forma
│       ├── __init__.py       fachada · mantiene el import de textual perezoso
│       ├── content.py        todo lo que el panel muestra en palabras y números
│       ├── theme.py          el tema Catppuccin Mocha y la hoja de estilos
│       ├── screens.py        los modales: borrar, confirmar, ayuda
│       ├── drawers.py        los tres apartados y su dibujado
│       ├── runner.py         ejecuta las etapas y recoge su salida
│       └── app.py            el armado del panel y sus teclas
├── tests/
├── assets/                   gitignored · lo baja y verifica la etapa `pdf`
│   └── books/                Book1..5.pdf + http.json (ETag por Libro)
├── output/                   gitignored · LO ÚNICO QUE SE ENTREGA
│   ├── README.md             qué es, de dónde salió, cómo navegarlo
│   └── book-i … book-v/      index.md + un .md por Título
└── data/                     gitignored
    ├── web/book-i … book-v/     extraído del portal
    │   ├── cache/*.html           el subárbol de ESE Libro y nada más
    │   ├── images/<sha>.ext
    │   ├── markdown/NNN-<tít>.md   un archivo por Título, en orden de lectura
    │   ├── changelog/*.md
    │   ├── state/                 documents.json + runs.jsonl del Libro
    │   ├── manifest.json · http.json · images.json · sections.json
    │   └── documents.jsonl · figures.jsonl (URL de origen de cada figura)
    │   ├── documents.json · documents.jsonl
    │   ├── figures.json · figures.jsonl
    │   └── changes.json
    └── pdf/book-i … book-v/      el PDF oficial, alineado al orden de la web
        ├── markdown/NNN-<tít>.md   mismos nombres que web/, para `diff` directo
        ├── images/<sha>.png        figuras embebidas en el PDF (pdfimages)
        ├── text.txt                salida cruda de pdftotext (caché)
        ├── documents.json          el PDF segmentado por los mismos pvid
        ├── images.json             índice p<página>-<n> -> sha256
        └── coverage.json · coverage.md
```

Los cinco Libros y sus `pvid` raíz están en `[[books]]` de `config.toml`, junto a sus cotas
medidas. Agregar un Libro es agregar una tabla; el canario de red avisa si la SP publica uno
que no esté listado.
