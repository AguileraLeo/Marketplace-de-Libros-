"""
Capa de dominio del MVP: entidades, máquinas de estado, permisos y un
repositorio en memoria (sin base de datos).

Toda regla de negocio y de autorización vive aquí, NO en la interfaz:
la UI solo oculta/deshabilita acciones, pero cada método del Store vuelve
a validar el rol, la propiedad del recurso y el estado (AGENTS.md §18.7).

Los datos viven únicamente mientras la app está abierta.
"""

from __future__ import annotations

import itertools
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Iterable, Optional


# --------------------------------------------------------------------------
# Constantes de dominio
# --------------------------------------------------------------------------
class Role:
    READER = "lector"
    SELLER = "vendedor"
    ADMIN = "admin"

    PUBLIC = (READER, SELLER)  # roles permitidos en registro público
    LABELS = {READER: "Lector", SELLER: "Vendedor", ADMIN: "Administrador"}


class UserStatus:
    ACTIVE = "ACTIVO"
    SUSPENDED = "SUSPENDIDO"


class RequestStatus:
    DRAFT = "BORRADOR"
    PUBLISHED = "PUBLICADA"
    WITH_OFFERS = "CON_OFERTAS"
    IN_DEAL = "EN_COORDINACION"
    RESOLVED = "RESUELTA"
    CANCELLED = "CANCELADA"

    OPEN = (PUBLISHED, WITH_OFFERS)  # visibles para recibir nuevas ofertas
    ACTIVE = (PUBLISHED, WITH_OFFERS, IN_DEAL)
    TRANSITIONS = {
        DRAFT: {PUBLISHED},
        PUBLISHED: {WITH_OFFERS, CANCELLED},
        WITH_OFFERS: {IN_DEAL, RESOLVED, CANCELLED},
        IN_DEAL: {RESOLVED, WITH_OFFERS, PUBLISHED, CANCELLED},
        RESOLVED: set(),
        CANCELLED: set(),
    }
    LABELS = {
        DRAFT: "Borrador",
        PUBLISHED: "Publicada",
        WITH_OFFERS: "Con ofertas",
        IN_DEAL: "En coordinación",
        RESOLVED: "Resuelta",
        CANCELLED: "Cancelada",
    }


class OfferStatus:
    PUBLISHED = "PUBLICADA"
    IN_DEAL = "POR_CONCRETAR"
    ON_HOLD = "EN_ESPERA"
    ACCEPTED = "ACEPTADA"
    REJECTED = "RECHAZADA"
    CANCELLED = "CANCELADA"

    ACTIVE = (PUBLISHED, IN_DEAL, ON_HOLD)
    TRANSITIONS = {
        PUBLISHED: {IN_DEAL, ON_HOLD, REJECTED, CANCELLED},
        IN_DEAL: {ACCEPTED, REJECTED, CANCELLED},
        ON_HOLD: {PUBLISHED, REJECTED, CANCELLED},
        ACCEPTED: set(),
        REJECTED: set(),
        CANCELLED: set(),
    }
    LABELS = {
        PUBLISHED: "Activa",
        IN_DEAL: "Por concretar",
        ON_HOLD: "En espera",
        ACCEPTED: "Concretada",
        REJECTED: "Rechazada",
        CANCELLED: "Cancelada",
    }


class Condition:
    ANY = "cualquiera"
    NEW = "nuevo"
    USED = "usado"

    ACCEPTED_OPTIONS = (ANY, NEW, USED)  # lo que acepta el lector
    OFFER_OPTIONS = (NEW, USED)  # lo que ofrece el vendedor
    LABELS = {ANY: "Cualquiera", NEW: "Nuevo", USED: "Usado"}


class Delivery:
    IN_PERSON = "presencial"
    SHIPPING = "envio"
    ANY = "cualquiera"

    OPTIONS = (IN_PERSON, SHIPPING, ANY)
    LABELS = {IN_PERSON: "Presencial", SHIPPING: "Envío", ANY: "Cualquiera"}


# --------------------------------------------------------------------------
# Errores
# --------------------------------------------------------------------------
class DomainError(Exception):
    """Error de negocio con mensaje apto para mostrar al usuario."""


