"""Pruebas de analitica.py (RA3): formato del registro, exclusión de cuentas y KPIs.

Todo se hace con archivos temporales: nunca se toca el data.json real.
"""

import os
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import analitica  # noqa: E402
from models.store import Condition, Delivery, build_demo_store  # noqa: E402
from services.books_api import catalog_lookup  # noqa: E402
from services.persistence import save_store  # noqa: E402


def evento(at, actor, action, detail):
    return {"at": at, "actor_id": actor, "action": action, "detail": detail}


def flujo_real_guardado(carpeta):
    """Usa la app de verdad (Store) y guarda su data.json en una carpeta temporal."""
    store = build_demo_store(catalog_lookup)
    lectora = store.register("Lectora Real", "lectora@ejemplo.cl", "1234", "lector")
    vendedor = store.register("Vendedor Real", "vendedor@ejemplo.cl", "1234", "vendedor", "Temuco")
    otro = store.register("Otro Vendedor", "otro@ejemplo.cl", "1234", "vendedor", "Temuco")
    store.authenticate("lectora@ejemplo.cl", "1234")
    libro = store.upsert_book(catalog_lookup("demo-rayuela")).id

    def nueva():
        return store.create_request(lectora, libro, "", Condition.ANY, "Temuco", Delivery.ANY, "")

    resuelta, _sin_ofertas, cancelada = nueva(), nueva(), nueva()
    o1 = store.create_offer(vendedor, resuelta.id, "5000", Condition.NEW, phone="1")
    o2 = store.create_offer(otro, resuelta.id, "4000", Condition.USED, phone="2")
    store.accept_offer(lectora, o1.id)
    store.cancel_deal(lectora, o1.id)  # desiste y elige la otra
    store.accept_offer(lectora, o2.id)
    store.confirm_deal(lectora, o2.id)
    store.create_offer(vendedor, cancelada.id, "3000", Condition.NEW, phone="1")
    store.cancel_request(lectora, cancelada.id)
    ruta = os.path.join(carpeta, "data.json")
    save_store(store, ruta)
    return ruta


