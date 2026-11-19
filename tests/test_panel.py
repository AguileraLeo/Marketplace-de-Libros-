"""Pruebas del panel de métricas (SPEC-004): metricas.json sin datos personales, KPIs iguales a los de
analitica.py, modo en vivo que no altera el periodo base y una página sin HTML inyectado.

Todo se hace en carpetas temporales.
"""

import json
import os
import re
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


def leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return f.read()


class MetricasTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.carpeta = tempfile.TemporaryDirectory()
        cls.datos = os.path.join(cls.carpeta.name, "sim.json")
        cls.panel = os.path.join(cls.carpeta.name, "publico")
        simulador.simular(salida=cls.datos, panel=cls.panel, **PARAMETROS)
        cls.texto = leer(os.path.join(cls.panel, "metricas.json"))
        cls.metricas = json.loads(cls.texto)

    @classmethod
    def tearDownClass(cls):
        cls.carpeta.cleanup()

    def test_rotulado_como_simulado(self):  # criterio 1
        self.assertIs(self.metricas["simulado"], True)
        self.assertIn("ficticios", self.metricas["aviso"])

    def test_sin_datos_personales(self):  # criterio 2
        data = json.loads(leer(self.datos))
        for u in data["users"]:
            self.assertNotIn(u["email"], self.texto)
            self.assertNotIn(u["name"], self.texto)
        for c in data["contacts"]:
            if c["phone"]:
                self.assertNotIn(c["phone"], self.texto)
        self.assertNotIn("@", self.texto)
        self.assertNotIn(simulador.CLAVE, self.texto)

    def test_kpis_iguales_a_analitica(self):  # criterio 3
        usuarios, eventos = analitica.cargar(self.datos)
        r = analitica.calcular(eventos, analitica.ids_excluidos(usuarios, analitica.CORREOS_DEMO))
        k = self.metricas["kpis"]
        self.assertEqual(
            (k["resolucion_pct"], k["respuesta_pct"], k["horas_primera_oferta"]),
            (r["kpi_tasa_resolucion"], r["kpi_tasa_respuesta"], r["kpi_horas_primera_oferta"]),
        )
        self.assertEqual(self.metricas["totales"]["solicitudes"], r["solicitudes_publicadas"])

    def test_en_vivo_agrega_actividad_sin_tocar_el_periodo_base(self):  # criterio 7
        base = json.loads(leer(self.datos))["activity"]
        with tempfile.TemporaryDirectory() as d:
            ruta, panel = os.path.join(d, "sim.json"), os.path.join(d, "publico")
            simulador.simular(salida=ruta, panel=panel, en_vivo=0.001, **PARAMETROS)
            vivo = json.loads(leer(ruta))["activity"]
            metricas = json.loads(leer(os.path.join(panel, "metricas.json")))
        corte = "2026-11-09"  # día siguiente al periodo base de 6 días
        self.assertEqual([e for e in vivo if e["at"] < corte], base)
        self.assertGreater(len(vivo), len(base))
        self.assertIs(metricas["en_vivo"], False)  # al terminar, el panel deja de decir "en vivo"
        self.assertEqual(metricas["periodo"]["hasta"], corte)


class PaginaTest(unittest.TestCase):
    def setUp(self):
        self.html = leer(os.path.join(RAIZ, "panel", "index.html"))

    def test_avisa_que_los_datos_son_simulados(self):  # criterio 1
        self.assertIn("Datos simulados", self.html)

    def test_no_inserta_html_ni_usa_librerias_externas(self):  # criterio 4
        for prohibido in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval("):
            self.assertNotIn(prohibido, self.html)
        self.assertEqual(re.findall(r"<script[^>]*\bsrc=", self.html), [])

    def test_tiene_tablas_y_mantiene_lo_ultimo_si_falla(self):  # criterios 5 y 6
        self.assertIn("Ver los datos en tablas", self.html)
        self.assertIn("se muestran los últimos recibidos", self.html)


if __name__ == "__main__":
    unittest.main()
