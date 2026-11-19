"""Pruebas de simulador.py (SPEC-003): datos ficticios, reproducibles y legibles por analitica.py.

Todo se hace en carpetas temporales: nunca se toca data/user/ ni data/simulacion/.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import analitica  # noqa: E402
import simulador  # noqa: E402

import models.store as modelo


def setUpModule():
    # SPEC-012: acelerar las cuentas ficticias y restaurar el coste de la app al terminar.
    unittest.addModuleCleanup(setattr, modelo, "PBKDF2_ITERATIONS", modelo.PBKDF2_ITERATIONS)
    modelo.PBKDF2_ITERATIONS = 1_000

PARAMETROS = dict(semilla=7, dias=6, inicio="2026-11-03", lectores=8, vendedores=4)


class SimuladorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.carpeta = tempfile.TemporaryDirectory()
        cls.ruta = os.path.join(cls.carpeta.name, "sim.json")
        cls.resumen = simulador.simular(salida=cls.ruta, **PARAMETROS)
        cls.archivos = sorted(os.listdir(cls.carpeta.name))
        with open(cls.ruta, encoding="utf-8") as f:
            cls.data = json.load(f)

    @classmethod
    def tearDownClass(cls):
        cls.carpeta.cleanup()

    def test_misma_semilla_mismo_archivo(self):  # criterio 3
        with tempfile.TemporaryDirectory() as d:
            otra = os.path.join(d, "sim.json")
            simulador.simular(salida=otra, **PARAMETROS)
            with open(otra, "rb") as a, open(self.ruta, "rb") as b:
                self.assertEqual(a.read(), b.read())

    def test_escribe_solo_donde_se_le_indica(self):  # criterio 4
        self.assertEqual(self.archivos, ["sim.json", "sim_resumen.json"])
        with self.assertRaises(SystemExit):
            simulador.simular(salida=os.path.join(RAIZ, "data", "user", "data.json"), **PARAMETROS)

    def test_cuentas_y_contactos_ficticios(self):  # criterio 2
        simuladas = [u for u in self.data["users"] if u["email"] not in analitica.CORREOS_DEMO]
        self.assertTrue(simuladas)
        for u in simuladas:
            self.assertTrue(u["email"].endswith("@bookwho.test"), u["email"])
            self.assertTrue(u["name"].endswith("(sim)"), u["name"])
        ids = {u["id"] for u in simuladas}
        # Al registrarse, el vendedor queda con un contacto vacío que se completa en su primera oferta.
        con_datos = [c for c in self.data["contacts"] if c["seller_id"] in ids and c["phone"]]
        self.assertTrue(con_datos)
        for c in con_datos:
            self.assertTrue(c["phone"].startswith("+56 9 0000"), c["phone"])
            self.assertTrue(c["email"].endswith("@bookwho.test"), c["email"])
            self.assertIn("ficticio", c["address_or_meeting_point"])

    def test_la_app_respeta_sus_reglas_durante_la_simulacion(self):  # criterios 7 y 8
        self.assertEqual(self.resumen["fallas_inesperadas"], [])
        self.assertGreater(self.resumen["contacto"]["verificaciones"], 0)
        self.assertEqual(self.resumen["contacto"]["violaciones"], [])
        self.assertGreater(self.resumen["sondas"]["verificaciones"], 0)
        self.assertEqual(self.resumen["sondas"]["violaciones"], [])

    def test_analitica_interpreta_todo_y_lo_rotula_como_simulado(self):  # criterios 5 y 6
        usuarios, eventos = analitica.cargar(self.ruta)
        excluidos = analitica.ids_excluidos(usuarios, analitica.CORREOS_DEMO)
        r = analitica.calcular(eventos, excluidos)
        self.assertEqual((r["mal_formados"], r["no_procesados"]), (0, 0))
        self.assertGreater(r["solicitudes_publicadas"], 0)
        self.assertIsNotNone(r["kpi_horas_primera_oferta"])  # el reloj simulado separa los eventos en el tiempo
        self.assertEqual(r["periodo"], ("2026-11-03", "2026-11-08"))
        self.assertEqual(analitica.poblacion(usuarios, eventos, excluidos), "simulados")
        salida = subprocess.run(
            [sys.executable, os.path.join(RAIZ, "analitica.py"), self.ruta],
            cwd=self.carpeta.name, capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(salida.returncode, 0, salida.stderr)
        self.assertIn("DATOS SIMULADOS", salida.stdout)
        self.assertNotIn("@", salida.stdout)

    def test_analitica_avisa_si_se_mezclan_simulados_y_reales(self):
        usuarios = [{"id": 1, "email": "ana@bookwho.test"}, {"id": 2, "email": "real@ejemplo.cl"}]
        eventos = [{"actor_id": 1}, {"actor_id": 2}]
        self.assertEqual(analitica.poblacion(usuarios, eventos), "mezclados")
        self.assertEqual(analitica.poblacion(usuarios, eventos, {1}), "reales")


if __name__ == "__main__":
    unittest.main()
