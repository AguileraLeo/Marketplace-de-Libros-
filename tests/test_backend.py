"""Contrato HTTP de SPEC-005, sin red externa ni datos de usuarios reales.

Ejecutar desde la raíz:
    python -B -m unittest discover -s tests -p test_backend.py -v

Requiere el servidor y las dependencias ya disponibles. No se omiten pruebas si
falta backend.servidor: ese caso debe aparecer como un error de importación.
Los argumentos RPC son posicionales del Store, siempre sin el actor.
"""

import json
import hmac
import inspect
import os
import re
import sys
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from datetime import datetime
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastapi.testclient import TestClient
except ImportError:  # el backend es opcional: sin FastAPI (p. ej. en el PC de un integrante) se omiten estas pruebas
    raise unittest.SkipTest("Instala backend/requirements.txt para probar el servidor.")

from backend.servidor import RAIZ, crear_app, dias_seguidos
import analitica
from models.store import Condition, Delivery, OfferStatus, RequestStatus, Role
from services.books_api import catalog_lookup
from services.persistence import load_store


def correo_completo(correo):
    """El correo como palabra completa: no coincide dentro de otro correo más largo."""
    return re.compile(r"(?<![\w.+-])" + re.escape(correo.lower()) + r"(?![\w-])")


class BackendTest(unittest.TestCase):
    ADMIN = ("admin@prueba.cl", "clave-admin")
    TELEFONO = "+56 9 0000 0042"

    def setUp(self):
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        # ruta_datos es el archivo JSON que también recibe load_store().
        self.ruta_datos = os.path.join(carpeta.name, "bookwho.json")
        self.app = crear_app(self.ruta_datos, admin=self.ADMIN)
        contextos = ExitStack()
        self.addCleanup(contextos.close)
        self.client = contextos.enter_context(TestClient(self.app))
        self.correos = {self.ADMIN[0]}
        self.claves = {self.ADMIN[1]}
        self.sesiones = {}
        self.respuestas = []

    def assert_privacidad(self, response, correos_visibles=(), contacto=False):
        """Inspeccionar el JSON crudo y su versión decodificada, incluso errores."""
        crudo = response.text
        self.assertNotIn('"password"', crudo.lower())
        for clave in self.claves:
            self.assertNotIn(clave, crudo)
        # El correo como palabra completa: aparece solo o dentro de una frase, pero no dentro de "otro-lector@x".
        for correo in self.correos - set(correos_visibles):
            self.assertIsNone(correo_completo(correo).search(crudo.lower()), correo)
        if not contacto:
            self.assertNotIn(self.TELEFONO, crudo)
        if not response.content:  # DELETE /api/sesion devuelve 204 sin cuerpo.
            return
        data = response.json()
        # Decodificar evita que escapes JSON oculten una filtración al chequeo crudo.
        texto = json.dumps(data, ensure_ascii=False).lower()
        self.assertNotIn('"password"', texto)
        for clave in self.claves:
            self.assertNotIn(clave.lower(), texto)
        for correo in self.correos - set(correos_visibles):
            self.assertIsNone(correo_completo(correo).search(texto), correo)
        if not contacto:
            self.assertNotIn(self.TELEFONO, texto)

    def peticion(self, verbo, ruta, *, token=None, cuerpo=None,
                 correo_propio=None, contacto=False, admin=False):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        response = self.client.request(verbo, ruta, headers=headers, json=cuerpo)
        correo = correo_propio or self.sesiones.get(token)
        visibles = set(self.correos) if admin else ({correo} if correo else set())
        self.respuestas.append((response, visibles, contacto))
        self.assert_privacidad(response, visibles, contacto)
        return response

    def registrar(self, correo="lector@prueba.cl", rol=Role.READER):
        clave = "clave-" + correo.split("@")[0]
        self.correos.add(correo)
        self.claves.add(clave)
        response = self.peticion(
            "POST", "/api/registro", correo_propio=correo,
            cuerpo={
                "nombre": "Lector de prueba" if rol == Role.READER else "Vendedor de prueba",
                "correo": correo,
                "clave": clave,
                "rol": rol,
                "comuna": "Temuco" if rol == Role.SELLER else "",
            },
        )
        # SPEC-005 no distingue 200 y 201 para el registro.
        self.assertIn(response.status_code, (200, 201), response.text)
        data = response.json()
        self.assertIsInstance(data["token"], str)
        self.assertTrue(data["token"])
        usuario = data["usuario"]
        self.assertEqual(usuario["_tipo"], "User")
        self.assertEqual(usuario["email"], correo)
        self.assertEqual(usuario["role"], rol)
        self.assertIsInstance(usuario["id"], int)
        self.assertNotIn("password", usuario)
        self.sesiones[data["token"]] = correo
        return data

    def rpc(self, sesion, metodo, args=(), *, codigo=200, tipo=None,
            contacto=False, admin=False):
        response = self.peticion(
            "POST", "/api/rpc", token=sesion["token"],
            cuerpo={"metodo": metodo, "args": list(args)},
            contacto=contacto, admin=admin,
        )
        self.assertEqual(response.status_code, codigo, response.text)
        if codigo == 200:
            self.assertIn("resultado", response.json())
            return response.json()["resultado"]
        self.assert_error(response, codigo, tipo)
        return response.json()

    def assert_error(self, response, codigo=None, tipo=None):
        if codigo is not None:
            self.assertEqual(response.status_code, codigo, response.text)
        else:
            # El contrato exige error para credenciales incorrectas, sin fijar código.
            self.assertGreaterEqual(response.status_code, 400, response.text)
            self.assertLess(response.status_code, 500, response.text)
        data = response.json()
        self.assertIsInstance(data.get("error"), str)
        self.assertTrue(data["error"])
        self.assertIsInstance(data.get("tipo"), str)
        if tipo is not None:
            self.assertEqual(data["tipo"], tipo)

    def nueva_solicitud(self, lector):
        libro = self.rpc(lector, "upsert_book", [catalog_lookup("demo-rayuela")])
        self.assertEqual(libro["_tipo"], "Book")
        self.assertEqual(libro["external_id"], "demo-rayuela")
        solicitud = self.rpc(lector, "create_request", [
            libro["id"], "20000", Condition.ANY, "Temuco", Delivery.ANY,
            "Solicitud ficticia de la prueba HTTP",
        ])
        self.assertEqual(solicitud["_tipo"], "BookRequest")
        self.assertEqual(solicitud["reader_id"], lector["usuario"]["id"])
        self.assertEqual(solicitud["book_id"], libro["id"])
        self.assertEqual(solicitud["status"], RequestStatus.PUBLISHED)
        for campo in ("created_at", "updated_at"):
            self.assertIsInstance(solicitud[campo], str)
            datetime.fromisoformat(solicitud[campo])
        return solicitud

    def nueva_oferta(self):
        lector = self.registrar()
        solicitud = self.nueva_solicitud(lector)
        vendedor = self.registrar("vendedor@prueba.cl", Role.SELLER)
        self.assertEqual(vendedor["usuario"]["location"], "Temuco")
        abiertas = self.rpc(vendedor, "open_requests")
        self.assertIn(solicitud["id"], [r["id"] for r in abiertas])
        oferta = self.rpc(vendedor, "create_offer", [
            solicitud["id"], "12000", Condition.USED, "Buen estado", "",
            self.TELEFONO, "", "Punto ficticio de prueba",
        ])
        self.assertEqual(oferta["_tipo"], "Offer")
        self.assertEqual(oferta["request_id"], solicitud["id"])
        self.assertEqual(oferta["seller_id"], vendedor["usuario"]["id"])
        self.assertEqual(oferta["status"], OfferStatus.PUBLISHED)
        return lector, vendedor, solicitud, oferta

    def test_registro_y_sesion_devuelven_token_y_usuario_sin_password(self):
        lector = self.registrar()
        response = self.peticion(
            "POST", "/api/sesion", correo_propio="lector@prueba.cl",
            cuerpo={"correo": "lector@prueba.cl", "clave": "clave-lector"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertIsInstance(data["token"], str)
        self.assertTrue(data["token"])
        self.assertEqual(data["usuario"]["id"], lector["usuario"]["id"])
        self.assertEqual(data["usuario"]["_tipo"], "User")
        self.assertNotIn("password", data["usuario"])
        # El token obtenido por login sirve para operar, no solo existe en el JSON.
        self.sesiones[data["token"]] = "lector@prueba.cl"
        self.assertEqual(self.rpc(data, "reader_requests"), [])

    def test_credenciales_incorrectas_devuelven_error(self):
        self.registrar()
        for correo, clave in (
            ("lector@prueba.cl", "clave-incorrecta"),
            ("inexistente@prueba.cl", "clave-incorrecta"),
        ):
            with self.subTest(correo=correo):
                self.correos.add(correo)
                self.claves.add(clave)
                response = self.peticion(
                    "POST", "/api/sesion", correo_propio=correo,
                    cuerpo={"correo": correo, "clave": clave},
                )
                self.assert_error(response)

    def test_rpc_sin_token_o_con_token_invalido_devuelve_401(self):
        for token in (None, "token-inexistente"):
            with self.subTest(token=token):
                response = self.peticion(
                    "POST", "/api/rpc", token=token,
                    cuerpo={"metodo": "reader_requests", "args": []},
                )
                self.assert_error(response, 401)

    def test_rpc_no_expone_metodos_fuera_de_la_lista_permitida(self):
        lector = self.registrar()
        for metodo in ("authenticate", "_log", "add_user"):
            with self.subTest(metodo=metodo):
                self.rpc(lector, metodo, codigo=404)

    def test_flujo_compartido_y_privacidad_del_contacto(self):
        lector, vendedor, solicitud, oferta = self.nueva_oferta()
        recibidas = self.rpc(lector, "offers_for_request", [solicitud["id"]])
        self.assertIn(oferta["id"], [o["id"] for o in recibidas])
        self.rpc(lector, "offer_contact", [oferta["id"]],
                 codigo=403, tipo="PermissionDenied")

        aceptada = self.rpc(lector, "accept_offer", [oferta["id"]])
        self.assertEqual(aceptada["status"], OfferStatus.IN_DEAL)
        actual = self.rpc(lector, "get_request", [solicitud["id"]])
        self.assertEqual(actual["status"], RequestStatus.IN_DEAL)
        contacto = self.rpc(lector, "offer_contact", [oferta["id"]], contacto=True)
        self.assertEqual(contacto["_tipo"], "SellerContact")
        self.assertEqual(contacto["phone"], self.TELEFONO)

        otro_lector = self.registrar("otro-lector@prueba.cl")
        otro_vendedor = self.registrar("otro-vendedor@prueba.cl", Role.SELLER)
        for intruso in (otro_lector, otro_vendedor):
            with self.subTest(rol=intruso["usuario"]["role"]):
                self.rpc(intruso, "offer_contact", [oferta["id"]],
                         codigo=403, tipo="PermissionDenied")
        # Reexaminar toda la traza con todos los correos ya conocidos.
        for response, visibles, contacto_permitido in self.respuestas:
            self.assert_privacidad(response, visibles, contacto_permitido)

    def test_actor_sale_del_token_y_no_permite_aceptar_a_un_vendedor(self):
        lector, vendedor, solicitud, oferta = self.nueva_oferta()
        self.rpc(vendedor, "accept_offer", [oferta["id"]],
                 codigo=403, tipo="PermissionDenied")
        # El rechazo no debe cambiar estados y el lector legítimo aún puede aceptar.
        actual = self.rpc(lector, "get_offer", [oferta["id"]])
        self.assertEqual(actual["status"], OfferStatus.PUBLISHED)
        self.rpc(lector, "accept_offer", [oferta["id"]])

    def test_otro_lector_no_puede_aceptar_ni_cancelar_la_solicitud(self):
        lector, vendedor, solicitud, oferta = self.nueva_oferta()
        intruso = self.registrar("otro-lector@prueba.cl")
        for metodo, ident in (("accept_offer", oferta["id"]),
                              ("cancel_request", solicitud["id"])):
            with self.subTest(metodo=metodo):
                self.rpc(intruso, metodo, [ident], codigo=403, tipo="PermissionDenied")
        self.assertEqual(self.rpc(lector, "get_offer", [oferta["id"]])["status"],
                         OfferStatus.PUBLISHED)

    def test_user_y_listados_no_filtran_correo_ajeno_ni_password(self):
        lector, vendedor, solicitud, oferta = self.nueva_oferta()
        for sesion, otro in ((lector, vendedor), (vendedor, lector)):
            with self.subTest(correo=self.sesiones[sesion["token"]]):
                propio = self.rpc(sesion, "user", [sesion["usuario"]["id"]])
                self.assertEqual(propio["email"], sesion["usuario"]["email"])
                ajeno = self.rpc(sesion, "user", [otro["usuario"]["id"]])
                self.assertEqual(ajeno["id"], otro["usuario"]["id"])
                self.assertNotIn(otro["usuario"]["email"], json.dumps(ajeno))
        self.rpc(lector, "reader_requests")
        self.rpc(vendedor, "seller_offers")
        self.rpc(lector, "get_request", [solicitud["id"]])
        self.rpc(lector, "get_offer", [oferta["id"]])

    def test_create_request_se_guarda_antes_de_responder(self):
        lector = self.registrar()
        solicitud = self.nueva_solicitud(lector)
        # Leer durante la sesión obliga a persistir antes de apagar el servidor.
        guardado = load_store(self.ruta_datos)
        self.assertIsNotNone(guardado)
        self.assertIn(solicitud["id"], guardado.requests)
        persistida = guardado.requests[solicitud["id"]]
        self.assertEqual(persistida.reader_id, lector["usuario"]["id"])
        self.assertEqual(persistida.book_id, solicitud["book_id"])
        self.assertEqual(persistida.location, "Temuco")
        self.assertEqual(persistida.status, RequestStatus.PUBLISHED)

    def test_no_hay_cuentas_demo_en_el_servidor(self):
        response = self.peticion(
            "POST", "/api/sesion",
            cuerpo={"correo": "lector@demo.cl", "clave": "1234"},
        )
        self.assert_error(response)

    def test_metricas_son_publicas_reales_y_no_exponen_datos_personales(self):
        lector, vendedor, solicitud, oferta = self.nueva_oferta()

        def metricas():
            response = self.peticion("GET", "/api/metricas")  # Sin token.
            self.assertEqual(response.status_code, 200, response.text)
            self.assertNotIn("@", response.text)
            datos = response.json()
            self.assertIs(datos["simulado"], False)
            self.assertIn("kpis", datos)
            for campo in ("resolucion_pct", "respuesta_pct", "horas_primera_oferta"):
                self.assertIn(campo, datos["kpis"])
            return datos["kpis"]

        kpis = metricas()
        self.assertEqual(kpis["respuesta_pct"], 100)
        self.assertEqual(kpis["resolucion_pct"], 0)
        self.assertIsInstance(kpis["horas_primera_oferta"], (int, float))
        self.assertGreaterEqual(kpis["horas_primera_oferta"], 0)
        self.rpc(lector, "accept_offer", [oferta["id"]])
        self.assertEqual(metricas()["resolucion_pct"], 0)
        self.rpc(lector, "confirm_deal", [oferta["id"]])
        self.assertEqual(metricas()["resolucion_pct"], 100)

    def test_precio_cero_devuelve_400_validation_error_y_no_crea_oferta(self):
        lector = self.registrar()
        solicitud = self.nueva_solicitud(lector)
        vendedor = self.registrar("vendedor@prueba.cl", Role.SELLER)
        self.rpc(vendedor, "create_offer", [
            solicitud["id"], "0", Condition.USED, "Buen estado", "",
            self.TELEFONO, "", "Punto ficticio de prueba",
        ], codigo=400, tipo="ValidationError")
        self.assertEqual(self.rpc(lector, "offers_for_request", [solicitud["id"]]), [])

    def test_cancelar_dos_veces_devuelve_409_invalid_transition(self):
        lector = self.registrar()
        solicitud = self.nueva_solicitud(lector)
        cancelada = self.rpc(lector, "cancel_request", [solicitud["id"]])
        self.assertEqual(cancelada["status"], RequestStatus.CANCELLED)
        self.rpc(lector, "cancel_request", [solicitud["id"]],
                 codigo=409, tipo="InvalidTransition")
        self.assertEqual(self.rpc(lector, "get_request", [solicitud["id"]])["status"],
                         RequestStatus.CANCELLED)

    def test_recurso_inexistente_devuelve_404_not_found(self):
        lector = self.registrar()
        # Aún no se publicó ninguna solicitud.
        self.rpc(lector, "get_request", [1], codigo=404, tipo="NotFound")

    def test_salud_publica(self):
        response = self.peticion("GET", "/api/salud")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIs(response.json()["ok"], True)

    def test_cerrar_sesion_revoca_el_token(self):
        lector = self.registrar()
        response = self.peticion("DELETE", "/api/sesion", token=lector["token"])
        self.assertEqual(response.status_code, 204, response.text)
        self.assertEqual(response.content, b"")
        self.rpc(lector, "reader_requests", codigo=401)

    def test_registro_publico_no_permite_admin(self):
        response = self.peticion(
            "POST", "/api/registro", correo_propio="intruso@prueba.cl",
            cuerpo={"nombre": "Intruso de prueba", "correo": "intruso@prueba.cl",
                    "clave": "clave-intruso", "rol": Role.ADMIN, "comuna": ""},
        )
        self.assert_error(response, 403, "PermissionDenied")

    def test_admin_configurado_puede_listar_usuarios_sin_password(self):
        lector = self.registrar()
        self.rpc(lector, "admin_users", codigo=403, tipo="PermissionDenied")
        response = self.peticion(
            "POST", "/api/sesion", correo_propio=self.ADMIN[0],
            cuerpo={"correo": self.ADMIN[0], "clave": self.ADMIN[1]},
        )
        self.assertEqual(response.status_code, 200, response.text)
        admin = response.json()
        self.assertEqual(admin["usuario"]["role"], Role.ADMIN)
        self.sesiones[admin["token"]] = self.ADMIN[0]
        usuarios = self.rpc(admin, "admin_users", admin=True)
        self.assertIn(lector["usuario"]["email"], [u.get("email") for u in usuarios])
        for usuario in usuarios:
            self.assertNotIn("password", usuario)


class SeguridadTest(unittest.TestCase):
    """F1–F8: transporte compatible con los teléfonos y datos solo temporales."""

    ADMIN = ("admin@prueba.cl", "clave-admin")
    IP = "203.0.113.10"
    MENSAJE_LIMITE = {"error": "Demasiados intentos. Espera unos minutos.",
                      "tipo": "PermissionDenied"}

    def setUp(self):
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        self.ruta = os.path.join(carpeta.name, "seguridad.json")
        self.app = crear_app(self.ruta, admin=self.ADMIN)
        contextos = ExitStack()
        self.addCleanup(contextos.close)
        self.client = contextos.enter_context(TestClient(self.app))

    def registro(self, correo="lector@prueba.cl", ip=None, **cambios):
        datos = {"nombre": "Persona de prueba", "correo": correo, "clave": "clave-prueba",
                 "rol": Role.READER, "comuna": ""}
        datos.update(cambios)
        return self.client.post("/api/registro", json=datos,
                                headers={"cf-connecting-ip": ip} if ip is not None else {})

    def sesion(self, correo="lector@prueba.cl", clave="clave-prueba", ip=None):
        return self.client.post("/api/sesion", json={"correo": correo, "clave": clave},
                                headers={"cf-connecting-ip": ip} if ip is not None else {})

    def rpc(self, sesion, metodo, args=()):
        return self.client.post("/api/rpc", json={"metodo": metodo, "args": list(args)},
                                headers={"Authorization": "Bearer " + sesion["token"]})

    def reloj(self, ahora=1000.0):
        # Reemplazar la referencia del backend evita congelar los relojes de AnyIO/httpx.
        reloj = Mock(wraps=time)
        reloj.time.return_value = reloj.monotonic.return_value = ahora
        self.enterContext(patch("backend.servidor.time", reloj))
        return reloj

    def assert_limite(self, respuesta):
        self.assertEqual(respuesta.status_code, 429, respuesta.text)
        self.assertEqual(respuesta.json(), self.MENSAJE_LIMITE)

    def test_cuentas_de_agentes_solo_entran_y_se_registran_sin_cloudflare(self):
        correo = "agente@" + analitica.DOMINIO_SIMULADO
        self.assertEqual(self.registro(correo).status_code, 200)
        self.assertEqual(self.sesion(correo).status_code, 200)
        esperado = {"error": "Esta cuenta está reservada para la demostración.",
                    "tipo": "PermissionDenied"}
        for intento in (
            self.sesion("  " + correo.upper() + "  ", ip=self.IP),
            self.registro("nuevo@" + analitica.DOMINIO_SIMULADO, self.IP),
        ):
            self.assertEqual(intento.status_code, 403, intento.text)
            self.assertEqual(intento.json(), esperado)
        self.assertIsNone(load_store(self.ruta).find_user_by_email("nuevo@" + analitica.DOMINIO_SIMULADO))
        # El dominio reservado no incluye sufijos parecidos de dominios distintos.
        self.assertEqual(self.registro("lector@" + analitica.DOMINIO_SIMULADO + ".example", self.IP).status_code, 200)

    def test_ocho_fallos_por_correo_normalizado_aunque_cambie_la_ip(self):
        self.reloj()
        self.assertEqual(self.registro().status_code, 200)
        for i in range(8):
            correo = "  LECTOR@PRUEBA.CL  " if i % 2 else "lector@prueba.cl"
            r = self.sesion(correo, "incorrecta", f"203.0.113.{i + 20}")
            self.assertEqual(r.status_code, 400, r.text)
        self.assert_limite(self.sesion(ip="203.0.113.80"))
        self.assertEqual(self.sesion().status_code, 200)  # agente/local: no aplica el límite

    def test_registro_no_elude_la_reserva_con_un_correo_que_el_modelo_recorta(self):
        sufijo = "@" + analitica.DOMINIO_SIMULADO
        efectivo = "a" * (120 - len(sufijo)) + sufijo
        r = self.registro(efectivo + ".otro", self.IP)
        self.assertEqual(r.status_code, 403, r.text)
        self.assertEqual(r.json(), {"error": "Esta cuenta está reservada para la demostración.",
                                    "tipo": "PermissionDenied"})
        self.assertIsNone(load_store(self.ruta).find_user_by_email(efectivo))

    def test_treinta_fallos_por_ip_aunque_cambie_el_correo(self):
        self.reloj()
        for i in range(30):
            r = self.sesion(f"desconocido-{i}@prueba.cl", "incorrecta", self.IP)
            self.assertEqual(r.status_code, 400, r.text)
        self.assert_limite(self.sesion("otro@prueba.cl", "incorrecta", self.IP))
        r = self.sesion("otro@prueba.cl", "incorrecta", "203.0.113.11")
        self.assertEqual(r.status_code, 400)

    def test_login_correcto_reinicia_correo_y_conserva_los_fallos_de_la_ip(self):
        self.reloj()
        self.assertEqual(self.registro().status_code, 200)
        for _ in range(7):
            self.assertEqual(self.sesion(clave="incorrecta", ip=self.IP).status_code, 400)
        self.assertEqual(self.sesion(ip=self.IP).status_code, 200)
        for _ in range(8):
            self.assertEqual(self.sesion(clave="incorrecta", ip=self.IP).status_code, 400)
        self.assert_limite(self.sesion(ip=self.IP))
        for i in range(15):
            self.assertEqual(self.sesion(f"otro-{i}@prueba.cl", "incorrecta", self.IP).status_code, 400)
        self.assert_limite(self.sesion("ultimo@prueba.cl", "incorrecta", self.IP))

    def test_fallos_de_correo_e_ip_caducan_a_los_diez_minutos(self):
        reloj = self.reloj()
        for _ in range(8):
            self.assertEqual(self.sesion(clave="incorrecta", ip=self.IP).status_code, 400)
        self.assert_limite(self.sesion(clave="incorrecta", ip=self.IP))
        reloj.time.return_value = reloj.monotonic.return_value = 1601.0
        self.assertEqual(self.sesion(clave="incorrecta", ip=self.IP).status_code, 400)
        for i in range(29):
            self.assertEqual(self.sesion(f"otro-{i}@prueba.cl", "incorrecta", self.IP).status_code, 400)
        self.assert_limite(self.sesion("ultimo@prueba.cl", "incorrecta", self.IP))
        reloj.time.return_value = reloj.monotonic.return_value = 2202.0
        self.assertEqual(self.sesion("ultimo@prueba.cl", "incorrecta", self.IP).status_code, 400)

    def test_los_contadores_descartan_las_claves_que_ya_no_tienen_eventos_vigentes(self):
        reloj = self.reloj()
        self.assertEqual(self.sesion("anterior@prueba.cl", "incorrecta", self.IP).status_code, 400)
        self.assertEqual(self.registro("anterior@prueba.cl", self.IP).status_code, 200)
        login = next(r.endpoint for r in self.app.routes
                     if getattr(r, "path", None) == "/api/sesion" and "POST" in r.methods)
        registro = next(r.endpoint for r in self.app.routes if getattr(r, "path", None) == "/api/registro")
        contadores = inspect.getclosurevars(login).nonlocals
        registros = inspect.getclosurevars(registro).nonlocals["registros_ip"]
        self.assertIn("anterior@prueba.cl", contadores["fallos_correo"])
        self.assertIn(self.IP, contadores["fallos_ip"])
        self.assertIn(self.IP, registros)
        reloj.time.return_value = reloj.monotonic.return_value = 4601.0
        self.assertEqual(self.sesion("actual@prueba.cl", "incorrecta", "203.0.113.11").status_code, 400)
        self.assertNotIn("anterior@prueba.cl", contadores["fallos_correo"])
        self.assertNotIn(self.IP, contadores["fallos_ip"])
        self.assertNotIn(self.IP, registros)

    def test_intentos_concurrentes_no_rebasan_los_ocho_fallos_por_correo(self):
        self.reloj()
        barrera = threading.Barrier(12)

        def intentar(i):
            barrera.wait(timeout=3)
            return self.sesion("concurrente@prueba.cl", "incorrecta", f"203.0.113.{i + 20}")

        with ThreadPoolExecutor(max_workers=12) as pool:
            respuestas = list(pool.map(intentar, range(12)))
        self.assertEqual(sum(r.status_code == 400 for r in respuestas), 8)
        self.assertEqual(sum(r.status_code == 429 for r in respuestas), 4)

    def test_registro_admite_cuarenta_por_ip_y_libera_el_cupo_despues_de_una_hora(self):
        reloj = self.reloj()
        # Un registro inválido no consume uno de los cuarenta registros exitosos.
        self.assertEqual(self.registro("invalido", self.IP).status_code, 400)
        for i in range(40):
            r = self.registro(f"alumno-{i}@prueba.cl", self.IP)
            self.assertEqual(r.status_code, 200, r.text)
        self.assert_limite(self.registro("alumno-40@prueba.cl", self.IP))
        self.assertEqual(self.registro("otra-ip@prueba.cl", "203.0.113.11").status_code, 200)
        reloj.time.return_value = reloj.monotonic.return_value = 4601.0
        self.assertEqual(self.registro("alumno-40@prueba.cl", self.IP).status_code, 200)

    def test_los_agentes_locales_no_tienen_los_limites_de_cloudflare(self):
        self.reloj()
        for i in range(41):
            correo = f"agente-{i}@" + analitica.DOMINIO_SIMULADO
            self.assertEqual(self.registro(correo).status_code, 200)
        for _ in range(31):
            r = self.sesion("agente-0@" + analitica.DOMINIO_SIMULADO, "incorrecta")
            self.assertEqual(r.status_code, 400, r.text)
        self.assertEqual(self.sesion("agente-0@" + analitica.DOMINIO_SIMULADO).status_code, 200)

    def test_transfer_encoding_en_api_se_rechaza_antes_de_leer_el_cuerpo(self):
        for codificacion in ("chunked", "identity"):
            with self.subTest(codificacion=codificacion):
                r = self.client.post("/api/sesion", content=iter([b'{"correo":', b'"prueba"}']),
                                     headers={"Transfer-Encoding": codificacion,
                                              "Content-Type": "application/json"})
                self.assertEqual(r.status_code, 411, r.text)
                self.assertEqual(r.json()["tipo"], "ValidationError")
                self.assertIsInstance(r.json()["error"], str)
        self.assertEqual(self.client.get("/", headers={"Transfer-Encoding": "chunked"}).status_code, 200)

    def test_cerrar_sesion_sin_content_length_sigue_devolviendo_204(self):
        sesion = self.registro().json()
        request = self.client.build_request("DELETE", "/api/sesion", headers={"Authorization": "Bearer " + sesion["token"]})
        request.headers.pop("Content-Length", None)
        self.assertNotIn("Content-Length", request.headers)
        r = self.client.send(request)
        self.assertEqual((r.status_code, r.content), (204, b""))
        self.assertEqual(self.rpc(sesion, "reader_requests").status_code, 401)

    def test_tamano_y_longitud_invalida_siguen_dando_errores_json(self):
        grande = self.client.post("/api/sesion", content=b"x" * (16 * 1024 + 1))
        self.assertEqual(grande.status_code, 413)
        self.assertEqual(grande.json()["tipo"], "ValidationError")
        invalida = self.client.post("/api/sesion", content=b"{}", headers={"Content-Length": "no-es-numero"})
        self.assertEqual(invalida.status_code, 400)
        self.assertEqual(invalida.json()["tipo"], "ValidationError")

    def test_metricas_comparten_cache_tres_segundos_entre_las_tres_rutas(self):
        reloj = self.reloj()
        original = analitica.cargar
        with patch("backend.servidor.analitica.cargar", wraps=original) as cargar:
            uno = self.client.get("/api/metricas")
            dos = self.client.get("/en-vivo/metricas.json")
            tres = self.client.get("/reales/metricas.json")
            self.assertEqual(uno.status_code, 200)
            self.assertEqual(uno.json(), dos.json())
            self.assertEqual(uno.json(), tres.json())
            self.assertEqual(cargar.call_count, 1)
            reloj.time.return_value = reloj.monotonic.return_value = 1002.9
            self.assertEqual(self.client.get("/en-vivo/metricas.json").status_code, 200)
            self.assertEqual(cargar.call_count, 1)
            reloj.time.return_value = reloj.monotonic.return_value = 1003.1
            self.assertEqual(self.client.get("/reales/metricas.json").status_code, 200)
            self.assertEqual(cargar.call_count, 2)

    def test_lecturas_concurrentes_de_metricas_comparten_un_solo_calculo(self):
        self.reloj()
        original = analitica.cargar
        barrera = threading.Barrier(8)
        empezo, liberar = threading.Event(), threading.Event()

        def cargar_lento(*args):
            empezo.set()
            self.assertTrue(liberar.wait(3), "No se liberó la lectura de prueba")
            return original(*args)

        def pedir(indice):
            barrera.wait(timeout=3)
            ruta = ("/api/metricas", "/en-vivo/metricas.json", "/reales/metricas.json")[indice % 3]
            return self.client.get(ruta)

        with patch("backend.servidor.analitica.cargar", side_effect=cargar_lento) as cargar:
            with ThreadPoolExecutor(max_workers=8) as pool:
                futuros = [pool.submit(pedir, i) for i in range(8)]
                try:
                    self.assertTrue(empezo.wait(3))
                finally:
                    liberar.set()
                respuestas = [f.result(timeout=5) for f in futuros]
            self.assertTrue(all(r.status_code == 200 for r in respuestas))
            self.assertEqual(cargar.call_count, 1)
            self.assertTrue(all(r.json() == respuestas[0].json() for r in respuestas))

    def assert_cabeceras(self, respuesta):
        esperado = {
            "x-content-type-options": "nosniff",
            "referrer-policy": "strict-origin-when-cross-origin",
            "x-frame-options": "DENY",
            "permissions-policy": "camera=(), microphone=(), geolocation=()",
            "strict-transport-security": "max-age=31536000",
        }
        for nombre, valor in esperado.items():
            self.assertEqual(respuesta.headers.get(nombre), valor, (respuesta.url, nombre))

    def test_cabeceras_cubren_paginas_recursos_y_errores_incluidos_los_del_middleware(self):
        casos = [self.client.get(ruta) for ruta in (
            "/", "/privacidad/", "/en-vivo/", "/api/salud", "/api/docs", "/api/openapi.json",
            "/demo/app.mp4", "/demo/app.jpg", "/og-image.jpg", "/no-existe", "/descargar",
        )]
        casos += [self.client.post("/api/rpc", json={"metodo": "reader_requests"}),
                  self.client.post("/api/sesion", content=b"no es json"),
                  self.client.post("/api/sesion", content=b"x" * (16 * 1024 + 1)),
                  self.client.post("/api/sesion", content=b"{}", headers={"Transfer-Encoding": "chunked"})]
        for respuesta in casos:
            with self.subTest(ruta=str(respuesta.url), codigo=respuesta.status_code):
                self.assert_cabeceras(respuesta)
        for _ in range(8):
            self.sesion(clave="incorrecta", ip=self.IP)
        limitada = self.sesion(clave="incorrecta", ip=self.IP)
        self.assert_limite(limitada)
        self.assert_cabeceras(limitada)

    def test_csp_html_permite_los_recursos_actuales_y_excluye_solo_api_docs(self):
        esperado = ("default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data:; media-src 'self'; font-src 'self'; connect-src 'self'; "
                    "object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'")
        for ruta in ("/", "/privacidad/", "/en-vivo/", "/simulacion/"):
            respuesta = self.client.get(ruta)
            self.assertEqual(respuesta.status_code, 200)
            self.assertEqual(respuesta.headers.get("content-security-policy"), esperado, ruta)
        docs = self.client.get("/api/docs")
        self.assertEqual(docs.status_code, 200)
        self.assertNotIn("content-security-policy", docs.headers)
        self.assertNotIn("content-security-policy", self.client.get("/api/salud").headers)

    def test_error_interno_conserva_cabeceras_y_no_revela_el_detalle_de_la_excepcion(self):
        @self.app.get("/api/fallo-exclusivo-de-la-prueba")
        def fallo():
            raise RuntimeError("Detalle interno exclusivo de la prueba")

        # El sitio está montado en "/": esta ruta de prueba debe preceder ese montaje.
        self.app.router.routes.insert(0, self.app.router.routes.pop())
        with self.assertLogs("backend.servidor", level="ERROR"):
            respuesta = self.client.get("/api/fallo-exclusivo-de-la-prueba")
        self.assertEqual(respuesta.status_code, 500)
        self.assert_cabeceras(respuesta)
        self.assertEqual(set(respuesta.json()), {"error", "tipo"})
        self.assertNotIn("Detalle interno exclusivo de la prueba", respuesta.text)

    def test_login_usa_comparacion_constante_sin_migrar_el_hash_existente(self):
        self.assertEqual(self.registro().status_code, 200)
        hash_antes = load_store(self.ruta).find_user_by_email("lector@prueba.cl").password
        comparador = hmac.compare_digest
        with patch("models.store.hmac.compare_digest", wraps=comparador) as comparar:
            self.assertEqual(self.sesion().status_code, 200)
            self.assertEqual(self.sesion(clave="incorrecta").status_code, 400)
            self.assertEqual(comparar.call_count, 2)
        self.assertEqual(load_store(self.ruta).find_user_by_email("lector@prueba.cl").password, hash_antes)

    def test_crear_una_sesion_elimina_las_expiradas_sin_usar_sus_tokens(self):
        reloj = self.reloj()
        uno = self.registro().json()
        dos = self.registro("otro@prueba.cl").json()
        endpoint = next(r.endpoint for r in self.app.routes if getattr(r, "path", None) == "/api/registro")
        crear_sesion = inspect.getclosurevars(endpoint).nonlocals["nueva_sesion"]
        sesiones = inspect.getclosurevars(crear_sesion).nonlocals["sesiones"]
        self.assertIn(uno["token"], sesiones)
        self.assertIn(dos["token"], sesiones)
        from backend.servidor import DURACION_SESION
        reloj.time.return_value = reloj.monotonic.return_value = 1000.0 + DURACION_SESION + 1
        nueva = self.sesion().json()
        self.assertEqual(set(sesiones), {nueva["token"]})
        self.assertEqual(self.rpc(nueva, "reader_requests").status_code, 200)
        self.assertEqual(self.rpc(uno, "reader_requests").status_code, 401)

    def test_actividad_sin_correo_en_detalle_conserva_actor_busqueda_y_exportacion_admin(self):
        persona = self.registro().json()
        self.assertEqual(self.sesion().status_code, 200)
        admin = self.sesion(self.ADMIN[0], self.ADMIN[1]).json()
        respuesta = self.rpc(admin, "admin_activity", [50, "lector@prueba.cl"])
        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        entradas = respuesta.json()["resultado"]
        self.assertEqual({e["action"] for e in entradas}, {"registro", "login"})
        for entrada in entradas:
            self.assertNotIn("@", entrada["detail"])
            self.assertEqual(entrada["actor_id"], persona["usuario"]["id"])
            autor = self.rpc(admin, "user", [entrada["actor_id"]]).json()["resultado"]
            self.assertEqual(autor["name"], "Persona de prueba")
        exportado = self.rpc(admin, "export_activity_log")
        self.assertEqual(exportado.status_code, 200)
        texto = exportado.json()["resultado"]
        self.assertIn("Actor:  Persona de prueba (lector@prueba.cl)", texto)
        for linea in texto.splitlines():
            if "Detalle:" in linea:
                self.assertNotIn("@", linea)


class SitioTest(unittest.TestCase):
    """Sitio público (SPEC-008): landing, privacidad, descarga del APK, configuración remota y paneles."""

    def setUp(self):
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        self.publico = carpeta.name
        self.client = TestClient(crear_app(os.path.join(carpeta.name, "bookwho.json"), publico=self.publico))
        self.addCleanup(self.client.close)

    def subir(self, nombre, contenido):  # lo que el equipo copia a BOOKWHO_PUBLICO en el servidor
        with open(os.path.join(self.publico, nombre), "wb") as f:
            f.write(contenido)

    def test_paginas(self):
        for ruta, texto in (("/", "Descargar para Android"), ("/privacidad", "Qué datos guarda la app"),
                            ("/en-vivo/", "Panel de métricas"), ("/simulacion", "Panel de métricas")):
            r = self.client.get(ruta)
            self.assertEqual(r.status_code, 200, ruta)
            self.assertIn(texto, r.text, ruta)
        self.assertEqual(self.client.get("/qr-descarga.svg").headers["content-type"], "image/svg+xml")
        for ruta in ("/logo.svg", "/favicon.ico", "/apple-touch-icon.png"):  # logo y favicon de todas las páginas
            self.assertEqual(self.client.get(ruta).status_code, 200, ruta)
        for ruta in ("/demo/app.mp4", "/demo/app.jpg", "/og-image.jpg"):
            self.assertEqual(self.client.get(ruta).status_code, 200, ruta)
        self.assertEqual(self.client.get("/api/salud").json(), {"ok": True})  # el sitio no tapa la API

    def test_descarga_del_apk(self):
        self.assertEqual(self.client.get("/descargar").status_code, 404)
        self.subir("bookwho.apk", b"PK apk de prueba")
        r = self.client.get("/descargar")
        self.assertEqual((r.status_code, r.content), (200, b"PK apk de prueba"))
        self.assertEqual(r.headers["content-type"], "application/vnd.android.package-archive")
        self.assertIn('filename="BookWho.apk"', r.headers["content-disposition"])
        cabeza = self.client.head("/descargar")
        self.assertEqual((cabeza.status_code, cabeza.headers["content-type"]), (200, "application/vnd.android.package-archive"))
        self.client.get("/descargar", headers={"Range": "bytes=10-"})  # continuación de la misma descarga
        self.assertEqual(self.client.get("/en-vivo/metricas.json").json()["totales"]["descargas_apk"], 1)

    def test_configuracion_remota_editable_en_el_servidor(self):
        with open(os.path.join(RAIZ, "data", "remote_config.json"), encoding="utf-8") as f:
            self.assertEqual(self.client.get("/config.json").json(), json.load(f))
        self.subir("config.json", json.dumps({"banner": "Demo en clase"}).encode())
        r = self.client.get("/config.json")
        self.assertEqual((r.json(), r.headers["cache-control"]), ({"banner": "Demo en clase"}, "no-store"))

    def test_un_dia_sin_actividad_cuenta_como_cero(self):
        self.assertEqual(dias_seguidos({"2026-11-16": 5, "2026-11-18": 2}), ["2026-11-16", "2026-11-17", "2026-11-18"])

    def test_panel_de_la_simulacion(self):
        self.assertEqual(self.client.get("/simulacion/metricas.json").status_code, 404)
        self.subir("metricas.json", json.dumps({"simulado": True}).encode())
        self.assertTrue(self.client.get("/simulacion/metricas.json").json()["simulado"])


if __name__ == "__main__":
    unittest.main()
