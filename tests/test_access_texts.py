"""La traducción de la interfaz conserva datos y errores originales del dominio."""
import unittest
from views.access_texts import ENGLISH, translate, translate_error
from string import Formatter


class AccessTextsTest(unittest.TestCase):
    def test_identidades_y_contenido_externo_se_conservan(self):
        for text in ('soporte@quadcorestore.com', 'BookWho?',
                     'El Hobbit · J. R. R. Tolkien', 'Mensaje del servidor: sin conexión'):
            with self.subTest(text=text):
                self.assertEqual(translate(text, 'en'), text)

    def test_espanol_conserva_el_original(self):
        self.assertEqual(translate('Iniciar sesión', 'es'), 'Iniciar sesión')
        self.assertEqual(translate('Iniciar sesión', 'fr'), 'Iniciar sesión')

    def test_ingles_explica_limites_reales(self):
        self.assertEqual(translate('Iniciar sesión', 'en'), 'Sign in')
        self.assertEqual(translate('Todavía no disponible.', 'en'), 'Not available yet.')
        self.assertIn('not yet active', translate('Correo informativo · aún no habilitado', 'en'))
        self.assertEqual(translate('Idioma de la aplicación', 'en'), 'Application language')

    def test_plantillas_conservan_campos_y_datos_del_usuario(self):
        for original, english in ENGLISH.items():
            with self.subTest(original=original):
                fields = lambda text: {key for _, key, _, _ in Formatter().parse(text) if key}
                self.assertEqual(fields(original), fields(english))
        self.assertEqual(translate('¡Bienvenido/a, {v1}!', 'en', v1='Ana {lectora}'),
                         'Welcome, Ana {lectora}!')

    def test_errores_del_dominio_se_traducen_sin_cambiar_el_original(self):
        from models.store import Store, ValidationError
        store = Store()
        with self.assertRaises(ValidationError) as raised:
            store.authenticate('desconocido@example.com', 'incorrecta')
        original = str(raised.exception)
        self.assertEqual(translate_error(original, 'en'), 'Incorrect email or password.')
        self.assertEqual(str(raised.exception), original)
        self.assertEqual(translate_error('El precio debe ser mayor que 0.', 'en'),
                         'The price must be greater than 0.')
        unknown = 'Respuesta externa desconocida {sin formato}'
        self.assertEqual(translate_error(unknown, 'en'), unknown)


if __name__ == '__main__':
    unittest.main()
