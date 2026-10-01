"""
Servicio y catálogo normalizado de ubicaciones (Ciudades / Comunas y Regiones).

Permite:
- Búsqueda y autocompletado rápido de comunas y ciudades normalizadas.
- Filtrado consistente entre la creación de solicitudes y los filtros de vendedores.
"""

from __future__ import annotations

import unicodedata
from typing import Optional

# Catálogo oficial normalizado de regiones y comunas
CHILE_LOCATIONS: list[dict[str, str]] = [
    # Arica y Parinacota
    {"comuna": "Arica", "region": "Arica y Parinacota"},
    {"comuna": "Camarones", "region": "Arica y Parinacota"},
    {"comuna": "Putre", "region": "Arica y Parinacota"},
    {"comuna": "General Lagos", "region": "Arica y Parinacota"},
    # Tarapacá
    {"comuna": "Iquique", "region": "Tarapacá"},
    {"comuna": "Alto Hospicio", "region": "Tarapacá"},
    {"comuna": "Pozo Almonte", "region": "Tarapacá"},
    {"comuna": "Pica", "region": "Tarapacá"},
    # Antofagasta
    {"comuna": "Antofagasta", "region": "Antofagasta"},
    {"comuna": "Calama", "region": "Antofagasta"},
    {"comuna": "Tocopilla", "region": "Antofagasta"},
    {"comuna": "Mejillones", "region": "Antofagasta"},
    {"comuna": "San Pedro de Atacama", "region": "Antofagasta"},
    # Atacama
    {"comuna": "Copiapó", "region": "Atacama"},
    {"comuna": "Vallenar", "region": "Atacama"},
    {"comuna": "Caldera", "region": "Atacama"},
    {"comuna": "Chañaral", "region": "Atacama"},
    # Coquimbo
    {"comuna": "La Serena", "region": "Coquimbo"},
    {"comuna": "Coquimbo", "region": "Coquimbo"},
    {"comuna": "Ovalle", "region": "Coquimbo"},
    {"comuna": "Illapel", "region": "Coquimbo"},
    {"comuna": "Vicuña", "region": "Coquimbo"},
    {"comuna": "Salamanca", "region": "Coquimbo"},
    # Valparaíso
    {"comuna": "Valparaíso", "region": "Valparaíso"},
    {"comuna": "Viña del Mar", "region": "Valparaíso"},
    {"comuna": "Quilpué", "region": "Valparaíso"},
    {"comuna": "Villa Alemana", "region": "Valparaíso"},
    {"comuna": "Concón", "region": "Valparaíso"},
    {"comuna": "Quillota", "region": "Valparaíso"},
    {"comuna": "San Antonio", "region": "Valparaíso"},
    {"comuna": "Los Andes", "region": "Valparaíso"},
    {"comuna": "San Felipe", "region": "Valparaíso"},
    # Región Metropolitana de Santiago
    {"comuna": "Santiago", "region": "Metropolitana"},
    {"comuna": "Providencia", "region": "Metropolitana"},
    {"comuna": "Las Condes", "region": "Metropolitana"},
    {"comuna": "Ñuñoa", "region": "Metropolitana"},
    {"comuna": "La Florida", "region": "Metropolitana"},
    {"comuna": "Maipú", "region": "Metropolitana"},
    {"comuna": "Puente Alto", "region": "Metropolitana"},
    {"comuna": "San Miguel", "region": "Metropolitana"},
    {"comuna": "Vitacura", "region": "Metropolitana"},
    {"comuna": "Lo Barnechea", "region": "Metropolitana"},
    {"comuna": "La Reina", "region": "Metropolitana"},
    {"comuna": "Macul", "region": "Metropolitana"},
    {"comuna": "Peñalolén", "region": "Metropolitana"},
    {"comuna": "Estación Central", "region": "Metropolitana"},
    {"comuna": "Recoleta", "region": "Metropolitana"},
    {"comuna": "Independencia", "region": "Metropolitana"},
    {"comuna": "Quinta Normal", "region": "Metropolitana"},
    {"comuna": "San Bernardo", "region": "Metropolitana"},
    {"comuna": "Colina", "region": "Metropolitana"},
    {"comuna": "Melipilla", "region": "Metropolitana"},
    {"comuna": "Talagante", "region": "Metropolitana"},
    # O'Higgins
    {"comuna": "Rancagua", "region": "O'Higgins"},
    {"comuna": "Machalí", "region": "O'Higgins"},
    {"comuna": "Rengo", "region": "O'Higgins"},
    {"comuna": "San Fernando", "region": "O'Higgins"},
    {"comuna": "Santa Cruz", "region": "O'Higgins"},
    {"comuna": "Pichilemu", "region": "O'Higgins"},
    # Maule
    {"comuna": "Talca", "region": "Maule"},
    {"comuna": "Curicó", "region": "Maule"},
    {"comuna": "Linares", "region": "Maule"},
    {"comuna": "Constitución", "region": "Maule"},
    {"comuna": "Cauquenes", "region": "Maule"},
    {"comuna": "Molina", "region": "Maule"},
    {"comuna": "San Javier", "region": "Maule"},
    # Ñuble
    {"comuna": "Chillán", "region": "Ñuble"},
    {"comuna": "Chillán Viejo", "region": "Ñuble"},
    {"comuna": "San Carlos", "region": "Ñuble"},
    {"comuna": "Bulnes", "region": "Ñuble"},
    {"comuna": "Yungay", "region": "Ñuble"},
    # Biobío
    {"comuna": "Concepción", "region": "Biobío"},
    {"comuna": "San Pedro de la Paz", "region": "Biobío"},
    {"comuna": "Talcahuano", "region": "Biobío"},
    {"comuna": "Chiguayante", "region": "Biobío"},
    {"comuna": "Hualpén", "region": "Biobío"},
    {"comuna": "Coronel", "region": "Biobío"},
    {"comuna": "Lota", "region": "Biobío"},
    {"comuna": "Tomé", "region": "Biobío"},
    {"comuna": "Penco", "region": "Biobío"},
    {"comuna": "Los Ángeles", "region": "Biobío"},
    # La Araucanía
    {"comuna": "Temuco", "region": "La Araucanía"},
    {"comuna": "Padre Las Casas", "region": "La Araucanía"},
    {"comuna": "Villarrica", "region": "La Araucanía"},
    {"comuna": "Pucón", "region": "La Araucanía"},
    {"comuna": "Angol", "region": "La Araucanía"},
    {"comuna": "Victoria", "region": "La Araucanía"},
    # Los Ríos
    {"comuna": "Valdivia", "region": "Los Ríos"},
    {"comuna": "La Unión", "region": "Los Ríos"},
    {"comuna": "Río Bueno", "region": "Los Ríos"},
    {"comuna": "Panguipulli", "region": "Los Ríos"},
    # Los Lagos
    {"comuna": "Puerto Montt", "region": "Los Lagos"},
    {"comuna": "Puerto Varas", "region": "Los Lagos"},
    {"comuna": "Osorno", "region": "Los Lagos"},
    {"comuna": "Castro", "region": "Los Lagos"},
    {"comuna": "Ancud", "region": "Los Lagos"},
    {"comuna": "Frutillar", "region": "Los Lagos"},
    # Aysén
    {"comuna": "Coyhaique", "region": "Aysén"},
    {"comuna": "Puerto Aysén", "region": "Aysén"},
    {"comuna": "Chile Chico", "region": "Aysén"},
    # Magallanes
    {"comuna": "Punta Arenas", "region": "Magallanes"},
    {"comuna": "Puerto Natales", "region": "Magallanes"},
    {"comuna": "Porvenir", "region": "Magallanes"},
]

POPULAR_LOCATIONS: list[str] = [
    "Concepción",
    "Santiago",
    "Valparaíso",
    "Viña del Mar",
    "La Serena",
    "Temuco",
    "Antofagasta",
    "Puerto Montt",
]


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
