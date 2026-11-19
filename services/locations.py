"""
Servicio y catálogo normalizado de ubicaciones (Ciudades / Comunas y Regiones).

Permite:
- Búsqueda y autocompletado rápido de comunas y ciudades normalizadas.
- Filtrado consistente entre la creación de solicitudes y los filtros de vendedores.
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path


def _load_locations() -> list[dict[str, str]]:
    """Carga las comunas y regiones desde el recurso local del proyecto."""
    data_path = Path(__file__).resolve().parents[1] / "data" / "comunas.json"
    with data_path.open(encoding="utf-8") as file:
        data = json.load(file)
    return [
        {"comuna": item["name"], "region": item["region_name"]}
        for item in data["data"]
    ]


CHILE_LOCATIONS: list[dict[str, str]] = _load_locations()


def _normalize_text(text: str) -> str:
    """Elimina tildes y convierte a minúsculas para búsqueda tolerante."""
    norm = unicodedata.normalize("NFD", text or "")
    return "".join(c for c in norm if unicodedata.category(c) != "Mn").lower().strip()


# (comuna normalizada, región normalizada, "Comuna (Región)"): se normaliza una vez, no en cada tecla.
_INDEX = [
    (_normalize_text(item["comuna"]), _normalize_text(item["region"]), f"{item['comuna']} ({item['region']})")
    for item in CHILE_LOCATIONS
]
_DISPLAY_BY_NORM = {norm: display for c_norm, _, display in _INDEX for norm in (c_norm, _normalize_text(display))}


def search_locations(query: str, limit: int = 15) -> list[str]:
    """Comunas que empiezan con la consulta y después las que la contienen (en la comuna o la región)."""
    q = _normalize_text(query)
    first = [d for c, _, d in _INDEX if c.startswith(q)]
    rest = [d for c, r, d in _INDEX if not c.startswith(q) and (q in c or q in r)]
    return (first + rest)[:limit]


def known_location(text: str) -> str:
    """"Comuna (Región)" si el texto es una comuna del catálogo; si no, ""."""
    return _DISPLAY_BY_NORM.get(_normalize_text(text), "")


def normalize_location_name(text: str) -> str:
    """Nombre estándar "Comuna (Región)" si coincide con una comuna conocida; si no, el texto limpio."""
    raw = (text or "").strip()
    return known_location(raw) or raw


_REGION_BY_COMUNA: dict[str, str] = {
    _normalize_text(item["comuna"]): item["region"] for item in CHILE_LOCATIONS
}


def _comuna_key(location_text: str) -> str:
    """Extrae la comuna de 'Comuna (Región)' o de un texto plano ya normalizado."""
    return _normalize_text((location_text or "").split(" (")[0])


def proximity_label(seller_location: str, request_location: str) -> str:
    """
    Cercanía aproximada entre la comuna del vendedor y la de la solicitud,
    usando solo el catálogo de comunas/regiones (sin coordenadas exactas,
    para no exponer la ubicación real de nadie).
    """
    seller_key = _comuna_key(seller_location)
    request_key = _comuna_key(request_location)
    if not seller_key or not request_key:
        return ""
    if seller_key == request_key:
        return "Misma comuna"
    seller_region = _REGION_BY_COMUNA.get(seller_key)
    request_region = _REGION_BY_COMUNA.get(request_key)
    if seller_region and seller_region == request_region:
        return "Misma región"
    if request_region:
        return f"Otra región ({request_region})"
    return ""
