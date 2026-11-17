"""Widgets reutilizables y formato visual compartido por las vistas KV."""

import os

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    ListProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton
from kivymd.uix.card import MDCard
from kivymd.uix.relativelayout import MDRelativeLayout

from models.store import OfferStatus, RequestStatus, UserStatus
from services.books_api import download_and_cache_cover, get_cover_cache_path


ACCENT = "#1F4D3A"
PAPER = "#FBFAF7"

# (punto, texto) por estado — mismos colores en todas las pantallas.
# Solicitud y oferta comparten "PUBLICADA" y "CANCELADA", así que comparten color.
GRAY = ("#A8A397", "#3F3D38")
GREEN = (ACCENT, ACCENT)
AMBER = ("#B26B00", "#8A5300")
RED = ("#A33A2F", "#7A1C14")
STATUS_COLORS = {
    RequestStatus.PUBLISHED: GRAY,
    RequestStatus.WITH_OFFERS: GREEN,
    RequestStatus.IN_DEAL: AMBER,
    RequestStatus.RESOLVED: GREEN,
    RequestStatus.CANCELLED: RED,
    OfferStatus.IN_DEAL: AMBER,
    OfferStatus.ON_HOLD: GRAY,
    OfferStatus.ACCEPTED: GREEN,
    OfferStatus.REJECTED: GRAY,
    UserStatus.ACTIVE: GREEN,
    UserStatus.SUSPENDED: RED,
    ("offer", OfferStatus.PUBLISHED): GREEN,  # "Activa": una oferta publicada sí está viva
}
STATUS_LABELS = {
    "request": RequestStatus.LABELS,
    "offer": OfferStatus.LABELS,
    "user": {UserStatus.ACTIVE: "Activo", UserStatus.SUSPENDED: "Suspendido"},
}


def fmt_date(value) -> str:
    return value.strftime("%d/%m/%Y %H:%M")


# ==========================================================================
# Widgets reutilizables (su aspecto está en views/libros.kv)
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
    dot = ColorProperty(GRAY[0])
    fg = ColorProperty(GRAY[1])

    def on_status(self, *_):
        self._update()

    def on_kind(self, *_):
        self._update()

    def _update(self):
        from kivy.utils import get_color_from_hex as c

        dot, fg = STATUS_COLORS.get((self.kind, self.status)) or STATUS_COLORS.get(self.status, GRAY)
        self.dot, self.fg = c(dot), c(fg)
        self.text = STATUS_LABELS.get(self.kind, {}).get(self.status, self.status)


class WideButton(MDButton):
    """MDButton a todo el ancho con icono + texto centrados."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind(size=Clock.create_trigger(self.adjust_pos))

    def adjust_pos(self, *args) -> None:
        text, icon = self._button_text, self._button_icon
        text_w = text.texture_size[0] if text else 0
        icon_w = icon.width + dp(8) if icon else 0
        start = (self.width - text_w - icon_w) / 2
        if icon:
            icon.x = start
        if text:
            text.x = start + icon_w


class SegmentButton(ButtonBehavior, MDBoxLayout):
    text = StringProperty()
    selected = BooleanProperty(False)


class SegmentedRow(MDBoxLayout):
    """Control segmentado de selección única (estilo de la maqueta editorial)."""

    options = ListProperty()  # [(valor, etiqueta), ...]
    value = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._trigger = Clock.create_trigger(self._rebuild)
        self.bind(options=self._trigger, value=self._trigger)
        self._trigger()

    def _rebuild(self, *_):
        self.clear_widgets()
        for value, label in self.options:
            btn = SegmentButton(text=label, selected=value == self.value)
            btn.bind(on_release=lambda _b, v=value: setattr(self, "value", v))
            self.add_widget(btn)


class RequestRow(ButtonBehavior, MDBoxLayout):
    title = StringProperty()
    author = StringProperty()
    meta = StringProperty()
    price = StringProperty()
    cover = StringProperty()
    status = StringProperty()
    detail = StringProperty()
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
    icon = StringProperty("chart-box-outline")


class InfoRow(MDBoxLayout):
    icon = StringProperty("information-outline")
    label = StringProperty()
    value = StringProperty()


class EmptyState(MDBoxLayout):
    icon = StringProperty("book-search-outline")
    text = StringProperty()
