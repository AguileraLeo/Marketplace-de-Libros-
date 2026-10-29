"""
Configuración remota: la app arranca con DEFAULTS y, en segundo plano, descarga
remote_config.json desde GitHub. Si llega, reemplaza los valores; si no hay red
o el JSON viene mal, se quedan los DEFAULTS (fallback) y la app no se bloquea.
"""

import json
import time

import certifi
from kivy.network.urlrequest import UrlRequest

URL = "https://raw.githubusercontent.com/AguileraLeo/Marketplace-de-Libros-/main/remote_config.json"

DEFAULTS = {
    "banner": "Modo sin conexión: mostrando la configuración local.",
}


def fetch(on_update) -> None:
    """Pide la config sin bloquear la UI; llama on_update(dict) solo si llega una config válida."""

    def _ok(_req, result):
        if isinstance(result, (str, bytes)):  # GitHub raw responde text/plain
            try:
                result = json.loads(result)
            except ValueError:
                return
        if not isinstance(result, dict):
            return
        # Solo se aceptan claves conocidas y del mismo tipo que el default.
        clean = {k: v for k, v in result.items() if k in DEFAULTS and type(v) is type(DEFAULTS[k])}
        if clean:
            on_update(clean)

    UrlRequest(
        f"{URL}?t={int(time.time())}",  # evita respuestas cacheadas
        on_success=_ok,
        timeout=6,
        ca_file=certifi.where(),  # Android no trae los certificados raíz para HTTPS
    )
