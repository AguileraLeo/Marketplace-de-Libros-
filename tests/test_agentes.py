"""Pruebas de los agentes en vivo (SPEC-006) contra un servidor real levantado en la prueba.

Todo en una carpeta temporal. Sin FastAPI ni uvicorn instalados, se omiten.
"""

import json
import os
import socket
import sys
import tempfile
import threading
import time
import unittest
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import uvicorn
    from backend.servidor import crear_app
except ImportError:
    raise unittest.SkipTest("Instala backend/requirements.txt para probar los agentes.")

from backend.agentes import Demo  # noqa: E402
from services.persistence import load_store  # noqa: E402


class AgentesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.carpeta = tempfile.TemporaryDirectory()
        cls.datos = os.path.join(cls.carpeta.name, "datos.json")
        with socket.socket() as s:  # un puerto libre
            s.bind(("127.0.0.1", 0))
            puerto = s.getsockname()[1]
        cls.url = f"http://127.0.0.1:{puerto}"
        cls.servidor = uvicorn.Server(uvicorn.Config(crear_app(cls.datos), host="127.0.0.1", port=puerto, log_level="error"))
        threading.Thread(target=cls.servidor.run, daemon=True).start()
        for _ in range(100):
            if cls.servidor.started:
                break
            time.sleep(0.05)
        cls.log = []
        Demo(cls.url, lectores=4, vendedores=3, semilla=3, salida=cls.log.append).correr(minutos=0.05, ritmo=(0, 0.02))

    @classmethod
    def tearDownClass(cls):
        cls.servidor.should_exit = True
        cls.carpeta.cleanup()

    def test_los_agentes_usan_la_app_por_la_api(self):  # criterio 2
        store = load_store(self.datos)
        self.assertEqual(len(store.users), 7)
        self.assertGreater(len(store.requests), 0)
        acciones = {e.action for e in store.activity}
        # al registrarse ya reciben la sesión: no hay evento login aparte
        self.assertTrue({"registro", "solicitud_publicada", "oferta_publicada"} <= acciones, acciones)

    def test_cuentas_y_contactos_ficticios(self):  # criterio 1
        store = load_store(self.datos)
        for u in store.users.values():
            self.assertTrue(u.email.endswith("@bookwho.test"), u.email)
            self.assertTrue(u.name.endswith("(sim)"), u.name)
        for c in store.contacts.values():
            self.assertTrue(not c.phone or c.phone.startswith("+56 9 0000"), c.phone)

    def test_el_panel_los_presenta_como_agentes(self):  # criterio 3
        with urllib.request.urlopen(f"{self.url}/api/metricas", timeout=10) as r:
            texto = r.read().decode("utf-8")
        m = json.loads(texto)
        self.assertGreater(m["origen"]["agentes_simulados"], 0)
        self.assertEqual(m["origen"]["personas"], 0)
        self.assertIn("agentes simulados", m["aviso"])
        self.assertNotIn("@", texto)

    def test_el_registro_de_acciones_no_muestra_correos(self):
        self.assertTrue(self.log)
        for linea in self.log:
            self.assertIn("(sim)", linea)
            self.assertNotIn("@", linea)


if __name__ == "__main__":
    unittest.main()
