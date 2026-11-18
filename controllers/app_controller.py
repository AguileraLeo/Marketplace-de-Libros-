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

from kivy.base import ExceptionHandler, ExceptionManager
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import DictProperty, ObjectProperty, StringProperty
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
    RequestStatus,
    Role,
    build_demo_store,
)
from services.books_api import catalog_lookup
from services import notifications, persistence, remote_config, remoto
from services.locations import proximity_label
from views.localization import tr, format_price
from views.components import ACCENT, LIGHT_PALETTE, RequestRow, fmt_date
from views.access_texts import SUPPORTED_LANGUAGES, translate, translate_error

BASE_DIR = str(Path(__file__).resolve().parents[1])
KV_FILE = os.path.join(BASE_DIR, "views", "libros.kv")
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")

LabelBase.register(
    name="Manrope",
    fn_regular=os.path.join(FONTS_DIR, "Manrope-Regular.ttf"),
    fn_bold=os.path.join(FONTS_DIR, "Manrope-SemiBold.ttf"),
)


class _AvisoRemoto(ExceptionHandler):
    """Modo servidor: un error de red o de sesión al refrescar una pantalla se avisa y no cierra la app."""

    def __init__(self, app):
        super().__init__()
        self.app = app

    def handle_exception(self, inst):
        if not isinstance(inst, DomainError):
            return ExceptionManager.RAISE
        Clock.schedule_once(lambda *_: self.app.aviso_remoto(inst))
        return ExceptionManager.PASS


