"""Pruebas de los agentes en vivo (SPEC-006) y del historial cargado en el servidor, contra un servidor
real levantado en la prueba. Todo en carpetas temporales. Sin FastAPI ni uvicorn instalados, se omiten.
"""

import http.client
import json
import os
import shutil
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

import analitica  # noqa: E402
import simulador  # noqa: E402
from backend.agentes import Demo  # noqa: E402
from services.persistence import load_store  # noqa: E402


def levantar(app):
    """Servidor uvicorn real en un puerto libre; devuelve (url, servidor)."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        puerto = s.getsockname()[1]
    servidor = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=puerto, log_level="error"))
    threading.Thread(target=servidor.run, daemon=True).start()
    for _ in range(100):
        if servidor.started:
            break
        time.sleep(0.05)
    return f"http://127.0.0.1:{puerto}", servidor


def leer(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return r.read().decode("utf-8")


class AgentesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.carpeta = tempfile.TemporaryDirectory()
        cls.datos = os.path.join(cls.carpeta.name, "datos.json")
        cls.url, cls.servidor = levantar(crear_app(cls.datos))
        cls.log = []
        Demo(cls.url, lectores=4, vendedores=3, semilla=3, salida=cls.log.append).correr(minutos=0.05, ritmo=(0, 0.02))

    @classmethod
    def tearDownClass(cls):
        cls.servidor.should_exit = True
        cls.carpeta.cleanup()

    def test_los_agentes_usan_la_app_por_la_api(self):  # criterio 2
        store = load_store(self.datos)
        self.assertGreaterEqual(len(store.users), 7)  # más los nuevos que alcanzaron a llegar
        acciones = {e.action for e in store.activity}
        self.assertTrue({"registro", "login", "solicitud_publicada", "oferta_publicada"} <= acciones, acciones)

    def test_cuentas_y_contactos_ficticios(self):  # criterio 1
        store = load_store(self.datos)
        for u in store.users.values():
            self.assertTrue(u.email.endswith("@bookwho.test"), u.email)
            self.assertTrue(u.name.endswith("(sim)"), u.name)
        for c in store.contacts.values():
            self.assertTrue(not c.phone or c.phone.startswith("+56 9 0000"), c.phone)

    def test_el_panel_los_presenta_como_agentes(self):  # criterio 3
        texto = leer(f"{self.url}/en-vivo/metricas.json")
        m = json.loads(texto)
        self.assertGreater(m["origen"]["agentes_simulados"], 0)
        self.assertEqual(m["origen"]["personas"], 0)
        self.assertIn("agentes simulados", m["aviso"])
        self.assertNotIn("@", texto)
        self.assertIn("Panel de métricas", leer(f"{self.url}/en-vivo/"))

    def test_el_registro_de_acciones_no_muestra_correos(self):
        self.assertTrue(self.log)
        for linea in self.log:
            self.assertIn("(sim)", linea)
            self.assertNotIn("@", linea)

    def test_la_redireccion_no_lleva_a_otro_sitio(self):
        conexion = http.client.HTTPConnection(self.url.removeprefix("http://"), timeout=10)
        conexion.request("GET", "/en-vivo?ruta=https://sitio-ajeno.example")
        respuesta = conexion.getresponse()
        self.assertEqual(respuesta.getheader("location"), "/en-vivo/")
        conexion.close()


class HistorialTest(unittest.TestCase):
    """El historial de la simulación cargado en el servidor: sin cuentas demo y con los mismos KPIs."""

    @classmethod
    def setUpClass(cls):
        cls.carpeta = tempfile.TemporaryDirectory()
        cls.simulacion = os.path.join(cls.carpeta.name, "sim.json")
        simulador.simular(salida=cls.simulacion, semilla=5, dias=5, inicio="2026-11-03", lectores=8, vendedores=4)
        cls.datos = os.path.join(cls.carpeta.name, "servidor.json")
        shutil.copy(cls.simulacion, cls.datos)
        cls.url, cls.servidor = levantar(crear_app(cls.datos))
        cls.kpis_al_cargar = json.loads(leer(f"{cls.url}/en-vivo/metricas.json"))["kpis"]  # antes de que actúen los agentes

    @classmethod
    def tearDownClass(cls):
        cls.servidor.should_exit = True
        cls.carpeta.cleanup()

    def test_no_quedan_cuentas_demo(self):
        correos = {u.email for u in load_store(self.datos).users.values()}
        self.assertFalse(correos & analitica.CORREOS_DEMO)
        pedido = urllib.request.Request(f"{self.url}/api/sesion", method="POST", headers={"Content-Type": "application/json"},
                                        data=json.dumps({"correo": "admin@demo.cl", "clave": "admin"}).encode())
        with self.assertRaises(urllib.error.HTTPError):
            urllib.request.urlopen(pedido, timeout=10)

    def test_los_kpis_son_los_de_la_simulacion(self):
        usuarios, eventos = analitica.cargar(self.simulacion)
        r = analitica.calcular(eventos, analitica.ids_excluidos(usuarios, analitica.CORREOS_DEMO))
        k = self.kpis_al_cargar
        self.assertEqual((k["resolucion_pct"], k["respuesta_pct"], k["horas_primera_oferta"]),
                         (r["kpi_tasa_resolucion"], r["kpi_tasa_respuesta"], r["kpi_horas_primera_oferta"]))

    def test_los_agentes_siguen_con_las_cuentas_del_historial(self):
        antes = len(load_store(self.datos).users)
        Demo(self.url, lectores=8, vendedores=4, semilla=9, salida=lambda _t: None).correr(minutos=0.02, ritmo=(0, 0.01))
        store = load_store(self.datos)
        self.assertGreater(sum(e.action == "login" for e in store.activity), 0)  # entraron, no se registraron de nuevo
        nuevos = len(store.users) - antes
        self.assertLessEqual(nuevos, 8)  # solo pueden sumarse las personas nuevas de la demo


if __name__ == "__main__":
    unittest.main()
