"""Controlador de aplicacion: configuracion, ciclo de vida y navegacion."""

import os
import sys
import types
from pathlib import Path

from kivy.utils import platform

try:
    import materialshapes.kivy_widget  # noqa: F401
except ImportError:
    # Android: materialshapes requiere pycairo; la app no usa FitImage.
    _shape = types.ModuleType("materialshapes.kivy_widget")
    _shape.MaterialShape = type("MaterialShape", (), {})
    sys.modules["materialshapes"] = types.ModuleType("materialshapes")
    sys.modules["materialshapes.kivy_widget"] = _shape

from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogButtonContainer,
    MDDialogHeadlineText,
    MDDialogSupportingText,
)
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

# Importar las pantallas registra sus clases antes de cargar las reglas KV.
from controllers import screen_controllers as _screen_controllers
from models.store import (
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
from services.books_api import catalog_lookup
from services import notifications, persistence, remote_config
from services.locations import proximity_label
from views.components import ACCENT, PAPER, STATUS_LABELS, RequestRow, fmt_date

BASE_DIR = str(Path(__file__).resolve().parents[1])
KV_FILE = os.path.join(BASE_DIR, "views", "libros.kv")
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")

LabelBase.register(
    name="SourceSerif",
    fn_regular=os.path.join(FONTS_DIR, "SourceSerif4-Semibold.ttf"),
    fn_bold=os.path.join(FONTS_DIR, "SourceSerif4-Semibold.ttf"),
)
LabelBase.register(
    name="IBMPlexSans",
    fn_regular=os.path.join(FONTS_DIR, "IBMPlexSans-Regular.ttf"),
    fn_bold=os.path.join(FONTS_DIR, "IBMPlexSans-SemiBold.ttf"),
)


class DemoLibrosApp(MDApp):
    user = ObjectProperty(None, allownone=True)
    user_name = StringProperty("")
    banner = StringProperty(remote_config.DEFAULTS["banner"])  # lo reemplaza la config remota

    HOME_BY_ROLE = {Role.READER: "reader_home", Role.SELLER: "seller_home", Role.ADMIN: "admin_home"}

    def build(self):
        self.title = "BookWho? · Demo MVP"
        self.theme_cls.theme_style = "Light"
        # Material You deriva el esquema desde el acento; luego se fijan exactos el primario y el fondo.
        self.theme_cls.on_colors = self._apply_brand_colors
        self.theme_cls.primary_palette = ACCENT
        fonts = {"Display": "SourceSerif", "Headline": "SourceSerif", "Title": "SourceSerif",
                 "Body": "IBMPlexSans", "Label": "IBMPlexSans"}
        for style, font in fonts.items():
            for role in self.theme_cls.font_styles[style]:
                self.theme_cls.font_styles[style][role]["font-name"] = font
                if font == "SourceSerif":
                    self.theme_cls.font_styles[style][role]["line-height"] = 1.15
        # En Android el JSON va en user_data_dir; en escritorio se mantiene en data/user.
        data_dir = self.user_data_dir if platform == "android" else os.path.join(BASE_DIR, "data", "user")
        os.makedirs(data_dir, exist_ok=True)
        self.data_file = os.path.join(data_dir, "data.json")
        if platform != "android":
            legacy_data_file = os.path.join(BASE_DIR, "data.json")
            persistence.migrate_legacy_data_file(legacy_data_file, self.data_file)
        self.store = persistence.load_store(self.data_file) or build_demo_store(catalog_lookup)
        self.save()
        self.history: list[str] = []
        self.selected_book = None
        self.current_request_id = None
        self.current_offer_id = None
        Window.bind(on_keyboard=self._on_keyboard)
        return Builder.load_file(KV_FILE)

    def on_start(self):
        notifications.request_permission()
        remote_config.fetch(self.apply_remote_config)

    def apply_remote_config(self, config):
        self.banner = config["banner"]

    def save(self):
        persistence.save_store(self.store, self.data_file)

    def on_pause(self):  # Android puede cerrar la app en segundo plano sin llamar on_stop
        self.save()
        return True

    def on_stop(self):
        self.save()

    def _apply_brand_colors(self):
        from kivy.utils import get_color_from_hex as c
        self.theme_cls.primaryColor = c(ACCENT)
        self.theme_cls.backgroundColor = c(PAPER)
        self.theme_cls.surfaceColor = c(PAPER)

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
        if user.role == Role.READER:
            n = sum(self.store.active_offer_count(r.id) for r in self.store.reader_requests(user)
                    if r.status in RequestStatus.OPEN)
            if n:
                notifications.send("Tienes ofertas por revisar", f"{n} oferta(s) activa(s) en tus solicitudes.")

    def logout(self):
        self.user = None
        self.user_name = ""
        self.history = []
        self.root.transition.direction = "right"
        self.root.current = "login"

    # ----------------------------------------------------------- feedback
    def safe(self, fn, *args, **kwargs):
        """Ejecuta un caso de uso, guarda el JSON si funcionó y muestra los errores de negocio."""
        try:
            result = fn(*args, **kwargs)
            self.save()
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
    def request_card(self, req, on_open, for_seller=False):
        """Fila editorial de una solicitud, usada en todas las listas de solicitudes."""
        book = self.store.book(req.book_id)
        if for_seller:
            detail = proximity_label(self.user.location, req.location)
        elif req.status in RequestStatus.OPEN:
            n = self.store.active_offer_count(req.id)
            detail = "sin ofertas aún" if n == 0 else f"{n} activa" + ("s" if n > 1 else "")
        else:
            detail = ""
        condition = "Nuevo o usado" if req.accepted_condition == Condition.ANY else Condition.LABELS[req.accepted_condition]
        price = (
            "[b]Sin tope[/b]" if req.max_price is None
            else f"[size=12sp][color=#6F6B62]máx. [/color][/size][b]{format_price(req.max_price)}[/b]"
        )
        return RequestRow(
            title=book.title,
            author=book.authors_text,
            meta=f"{req.location} · {condition}",
            price=price,
            cover=book.cover_url,
            status=req.status,
            detail=f"· {detail}" if detail else "",
            callback=lambda _r, rid=req.id: on_open(rid),
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