class ValidationError(DomainError):
    pass


class PermissionDenied(DomainError):
    pass


class NotFound(DomainError):
    pass


class InvalidTransition(DomainError):
    pass


# --------------------------------------------------------------------------
# Entidades
# --------------------------------------------------------------------------
@dataclass
class User:
    id: int
    name: str
    email: str
    password: str  # MVP: texto plano en memoria. Nunca así en producción.
    role: str
    status: str = UserStatus.ACTIVE
    location: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def first_name(self) -> str:
        return self.name.split()[0] if self.name else ""


@dataclass
class Book:
    id: int
    external_provider: str
    external_id: str
    isbn: str
    title: str
    authors: list[str]
    cover_url: str
    publisher: str
    published_date: str

    @property
    def authors_text(self) -> str:
        return ", ".join(self.authors) if self.authors else "Autor desconocido"


@dataclass
class BookRequest:
    id: int
    reader_id: int
    book_id: int
    max_price: Optional[int]
    accepted_condition: str
    location: str
    delivery_preference: str
    notes: str
    status: str = RequestStatus.DRAFT
    canceled_by_role: Optional[str] = None
    cancellation_reason: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Offer:
    id: int
    request_id: int
    seller_id: int
    price: int
    book_condition: str
    condition_description: str
    notes: str
    status: str = OfferStatus.PUBLISHED
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SellerContact:
    seller_id: int
    phone: str = ""
    email: str = ""
    address_or_meeting_point: str = ""

    def is_empty(self) -> bool:
        return not (self.phone or self.email or self.address_or_meeting_point)


@dataclass
class ActivityEntry:
    at: datetime
    actor_id: Optional[int]
    action: str
    detail: str


# --------------------------------------------------------------------------
# Utilidades de validación
# --------------------------------------------------------------------------
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _clean(value, max_len: int = 500) -> str:
    return str(value or "").strip()[:max_len]


def _parse_price(value, *, required: bool, field_name: str) -> Optional[int]:
    raw = "" if value is None else str(value).strip()
    if not raw:
        if required:
            raise ValidationError(f"{field_name} es obligatorio.")
        return None
    if not raw.isdigit():
        raise ValidationError(f"{field_name} debe ser un número entero.")
    price = int(raw)
    if price <= 0:
        raise ValidationError(f"{field_name} debe ser mayor que 0.")
    if price > 10_000_000:
        raise ValidationError(f"{field_name} es demasiado alto.")
    return price


def format_price(value: Optional[int]) -> str:
    if value is None:
        return "Sin máximo"
    return "$" + f"{value:,}".replace(",", ".")


def condition_compatible(accepted: str, offered: str) -> bool:
    return accepted == Condition.ANY or accepted == offered


