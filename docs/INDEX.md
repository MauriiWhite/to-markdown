# Documentación · to-markdown

**to-markdown** convierte fuentes documentales a Markdown verificable. La primera fuente —y
la que define el diseño— es el **Compendio de Normas del Sistema de Pensiones** de la
Superintendencia de Pensiones de Chile (SP).

Se opera desde una TUI (`uv run python -m to_markdown tui`); la CLI hace exactamente lo
mismo y sigue disponible para scripts.

Esta documentación está organizada por **lo que viniste a hacer**, no por cómo está
dividido el código. Si no sabés por dónde empezar, empieza por la primera fila.

| Si quieres… | Lee | Tipo |
| --- | --- | --- |
| Correrlo por primera vez y obtener `output/` | [getting-started.md](GETTING_STARTED.md) | Tutorial |
| Actualizar el corpus, reprocesar un Libro, resolver un fallo | [operations.md](OPERATIONS.md) | Guía práctica |
| Saber qué hace cada etapa y qué archivos escribe | [pipeline.md](PIPELINE.md) | Referencia |
| Consumir los datos: claves, tipos, formatos | [schemas.md](SCHEMAS.md) | Referencia |
| Entender por qué está hecho así | [architecture.md](ARCHITECTURE.md) | Explicación |

Documentos vecinos, fuera de `docs/`:

- [`../README.md`](../README.md) — presentación del proyecto y sus resultados medidos.
- [`../AGENTS.md`](../AGENTS.md) — contrato de trabajo para agentes que modifiquen el repo.
- [`../config.toml`](../config.toml) — la única configuración que se ajusta.
- `../output/README.md` — se **genera**; describe el entregable para quien lo recibe.

## El proyecto en un párrafo

La SP publica el Compendio dos veces: capítulo por capítulo en su portal web, y como cinco
PDF únicos. El pipeline extrae el portal, lo convierte a Markdown de forma **determinista**
—sin modelo de lenguaje en ninguna etapa—, lo agrupa en un archivo por Título, y lo
**contrasta contra el PDF oficial** —que también baja y verifica solo— para poder afirmar
que la extracción quedó completa.
Lo único que se entrega es `output/`.

## Estado medido

Medición del 8 de septiembre de 2026 sobre el corpus real. Estos números son el resultado
de correr el pipeline, no una meta.

| Libro | pvid | Nodos | Normas | Títulos | Números normativos | Figuras | Notas | Texto | Págs. PDF | Alineados |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `book-i` | 2536 | 156 | 128 | 12 | 1.582 | 72 | 492 | 1,21 MB | 414 | 125/128 |
| `book-ii` | 2748 | 204 | 166 | 15 | 1.103 | 95 | 203 | 0,82 MB | 361 | 166/166 |
| `book-iii` | 2815 | 601 | 508 | 19 | 1.948 | 834 | 1.161 | 3,21 MB | 1.432 | 506/508 |
| `book-iv` | 2538 | 320 | 262 | 14 | 1.768 | 474 | 1.111 | 3,09 MB | 1.327 | 261/262 |
| `book-v` | 2539 | 195 | 156 | 20 | 799 | 272 | 191 | 0,94 MB | 488 | 156/156 |
| **Total** | | **1.476** | **1.220** | **80** | **7.200** | **1.747** | **3.158** | **9,27 MB** | **4.022** | **1.214/1.220** |

- **Entregable**: 80 archivos Markdown + 5 índices + 1 README = 86 archivos, 9,8 MB,
  1,51 millones de palabras.
- **Texto que solo está en el PDF**: 104 palabras sobre 4.022 páginas (≤0,02% por Libro).
- **Corrida completa sobre caché**: 33 segundos, sin credenciales.
- **Interfaz**: TUI en Catppuccin Mocha, contraste AA, se adapta de 60 a 200+ columnas.
- **Crawl del portal**: ~2,7 min en limpio, ~2,6 min revalidando (304 en las 1.476 páginas).
- **PDF oficiales**: 130 MB en 18 s, verificados Libro por Libro.
- **Suite**: 175 pruebas offline + 10 canarios de red, todas en verde.

Cómo se reproduce cada número: [operations.md → Verificar el estado](OPERATIONS.md#verificar-el-estado-del-proyecto).

## Principios que la documentación asume

Están explicados en [architecture.md](ARCHITECTURE.md), pero conviene tenerlos a mano:

1. **Sin servicios de pago ni credenciales.** Dos dependencias de Python y `poppler-utils`.
2. **La transformación es aditiva.** Ninguna etapa pierde información; toda figura conserva
   su URL en el sitio de la SP.
3. **Nada se interpreta.** Jerarquía, numeración y tablas salen de un parser. Lo que está
   encerrado en píxeles se enlaza a su original, no se adivina.
4. **Fallar cerrado.** Una salida degradada aborta antes de escribir; la anterior sobrevive.
   Vale también para los PDF oficiales: uno que no se verifica no pisa al que estaba.
5. **Un Libro, una carpeta.** Los cinco Libros son corpus independientes de punta a punta.
