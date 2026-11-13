"""Punto de entrada de la app BookWho."""

from kivy.utils import platform

if platform not in ("android", "ios"):
    from kivy.config import Config

    Config.set("graphics", "width", "420")
    Config.set("graphics", "height", "860")

from controllers.app_controller import DemoLibrosApp


if __name__ == "__main__":
    DemoLibrosApp().run()