# --------------------------------------------------------------------------
# Repositorio en memoria + casos de uso
# --------------------------------------------------------------------------
class Store:
    def __init__(self) -> None:
        self.users: dict[int, User] = {}
        self.books: dict[int, Book] = {}
        self.requests: dict[int, BookRequest] = {}
        self.offers: dict[int, Offer] = {}
        self.contacts: dict[int, SellerContact] = {}
        self.activity: list[ActivityEntry] = []
        self._ids = {
            name: itertools.count(1)
            for name in ("user", "book", "request", "offer")
        }

    # ------------------------------------------------------------ helpers
    def _next_id(self, kind: str) -> int:
        return next(self._ids[kind])

    def _log(self, actor: Optional[User], action: str, detail: str) -> None:
        self.activity.append(
            ActivityEntry(datetime.now(), actor.id if actor else None, action, detail)
        )

    def _require_active(self, actor: Optional[User]) -> User:
        if actor is None or actor.id not in self.users:
            raise PermissionDenied("Debes iniciar sesión.")
        # Se relee desde el repositorio: no se confía en el objeto del cliente.
        current = self.users[actor.id]
        if current.status != UserStatus.ACTIVE:
            raise PermissionDenied("Tu cuenta está suspendida.")
        return current

    def _require_role(self, actor: Optional[User], *roles: str) -> User:
        user = self._require_active(actor)
        if user.role not in roles:
            raise PermissionDenied("No tienes permisos para esta acción.")
        return user

    def _get(self, table: dict, obj_id: int, label: str):
        try:
            return table[obj_id]
        except KeyError:
            raise NotFound(f"{label} no encontrada.") from None

    @staticmethod
    def _transition(obj, new_status: str, transitions: dict) -> None:
        if new_status not in transitions.get(obj.status, set()):
            raise InvalidTransition(
                f"No se puede pasar de {obj.status} a {new_status}."
            )
        obj.status = new_status
        obj.updated_at = datetime.now()

    def user(self, user_id: int) -> User:
        return self._get(self.users, user_id, "Usuario")

    def book(self, book_id: int) -> Book:
        return self._get(self.books, book_id, "Libro")

    # --------------------------------------------------------------- auth
    def add_user(self, name, email, password, role, location="") -> User:
        """Alta interna (seed/hardcode). Permite cualquier rol, incluido admin."""
        user = User(self._next_id("user"), name, email.lower(), password, role, location=location)
        self.users[user.id] = user
        if role == Role.SELLER:
            self.contacts[user.id] = SellerContact(user.id)
        return user

    def find_user_by_email(self, email: str) -> Optional[User]:
        email = _clean(email).lower()
        return next((u for u in self.users.values() if u.email == email), None)

    def authenticate(self, email: str, password: str) -> User:
        user = self.find_user_by_email(email)
        if user is None or user.password != password:
            raise ValidationError("Correo o contraseña incorrectos.")
        if user.status != UserStatus.ACTIVE:
            raise PermissionDenied("Tu cuenta está suspendida. Contacta a soporte.")
        self._log(user, "login", f"{user.email} inició sesión")
        return user

    def register(self, name: str, email: str, password: str, role: str, location: str = "") -> User:
        name, email = _clean(name, 80), _clean(email, 120).lower()
        location = _clean(location, 80)
        if len(name) < 2:
            raise ValidationError("Ingresa tu nombre.")
        if not EMAIL_RE.match(email):
            raise ValidationError("Ingresa un correo válido.")
        if len(password or "") < 4:
            raise ValidationError("La contraseña debe tener al menos 4 caracteres.")
        if role not in Role.PUBLIC:
            raise PermissionDenied("Rol no permitido en el registro.")
        if role == Role.SELLER and len(location) < 2:
            raise ValidationError("Ingresa tu comuna para que los lectores sepan qué tan cerca estás.")
        if self.find_user_by_email(email):
            raise ValidationError("Ya existe una cuenta con ese correo.")
        user = self.add_user(name, email, password, role, location)
        self._log(user, "registro", f"Nuevo {Role.LABELS[role].lower()}: {email}")
        return user

    def recover_password(self, email: str) -> None:
        """Simulado: en el MVP solo se valida el formato; no se envía nada."""
        if not EMAIL_RE.match(_clean(email)):
            raise ValidationError("Ingresa un correo válido.")

    # -------------------------------------------------------------- books
    def upsert_book(self, data: dict) -> Book:
        """Guarda la referencia externa mínima de un libro (sin duplicar)."""
        provider = _clean(data.get("provider"), 40) or "desconocido"
        external_id = _clean(data.get("external_id"), 80)
        title = _clean(data.get("title"), 200)
        if not external_id or not title:
            raise ValidationError("El libro seleccionado no es válido.")
        for book in self.books.values():
            if (book.external_provider, book.external_id) == (provider, external_id):
                return book
        authors = [_clean(a, 100) for a in (data.get("authors") or []) if _clean(a)]
        cover = _clean(data.get("cover_url"), 500)
        if cover and not cover.startswith("https://"):
            cover = ""
        book = Book(
            id=self._next_id("book"),
            external_provider=provider,
            external_id=external_id,
            isbn=_clean(data.get("isbn"), 20),
            title=title,
            authors=authors[:5],
            cover_url=cover,
            publisher=_clean(data.get("publisher"), 120),
            published_date=_clean(data.get("published_date"), 20),
        )
        self.books[book.id] = book
        return book

    # ---------------------------------------------------- reader: requests
    def create_request(
        self,
        actor: User,
        book_id: Optional[int],
        max_price=None,
        accepted_condition: str = Condition.ANY,
        location: str = "",
        delivery_preference: str = Delivery.ANY,
        notes: str = "",
    ) -> BookRequest:
        """Crea la solicitud (BORRADOR) y la publica (PUBLICADA) en un paso."""
        reader = self._require_role(actor, Role.READER)
        if book_id is None or book_id not in self.books:
            raise ValidationError("Debes seleccionar un libro.")
        if accepted_condition not in Condition.ACCEPTED_OPTIONS:
            raise ValidationError("Selecciona la condición aceptada.")
        if delivery_preference not in Delivery.OPTIONS:
            raise ValidationError("Selecciona una preferencia de entrega.")
        location = _clean(location, 80)
        if len(location) < 2:
            raise ValidationError("Indica tu ubicación.")
        price = _parse_price(max_price, required=False, field_name="El precio máximo")

        req = BookRequest(
            id=self._next_id("request"),
            reader_id=reader.id,
            book_id=book_id,
            max_price=price,
            accepted_condition=accepted_condition,
            location=location,
            delivery_preference=delivery_preference,
            notes=_clean(notes, 500),
        )
        self._transition(req, RequestStatus.PUBLISHED, RequestStatus.TRANSITIONS)
        self.requests[req.id] = req
        self._log(
            reader, "solicitud_publicada",
            f"Solicitud #{req.id} · {self.book(book_id).title}",
        )
        return req

    def reader_requests(self, actor: User, status_filter: str = "todas") -> list[BookRequest]:
        reader = self._require_role(actor, Role.READER)
        groups = {
            "todas": None,
            "activas": RequestStatus.ACTIVE,
            "resueltas": (RequestStatus.RESOLVED,),
            "canceladas": (RequestStatus.CANCELLED,),
        }
        allowed = groups.get(status_filter)
        items = [
            r for r in self.requests.values()
            if r.reader_id == reader.id and (allowed is None or r.status in allowed)
        ]
        return sorted(items, key=lambda r: r.updated_at, reverse=True)

    def get_request(self, actor: User, request_id: int) -> BookRequest:
        user = self._require_active(actor)
        req = self._get(self.requests, request_id, "Solicitud")
        if user.role == Role.ADMIN:
            return req
        if user.role == Role.READER and req.reader_id == user.id:
            return req
        if user.role == Role.SELLER and (
            req.status in RequestStatus.OPEN
            or any(o.seller_id == user.id for o in self._offers_of(req.id))
        ):
            return req
        raise PermissionDenied("No puedes ver esta solicitud.")

    def cancel_request(self, actor: User, request_id: int, reason: str = "") -> BookRequest:
        user = self._require_role(actor, Role.READER, Role.ADMIN)
        req = self._get(self.requests, request_id, "Solicitud")
        if user.role == Role.READER and req.reader_id != user.id:
            raise PermissionDenied("Solo puedes cancelar tus propias solicitudes.")
        self._transition(req, RequestStatus.CANCELLED, RequestStatus.TRANSITIONS)
        req.canceled_by_role = user.role
        req.cancellation_reason = _clean(reason, 300)
        for offer in self._offers_of(req.id):
            if offer.status in OfferStatus.ACTIVE:
                self._transition(offer, OfferStatus.CANCELLED, OfferStatus.TRANSITIONS)
        who = "moderación" if user.role == Role.ADMIN else "lector"
        detail = f"Solicitud #{req.id} cancelada ({who})"
        if req.cancellation_reason:
            detail += f": {req.cancellation_reason}"
        self._log(user, "solicitud_cancelada", detail)
        return req

    # ------------------------------------------------------ seller: feed
    def open_requests(
        self,
        actor: User,
        text: str = "",
        location: str = "",
        min_budget=None,
        condition: str = "todas",
    ) -> list[BookRequest]:
        self._require_role(actor, Role.SELLER)
        text, location = _clean(text).lower(), _clean(location).lower()
        budget = _parse_price(min_budget, required=False, field_name="El presupuesto")
        result = []
        for req in self.requests.values():
            if req.status not in RequestStatus.OPEN:
                continue
            # Excluir solicitudes donde el vendedor actual ya tenga una oferta activa
            if self.seller_active_offer(actor, req.id) is not None:
                continue
            book = self.book(req.book_id)
            haystack = " ".join([book.title, book.authors_text, book.isbn]).lower()
            if text and text not in haystack:
                continue
            if location and location not in req.location.lower():
                continue
            if budget is not None and req.max_price is not None and req.max_price < budget:
                continue
            if condition != "todas" and not condition_compatible(req.accepted_condition, condition):
                continue
            result.append(req)
        return sorted(result, key=lambda r: r.created_at, reverse=True)

    # ---------------------------------------------------------- offers
    def _offers_of(self, request_id: int) -> Iterable[Offer]:
        return (o for o in self.offers.values() if o.request_id == request_id)

    def seller_active_offer(self, actor: User, request_id: int) -> Optional[Offer]:
        seller = self._require_role(actor, Role.SELLER)
        return next(
            (o for o in self._offers_of(request_id)
             if o.seller_id == seller.id and o.status in OfferStatus.ACTIVE),
            None,
        )

    def seller_contact(self, actor: User) -> SellerContact:
        seller = self._require_role(actor, Role.SELLER)
        return self.contacts.setdefault(seller.id, SellerContact(seller.id))

    def create_offer(
        self,
        actor: User,
        request_id: int,
        price,
        book_condition: str,
        condition_description: str = "",
        notes: str = "",
        phone: str = "",
        email: str = "",
        address: str = "",
    ) -> Offer:
        seller = self._require_role(actor, Role.SELLER)
        req = self._get(self.requests, request_id, "Solicitud")
        if req.status not in RequestStatus.OPEN:
            raise ValidationError("La solicitud ya no recibe ofertas.")
        if self.seller_active_offer(seller, req.id):
            raise ValidationError("Ya tienes una oferta activa para esta solicitud.")
        amount = _parse_price(price, required=True, field_name="El precio")
        if book_condition not in Condition.OFFER_OPTIONS:
            raise ValidationError("Indica si el libro es nuevo o usado.")
        # El estado del libro ofrecido no bloquea la creación de la oferta (el lector decide aceptar o no).
        phone, email, address = _clean(phone, 30), _clean(email, 120), _clean(address, 200)
        if email and not EMAIL_RE.match(email):
            raise ValidationError("El correo de contacto no es válido.")
        if not (phone or email or address):
            raise ValidationError("Agrega al menos un dato de contacto.")

        contact = self.contacts.setdefault(seller.id, SellerContact(seller.id))
        contact.phone, contact.email, contact.address_or_meeting_point = phone, email, address

        offer = Offer(
            id=self._next_id("offer"),
            request_id=req.id,
            seller_id=seller.id,
            price=amount,
            book_condition=book_condition,
            condition_description=_clean(condition_description, 300),
            notes=_clean(notes, 500),
        )
        self.offers[offer.id] = offer
        if req.status == RequestStatus.PUBLISHED:
            self._transition(req, RequestStatus.WITH_OFFERS, RequestStatus.TRANSITIONS)
        self._log(
            seller, "oferta_publicada",
            f"Oferta #{offer.id} para solicitud #{req.id} · {format_price(amount)}",
        )
        return offer

    def offers_for_request(self, actor: User, request_id: int) -> list[Offer]:
        user = self._require_active(actor)
        req = self.get_request(user, request_id)
        offers = list(self._offers_of(req.id))
        if user.role == Role.SELLER:
            offers = [o for o in offers if o.seller_id == user.id]
        return sorted(offers, key=lambda o: o.price)

    def get_offer(self, actor: User, offer_id: int) -> Offer:
        user = self._require_active(actor)
        offer = self._get(self.offers, offer_id, "Oferta")
        req = self.requests[offer.request_id]
        if (
            user.role == Role.ADMIN
            or (user.role == Role.SELLER and offer.seller_id == user.id)
            or (user.role == Role.READER and req.reader_id == user.id)
        ):
            return offer
        raise PermissionDenied("No puedes ver esta oferta.")

    def offer_contact(self, actor: User, offer_id: int) -> SellerContact:
        """Los datos de contacto se revelan cuando la oferta entra en coordinación o es aceptada."""
        offer = self.get_offer(actor, offer_id)
        user = self._require_active(actor)
        if offer.status not in (OfferStatus.IN_DEAL, OfferStatus.ACCEPTED) and user.role != Role.ADMIN:
            raise PermissionDenied("El contacto se muestra al coordinar o aceptar la oferta.")
        return self.contacts.get(offer.seller_id, SellerContact(offer.seller_id))

    def accept_offer(self, actor: User, offer_id: int) -> Offer:
        """El lector acepta preliminarmente la oferta para coordinar entrega/compra."""
        reader = self._require_role(actor, Role.READER)
        offer = self._get(self.offers, offer_id, "Oferta")
        req = self.requests[offer.request_id]
        if req.reader_id != reader.id:
            raise PermissionDenied("Solo puedes aceptar ofertas de tus solicitudes.")
        if offer.status != OfferStatus.PUBLISHED:
            raise InvalidTransition("Esta oferta ya no está disponible.")
        
        self._transition(req, RequestStatus.IN_DEAL, RequestStatus.TRANSITIONS)
        self._transition(offer, OfferStatus.IN_DEAL, OfferStatus.TRANSITIONS)
        # Las demás ofertas activas pasan a estar en espera (no se rechazan aún)
        for other in self._offers_of(req.id):
            if other.id != offer.id and other.status == OfferStatus.PUBLISHED:
                self._transition(other, OfferStatus.ON_HOLD, OfferStatus.TRANSITIONS)
        self._log(
            reader, "oferta_por_concretar",
            f"Oferta #{offer.id} por concretar · solicitud #{req.id} en coordinación",
        )
        return offer

    def confirm_deal(self, actor: User, offer_id: int) -> Offer:
        """El lector confirma que el trato se cerró exitosamente."""
        reader = self._require_role(actor, Role.READER)
        offer = self._get(self.offers, offer_id, "Oferta")
        req = self.requests[offer.request_id]
        if req.reader_id != reader.id:
            raise PermissionDenied("Solo puedes confirmar tratos de tus solicitudes.")
        if offer.status != OfferStatus.IN_DEAL:
            raise InvalidTransition("Solo puedes confirmar ofertas que estén en coordinación.")
        
        self._transition(req, RequestStatus.RESOLVED, RequestStatus.TRANSITIONS)
        self._transition(offer, OfferStatus.ACCEPTED, OfferStatus.TRANSITIONS)
        for other in self._offers_of(req.id):
            if other.id != offer.id and other.status == OfferStatus.ON_HOLD:
                self._transition(other, OfferStatus.REJECTED, OfferStatus.TRANSITIONS)
        self._log(
            reader, "trato_concretado",
            f"Oferta #{offer.id} concretada · solicitud #{req.id} resuelta",
        )
        return offer

    def cancel_deal(self, actor: User, offer_id: int, reason: str = "") -> Offer:
        """El lector o vendedor desiste de la coordinación en curso."""
        user = self._require_role(actor, Role.READER, Role.SELLER, Role.ADMIN)
        offer = self._get(self.offers, offer_id, "Oferta")
        req = self.requests[offer.request_id]
        if user.role == Role.READER and req.reader_id != user.id:
            raise PermissionDenied("No puedes desistir de este trato.")
        if user.role == Role.SELLER and offer.seller_id != user.id:
            raise PermissionDenied("No puedes desistir de este trato.")
        if offer.status != OfferStatus.IN_DEAL:
            raise InvalidTransition("Esta oferta no está en coordinación.")

        new_offer_status = OfferStatus.CANCELLED if user.role == Role.SELLER else OfferStatus.REJECTED
        self._transition(offer, new_offer_status, OfferStatus.TRANSITIONS)

        # Reactivar las demás ofertas que estaban en espera
        active_on_hold = [o for o in self._offers_of(req.id) if o.status == OfferStatus.ON_HOLD]
        for other in active_on_hold:
            self._transition(other, OfferStatus.PUBLISHED, OfferStatus.TRANSITIONS)

        new_req_status = RequestStatus.WITH_OFFERS if active_on_hold else RequestStatus.PUBLISHED
        self._transition(req, new_req_status, RequestStatus.TRANSITIONS)

        self._log(
            user, "trato_desistido",
            f"Coordinación de oferta #{offer.id} cancelada · solicitud #{req.id} reactivada",
        )
        return offer

    def cancel_offer(self, actor: User, offer_id: int) -> Offer:
        seller = self._require_role(actor, Role.SELLER)
        offer = self._get(self.offers, offer_id, "Oferta")
        if offer.seller_id != seller.id:
            raise PermissionDenied("Solo puedes cancelar tus propias ofertas.")
        self._transition(offer, OfferStatus.CANCELLED, OfferStatus.TRANSITIONS)
        self._log(seller, "oferta_cancelada", f"Oferta #{offer.id} cancelada")
        return offer

    def seller_offers(self, actor: User, status_filter: str = "todas") -> list[Offer]:
        seller = self._require_role(actor, Role.SELLER)
        groups = {
            "todas": None,
            "activas": (OfferStatus.PUBLISHED, OfferStatus.IN_DEAL, OfferStatus.ON_HOLD),
            "aceptadas": (OfferStatus.ACCEPTED,),
            "finalizadas": (OfferStatus.REJECTED, OfferStatus.CANCELLED),
        }
        allowed = groups.get(status_filter)
        items = [
            o for o in self.offers.values()
            if o.seller_id == seller.id and (allowed is None or o.status in allowed)
        ]
        return sorted(items, key=lambda o: o.updated_at, reverse=True)

    def active_offer_count(self, request_id: int) -> int:
        return sum(1 for o in self._offers_of(request_id) if o.status in OfferStatus.ACTIVE)

    # ------------------------------------------------------------ admin
    def admin_stats(self, actor: User) -> dict[str, int]:
        self._require_role(actor, Role.ADMIN)
        reqs = list(self.requests.values())
        users = [u for u in self.users.values() if u.role != Role.ADMIN]
        return {
            "usuarios": len(users),
            "lectores": sum(u.role == Role.READER for u in users),
            "vendedores": sum(u.role == Role.SELLER for u in users),
            "solicitudes": len(reqs),
            "activas": sum(r.status in RequestStatus.ACTIVE for r in reqs),
            "con_ofertas": sum(r.status in (RequestStatus.WITH_OFFERS, RequestStatus.IN_DEAL) for r in reqs),
            "resueltas": sum(r.status == RequestStatus.RESOLVED for r in reqs),
            "canceladas": sum(r.status == RequestStatus.CANCELLED for r in reqs),
            "ofertas": len(self.offers),
        }

    def admin_users(self, actor: User) -> list[User]:
        self._require_role(actor, Role.ADMIN)
        return sorted(self.users.values(), key=lambda u: (u.role, u.name))

    def admin_requests(self, actor: User, status_filter: str = "todas") -> list[BookRequest]:
        self._require_role(actor, Role.ADMIN)
        groups = {
            "todas": None,
            "activas": RequestStatus.ACTIVE,
            "resueltas": (RequestStatus.RESOLVED,),
            "canceladas": (RequestStatus.CANCELLED,),
        }
        allowed = groups.get(status_filter)
        items = [r for r in self.requests.values() if allowed is None or r.status in allowed]
        return sorted(items, key=lambda r: r.updated_at, reverse=True)

    def admin_offers(self, actor: User) -> list[Offer]:
        self._require_role(actor, Role.ADMIN)
        return sorted(self.offers.values(), key=lambda o: o.updated_at, reverse=True)

    def admin_activity(self, actor: User, limit: int = 50, text: str = "") -> list[ActivityEntry]:
        self._require_role(actor, Role.ADMIN)
        entries = list(reversed(self.activity))
        query = _clean(text, 120).lower()
        if query:
            def matches(entry: ActivityEntry) -> bool:
                actor_user = self.users.get(entry.actor_id) if entry.actor_id else None
                haystack = " ".join([
                    entry.action,
                    entry.detail,
                    actor_user.name if actor_user else "",
                    actor_user.email if actor_user else "",
                ]).lower()
                return query in haystack

            entries = [e for e in entries if matches(e)]
        return entries[:limit]

    def set_user_status(self, actor: User, user_id: int, status: str) -> User:
        admin = self._require_role(actor, Role.ADMIN)
        target = self.user(user_id)
        if target.role == Role.ADMIN:
            raise PermissionDenied("No se puede suspender a un administrador.")
        if status not in (UserStatus.ACTIVE, UserStatus.SUSPENDED):
            raise ValidationError("Estado de usuario inválido.")
        target.status = status
        verb = "suspendido" if status == UserStatus.SUSPENDED else "reactivado"
        self._log(admin, "usuario_" + verb, f"{target.email} {verb}")
        return target

    def export_activity_log(self, actor: User, file_path: str = "registro_actividad.txt") -> str:
        """Exporta el historial de actividad y auditoría a un archivo de texto/log."""
        self._require_role(actor, Role.ADMIN)
        lines = [
            "============================================================",
            "   REGISTRO DE ACTIVIDAD Y AUDITORÍA - APP DE LIBROS",
            f"   Exportado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            f"   Por administrador: {actor.name} ({actor.email})",
            "============================================================",
            "",
        ]
        if not self.activity:
            lines.append("No hay eventos registrados.")
        else:
            for idx, entry in enumerate(reversed(self.activity), 1):
                actor_user = self.users.get(entry.actor_id) if entry.actor_id else None
                actor_str = f"{actor_user.name} ({actor_user.email})" if actor_user else "Sistema"
                dt_str = entry.at.strftime("%d/%m/%Y %H:%M:%S")
                lines.append(f"{idx:03d}. [{dt_str}] [{entry.action.upper()}]")
                lines.append(f"     Actor:  {actor_str}")
                lines.append(f"     Detalle: {entry.detail}")
                lines.append("-" * 60)
        content = "\n".join(lines)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return os.path.abspath(file_path)