class DemoLibrosApp(MDApp):
    language = StringProperty("es")
    ui_palette = DictProperty(LIGHT_PALETTE)
    user = ObjectProperty(None, allownone=True)
    user_name = StringProperty("")
    banner = StringProperty(remote_config.DEFAULTS["banner"])  # lo reemplaza la config remota

    HOME_BY_ROLE = {Role.READER: "reader_home", Role.SELLER: "seller_home", Role.ADMIN: "admin_home"}

    def build(self):
        self.title = tr("BookWho? · Tu próximo libro")
        self.theme_cls.theme_style = "Light"
        # Material You deriva el esquema desde el acento; luego se fijan exactos el primario y el fondo.
        self.theme_cls.on_colors = self._apply_brand_colors
        self.theme_cls.primary_palette = ACCENT
        for style in ("Display", "Headline", "Title", "Body", "Label"):
            for role in self.theme_cls.font_styles[style]:
                self.theme_cls.font_styles[style][role]["font-name"] = "Manrope"
                self.theme_cls.font_styles[style][role]["line-height"] = 1.08 if style in ("Display", "Headline", "Title") else 1.1
        # Modo servidor (SPEC-005): si hay servidor configurado y responde, el modelo es remoto y compartido.
        servidor = remoto.servidor_configurado()
        self.remoto = remoto.RemoteStore(servidor) if servidor else None
        if self.remoto and self.remoto.disponible():
            self.store = self.remoto
            ExceptionManager.add_handler(_AvisoRemoto(self))
        else:
            if self.remoto:
                Clock.schedule_once(lambda *_: self.notify(tr('Modo sin conexión: los datos quedan solo en este teléfono.')), 2)
            self.remoto = None
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
        # En Android, al enfocar un campo la pantalla se desplaza para que el teclado no lo tape.
        Window.softinput_mode = "below_target"
        return Builder.load_file(KV_FILE)

    def on_start(self):
        notifications.request_permission()
        remote_config.fetch(self.apply_remote_config)

    def apply_remote_config(self, config):
        self.banner = config["banner"]

    def save(self) -> bool:
        """Guarda el Store en data.json. Si el disco falla devuelve False en vez de cerrar la app."""
        if self.remoto:
            return True  # modo servidor: cada acción ya quedó guardada en el servidor
        try:
            persistence.save_store(self.store, self.data_file)
            return True
        except OSError as exc:  # disco lleno, sin permisos, carpeta inexistente…
            Logger.error(f"BookWho: no se pudo guardar {self.data_file}: {exc}")
            return False

    def on_pause(self):  # Android puede cerrar la app en segundo plano sin llamar on_stop
        self.save()
        return True

    def on_stop(self):
        self.save()

    def _apply_brand_colors(self):
        from kivy.utils import get_color_from_hex as c
        colors = LIGHT_PALETTE
        self.ui_palette = dict(colors)
        self.theme_cls.primaryColor = c(colors["accent"])
        self.theme_cls.backgroundColor = c(colors["background"])
        self.theme_cls.surfaceColor = c(colors["background"])
        self.theme_cls.onPrimaryColor = c(colors["on_accent"])
        self.theme_cls.onSurfaceColor = c(colors["ink"])
        self.theme_cls.onSurfaceVariantColor = c(colors["muted"])
        self.theme_cls.primaryContainerColor = c(colors["soft"])
        self.theme_cls.onPrimaryContainerColor = c(colors["accent"])
        self.theme_cls.outlineColor = c(colors["muted"])
        self.theme_cls.outlineVariantColor = c(colors["rule"])

    def ui_text(self, text, language=None):
        return translate(text, language or self.language)

    def set_language(self, language):
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError("Idioma no disponible")
        self.language = language
        self.title = self.ui_text("BookWho? · Tu próximo libro")

    def show_language_picker(self):
        buttons = [MDButton(MDButtonText(text=label), style="text")
                   for label in ("Español", "English", self.ui_text("Cerrar"))]
        dialog = self._dialog(
            self.ui_text("Seleccionar idioma"),
            self.ui_text("Idioma de la aplicación"),
            buttons,
        )
        def choose(language):
            self.set_language(language)
            dialog.dismiss()
        buttons[0].bind(on_release=lambda *_: choose("es"))
        buttons[1].bind(on_release=lambda *_: choose("en"))
        buttons[2].bind(on_release=lambda *_: dialog.dismiss())
        dialog.open()
        return dialog

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
                notifications.send(tr('Tienes ofertas por revisar'), tr('{v0} oferta(s) activa(s) en tus solicitudes.', v0=n))

    def logout(self):
        if self.remoto:
            self.remoto.token = None
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
        except DomainError as exc:
            self.aviso_remoto(exc)
            return None
        if not self.save():
            # Lo que se ve debe ser lo que quedó guardado: se vuelve al último data.json
            # (así, si la persona reintenta, la acción no queda duplicada).
            self.store = persistence.load_store(self.data_file) or self.store
            self.notify(tr('No se pudieron guardar los cambios.'))
            return None
        return True if result is None else result

    def aviso_remoto(self, exc):
        """Muestra un error de negocio; si la sesión del servidor venció, vuelve al login."""
        self.notify(str(exc))
        if isinstance(exc, remoto.SesionVencida) and self.user is not None:
            self.logout()

    def notify(self, text):
        text = translate_error(text, self.language)
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
        ok = MDButton(MDButtonText(text=tr('Entendido')), style="text")
        dialog = self._dialog(title, text, [ok])
        ok.bind(on_release=lambda *_: dialog.dismiss())
        dialog.open()

    def confirm(self, title, text, confirm_text, on_confirm):
        no = MDButton(MDButtonText(text=tr('Volver')), style="text")
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
        """Tarjeta de solicitud compartida por las listas del lector y vendedor."""
        book = self.store.book(req.book_id)
        if for_seller:
            detail = proximity_label(self.user.location, req.location)
            if detail.startswith("Otra región ("):
                detail = tr("Otra región ({v0})", v0=detail[len("Otra región ("):-1])
            else:
                detail = tr(detail)
        elif req.status in RequestStatus.OPEN:
            n = self.store.active_offer_count(req.id)
            detail = tr('Sin ofertas todavía') if n == 0 else tr('{v0} oferta', v0=n) + (tr('s') if n > 1 else "") + tr(' por revisar')
        else:
            detail = ""
        condition = tr('Nuevo o usado') if req.accepted_condition == Condition.ANY else tr(Condition.LABELS[req.accepted_condition])
        price = (
            tr('[b]Sin tope[/b]') if req.max_price is None
            else tr('[size=12sp]Máximo [/size][b]{v1}[/b]', v1=format_price(req.max_price))
        )
        return RequestRow(
            title=book.title,
            author=book.authors_text,
            meta=f"{req.location} · {condition}",
            price=price,
            cover=book.cover_url,
            status=req.status,
            detail=detail,
            callback=lambda _r, rid=req.id: on_open(rid),
        )

    def request_info_rows(self, req):
        return [
            ("cash", tr('Precio máximo'), format_price(req.max_price)),
            ("book-open-variant", tr('Condición aceptada'), tr(Condition.LABELS[req.accepted_condition])),
            ("map-marker-outline", tr('Ubicación'), req.location),
            ("truck-outline", tr('Entrega'), tr(Delivery.LABELS[req.delivery_preference])),
            ("note-text-outline", tr('Notas'), req.notes or "—"),
            ("calendar", tr('Publicada'), fmt_date(req.created_at)),
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
