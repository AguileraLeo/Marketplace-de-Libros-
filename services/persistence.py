"""
Persistencia en JSON: guarda el Store completo en un archivo y lo recupera al abrir la app.

- save_store(): serializa cada entidad (dataclass) a diccionario con asdict().
- load_store(): reconstruye los objetos; si el archivo no existe devuelve None
  y la app arranca con los datos de demo.
"""

from __future__ import annotations

import itertools
import json
import os
from dataclasses import asdict
from datetime import datetime
from typing import Optional

from store import ActivityEntry, Book, BookRequest, Offer, SellerContact, Store, User

# tabla del Store -> clase de sus objetos
TABLES = {
    "users": User,
    "books": Book,
    "requests": BookRequest,
    "offers": Offer,
    "contacts": SellerContact,
}
DATE_FIELDS = ("created_at", "updated_at", "at")


def _to_json(obj):
    """json.dump no sabe guardar datetime: lo pasamos a texto ISO."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"No serializable: {type(obj)}")


def _parse_dates(data: dict) -> dict:
    for key in DATE_FIELDS:
        if isinstance(data.get(key), str):
            data[key] = datetime.fromisoformat(data[key])
    return data


def save_store(store: Store, path: str) -> None:
    data = {name: [asdict(o) for o in getattr(store, name).values()] for name in TABLES}
    data["activity"] = [asdict(a) for a in store.activity]
    # Se escribe a un .tmp y luego se reemplaza: si la app se cierra a mitad, el JSON anterior queda intacto.
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=_to_json)
    os.replace(tmp, path)


def load_store(path: str) -> Optional[Store]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return None  # primera vez que se abre la app
    except (json.JSONDecodeError, UnicodeDecodeError):
        os.replace(path, path + ".corrupto")  # se respalda, no se pisa
        return None

    store = Store()
    try:
        for name, cls in TABLES.items():
            key = "seller_id" if name == "contacts" else "id"
            table = getattr(store, name)
            for item in data.get(name, []):
                obj = cls(**_parse_dates(item))
                table[getattr(obj, key)] = obj
        store.activity = [ActivityEntry(**_parse_dates(a)) for a in data.get("activity", [])]
    except (TypeError, ValueError):
        os.replace(path, path + ".corrupto")
        return None

    # Los contadores de id siguen desde el mayor guardado, para no repetir ids.
    for kind, table in (("user", store.users), ("book", store.books),
                        ("request", store.requests), ("offer", store.offers)):
        store._ids[kind] = itertools.count(max(table, default=0) + 1)
    return store
