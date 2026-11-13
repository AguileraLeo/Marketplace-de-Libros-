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
    data_path = Path(__file__).resolve().with_name("comunas.json")
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


def format_location_display(item: dict[str, str]) -> str:
    """Formatea la ubicación para mostrar: 'Comuna (Región)' o solo 'Comuna'."""
    comuna, region = item["comuna"], item["region"]
    return f"{comuna} ({region})"


def search_locations(query: str, limit: int = 15) -> list[str]:
    """
    Busca comunas y ciudades que coincidan con la consulta.
    Retorna nombres normalizados con su región.
    """
    q = _normalize_text(query)
    if not q:
        return [format_location_display(item) for item in CHILE_LOCATIONS[:limit]]

    matches: list[str] = []
    # 1. Coincidencia exacta o inicio de comuna
    for item in CHILE_LOCATIONS:
        c_norm = _normalize_text(item["comuna"])
        if c_norm.startswith(q):
            matches.append(format_location_display(item))
            if len(matches) >= limit:
                return matches

    # 2. Substring en comuna o región
    for item in CHILE_LOCATIONS:
        c_norm = _normalize_text(item["comuna"])
        r_norm = _normalize_text(item["region"])
        display = format_location_display(item)
        if display not in matches and (q in c_norm or q in r_norm):
            matches.append(display)
            if len(matches) >= limit:
                return matches

    return matches


def normalize_location_name(text: str) -> str:
    """
    Normaliza el nombre de ubicación ingresado. Si coincide con una comuna conocida,
    devuelve su nombre estándar; de lo contrario limpia el texto.
    """
    raw = (text or "").strip()
    if not raw:
        return ""
    q = _normalize_text(raw)
    for item in CHILE_LOCATIONS:
        c_norm = _normalize_text(item["comuna"])
        disp_norm = _normalize_text(format_location_display(item))
        if q == c_norm or q == disp_norm:
            return format_location_display(item)
    return raw


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
