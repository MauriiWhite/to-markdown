# Compendio de Normas del Sistema de Pensiones

Superintendencia de Pensiones de Chile, extraído de su portal y convertido a Markdown.

**80 archivos** en 5 Libros · 1.220 normas · 7.200 números normativos · 3.158 notas de actualización.

## Los cinco Libros

| Carpeta | Libro | Títulos | Normas | Extraído |
| --- | --- | ---: | ---: | --- |
| `book-i/` | Libro I. Afiliación al Sistema de Pensiones | 12 | 128 | 2026-09-09 |
| `book-ii/` | Libro II. Cotizaciones Previsionales | 15 | 166 | 2026-09-09 |
| `book-iii/` | Libro III. Beneficios Previsionales | 19 | 508 | 2026-09-09 |
| `book-iv/` | Libro IV. Fondos de Pensiones y Regulación de Conflictos de Intereses | 14 | 262 | 2026-09-09 |
| `book-v/` | Libro V. Aspectos Administrativos y Operacionales | 20 | 156 | 2026-09-09 |

## Cómo está organizado

Una carpeta por Libro. Dentro, un archivo Markdown por **Título** —la unidad con la que la norma se cita y se modifica entera— y un `index.md` que lista sus Títulos, los Capítulos que contiene cada uno y las materias que cubre.

```
book-i/
├── index.md                      ← empezar aquí
├── 1-titulo-i-afiliacion-....md
└── ...
```

Para ubicar una norma: leer el `index.md` del Libro, encontrar el Título que la contiene, y abrir ese archivo. Dentro, la jerarquía va como encabezados (`##` Letra, `###` Capítulo) y cada norma conserva su `pvid` y su URL de origen en un comentario.

## Sobre el contenido

- El texto normativo está **íntegro y sin resumir**, tal como lo publica la SP.
- Las tablas se convirtieron desde el HTML original, así que conservan sus filas y columnas.
- Las **figuras se enlazan a la imagen original en `spensiones.cl`**: no hay copias locales que puedan diferir de la fuente. Requieren conexión para verse.
- Las **notas de actualización** están marcadas como citas (`>`) e indican qué Norma de Carácter General modificó cada número.

## Procedencia

Portal de origen: https://www.spensiones.cl/portal/compendio/596/

Cada archivo lleva en su front matter el `pvid` de las páginas que lo componen, y cada norma un comentario con su URL. Cualquier afirmación de este corpus se puede contrastar contra la página del organismo.

Paquete generado el 2026-09-09.
