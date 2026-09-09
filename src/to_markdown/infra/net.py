"""Transporte HTTP: conexiones vivas, gzip, redirecciones y reintentos.

Va aparte del recorrido del árbol porque son dos responsabilidades distintas y una de las
dos es la que más cuesta acertar. Lo que este módulo garantiza:

  - **Una conexión viva por hilo.** `urllib` abría una conexión TCP nueva —con su handshake
    TLS— en cada una de las 1.476 páginas: 917 ms por página contra 310 reutilizándola. 3x,
    sin tocar la concurrencia.
  - **Se pide gzip**, que el servidor ya servía: 4,7x menos bytes.
  - **El ETag se normaliza.** Apache le agrega `-gzip` al servir comprimido y ese ETag no
    vuelve a calzar; sin quitarlo, `refresh` re-descargaría todo en cada corrida.
  - **Las redirecciones se siguen.** El sitio responde 302 a cualquier pvid inexistente, y
    sin seguirla se cachearía el stub de 267 bytes como si fuera la norma.
  - **El cuerpo se compara contra `Content-Length`.** Una respuesta cortada se reintenta en
    vez de cachearse como HTML válido.
"""

from __future__ import annotations

import gzip
import http.client
import json
import re
import threading
import time
import urllib.parse

from fake_useragent import UserAgent

from ..core import CONFIG, Book
from .monitor import bump

BASE = CONFIG["crawl"]["base_url"]
WORKERS = CONFIG["crawl"]["max_workers"]
RETRIES = CONFIG["crawl"]["max_retries"]
# Saltos de redirección que se siguen. `urllib.urlopen` las seguía solo; `http.client` no,
# y sin esto una página movida se cacheaba como el stub de 267 bytes que devuelve el 302
# —HTML válido, sin cuerpo normativo— y el parser la habría dado por vacía en silencio.
# Este sitio responde 302 a cualquier pvid inexistente, así que el caso es real.
MAX_REDIRECTS = 5
TIMEOUT = CONFIG["crawl"]["timeout"]

# User-Agent rotatorio, uno por petición. `fake_useragent` trae su catálogo empaquetado y
# no toca la red al inicializarse, así que no agrega un punto de fallo al crawl.
#
# Si el catálogo no cargara, se sigue con un UA propio en vez de reventar: quedarse sin
# corpus porque una biblioteca de cadenas de texto no abrió su JSON sería absurdo. Es la
# única excepción al "fallar cerrado" del proyecto, y lo es porque aquí no hay riesgo de
# escribir datos degradados — solo de no descargarlos.
FALLBACK_USER_AGENT = "to-markdown/0.1 (+extracción normativa AFP Capital)"
try:
    _AGENTS = UserAgent(
        browsers=["Chrome", "Firefox", "Edge", "Safari"],
        os=["Windows", "Mac OS X", "Linux"],
        platforms="desktop",
    )
except Exception as exc:  # noqa: BLE001 — el catálogo es opcional, el crawl no
    print(f"WARNING: fake_useragent failed to load ({exc}); using {FALLBACK_USER_AGENT}")
    _AGENTS = None


# Metadatos HTTP por página (ETag / Last-Modified). Son la señal de cambio más barata y más
# autoritativa que hay: el servidor la publica y honra peticiones condicionales. Van con el
# transporte porque son suyos: quien recorre el árbol no tiene por qué saber que existen.
_HTTP: dict[str, dict[str, dict]] = {}


def load_http(book: Book) -> dict[str, dict]:
    if book.slug not in _HTTP:
        path = book.file("http.json")
        _HTTP[book.slug] = (
            json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        )
    return _HTTP[book.slug]


def save_http(book: Book) -> None:
    book.file("http.json").write_text(
        json.dumps(load_http(book), ensure_ascii=False, indent=2), encoding="utf-8"
    )


def user_agent() -> str:
    """Un User-Agent de escritorio distinto por petición."""
    return _AGENTS.random if _AGENTS else FALLBACK_USER_AGENT


GZIP_ETAG = re.compile(r'-gzip(")?$')


def _headers(response) -> dict[str, str]:
    """Cabeceras en minúsculas, con el ETag normalizado.

    `dict(response.headers)` pierde la insensibilidad a mayúsculas de `HTTPMessage`, y este
    servidor manda `Etag` — ni `ETag` ni `etag`. Sin normalizar, el ETag no se guardaba
    nunca y la revalidación caía en silencio al `Last-Modified`, que es una señal más débil.
    """
    head = {key.lower(): value for key, value in response.getheaders()}
    if "etag" in head:
        head["etag"] = GZIP_ETAG.sub(r"\1", head["etag"])
    return head


