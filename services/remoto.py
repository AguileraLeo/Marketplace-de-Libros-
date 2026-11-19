"""Modelo remoto (SPEC-005): la misma interfaz que models.store.Store, pero cada llamada va al servidor.

Los controladores y las vistas no cambian: usan app.store igual que antes. El actor no viaja:
el servidor lo saca del token, así nadie puede actuar como otro usuario.
"""
import inspect
import json
import os
import ssl
import urllib.error
import urllib.request
from datetime import datetime

import certifi

from models.store import (
    ActivityEntry, Book, BookRequest, DomainError, InvalidTransition, NotFound, Offer, PermissionDenied,
    SellerContact, Store, User, ValidationError,
)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(RAIZ, "data", "servidor.json")
CON_ACTOR = (
    "reader_requests", "offers_for_request", "get_request", "cancel_request", "cancel_deal", "set_user_status",
    "seller_offers", "seller_contact", "seller_active_offer", "open_requests", "offer_contact", "get_offer",
    "create_request", "create_offer", "accept_offer", "confirm_deal", "cancel_offer",
    "admin_users", "admin_stats", "admin_requests", "admin_offers", "admin_activity",
)
SIN_ACTOR = ("user", "active_offer_count", "upsert_book")
ERRORES = {"ValidationError": ValidationError, "PermissionDenied": PermissionDenied, "NotFound": NotFound,
           "InvalidTransition": InvalidTransition}
TIPOS = {c.__name__: c for c in (User, Book, BookRequest, Offer, SellerContact, ActivityEntry)}
FECHAS = {"created_at", "updated_at", "at"}


class SinConexion(DomainError):
    """El servidor no respondió. Es un DomainError: app.safe() lo muestra como cualquier mensaje."""


class SesionVencida(PermissionDenied):
    """El token venció o el servidor se reinició: la app vuelve al login."""


def servidor_configurado():
    """URL del servidor: variable BOOKWHO_SERVIDOR ("local" lo desactiva) o data/servidor.json."""
    url = os.environ.get("BOOKWHO_SERVIDOR", "").strip()
    if url:
        return None if url == "local" else url
    try:
        with open(CONFIG, encoding="utf-8") as f:
            return str(json.load(f).get("url", "")).strip() or None
    except (OSError, ValueError, AttributeError):
        return None


def desde_json(valor):
    """Diccionarios con "_tipo" → las mismas dataclasses del modelo."""
    if isinstance(valor, list):
        return [desde_json(v) for v in valor]
    if not isinstance(valor, dict):
        return valor
    tipo = valor.get("_tipo")
    datos = {k: (datetime.fromisoformat(v) if k in FECHAS and isinstance(v, str) else desde_json(v))
             for k, v in valor.items() if k != "_tipo"}
    if tipo == "User":
        datos.setdefault("password", "")  # el servidor nunca la envía
    return TIPOS[tipo](**datos) if tipo in TIPOS else datos


class _Mapa:
    """store.requests / store.offers / store.users: los controladores los leen como diccionarios."""

    def __init__(self, obtener):
        self._obtener = obtener

    def get(self, clave, defecto=None):
        try:
            return self._obtener(clave)
        except (NotFound, PermissionDenied):
            return defecto

    def __getitem__(self, clave):
        valor = self.get(clave)
        if valor is None:
            raise KeyError(clave)
        return valor


