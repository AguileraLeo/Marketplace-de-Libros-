"""
App de libros — demo MVP en KivyMD 2.0.x

Ejecutar:  python main.py
Estilos/estructura visual: libros.kv
Dominio, reglas y permisos: store.py
Búsqueda de libros: books_api.py
"""

from kivy.utils import platform

if platform not in ("android", "ios"):
    from kivy.config import Config

    # Ventana tipo teléfono en escritorio.
    Config.set("graphics", "width", "420")
    Config.set("graphics", "height", "860")

import os
import threading
from datetime import datetime

from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogButtonContainer,
    MDDialogHeadlineText,
    MDDialogSupportingText,
)
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.stacklayout import MDStackLayout

from books_api import (
    catalog_lookup,
    download_and_cache_cover,
    get_cover_cache_path,
    is_cover_cached,
    search_books,
)
from locations import normalize_location_name, search_locations
from store import (
    Condition,
    Delivery,
    DomainError,
    OfferStatus,
    RequestStatus,
    Role,
    UserStatus,
    build_demo_store,
    format_price,
)

KV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "libros.kv")

# (fondo, texto) por estado — mismos colores en todas las pantallas.
STATUS_COLORS = {
    RequestStatus.PUBLISHED: ("#DCE8FF", "#123A7A"),
    RequestStatus.WITH_OFFERS: ("#FFE9C7", "#6B3F00"),
    RequestStatus.IN_DEAL: ("#FFF0D4", "#8A5300"),
    RequestStatus.RESOLVED: ("#D6F5DF", "#11562A"),
    RequestStatus.CANCELLED: ("#FADBD8", "#7A1C14"),
    OfferStatus.PUBLISHED: ("#E2EDF8", "#1E4976"),
    OfferStatus.IN_DEAL: ("#D4E5FF", "#0C448C"),
    OfferStatus.ON_HOLD: ("#EFEBE9", "#5D4037"),
    OfferStatus.ACCEPTED: ("#D6F5DF", "#11562A"),
    OfferStatus.REJECTED: ("#ECE6EE", "#4A4458"),
    OfferStatus.CANCELLED: ("#FADBD8", "#7A1C14"),
    UserStatus.ACTIVE: ("#D6F5DF", "#11562A"),
    UserStatus.SUSPENDED: ("#FADBD8", "#7A1C14"),
}
STATUS_LABELS = {
    "request": RequestStatus.LABELS,
    "offer": OfferStatus.LABELS,
    "user": {UserStatus.ACTIVE: "Activo", UserStatus.SUSPENDED: "Suspendido"},
}

# (fondo, texto) para diferenciar visualmente las tarjetas de métricas del admin.
STAT_TONES = {
    "blue": ("#DCE8FF", "#123A7A"),
    "green": ("#D6F5DF", "#11562A"),
    "orange": ("#FFE9C7", "#6B3F00"),
    "purple": ("#EADDFF", "#4F378B"),
    "red": ("#FADBD8", "#7A1C14"),
    "teal": ("#CCE8E2", "#0B4F4A"),
    "gray": ("#ECE6EE", "#4A4458"),
    "default": ("#DCE8FF", "#123A7A"),
}


def fmt_date(value) -> str:
    return value.strftime("%d/%m/%Y %H:%M")


# ==========================================================================
# Widgets reutilizables (su aspecto está en libros.kv)
# ==========================================================================
class BookCover(MDRelativeLayout):
    source = StringProperty("")
    local_source = StringProperty("")
    loaded = BooleanProperty(False)

    def on_source(self, _instance, value):
        self.loaded = False
        if not value:
            self.local_source = ""
            return
        if os.path.exists(value):
            self.local_source = value
            self.loaded = True
            return
        cache_path = get_cover_cache_path(value)
        if cache_path and os.path.exists(cache_path) and os.path.getsize(cache_path) > 100:
            self.local_source = cache_path
            self.loaded = True
            return
        self.local_source = ""
        download_and_cache_cover(value, self._on_download_complete)

    def _on_download_complete(self, url, local_path):
        if self.source == url and os.path.exists(local_path):
            self.local_source = local_path
            self.loaded = True


class StatusChip(MDBoxLayout):
    status = StringProperty("")
    kind = StringProperty("request")  # request | offer | user
    text = StringProperty("")
    bg = ColorProperty("#DCE8FF")
    fg = ColorProperty("#123A7A")

    def on_status(self, *_):
        self._update()

    def on_kind(self, *_):
        self._update()

    def _update(self):
        from kivy.utils import get_color_from_hex as c

        bg, fg = STATUS_COLORS.get(self.status, ("#DCE8FF", "#123A7A"))
        self.bg, self.fg = c(bg), c(fg)
        self.text = STATUS_LABELS.get(self.kind, {}).get(self.status, self.status)


