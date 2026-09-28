"""
Búsqueda de libros en API externa con respaldo:
Google Books -> Open Library -> catálogo local de ejemplo.

- search_books() es bloqueante: la UI la ejecuta en un hilo.
- Los datos externos se normalizan/validan antes de entregarse (AGENTS.md §18.13).
- Si no hay conexión o la API falla, se usa un catálogo de ejemplo para que
  el demo funcione offline.
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import urllib.parse
import urllib.request
from typing import Callable, Optional

GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
OPEN_LIBRARY_URL = "https://openlibrary.org/search.json"
# Opcional: sin clave, Google Books limita las peticiones (HTTP 429).
GOOGLE_BOOKS_API_KEY = os.environ.get("GOOGLE_BOOKS_API_KEY", "")
TIMEOUT_SECONDS = 6
MAX_RESULTS = 15

SEARCH_MODES = {
    "titulo": "intitle:",
    "autor": "inauthor:",
    "isbn": "isbn:",
}

# Directorio de caché local persistente para portadas
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache", "covers")
os.makedirs(CACHE_DIR, exist_ok=True)


def get_cover_cache_path(url: str) -> Optional[str]:
    """Retorna la ruta local en disco para la URL dada si es válida."""
    if not url or not url.strip():
        return None
    url_hash = hashlib.md5(url.strip().encode("utf-8")).hexdigest()
    ext = ".png" if ".png" in url.lower() else ".jpg"
    return os.path.join(CACHE_DIR, f"{url_hash}{ext}")


def is_cover_cached(url: str) -> bool:
    """Indica si la portada ya está descargada localmente en disco."""
    path = get_cover_cache_path(url)
    return bool(path and os.path.exists(path) and os.path.getsize(path) > 100)


def download_and_cache_cover(
    url: str,
    on_complete: Optional[Callable[[str, str], None]] = None,
) -> Optional[str]:
    """
    Obtiene la ruta local de la portada. Si ya existe, la retorna de inmediato.
    Si no, inicia la descarga en segundo plano y llama a on_complete(url, local_path).
    """
    if not url or not url.startswith(("http://", "https://")):
        return None
    cache_path = get_cover_cache_path(url)
    if not cache_path:
        return None

    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 100:
        if on_complete:
            on_complete(url, cache_path)
        return cache_path

    def _worker():
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
                data = resp.read()
                if data and len(data) > 100:
                    with open(cache_path, "wb") as f:
                        f.write(data)
                    if on_complete:
                        try:
                            from kivy.clock import Clock
                            Clock.schedule_once(lambda *_: on_complete(url, cache_path))
                        except Exception:
                            on_complete(url, cache_path)
        except Exception:
            pass

    threading.Thread(target=_worker, daemon=True).start()
    return cache_path if os.path.exists(cache_path) else None


def prefetch_covers(books: list[dict]) -> None:
    """Inicia la descarga en caché en segundo plano para una lista de libros."""
    for b in books:
        cover = b.get("cover_url")
        if cover:
            download_and_cache_cover(cover)


def _ol_cover(isbn: str) -> str:
    return f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg?default=false"


# Catálogo de respaldo (mismo formato que devuelve search_books).
LOCAL_CATALOG = [
    {
        "provider": "demo", "external_id": "demo-hobbit", "isbn": "9788445000663",
        "title": "El Hobbit", "authors": ["J. R. R. Tolkien"],
        "publisher": "Minotauro", "published_date": "1982",
    },
    {
        "provider": "demo", "external_id": "demo-cien-anos", "isbn": "9780307474728",
        "title": "Cien años de soledad", "authors": ["Gabriel García Márquez"],
        "publisher": "Vintage Español", "published_date": "2009",
    },
    {
        "provider": "demo", "external_id": "demo-1984", "isbn": "9788499890944",
        "title": "1984", "authors": ["George Orwell"],
        "publisher": "Debolsillo", "published_date": "2013",
    },
    {
        "provider": "demo", "external_id": "demo-quijote", "isbn": "9788420412146",
        "title": "Don Quijote de la Mancha", "authors": ["Miguel de Cervantes"],
        "publisher": "Alfaguara", "published_date": "2004",
    },
    {
        "provider": "demo", "external_id": "demo-principito", "isbn": "9788498381498",
        "title": "El principito", "authors": ["Antoine de Saint-Exupéry"],
        "publisher": "Salamandra", "published_date": "2008",
    },
    {
        "provider": "demo", "external_id": "demo-rayuela", "isbn": "9788437604572",
        "title": "Rayuela", "authors": ["Julio Cortázar"],
        "publisher": "Cátedra", "published_date": "1984",
    },
    {
        "provider": "demo", "external_id": "demo-casa-espiritus", "isbn": "9788401352836",
        "title": "La casa de los espíritus", "authors": ["Isabel Allende"],
        "publisher": "Plaza & Janés", "published_date": "1982",
    },
    {
        "provider": "demo", "external_id": "demo-sapiens", "isbn": "9788499926223",
        "title": "Sapiens. De animales a dioses", "authors": ["Yuval Noah Harari"],
        "publisher": "Debate", "published_date": "2014",
    },
    {
        "provider": "demo", "external_id": "demo-ficciones", "isbn": "9788499089508",
        "title": "Ficciones", "authors": ["Jorge Luis Borges"],
        "publisher": "Debolsillo", "published_date": "2011",
    },
    {
        "provider": "demo", "external_id": "demo-pedro-paramo", "isbn": "9788437604183",
        "title": "Pedro Páramo", "authors": ["Juan Rulfo"],
        "publisher": "Cátedra", "published_date": "1983",
    },
]
for _book in LOCAL_CATALOG:
    _book["cover_url"] = _ol_cover(_book["isbn"])


def catalog_lookup(external_id: str) -> dict:
    return next(b for b in LOCAL_CATALOG if b["external_id"] == external_id)


def _search_local(query: str, mode: str) -> list[dict]:
    q = query.lower().replace("-", "").strip()
    results = []
    for book in LOCAL_CATALOG:
        if mode == "isbn":
            hit = q in book["isbn"]
        elif mode == "autor":
            hit = any(q in a.lower() for a in book["authors"])
        else:
            hit = q in book["title"].lower()
        if hit:
            results.append(dict(book))
    return results


def _normalize_google_item(item: dict) -> dict | None:
    info = item.get("volumeInfo") or {}
    title = str(info.get("title") or "").strip()
    external_id = str(item.get("id") or "").strip()
    if not title or not external_id:
        return None
    if info.get("subtitle"):
        title = f"{title}. {str(info['subtitle']).strip()}"

    isbn = ""
    for ident in info.get("industryIdentifiers") or []:
        if ident.get("type") == "ISBN_13":
            isbn = ident.get("identifier", "")
            break
        if ident.get("type") == "ISBN_10" and not isbn:
            isbn = ident.get("identifier", "")

    images = info.get("imageLinks") or {}
    cover = images.get("thumbnail") or images.get("smallThumbnail") or ""
    cover = cover.replace("http://", "https://", 1)
    if not cover and isbn:
        cover = _ol_cover(isbn)

    authors = info.get("authors") or []
    return {
        "provider": "google_books",
        "external_id": external_id[:80],
        "isbn": str(isbn)[:20],
        "title": title[:200],
        "authors": [str(a)[:100] for a in authors if a][:5],
        "cover_url": cover[:500],
        "publisher": str(info.get("publisher") or "")[:120],
        "published_date": str(info.get("publishedDate") or "")[:20],
    }


def _get_json(url: str, params: dict) -> dict:
    req = urllib.request.Request(
        f"{url}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": "demolibros-mvp/0.1"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _search_google(query: str, mode: str) -> list[dict]:
    q = query.replace("-", "") if mode == "isbn" else query
    params = {
        "q": SEARCH_MODES.get(mode, "") + q,
        "maxResults": MAX_RESULTS,
        "printType": "books",
    }
    if GOOGLE_BOOKS_API_KEY:
        params["key"] = GOOGLE_BOOKS_API_KEY
    payload = _get_json(GOOGLE_BOOKS_URL, params)
    results = []
    for item in payload.get("items") or []:
        book = _normalize_google_item(item)
        if book:
            results.append(book)
    return results


def _normalize_open_library_doc(doc: dict) -> dict | None:
    title = str(doc.get("title") or "").strip()
    key = str(doc.get("key") or "").strip()  # ej: /works/OL45804W
    if not title or not key:
        return None
    isbns = [str(i) for i in doc.get("isbn") or []]
    isbn = next((i for i in isbns if len(i) == 13), isbns[0] if isbns else "")
    cover = ""
    if doc.get("cover_i"):
        cover = f"https://covers.openlibrary.org/b/id/{int(doc['cover_i'])}-M.jpg"
    publishers = doc.get("publisher") or []
    year = doc.get("first_publish_year")
    return {
        "provider": "open_library",
        "external_id": key[:80],
        "isbn": isbn[:20],
        "title": title[:200],
        "authors": [str(a)[:100] for a in doc.get("author_name") or [] if a][:5],
        "cover_url": cover,
        "publisher": str(publishers[0])[:120] if publishers else "",
        "published_date": str(year) if year else "",
    }


def _search_open_library(query: str, mode: str) -> list[dict]:
    field = {"titulo": "title", "autor": "author", "isbn": "isbn"}.get(mode, "q")
    q = query.replace("-", "") if mode == "isbn" else query
    payload = _get_json(OPEN_LIBRARY_URL, {
        field: q,
        "limit": MAX_RESULTS,
        "fields": "key,title,author_name,isbn,publisher,first_publish_year,cover_i",
    })
    results = []
    for doc in payload.get("docs") or []:
        book = _normalize_open_library_doc(doc)
        if book:
            if mode == "isbn" and q in (doc.get("isbn") or []):
                book["isbn"] = q  # la obra agrupa ediciones: conservar la buscada
            results.append(book)
    return results


PROVIDERS = (
    ("google_books", _search_google),
    ("open_library", _search_open_library),
)


def search_books(query: str, mode: str = "titulo") -> tuple[list[dict], str]:
    """Devuelve (resultados, origen): 'google_books', 'open_library' o 'local'."""
    query = (query or "").strip()
    if len(query) < 2:
        raise ValueError("Escribe al menos 2 caracteres para buscar.")
    for name, provider in PROVIDERS:
        try:
            results = provider(query, mode)
            if results:
                prefetch_covers(results)
                return results, name
        except Exception:
            continue
    local_res = _search_local(query, mode)
    prefetch_covers(local_res)
    return local_res, "local"