# Una conexión HTTPS viva POR HILO, reutilizada entre peticiones.
#
# MEDIDO, y es la diferencia más grande del crawl: `urllib.urlopen` abre una conexión TCP
# nueva —con su handshake TLS— en cada una de las 1.476 páginas. Sobre este sitio eso cuesta
# 917 ms por página; reutilizando la conexión, 310 ms. **3x, sin tocar la concurrencia**:
# siguen siendo `max_workers` conexiones simultáneas, solo que no se tiran y se rehacen.
#
# Que sea por hilo y no un pool compartido es lo que lo mantiene simple y correcto: una
# conexión HTTP/1.1 sirve una petición a la vez, y `ThreadPoolExecutor` ya nos da
# exactamente `max_workers` hilos.

_LOCAL = threading.local()
HOST = urllib.parse.urlparse(BASE).netloc


def url_path(url: str) -> str:
    """Ruta y query de una URL. `http.client` pide la ruta, no la URL entera."""
    target = urllib.parse.urlparse(url)
    return target.path + (f"?{target.query}" if target.query else "")


def connection(reset: bool = False) -> http.client.HTTPSConnection:
    """La conexión de este hilo. Con `reset`, la descarta y abre otra."""
    conn = getattr(_LOCAL, "conn", None)
    if reset or conn is None:
        if conn is not None:
            conn.close()
        conn = http.client.HTTPSConnection(HOST, timeout=TIMEOUT)
        _LOCAL.conn = conn
    return conn


def close_connections() -> None:
    """Cierra la conexión de este hilo. El servidor las cierra solo por timeout, pero
    dejarlas abiertas al terminar mantiene un socket por hilo hasta que muere el proceso."""
    conn = getattr(_LOCAL, "conn", None)
    if conn is not None:
        conn.close()
        _LOCAL.conn = None


def request(
    url: str, headers: dict[str, str] | None = None, method: str = "GET"
) -> tuple[int, dict, bytes | None]:
    """Petición con reintento exponencial. Devuelve (código, cabeceras, cuerpo).

    El sitio responde 502 bajo carga: con `max_workers = 3` no falla, pero el reintento es
    la red de seguridad que hace reproducible el crawl completo. Un 304 no es un error:
    significa "no cambió", que es justo lo que buscamos, y se devuelve con cuerpo `None`.

    Se pide `gzip` explícitamente. El servidor ya lo sirve —`urllib` nunca lo pedía— y
    sobre este corpus son 0,19 MB en la red por cada 0,89 MB de HTML: 4,7x menos
    transferencia, que además es menos trabajo para el sitio del organismo.
    """
    path = url_path(url)
    last: Exception | str | None = None
    hops = 0

    for attempt in range(RETRIES + MAX_REDIRECTS):
        # Tras un fallo se abre conexión nueva: una conexión que dio error queda en estado
        # indefinido y reusarla arrastra el fallo a la petición siguiente.
        conn = connection(reset=attempt > 0)
        try:
            conn.request(method, path, headers={
                "User-Agent": user_agent(),
                "Accept-Encoding": "gzip",
                **(headers or {}),
            })
            response = conn.getresponse()
            # Hay que agotar el cuerpo SIEMPRE, incluso si no se usa: una respuesta a medio
            # leer deja la conexión inservible para la petición siguiente.
            raw = response.read()
            status, head = response.status, _headers(response)
            # `wire_bytes` es lo que de verdad viajó (comprimido) y `bytes` lo que se
            # entrega ya descomprimido. Los dos juntos son los que dicen cuánto ahorra el
            # gzip; uno solo no lo puede decir.
            bump("requests")
            bump("wire_bytes", len(raw))

            if status == 304:
                return 304, head, None
            if status in (301, 302, 303, 307, 308) and head.get("location"):
                if hops >= MAX_REDIRECTS:
                    raise RuntimeError(f"too many redirects for {url}")
                hops += 1
                path = url_path(urllib.parse.urljoin(f"https://{HOST}{path}", head["location"]))
                continue
            if status >= 500:
                last = f"HTTP {status}"
                time.sleep(1.5 * (attempt + 1))
                continue
            if status >= 400:
                raise RuntimeError(f"HTTP {status} for {url}")
            # Una respuesta cortada a la mitad es el fallo que más caro sale: se cachearía
            # como HTML válido y el parser extraería un documento truncado sin que nada
            # avise. Se compara ANTES de descomprimir, que es lo que mide Content-Length.
            declared = head.get("content-length")
            if method != "HEAD" and declared and len(raw) != int(declared):
                last = f"truncated: {len(raw)} of {declared} bytes"
                time.sleep(1.5 * (attempt + 1))
                continue
            if head.get("content-encoding") == "gzip" and raw:
                raw = gzip.decompress(raw)
            bump("bytes", len(raw))
            return status, head, raw
        except (http.client.HTTPException, TimeoutError, OSError) as exc:
            # Incluye `RemoteDisconnected`: el servidor cierra las conexiones ociosas y la
            # primera petición después de eso falla. Es normal, y se resuelve reabriendo.
            last = exc
            time.sleep(1.5 * (attempt + 1))
    close_connections()
    raise RuntimeError(f"could not download {url} ({last})")


def get_bytes(url: str) -> bytes:
    body = request(url)[2]
    if body is None:
        raise RuntimeError(f"empty response body for {url}")
    return body