class WideButton(MDButton):
    """MDButton a todo el ancho con icono + texto centrados."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind(size=lambda *_: Clock.schedule_once(self.adjust_pos))

    def adjust_pos(self, *args) -> None:
        text, icon = self._button_text, self._button_icon
        text_w = text.texture_size[0] if text else 0
        icon_w = icon.width + dp(8) if icon else 0
        start = (self.width - text_w - icon_w) / 2
        if icon:
            icon.x = start
        if text:
            text.x = start + icon_w


class ChoiceRow(MDStackLayout):
    """Grupo de botones de selección única (filled = seleccionado)."""

    options = ListProperty()  # [(valor, etiqueta), ...]
    value = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_height = True
        self.spacing = dp(8)
        self._trigger = Clock.create_trigger(self._rebuild)
        self.bind(options=self._trigger, value=self._trigger)
        self._trigger()

    def _rebuild(self, *_):
        self.clear_widgets()
        for value, label in self.options:
            btn = MDButton(
                MDButtonText(text=label),
                style="filled" if value == self.value else "outlined",
            )
            btn.bind(on_release=lambda _b, v=value: setattr(self, "value", v))
            self.add_widget(btn)


class RequestCard(MDCard):
    title = StringProperty()
    subtitle = StringProperty()
    meta = StringProperty()
    cover = StringProperty()
    status = StringProperty()
    badge = StringProperty()
    callback = ObjectProperty(None, allownone=True)


class ItemCard(MDCard):
    title = StringProperty()
    subtitle = StringProperty()
    meta = StringProperty()
    status = StringProperty()
    kind = StringProperty("offer")
    action_text = StringProperty()
    action_callback = ObjectProperty(None, allownone=True)
    callback = ObjectProperty(None, allownone=True)


class BookResultCard(MDCard):
    book = ObjectProperty(None, allownone=True)
    title = StringProperty()
    subtitle = StringProperty()
    meta = StringProperty()
    cover = StringProperty()


class StatTile(MDCard):
    value = StringProperty("0")
    label = StringProperty()
    tone = StringProperty("default")
    bg = ColorProperty([0.863, 0.910, 1.0, 1.0])
    fg = ColorProperty([0.071, 0.227, 0.478, 1.0])

    def on_tone(self, *_):
        from kivy.utils import get_color_from_hex as c

        bg, fg = STAT_TONES.get(self.tone, STAT_TONES["default"])
        self.bg, self.fg = c(bg), c(fg)


class InfoRow(MDBoxLayout):
    icon = StringProperty("information-outline")
    label = StringProperty()
    value = StringProperty()


class EmptyState(MDBoxLayout):
    icon = StringProperty("book-search-outline")
    text = StringProperty()


# ==========================================================================
# Pantallas
# ==========================================================================
class BaseScreen(MDScreen):
    @property
    def app(self):
        return MDApp.get_running_app()

    def on_pre_enter(self, *_):
        if self.app.user is not None or self.name in ("login", "register"):
            self.refresh()

    def refresh(self):
        pass

    @staticmethod
    def fill(container, widgets, empty_text="", empty_icon="book-search-outline"):
        container.clear_widgets()
        widgets = list(widgets)
        for w in widgets:
            container.add_widget(w)
        if not widgets and empty_text:
            container.add_widget(EmptyState(text=empty_text, icon=empty_icon))


# --------------------------------------------------------------- acceso
class LoginScreen(BaseScreen):
    def do_login(self):
        user = self.app.safe(
            self.app.store.authenticate, self.ids.email.text, self.ids.password.text
        )
        if user:
            self.ids.password.text = ""
            self.app.login(user)

    def fill_demo(self, email, password):
        self.ids.email.text = email
        self.ids.password.text = password

    def forgot_password(self):
        email = self.ids.email.text.strip()
        if not email:
            self.app.notify("Escribe tu correo en el campo de arriba.")
            return
        if self.app.safe(self.app.store.recover_password, email):
            self.app.info_dialog(
                "Recuperar contraseña",
                f"Si existe una cuenta asociada a {email}, recibirás un enlace para "
                "restablecer tu contraseña.\n\n(Simulado: el demo no envía correos.)",
            )


class RegisterScreen(BaseScreen):
    def refresh(self):
        for field in ("name", "email", "password"):
            self.ids[field].text = ""
        self.ids.role.value = Role.READER

    def do_register(self):
        user = self.app.safe(
            self.app.store.register,
            self.ids.name.text,
            self.ids.email.text,
            self.ids.password.text,
            self.ids.role.value,
        )
        if user:
            self.app.notify(f"¡Bienvenido/a, {user.first_name}!")
            self.app.login(user)


# --------------------------------------------------------------- lector
class ReaderHomeScreen(BaseScreen):
    def refresh(self):
        app, store = self.app, self.app.store
        requests = store.reader_requests(app.user)
        active = [r for r in requests if r.status in RequestStatus.OPEN]
        self.ids.stat_active.value = str(len(active))
        self.ids.stat_offers.value = str(sum(store.active_offer_count(r.id) for r in active))
        self.fill(
            self.ids.recent_list,
            [app.request_card(r, app.open_reader_request) for r in requests[:3]],
            "Aún no tienes solicitudes. Busca un libro para crear la primera.",
        )

    def search(self):
        self.app.start_book_search(self.ids.query.text, self.ids.mode.value)


class BookSearchScreen(BaseScreen):
    searching = BooleanProperty(False)
    status_text = StringProperty("")

    def prepare(self, query, mode):
        self.ids.query.text = query
        self.ids.mode.value = mode
        self.ids.results.clear_widgets()
        self.status_text = ""
        if query.strip():
            Clock.schedule_once(lambda *_: self.search(), 0.3)

    def search(self):
        query, mode = self.ids.query.text, self.ids.mode.value
        if len(query.strip()) < 2:
            self.app.notify("Escribe al menos 2 caracteres para buscar.")
            return
        self.searching = True
        self.status_text = "Buscando…"
        self.ids.results.clear_widgets()
        threading.Thread(target=self._worker, args=(query, mode), daemon=True).start()

    def _worker(self, query, mode):
        try:
            results, source = search_books(query, mode)
            self._show(results, source, None)
        except Exception as exc:  # noqa: BLE001 — se muestra al usuario
            self._show([], "", str(exc))

    @mainthread
    def _show(self, results, source, error):
        self.searching = False
        if error:
            self.status_text = error
            return
        origin = {
            "google_books": "Google Books",
            "open_library": "Open Library",
        }.get(source, "catálogo de ejemplo (sin conexión)")
        self.status_text = f"{len(results)} resultado(s) · {origin}"
        cards = []
        for book in results:
            authors = ", ".join(book["authors"]) or "Autor desconocido"
            details = " · ".join(filter(None, [book["publisher"], book["published_date"][:4]]))
            cards.append(
                BookResultCard(
                    book=book,
                    title=book["title"],
                    subtitle=authors,
                    meta="\n".join(filter(None, [details, f"ISBN {book['isbn']}" if book["isbn"] else ""])),
                    cover=book["cover_url"],
                )
            )
        self.fill(self.ids.results, cards, "No encontramos libros. Prueba con otro término.")


class CreateRequestScreen(BaseScreen):
    def refresh(self):
        book = self.app.selected_book
        if book is None:
            return
        self.ids.cover.source = book.cover_url
        self.ids.book_title.text = book.title
        self.ids.book_meta.text = f"{book.authors_text}\n{book.publisher}  ·  ISBN {book.isbn or '—'}"
        if hasattr(self.ids, "suggestions_box"):
            self.ids.suggestions_box.clear_widgets()

    def reset_form(self):
        self.ids.max_price.text = ""
        self.ids.location.text = ""
        self.ids.notes.text = ""
        self.ids.condition.value = Condition.ANY
        self.ids.delivery.value = Delivery.ANY
        if hasattr(self.ids, "suggestions_box"):
            self.ids.suggestions_box.clear_widgets()

    def on_location_text(self, text):
        if not hasattr(self.ids, "suggestions_box"):
            return
        self.ids.suggestions_box.clear_widgets()
        query = (text or "").strip()
        if len(query) < 2:
            return
        matches = search_locations(query, limit=4)
        for loc in matches:
            btn = MDButton(
                MDButtonText(text=loc),
                style="text",
                size_hint_x=1,
                height=dp(36),
            )
            btn.bind(on_release=lambda _b, l=loc: self.select_location(l))
            self.ids.suggestions_box.add_widget(btn)

    def select_location(self, loc):
        self.ids.location.text = loc
        if hasattr(self.ids, "suggestions_box"):
            self.ids.suggestions_box.clear_widgets()

    def publish(self):
        app = self.app
        loc = normalize_location_name(self.ids.location.text)
        req = app.safe(
            app.store.create_request,
            app.user,
            app.selected_book.id if app.selected_book else None,
            self.ids.max_price.text,
            self.ids.condition.value,
            loc,
            self.ids.delivery.value,
            self.ids.notes.text,
        )
        if req:
            app.current_request_id = req.id
            self.reset_form()
            app.go("request_published", reset_to="reader_home")


class RequestPublishedScreen(BaseScreen):
    def refresh(self):
        req = self.app.store.requests.get(self.app.current_request_id)
        if req:
            self.ids.book_title.text = self.app.store.book(req.book_id).title
            self.ids.request_id.text = f"Solicitud #{req.id} · estado: Publicada"


class ReaderRequestsScreen(BaseScreen):
    def refresh(self):
        app = self.app
        items = app.store.reader_requests(app.user, self.ids.filter.value)
        self.fill(
            self.ids.list,
            [app.request_card(r, app.open_reader_request) for r in items],
            "No hay solicitudes en esta categoría.",
        )


class ReaderRequestDetailScreen(BaseScreen):
    can_cancel = BooleanProperty(False)

    def refresh(self):
        app, store = self.app, self.app.store
        req = app.safe(store.get_request, app.user, app.current_request_id)
        if not req:
            return
        book = store.book(req.book_id)
        app.fill_book_header(self, book)
        self.ids.status.status = req.status
        self.ids.info.clear_widgets()
        rows = app.request_info_rows(req)
        if req.status == RequestStatus.CANCELLED:
            who = "moderación administrativa" if req.canceled_by_role == Role.ADMIN else "el lector"
            cancel_msg = f"Cancelada por {who}"
            if req.cancellation_reason:
                cancel_msg += f" · Motivo: {req.cancellation_reason}"
            rows.append(("alert-circle-outline", "Moderación / Cancelación", cancel_msg))
        for icon, label, value in rows:
            self.ids.info.add_widget(InfoRow(icon=icon, label=label, value=value))
        self.can_cancel = req.status in RequestStatus.OPEN

        offers = store.offers_for_request(app.user, req.id)
        self.ids.offers_title.text = f"Ofertas recibidas ({len(offers)})"
        cards = []
        for o in offers:
            seller = store.user(o.seller_id)
            cards.append(ItemCard(
                title=f"{format_price(o.price)}  ·  {Condition.LABELS[o.book_condition]}",
                subtitle=seller.name,
                meta=o.condition_description or "Sin descripción de condición",
                status=o.status, kind="offer",
                callback=lambda _c, oid=o.id: app.open_offer(oid),
            ))
        self.fill(self.ids.offers, cards, "Todavía no hay ofertas. Te avisaremos aquí cuando llegue una.", "timer-sand")

    def cancel(self):
        app = self.app

        def do_cancel():
            if app.safe(app.store.cancel_request, app.user, app.current_request_id, reason="Cancelada por el lector"):
                app.notify("Solicitud cancelada.")
                self.refresh()

        app.confirm(
            "¿Cancelar solicitud?",
            "Los vendedores dejarán de verla y las ofertas activas se cancelarán.",
            "Cancelar solicitud", do_cancel,
        )


class OfferDetailScreen(BaseScreen):
    can_accept = BooleanProperty(False)
    in_deal = BooleanProperty(False)
    accepted = BooleanProperty(False)
    on_hold = BooleanProperty(False)
    is_reader = BooleanProperty(False)

    def refresh(self):
        app, store = self.app, self.app.store
        offer = app.safe(store.get_offer, app.user, app.current_offer_id)
        if not offer:
            return
        req = store.requests[offer.request_id]
        book = store.book(req.book_id)
        seller = store.user(offer.seller_id)
        self.ids.book_title.text = book.title
        self.ids.price.text = format_price(offer.price)
        self.ids.status.status = offer.status
        self.is_reader = app.user.role == Role.READER and req.reader_id == app.user.id
        rows = [
            ("book-open-variant", "Estado del libro", Condition.LABELS[offer.book_condition]),
            ("text-box-outline", "Condición", offer.condition_description or "—"),
            ("storefront-outline", "Vendedor", seller.name),
            ("note-text-outline", "Información adicional", offer.notes or "—"),
            ("calendar", "Fecha de la oferta", fmt_date(offer.created_at)),
        ]
        if req.max_price and offer.price > req.max_price:
            rows.append(("alert-outline", "Atención", f"Supera tu precio máximo ({format_price(req.max_price)})"))
        if req.accepted_condition != Condition.ANY and req.accepted_condition != offer.book_condition:
            rows.append((
                "information-outline",
                "Nota de condición",
                f"Ofrecido como {Condition.LABELS[offer.book_condition].lower()} (solicitabas {Condition.LABELS[req.accepted_condition].lower()})",
            ))
        self.ids.info.clear_widgets()
        for icon, label, value in rows:
            self.ids.info.add_widget(InfoRow(icon=icon, label=label, value=value))
        
        self.can_accept = self.is_reader and offer.status == OfferStatus.PUBLISHED and req.status in RequestStatus.OPEN
        self.in_deal = offer.status == OfferStatus.IN_DEAL
        self.accepted = offer.status == OfferStatus.ACCEPTED
        self.on_hold = offer.status == OfferStatus.ON_HOLD

    def accept(self):
        app = self.app

        def do_accept():
            if app.safe(app.store.accept_offer, app.user, app.current_offer_id):
                app.go("offer_accepted")

        app.confirm(
            "¿Aceptar esta oferta?",
            "La oferta pasará a estado 'Por concretar' y verás los datos de contacto del vendedor para coordinar la entrega. Las demás ofertas quedarán en espera.",
            "Aceptar para coordinar", do_accept,
        )

    def confirm_deal(self):
        app = self.app

        def do_confirm():
            if app.safe(app.store.confirm_deal, app.user, app.current_offer_id):
                app.notify("¡Trato concretado con éxito! La solicitud quedó resuelta.")
                self.refresh()

        app.confirm(
            "¿Confirmar trato concretado?",
            "Confirma que compraste/recibiste el libro. La solicitud quedará resuelta definitivamente y las demás ofertas se cerrarán.",
            "Confirmar compra", do_confirm,
        )

    def cancel_deal(self):
        app = self.app

        def do_cancel():
            if app.safe(app.store.cancel_deal, app.user, app.current_offer_id):
                app.notify("Se canceló la coordinación. Las demás ofertas vuelven a estar activas.")
                self.refresh()

        app.confirm(
            "¿Desistir de este trato?",
            "Se cancelará la coordinación con este vendedor y las otras ofertas volverán a estar activas para que puedas elegir otra opción.",
            "Desistir del trato", do_cancel,
        )


class OfferAcceptedScreen(BaseScreen):
    def refresh(self):
        app, store = self.app, self.app.store
        contact = app.safe(store.offer_contact, app.user, app.current_offer_id)
        if contact is None:
            return
        offer = store.offers[app.current_offer_id]
        req = store.requests[offer.request_id]
        seller = store.user(offer.seller_id)
        self.ids.summary.text = (
            f"{store.book(req.book_id).title}\n{format_price(offer.price)} · "
            f"{Condition.LABELS[offer.book_condition]} · {seller.name}"
        )
        rows = [
            ("phone-outline", "Teléfono", contact.phone),
            ("email-outline", "Correo", contact.email),
            ("map-marker-outline", "Dirección / punto de entrega", contact.address_or_meeting_point),
        ]
        self.ids.contact.clear_widgets()
        for icon, label, value in rows:
            if value:
                self.ids.contact.add_widget(InfoRow(icon=icon, label=label, value=value))


# ------------------------------------------------------------- vendedor
class SellerHomeScreen(BaseScreen):
    def refresh(self):
        app, store = self.app, self.app.store
        items = app.safe(
            store.open_requests,
            app.user,
            self.ids.text.text,
            self.ids.location.text,
            self.ids.budget.text,
            self.ids.condition.value,
        )
        if items is None:
            return
        self.ids.count.text = f"{len(items)} solicitud(es) abiertas"
        cards = [
            app.request_card(r, app.open_seller_request, for_seller=True)
            for r in items
        ]
        self.fill(self.ids.list, cards, "No hay solicitudes que coincidan con los filtros.")

    def clear_filters(self):
        for field in ("text", "location", "budget"):
            self.ids[field].text = ""
        self.ids.condition.value = "todas"
        self.refresh()


class SellerRequestDetailScreen(BaseScreen):
    can_offer = BooleanProperty(False)
    offer_note = StringProperty("")

    def refresh(self):
        app, store = self.app, self.app.store
        req = app.safe(store.get_request, app.user, app.current_request_id)
        if not req:
            return
        book = store.book(req.book_id)
        app.fill_book_header(self, book)
        self.ids.status.status = req.status
        reader = store.user(req.reader_id)
        rows = [("account-outline", "Lector", reader.first_name)] + app.request_info_rows(req)
        self.ids.info.clear_widgets()
        for icon, label, value in rows:
            self.ids.info.add_widget(InfoRow(icon=icon, label=label, value=value))

        mine = store.seller_active_offer(app.user, req.id)
        if mine:
            self.offer_note = f"Ya tienes una oferta activa de {format_price(mine.price)} para esta solicitud."
        elif req.status not in RequestStatus.OPEN:
            self.offer_note = "Esta solicitud ya no recibe ofertas."
        else:
            self.offer_note = ""
        self.can_offer = req.status in RequestStatus.OPEN and mine is None


class CreateOfferScreen(BaseScreen):
    def refresh(self):
        app, store = self.app, self.app.store
        req = store.requests.get(app.current_request_id)
        if not req:
            return
        book = store.book(req.book_id)
        self.ids.book_title.text = book.title
        self.ids.book_meta.text = (
            f"Busca: {Condition.LABELS[req.accepted_condition]} · "
            f"Máximo {format_price(req.max_price)} · {req.location}"
        )
        for field in ("price", "description", "notes"):
            self.ids[field].text = ""
        self.ids.condition.value = (
            req.accepted_condition if req.accepted_condition != Condition.ANY else Condition.USED
        )
        contact = store.seller_contact(app.user)
        self.ids.phone.text = contact.phone
        self.ids.email.text = contact.email or app.user.email
        self.ids.address.text = contact.address_or_meeting_point

    def publish(self):
        app = self.app
        offer = app.safe(
            app.store.create_offer,
            app.user,
            app.current_request_id,
            self.ids.price.text,
            self.ids.condition.value,
            self.ids.description.text,
            self.ids.notes.text,
            self.ids.phone.text,
            self.ids.email.text,
            self.ids.address.text,
        )
        if offer:
            app.notify("¡Oferta publicada! El lector ya puede revisarla.")
            app.go("seller_offers", reset_to="seller_home")


class SellerOffersScreen(BaseScreen):
    def refresh(self):
        app, store = self.app, self.app.store
        offers = store.seller_offers(app.user, self.ids.filter.value)
        cards = []
        for o in offers:
            req = store.requests[o.request_id]
            if o.status == OfferStatus.IN_DEAL:
                meta = "¡En coordinación! El lector está revisando tus datos de contacto para cerrar la compra."
            elif o.status == OfferStatus.ON_HOLD:
                meta = "En espera: el lector está coordinando con otra oferta. Si desiste, tu oferta volverá a activarse."
            elif o.status == OfferStatus.ACCEPTED:
                meta = "¡Trato concretado! Compra finalizada con éxito."
            elif o.status == OfferStatus.REJECTED:
                meta = "El lector concretó otra oferta."
            else:
                meta = f"Solicitud #{req.id} · {req.location} · máx. {format_price(req.max_price)}"
            cards.append(ItemCard(
                title=store.book(req.book_id).title,
                subtitle=f"{format_price(o.price)} · {Condition.LABELS[o.book_condition]}",
                meta=meta,
                status=o.status, kind="offer",
                action_text="Cancelar oferta" if o.status in (OfferStatus.PUBLISHED, OfferStatus.ON_HOLD) else "",
                action_callback=lambda _c, oid=o.id: self.cancel(oid),
                callback=lambda _c, rid=req.id: app.open_seller_request(rid),
            ))
        self.fill(self.ids.list, cards, "No tienes ofertas en esta categoría.", "tag-outline")

    def cancel(self, offer_id):
        app = self.app

        def do_cancel():
            if app.safe(app.store.cancel_offer, app.user, offer_id):
                app.notify("Oferta cancelada.")
                self.refresh()

        app.confirm("¿Cancelar oferta?", "El lector ya no podrá aceptarla.", "Cancelar oferta", do_cancel)


# ---------------------------------------------------------------- admin
class AdminHomeScreen(BaseScreen):
    """Inicio del admin: solo métricas generales y accesos rápidos."""

    def refresh(self):
        stats = self.app.store.admin_stats(self.app.user)
        for key, value in stats.items():
            self.ids["st_" + key].value = str(value)


class AdminRequestsScreen(BaseScreen):
    def refresh(self):
        app, store = self.app, self.app.store
        cards = []
        for r in store.admin_requests(app.user, self.ids.filter.value):
            book = store.book(r.book_id)
            reader = store.user(r.reader_id)
            cards.append(ItemCard(
                title=f"#{r.id} · {book.title}",
                subtitle=f"{reader.name} · {r.location} · máx. {format_price(r.max_price)}",
                meta=f"{len(store.offers_for_request(app.user, r.id))} oferta(s) · actualizada {fmt_date(r.updated_at)}",
                status=r.status, kind="request",
                action_text="Cancelar (moderar)" if r.status in RequestStatus.OPEN else "",
                action_callback=lambda _c, rid=r.id: self.moderate(rid),
            ))
        self.fill(self.ids.list, cards, "Sin registros.", "database-off-outline")

    def moderate(self, request_id):
        app = self.app

        def do_cancel():
            if app.safe(app.store.cancel_request, app.user, request_id, reason="Moderación administrativa"):
                app.notify(f"Solicitud #{request_id} cancelada por moderación.")
                self.refresh()

        app.confirm("¿Cancelar solicitud?", "Acción de moderación: quedará registrada en la actividad y el lector verá el motivo.", "Cancelar", do_cancel)


class AdminUsersScreen(BaseScreen):
    def refresh(self):
        app, store = self.app, self.app.store
        cards = []
        for u in store.admin_users(app.user):
            action = ""
            if u.role != Role.ADMIN:
                action = "Suspender" if u.status == UserStatus.ACTIVE else "Reactivar"
            cards.append(ItemCard(
                title=u.name,
                subtitle=f"{u.email} · {Role.LABELS[u.role]}",
                meta=f"Alta: {fmt_date(u.created_at)}",
                status=u.status, kind="user",
                action_text=action,
                action_callback=lambda _c, uid=u.id: self.toggle(uid),
            ))
        self.fill(self.ids.list, cards, "Sin registros.", "database-off-outline")

    def toggle(self, user_id):
        app = self.app
        target = app.store.user(user_id)
        new_status = UserStatus.SUSPENDED if target.status == UserStatus.ACTIVE else UserStatus.ACTIVE
        if app.safe(app.store.set_user_status, app.user, user_id, new_status):
            app.notify(f"{target.name}: {STATUS_LABELS['user'][new_status].lower()}.")
            self.refresh()


class AdminOffersScreen(BaseScreen):
    def refresh(self):
        app, store = self.app, self.app.store
        cards = []
        for o in store.admin_offers(app.user):
            req = store.requests[o.request_id]
            cards.append(ItemCard(
                title=f"Oferta #{o.id} · {store.book(req.book_id).title}",
                subtitle=f"{format_price(o.price)} · {Condition.LABELS[o.book_condition]} · {store.user(o.seller_id).name}",
                meta=f"Solicitud #{req.id} · {fmt_date(o.updated_at)}",
                status=o.status, kind="offer",
            ))
        self.fill(self.ids.list, cards, "Sin registros.", "database-off-outline")


class AdminActivityScreen(BaseScreen):
    """Auditoría: consulta y exportación de logs de actividad."""

    limit = NumericProperty(50)

    def refresh(self):
        app, store = self.app, self.app.store
        if app.user is None or "search" not in self.ids:
            return
        entries = store.admin_activity(app.user, limit=self.limit, text=self.ids.search.text)
        cards = []
        for entry in entries:
            actor = store.users.get(entry.actor_id)
            cards.append(ItemCard(
                title=entry.detail,
                subtitle=f"{fmt_date(entry.at)} · {actor.name if actor else 'sistema'}",
                meta=entry.action,
            ))
        self.fill(self.ids.list, cards, "Sin registros de actividad.", "text-box-search-outline")

    def export_logs(self):
        app = self.app
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"registro_actividad_{stamp}.log"
        candidates = [
            os.path.join(os.path.expanduser("~"), filename),
            os.path.join(os.path.dirname(KV_FILE), filename),
        ]
        for candidate in candidates:
            try:
                path = app.store.export_activity_log(app.user, candidate)
            except OSError:
                continue
            app.info_dialog(
                "Logs exportados",
                f"Se guardó el registro de actividad en:\n\n{path}",
            )
            return
        app.notify("No se pudo exportar el registro de actividad.")


# ==========================================================================
# Aplicación
# ==========================================================================
class DemoLibrosApp(MDApp):
    user = ObjectProperty(None, allownone=True)
    user_name = StringProperty("")

    HOME_BY_ROLE = {Role.READER: "reader_home", Role.SELLER: "seller_home", Role.ADMIN: "admin_home"}

    def build(self):
        self.title = "App de libros · Demo MVP"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"
        self.store = build_demo_store(catalog_lookup)
        self.history: list[str] = []
        self.selected_book = None
        self.current_request_id = None
        self.current_offer_id = None
        Window.bind(on_keyboard=self._on_keyboard)
        return Builder.load_file(KV_FILE)

    # ----------------------------------------------------------- navegación
    def go(self, name, reset_to=None):
        sm = self.root
        if reset_to is not None:
            self.history = [reset_to] if reset_to != name else []
        elif sm.current != name:
            self.history.append(sm.current)
        sm.transition.direction = "left"
        sm.current = name

    def back(self):
        if not self.history:
            return False
        self.root.transition.direction = "right"
        self.root.current = self.history.pop()
        return True

    def go_home(self):
        self.history = []
        self.root.transition.direction = "right"
        self.root.current = self.HOME_BY_ROLE[self.user.role]

    def _on_keyboard(self, _window, key, *_):
        if key == 27:  # Escape / botón atrás de Android
            return self.back()
        return False

    def login(self, user):
        self.user = user
        self.user_name = user.first_name
        self.history = []
        self.root.transition.direction = "left"
        self.root.current = self.HOME_BY_ROLE[user.role]

    def logout(self):
        self.user = None
        self.user_name = ""
        self.history = []
        self.root.transition.direction = "right"
        self.root.current = "login"

    # ----------------------------------------------------------- feedback
    def safe(self, fn, *args, **kwargs):
        """Ejecuta un caso de uso y muestra los errores de negocio al usuario."""
        try:
            result = fn(*args, **kwargs)
            return True if result is None else result
        except DomainError as exc:
            self.notify(str(exc))
            return None

    def notify(self, text):
        MDSnackbar(
            MDSnackbarText(text=text),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.92,
        ).open()

    def _dialog(self, title, text, buttons):
        dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogSupportingText(text=text),
            MDDialogButtonContainer(Widget(), *buttons, spacing="8dp"),
        )
        return dialog

    def info_dialog(self, title, text):
        ok = MDButton(MDButtonText(text="Entendido"), style="text")
        dialog = self._dialog(title, text, [ok])
        ok.bind(on_release=lambda *_: dialog.dismiss())
        dialog.open()

    def confirm(self, title, text, confirm_text, on_confirm):
        no = MDButton(MDButtonText(text="Volver"), style="text")
        yes = MDButton(MDButtonText(text=confirm_text), style="filled")
        dialog = self._dialog(title, text, [no, yes])
        no.bind(on_release=lambda *_: dialog.dismiss())

        def _yes(*_):
            dialog.dismiss()
            on_confirm()

        yes.bind(on_release=_yes)
        dialog.open()

    # ---------------------------------------------------- helpers de vista
    def request_card(self, req, on_open, badge="", for_seller=False):
        book = self.store.book(req.book_id)
        offers = self.store.active_offer_count(req.id)
        parts = [req.location, f"máx. {format_price(req.max_price)}", Condition.LABELS[req.accepted_condition]]
        if not badge and not for_seller and req.status in RequestStatus.OPEN:
            badge = f"{offers} oferta(s) activa(s)"
        return RequestCard(
            title=book.title,
            subtitle=book.authors_text,
            meta=" · ".join(parts),
            cover=book.cover_url,
            status=req.status,
            badge=badge,
            callback=lambda _c, rid=req.id: on_open(rid),
        )

    def request_info_rows(self, req):
        return [
            ("cash", "Precio máximo", format_price(req.max_price)),
            ("book-open-variant", "Condición aceptada", Condition.LABELS[req.accepted_condition]),
            ("map-marker-outline", "Ubicación", req.location),
            ("truck-outline", "Entrega", Delivery.LABELS[req.delivery_preference]),
            ("note-text-outline", "Notas", req.notes or "—"),
            ("calendar", "Publicada", fmt_date(req.created_at)),
        ]

    @staticmethod
    def fill_book_header(screen, book):
        screen.ids.cover.source = book.cover_url
        screen.ids.book_title.text = book.title
        screen.ids.book_meta.text = (
            f"{book.authors_text}\n"
            + " · ".join(filter(None, [book.publisher, book.published_date[:4]]))
            + f"\nISBN {book.isbn or '—'}"
        )

    # -------------------------------------------------------- acciones
    def start_book_search(self, query="", mode="titulo"):
        self.go("book_search")
        self.root.get_screen("book_search").prepare(query, mode)

    def select_book(self, book_data):
        book = self.safe(self.store.upsert_book, book_data)
        if book:
            self.selected_book = book
            self.go("create_request")

    def open_reader_request(self, request_id):
        self.current_request_id = request_id
        self.go("reader_request_detail")

    def open_offer(self, offer_id):
        self.current_offer_id = offer_id
        self.go("offer_detail")

    def open_seller_request(self, request_id):
        self.current_request_id = request_id
        self.go("seller_request_detail")


if __name__ == "__main__":
    DemoLibrosApp().run()