# --------------------------------------------------------------------------
# Datos hardcodeados del demo
# --------------------------------------------------------------------------
DEMO_USERS = [
    # (nombre, correo, contraseña, rol, comuna)
    ("Juan Pérez", "lector@demo.cl", "1234", Role.READER, ""),
    ("María González", "maria@demo.cl", "1234", Role.READER, ""),
    ("Librería Los Andes", "vendedor@demo.cl", "1234", Role.SELLER, "Concepción"),
    ("Pedro Soto", "pedro@demo.cl", "1234", Role.SELLER, "Santiago"),
    ("Admin", "admin@demo.cl", "admin", Role.ADMIN, ""),
]


def build_demo_store(catalog_lookup: Callable[[str], dict]) -> Store:
    """Crea un Store con usuarios hardcodeados y algo de actividad de ejemplo."""
    store = Store()
    users = {
        email: store.add_user(n, email, pw, role, loc)
        for n, email, pw, role, loc in DEMO_USERS
    }
    juan, maria = users["lector@demo.cl"], users["maria@demo.cl"]
    andes, pedro = users["vendedor@demo.cl"], users["pedro@demo.cl"]

    hobbit = store.upsert_book(catalog_lookup("demo-hobbit"))
    cien = store.upsert_book(catalog_lookup("demo-cien-anos"))
    orwell = store.upsert_book(catalog_lookup("demo-1984"))

    r1 = store.create_request(
        juan, hobbit.id, "15000", Condition.ANY, "Concepción", Delivery.IN_PERSON,
        "Idealmente edición de Minotauro.",
    )
    store.create_request(juan, orwell.id, "", Condition.USED, "Concepción", Delivery.ANY, "")
    store.create_request(
        maria, cien.id, "12000", Condition.NEW, "Santiago", Delivery.SHIPPING,
        "Es para regalo.",
    )
    store.create_offer(
        andes, r1.id, "13990", Condition.NEW, "Nuevo, sellado.",
        "Lo puedo reservar hasta el viernes.",
        "+56 9 1234 5678", "ventas@librerialosandes.cl", "Av. Libertad 123, Concepción",
    )
    store.create_offer(
        pedro, r1.id, "8000", Condition.USED, "Buen estado, lomo algo gastado.", "",
        "+56 9 8765 4321", "pedro@demo.cl", "",
    )
    store.activity.clear()  # el seed no cuenta como actividad real
    return store
