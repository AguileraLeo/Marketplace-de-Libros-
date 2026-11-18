"""Contrato HTTP de SPEC-005, sin red externa ni datos de usuarios reales.

Ejecutar desde la raíz:
    python -B -m unittest discover -s tests -p test_backend.py -v

Requiere el servidor y las dependencias ya disponibles. No se omiten pruebas si
falta backend.servidor: ese caso debe aparecer como un error de importación.
Los argumentos RPC son posicionales del Store, siempre sin el actor.
"""

import json
import os
import re
import sys
import tempfile
import unittest
from contextlib import ExitStack
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastapi.testclient import TestClient
except ImportError:  # el backend es opcional: sin FastAPI (p. ej. en el PC de un integrante) se omiten estas pruebas
    raise unittest.SkipTest("Instala backend/requirements.txt para probar el servidor.")

from backend.servidor import RAIZ, crear_app, dias_seguidos
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