class RemoteStore:
    def __init__(self, url, timeout=10):
        self.url, self.timeout, self.token = url.rstrip("/"), timeout, None
        self._ssl = ssl.create_default_context(cafile=certifi.where())
        self._libros = {}  # los libros no cambian: se piden una vez
        self.requests = _Mapa(lambda rid: self._rpc("get_request", rid))
        self.offers = _Mapa(lambda oid: self._rpc("get_offer", oid))
        self.users = _Mapa(lambda uid: self.user(uid))

    # ------------------------------------------------------------ transporte
    def _http(self, metodo, ruta, cuerpo=None, timeout=None):
        cabeceras = {"Content-Type": "application/json", "User-Agent": "BookWho-App/1.0"}
        if self.token:
            cabeceras["Authorization"] = f"Bearer {self.token}"
        datos = None if cuerpo is None else json.dumps(cuerpo).encode("utf-8")
        pedido = urllib.request.Request(self.url + ruta, data=datos, method=metodo, headers=cabeceras)
        try:
            with urllib.request.urlopen(pedido, timeout=timeout or self.timeout, context=self._ssl) as r:
                texto = r.read()
                return json.loads(texto) if texto else None
        except urllib.error.HTTPError as exc:
            try:
                info = json.loads(exc.read())
            except ValueError:
                info = {}
            if exc.code == 401:
                raise SesionVencida("Tu sesión venció: vuelve a iniciar sesión.") from None
            raise ERRORES.get(info.get("tipo"), DomainError)(info.get("error") or f"Error del servidor ({exc.code}).") from None
        except (urllib.error.URLError, OSError, ValueError):  # sin red, DNS, tiempo agotado o respuesta rota
            raise SinConexion("Sin conexión con el servidor. Revisa internet e inténtalo de nuevo.") from None

    def _rpc(self, metodo, *args):
        return desde_json(self._http("POST", "/api/rpc", {"metodo": metodo, "args": list(args)})["resultado"])

    def disponible(self):
        try:
            return bool(self._http("GET", "/api/salud")["ok"])
        except (DomainError, TypeError, KeyError):
            return False

    # ------------------------------------------------------------ sesión
    def _entrar(self, ruta, cuerpo):
        respuesta = self._http("POST", ruta, cuerpo)
        self.token = respuesta["token"]
        return desde_json(respuesta["usuario"])

    def authenticate(self, email, password):
        return self._entrar("/api/sesion", {"correo": email, "clave": password})

    def cerrar_sesion(self):
        """Revoca el token en el servidor si hay red, y lo olvida siempre."""
        if self.token:
            try:
                self._http("DELETE", "/api/sesion", timeout=3)  # corto: salir no debe trabar la app
            except DomainError:
                pass  # sin red: el token vence solo (12 h)
        self.token = None

    def register(self, name, email, password, role, location=""):
        return self._entrar("/api/registro", {"nombre": name, "correo": email, "clave": password,
                                               "rol": role, "comuna": location})

    # ------------------------------------------------------------ casos especiales
    def book(self, book_id):
        if book_id not in self._libros:
            self._libros[book_id] = self._rpc("book", book_id)
        return self._libros[book_id]

    def export_activity_log(self, _actor, file_path="registro_actividad.txt"):
        texto = self._rpc("export_activity_log")  # el servidor devuelve el texto; el archivo queda en el teléfono
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(texto)
        return file_path


def _posicionales(nombre, args, kwargs):
    """Los argumentos en el orden del método real (admin_activity se llama con limit= y text=)."""
    enlazados = inspect.signature(getattr(Store, nombre)).bind(None, *args, **kwargs)
    enlazados.apply_defaults()
    return list(enlazados.arguments.values())[1:]  # sin self


def _con_actor(nombre):
    def metodo(self, *args, **kwargs):
        return self._rpc(nombre, *_posicionales(nombre, args, kwargs)[1:])  # sin el actor: lo pone el servidor
    metodo.__name__ = nombre
    return metodo


def _sin_actor(nombre):
    def metodo(self, *args, **kwargs):
        return self._rpc(nombre, *_posicionales(nombre, args, kwargs))
    metodo.__name__ = nombre
    return metodo


for _nombre in CON_ACTOR:
    setattr(RemoteStore, _nombre, _con_actor(_nombre))
for _nombre in SIN_ACTOR:
    setattr(RemoteStore, _nombre, _sin_actor(_nombre))
