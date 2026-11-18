"""Adaptador de traducción para widgets y controladores; sin cambios al dominio."""
from kivymd.app import MDApp
from views.access_texts import translate


def tr(text, **values):
    app = MDApp.get_running_app()
    return translate(text, getattr(app, 'language', 'es'), **values)


def format_price(value):
    from models.store import format_price as domain_format_price
    return tr(domain_format_price(value))
