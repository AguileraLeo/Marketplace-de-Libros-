"""
Notificaciones locales con plyer (las genera el propio dispositivo, no necesitan internet).

En Android 13+ hay que pedir el permiso POST_NOTIFICATIONS en tiempo de ejecución.
"""

from kivy.utils import platform

TIMEOUT = 5  # segundos visible (escritorio)


def request_permission() -> None:
    if platform == "android":
        from android.permissions import Permission, request_permissions

        request_permissions([Permission.POST_NOTIFICATIONS])


def _android_notification():
    """plyer 2.1.0 crea el PendingIntent con flag 0 y Android 12+ lo rechaza: se corrige solo ese paso."""
    from android import python_act
    from jnius import autoclass
    from plyer.platforms.android.notification import AndroidNotification

    Intent = autoclass("android.content.Intent")
    PendingIntent = autoclass("android.app.PendingIntent")

    class FixedNotification(AndroidNotification):
        def _set_open_behavior(self, notification):
            context = autoclass("org.kivy.android.PythonActivity").mActivity.getApplicationContext()
            intent = Intent(context, python_act)
            intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)
            intent.setAction(Intent.ACTION_MAIN)
            intent.addCategory(Intent.CATEGORY_LAUNCHER)
            pending = PendingIntent.getActivity(context, 0, intent, PendingIntent.FLAG_IMMUTABLE)
            notification.setContentIntent(pending)
            notification.setAutoCancel(True)

    return FixedNotification()


def send(title: str, message: str) -> bool:
    """Muestra la notificación del sistema. Si el sistema no la soporta, la app sigue igual."""
    try:
        if platform == "android":
            notification = _android_notification()
        else:
            from plyer import notification
        notification.notify(title=title, message=message, app_name="BookWho?", timeout=TIMEOUT)
        return True
    except Exception:  # sin backend nativo (p. ej. Linux sin notify-send): no es un error fatal
        return False