class FormatoDelRegistroTest(unittest.TestCase):
    """H10: si alguien cambia la redacción de store._log, esta prueba falla
    (antes los KPIs habrían quedado mal calculados sin ningún aviso)."""

    def test_el_registro_de_la_app_se_interpreta_completo(self):
        with tempfile.TemporaryDirectory() as d:
            usuarios, eventos = analitica.cargar(flujo_real_guardado(d))
        r = analitica.calcular(eventos, analitica.ids_excluidos(usuarios, analitica.CORREOS_DEMO))
        self.assertEqual((r["mal_formados"], r["no_procesados"]), (0, 0))
        self.assertEqual(r["solicitudes_publicadas"], 3)
        self.assertEqual(r["kpi_tasa_resolucion"], 33.3)  # 1 de 3: la cancelada cuenta en el denominador
        self.assertEqual(r["kpi_tasa_respuesta"], 66.7)  # 2 de 3: la cancelada sí alcanzó a recibir oferta
        self.assertIsNotNone(r["kpi_horas_primera_oferta"])

    def test_la_salida_no_muestra_correos_ni_detalles(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = flujo_real_guardado(d)
            salida = subprocess.run(
                [sys.executable, os.path.join(RAIZ, "analitica.py"), ruta],
                cwd=d, capture_output=True, text=True, timeout=120,
            )
        self.assertEqual(salida.returncode, 0, salida.stderr)
        self.assertIn("KPI 1", salida.stdout)
        self.assertNotIn("@", salida.stdout)  # los login/registro guardan correos en "detail"


class ExclusionTest(unittest.TestCase):
    """H03: los KPIs se calculan solo sobre la población real."""

    def test_cuentas_demo_y_tratos_con_ellas_no_cuentan(self):
        usuarios = [{"id": 1, "email": "lector@demo.cl"}, {"id": 3, "email": "vendedor@demo.cl"},
                    {"id": 10, "email": "real@ejemplo.cl"}, {"id": 11, "email": "tienda@ejemplo.cl"}]
        excluidos = analitica.ids_excluidos(usuarios, analitica.CORREOS_DEMO)
        self.assertEqual(excluidos, {1, 3})
        eventos = [
            evento("2026-11-10T10:00:00", 1, "solicitud_publicada", "Solicitud #1 · Demo"),
            evento("2026-11-10T10:00:00", 10, "solicitud_publicada", "Solicitud #2 · Rayuela"),
            evento("2026-11-10T11:00:00", 10, "solicitud_publicada", "Solicitud #3 · Ficciones"),
            evento("2026-11-10T12:00:00", 3, "oferta_publicada", "Oferta #1 para solicitud #2 · $5.000"),
            evento("2026-11-10T13:00:00", 10, "trato_concretado", "Oferta #1 concretada · solicitud #2 resuelta"),
            evento("2026-11-10T13:00:00", 11, "oferta_publicada", "Oferta #2 para solicitud #3 · $4.000"),
        ]
        r = analitica.calcular(eventos, excluidos)
        self.assertEqual((r["eventos_excluidos"], r["cuentas_excluidas"]), (2, 2))
        self.assertEqual(r["solicitudes_publicadas"], 2)  # la #1 era de una cuenta demo
        self.assertEqual(r["kpi_tasa_respuesta"], 50.0)  # solo la #3 recibió oferta de un vendedor real
        self.assertEqual(r["kpi_tasa_resolucion"], 0.0)  # el trato de la #2 fue con un vendedor demo
        self.assertEqual(r["kpi_horas_primera_oferta"], 2.0)  # #3: 11:00 -> 13:00

    def test_no_excluye_por_parecido(self):
        usuarios = [{"id": 7, "email": "lector@demo.cl.ar"}, {"id": 8, "email": "otro.lector@demo.cl"},
                    {"id": 9, "email": "LECTOR@demo.cl"}]
        self.assertEqual(analitica.ids_excluidos(usuarios, analitica.CORREOS_DEMO), {9})


class CasosLimiteTest(unittest.TestCase):
    def test_sin_eventos_no_divide_por_cero(self):
        r = analitica.calcular([])
        self.assertEqual((r["kpi_tasa_resolucion"], r["kpi_tasa_respuesta"]), (0.0, 0.0))
        self.assertIsNone(r["kpi_horas_primera_oferta"])
        self.assertIsNone(r["periodo"])

    def test_la_mediana_usa_la_primera_oferta_de_cada_solicitud(self):
        eventos = [
            evento("2026-11-10T10:00:00", 10, "solicitud_publicada", "Solicitud #1 · A"),
            evento("2026-11-10T11:00:00", 10, "solicitud_publicada", "Solicitud #2 · B"),
            evento("2026-11-10T11:00:00", 10, "solicitud_publicada", "Solicitud #3 · C"),  # sin ofertas
            evento("2026-11-10T12:00:00", 11, "oferta_publicada", "Oferta #1 para solicitud #1 · $1"),  # 2 h
            evento("2026-11-10T20:00:00", 12, "oferta_publicada", "Oferta #2 para solicitud #1 · $1"),  # 2.ª: no cuenta
            evento("2026-11-11T09:00:00", 11, "oferta_publicada", "Oferta #3 para solicitud #2 · $1"),  # 22 h
        ]
        r = analitica.calcular(eventos)
        self.assertEqual(r["kpi_horas_primera_oferta"], 12.0)  # mediana de 2 h y 22 h
        self.assertEqual(r["kpi_tasa_respuesta"], 66.7)
        self.assertEqual(r["kpi_tasa_resolucion"], 0.0)

    def test_eventos_incompletos_o_con_otra_redaccion_se_informan(self):
        eventos = [
            evento("2026-11-10T10:00:00", 10, "solicitud_publicada", "Solicitud #1 · A"),
            {"action": "oferta_publicada"},  # incompleto
            evento("2026-11-10T11:00:00", 11, "oferta_publicada", "Nueva oferta para la petición 1"),
            evento("2026-11-10T12:00:00", 11, "oferta_publicada", "Oferta #2 para solicitud #1 · $1"),
            evento("ayer", 10, "solicitud_publicada", "Solicitud #2 · B"),  # fecha ilegible
            evento("2026-11-10T13:00:00", 11, "oferta_publicada", "Oferta #3 para solicitud #2 · $1"),
        ]
        r = analitica.calcular(eventos)
        self.assertEqual(r["mal_formados"], 1)
        self.assertEqual(r["no_procesados"], 2)  # la redacción distinta y la fecha ilegible
        self.assertEqual(r["kpi_horas_primera_oferta"], 2.0)  # solo la #1 se pudo medir
        self.assertEqual(r["kpi_tasa_respuesta"], 100.0)


if __name__ == "__main__":
    unittest.main()
