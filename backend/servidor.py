"""Backend compartido de BookWho? (SPEC-005): el mismo models/store.py, ahora en el servidor.

El servidor solo traduce HTTP a métodos del Store: reglas, permisos y estados siguen en el modelo.
El actor de cada llamada sale del token de sesión, nunca de lo que envía el cliente.

En el Z40, desde la raíz del repositorio:
    BOOKWHO_ADMIN_CORREO=... BOOKWHO_ADMIN_CLAVE=... \
    python3 -m uvicorn backend.servidor:app_desde_entorno --factory --host 127.0.0.1 --port 8080
Variables: BOOKWHO_DATOS (datos reales), BOOKWHO_PUBLICO (carpeta con lo que sube el equipo: metricas.json
simulado, bookwho.apk y config.json), BOOKWHO_EXCLUIR (correos del equipo, separados por comas, fuera de los KPIs).
"""
import dataclasses
import logging
import os
import secrets
import threading
import time
from collections import Counter, defaultdict, deque
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import Body, FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

import analitica
from models.store import (
    DomainError, InvalidTransition, NotFound, OfferStatus, PermissionDenied, RequestStatus, Role, Store, User, UserStatus,
    ValidationError,
)
from services import persistence, remoto
from services.locations import known_location

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DURACION_SESION = 12 * 3600
LIMITE_CUERPO = 16 * 1024

# Métodos del Store que acepta /api/rpc (SPEC-005): los mismos que expone la app. Cualquier otro → 404.
CON_ACTOR = set(remoto.CON_ACTOR) | {"export_activity_log"}
SIN_ACTOR = set(remoto.SIN_ACTOR) | {"book"}
SOLO_LECTURA = {
    "reader_requests", "offers_for_request", "get_request", "seller_offers", "seller_contact", "seller_active_offer",
    "open_requests", "offer_contact", "get_offer", "admin_users", "admin_stats", "admin_requests", "admin_offers",
    "admin_activity", "book", "user", "active_offer_count", "export_activity_log",
}
CODIGOS = {ValidationError: 400, PermissionDenied: 403, NotFound: 404, InvalidTransition: 409}
ETIQUETAS = {  # actividad de mercado que puede mostrar el panel; excluye login y registro
    "solicitud_publicada": "Solicitud publicada", "oferta_publicada": "Oferta recibida",
    "oferta_por_concretar": "Aceptada para coordinar", "trato_concretado": "Compra confirmada por el lector",
    "trato_desistido": "Trato desistido", "solicitud_cancelada": "Solicitud cancelada",
    "oferta_cancelada": "Oferta retirada",
}


def a_json(valor, actor: Optional[User]):
    """Entidades → diccionarios con "_tipo". Nunca la contraseña; el correo, solo el propio o para el admin."""
    if dataclasses.is_dataclass(valor):
        datos = {"_tipo": type(valor).__name__}
        datos.update({f.name: a_json(getattr(valor, f.name), actor) for f in dataclasses.fields(valor)})
        if isinstance(valor, User):
            datos.pop("password", None)
            if not actor or (actor.id != valor.id and actor.role != Role.ADMIN):
                datos.update(email="", location="", status="")  # de otra persona la app solo muestra el nombre
        return datos
    if isinstance(valor, datetime):
        return valor.isoformat()
    if isinstance(valor, (list, tuple)):
        return [a_json(v, actor) for v in valor]
    if isinstance(valor, dict):
        return {str(k): a_json(v, actor) for k, v in valor.items()}
    return valor


def error(exc: Exception, codigo: Optional[int] = None) -> JSONResponse:
    codigo = codigo or next((c for tipo, c in CODIGOS.items() if isinstance(exc, tipo)), 400)
    return JSONResponse({"error": str(exc), "tipo": type(exc).__name__}, status_code=codigo)


def textos(datos: dict, *claves: str) -> list:
    """Los campos de registro y sesión deben ser texto: str(None) sería la clave "None"."""
    valores = [datos.get(clave, "") for clave in claves]
    if not all(isinstance(v, str) for v in valores):
        raise ValidationError("Los datos enviados no son válidos.")
    return valores


def no_autorizado() -> JSONResponse:
    return JSONResponse({"error": "Tu sesión venció: vuelve a iniciar sesión.", "tipo": "SesionVencida"}, 401)


def dias_seguidos(uso: dict) -> list:
    """Todos los días entre el primero y el último con eventos: un día sin actividad se ve como 0, no desaparece."""
    if not uso:
        return []
    primero, ultimo = date.fromisoformat(min(uso)), date.fromisoformat(max(uso))
    return [(primero + timedelta(days=n)).isoformat() for n in range((ultimo - primero).days + 1)]


def quitar_cuentas_demo(store: Store) -> int:
    """Ninguna cuenta demo (su clave es pública) llega al servidor, aunque venga en un archivo cargado,
    como el historial de la simulación. Se van con sus solicitudes, ofertas, contactos y eventos."""
    demo = {u.id for u in store.users.values() if u.email in analitica.CORREOS_DEMO}
    solicitudes = {q.id for q in store.requests.values() if q.reader_id in demo}
    ofertas = {o.id for o in store.offers.values() if o.seller_id in demo or o.request_id in solicitudes}
    for tabla, fuera in ((store.users, demo), (store.requests, solicitudes), (store.offers, ofertas), (store.contacts, demo),
                         (store.offer_contacts, ofertas)):
        for clave in [c for c in tabla if c in fuera]:
            del tabla[clave]
    store.activity = [e for e in store.activity if e.actor_id not in demo
                      and analitica.numero(analitica.OFERTA, {"detail": e.detail}) not in ofertas
                      and analitica.numero(analitica.SOLICITUD, {"detail": e.detail}) not in solicitudes]
    vivas = defaultdict(list)
    for oferta in store.offers.values():
        if oferta.status in OfferStatus.ACTIVE:
            vivas[oferta.request_id].append(oferta)
    for solicitud in store.requests.values():
        activas = vivas.get(solicitud.id, [])
        if solicitud.status == RequestStatus.IN_DEAL:
            if any(o.status == OfferStatus.IN_DEAL for o in activas):
                continue
            for oferta in activas:
                if oferta.status == OfferStatus.ON_HOLD:
                    store._transition(oferta, OfferStatus.PUBLISHED, OfferStatus.TRANSITIONS)
            destino = RequestStatus.WITH_OFFERS if activas else RequestStatus.PUBLISHED
            store._transition(solicitud, destino, RequestStatus.TRANSITIONS)
        elif solicitud.status == RequestStatus.WITH_OFFERS and not activas:
            store._transition(solicitud, RequestStatus.PUBLISHED, RequestStatus.TRANSITIONS)
    return len(demo)


def crear_app(ruta_datos: str, admin=None, publico: Optional[str] = None, excluir=()) -> FastAPI:
    store = persistence.load_store(ruta_datos, respaldar=False)
    if store is None and os.path.exists(ruta_datos):
        # Arrancar vacío y guardar encima perdería los datos: mejor no arrancar y que alguien lo revise.
        raise RuntimeError(f"No se pudo leer {ruta_datos}. Restaura un respaldo antes de iniciar el servidor.")
    store = store or Store()
    quitar_cuentas_demo(store)
    if admin and not store.find_user_by_email(admin[0]):
        store.add_user("Administrador", admin[0], admin[1], Role.ADMIN)
    candado = threading.Lock()  # un solo Store y un solo escritor: cada llamada pasa de a una
    sesiones: dict[str, tuple[int, float]] = {}
    descargas = [0]  # ponytail: en memoria, desde el último reinicio; guardarlas en disco si importa el histórico
    revision = [0]
    candado_limites = threading.Lock()
    fallos_correo, fallos_ip, registros_ip = {}, {}, {}
    candado_metricas = threading.Lock()
    cache_metricas = {"datos": None, "vence": 0, "revision": -1}

    def podar_limites(ahora):
        # Siempre bajo candado_limites. No conservar identificadores sin eventos vigentes.
        for contadores, ventana in ((fallos_correo, 600), (fallos_ip, 600), (registros_ip, 3600)):
            for clave, marcas in list(contadores.items()):
                while marcas and marcas[0] <= ahora - ventana:
                    marcas.popleft()
                if not marcas:
                    del contadores[clave]

    def origen_externo(request, datos):
        externo = "cf-connecting-ip" in request.headers
        correo = str(datos.get("correo", "")).strip().lower()
        return externo, request.headers.get("cf-connecting-ip", ""), correo

    def cuenta_reservada(externo, correo):
        return externo and correo.endswith("@" + analitica.DOMINIO_SIMULADO)

    def demasiados_intentos():
        return error(PermissionDenied("Demasiados intentos. Espera unos minutos."), 429)

    def guardar():
        nonlocal store
        os.makedirs(os.path.dirname(os.path.abspath(ruta_datos)), exist_ok=True)
        try:
            persistence.save_store(store, ruta_datos)
        except OSError:
            # Lo que se responde debe ser lo que quedó en disco: se vuelve al último guardado,
            # así un reintento del teléfono no duplica la acción (la respuesta es un 500).
            store = persistence.load_store(ruta_datos, respaldar=False) or Store()
            raise
        # Invalidar por versión no adquiere el candado de métricas dentro del Store.
        revision[0] += 1

    def nueva_sesion(usuario: User) -> dict:
        ahora = time.time()  # los llamadores mantienen el candado del Store
        for anterior, (_, vence) in list(sesiones.items()):
            if vence <= ahora:
                del sesiones[anterior]
        token = secrets.token_urlsafe(32)
        sesiones[token] = (usuario.id, ahora + DURACION_SESION)
        return {"token": token, "usuario": a_json(usuario, usuario)}

    def usuario_de(authorization: Optional[str]) -> Optional[User]:
        token = (authorization or "").removeprefix("Bearer ").strip()
        user_id, vence = sesiones.get(token, (None, 0))
        if user_id is None or vence <= time.time():
            sesiones.pop(token, None)
            return None
        return store.users.get(user_id)

    with candado:
        guardar()

    app = FastAPI(title="BookWho? API", version="1.0", docs_url="/api/docs", openapi_url="/api/openapi.json")

    @app.exception_handler(RequestValidationError)
    async def json_invalido(_request, _exc):
        return error(ValidationError("Los datos enviados no son válidos."))

    @app.middleware("http")
    async def limitar_cuerpo(request, call_next):
        if request.url.path.startswith("/api/") and "transfer-encoding" in request.headers:
            return error(ValidationError("No se admite Transfer-Encoding en la API."), 411)
        try:
            longitud = int(request.headers.get("content-length") or 0)
            if longitud < 0:
                raise ValueError
        except ValueError:
            return error(ValidationError("La longitud de la solicitud no es válida."))
        if longitud > LIMITE_CUERPO:
            return JSONResponse({"error": "La solicitud es demasiado grande.", "tipo": "ValidationError"}, 413)
        return await call_next(request)

    @app.middleware("http")
    async def cabeceras_seguras(request, call_next):
        # Se registra después para envolver también los rechazos del límite de cuerpo.
        try:
            respuesta = await call_next(request)
        except Exception:
            logging.getLogger(__name__).exception("Error interno al procesar una solicitud")
            respuesta = error(DomainError("No se pudo procesar la solicitud."), 500)
        respuesta.headers.update({
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "X-Frame-Options": "DENY",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            "Strict-Transport-Security": "max-age=31536000",
        })
        if respuesta.headers.get("content-type", "").startswith("text/html") and request.url.path != "/api/docs":
            respuesta.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; media-src 'self'; font-src 'self'; connect-src 'self'; "
                "object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
            )
        return respuesta

    @app.get("/api/salud")
    def salud():
        return {"ok": True}

    @app.post("/api/sesion")
    def iniciar_sesion(request: Request, datos: dict = Body(...)):
        try:
            correo_dado, clave = textos(datos, "correo", "clave")
        except ValidationError as exc:
            return error(exc)
        externo, ip, correo = origen_externo(request, datos)
        if cuenta_reservada(externo, correo):
            return error(PermissionDenied("Esta cuenta está reservada para la demostración."))
        with candado:
            # Store -> límites en ambos handlers: comprobar y contabilizar un intento
            # completo no deja pasar solicitudes concurrentes por encima del umbral.
            if externo:
                with candado_limites:
                    podar_limites(time.monotonic())
                    if len(fallos_correo.get(correo, ())) >= 8 or len(fallos_ip.get(ip, ())) >= 30:
                        return demasiados_intentos()
            try:
                usuario = store.authenticate(correo_dado, clave)
            except DomainError as exc:
                if externo:
                    with candado_limites:
                        ahora = time.monotonic()
                        podar_limites(ahora)
                        fallos_correo.setdefault(correo, deque()).append(ahora)
                        fallos_ip.setdefault(ip, deque()).append(ahora)
                return error(exc)
            if externo:
                with candado_limites:
                    fallos_correo.pop(correo, None)
            guardar()  # el login queda en el registro de eventos
            return nueva_sesion(usuario)

    @app.post("/api/registro")
    def registrar(request: Request, datos: dict = Body(...)):
        try:
            campos = textos(datos, "nombre", "correo", "clave", "rol", "comuna")
        except ValidationError as exc:
            return error(exc)
        externo, ip, correo = origen_externo(request, datos)
        # Comprobar también el correo efectivo que persistirá Store.register:
        # el modelo trunca a 120 caracteres antes de convertir a minúsculas.
        correo_guardado = str(datos.get("correo", "")).strip()[:120].lower()
        if cuenta_reservada(externo, correo) or cuenta_reservada(externo, correo_guardado):
            return error(PermissionDenied("Esta cuenta está reservada para la demostración."))
        with candado:
            if externo:
                with candado_limites:
                    podar_limites(time.monotonic())
                    if len(registros_ip.get(ip, ())) >= 40:
                        return demasiados_intentos()
            try:
                usuario = store.register(*campos)
            except DomainError as exc:
                return error(exc)
            if externo:
                with candado_limites:
                    ahora = time.monotonic()
                    podar_limites(ahora)
                    registros_ip.setdefault(ip, deque()).append(ahora)
            guardar()
            return nueva_sesion(usuario)

    @app.delete("/api/sesion")
    def cerrar_sesion(authorization: Optional[str] = Header(default=None)):
        with candado:
            sesiones.pop((authorization or "").removeprefix("Bearer ").strip(), None)
        return Response(status_code=204)

    @app.post("/api/rpc")
    def rpc(datos: dict = Body(...), authorization: Optional[str] = Header(default=None)):
        with candado:
            actor = usuario_de(authorization)
            if actor is None:
                return no_autorizado()
            if actor.status != UserStatus.ACTIVE:  # también para los métodos sin actor (SPEC-010)
                return error(PermissionDenied("Tu cuenta está suspendida."))
            metodo, args = datos.get("metodo"), datos.get("args", [])
            if not isinstance(args, list):
                return error(ValidationError("Los argumentos deben ser una lista."))
            if not isinstance(metodo, str) or metodo not in CON_ACTOR | SIN_ACTOR:
                return error(NotFound("Método no permitido."))
            try:
                # el archivo del log se arma en el teléfono: el servidor solo devuelve el texto
                funcion = store.activity_log_text if metodo == "export_activity_log" else getattr(store, metodo)
                resultado = funcion(actor, *args) if metodo in CON_ACTOR else funcion(*args)
            except DomainError as exc:
                return error(exc)
            except (TypeError, ValueError, AttributeError, KeyError):  # argumentos que no calzan con el método
                # se registra: si es un error del modelo y no del cliente, así no queda oculto
                logging.getLogger(__name__).warning("RPC %s con datos no válidos", metodo, exc_info=True)
                return error(ValidationError("Los datos enviados no son válidos."))
            if metodo not in SOLO_LECTURA:
                guardar()
            return {"resultado": a_json(resultado, actor)}

    def metricas_reales() -> dict:
        """Mismo formato que metricas.json (SPEC-004), con datos reales y sin datos personales."""
        with candado_metricas:
            ahora = time.monotonic()
            if (cache_metricas["datos"] is not None and ahora < cache_metricas["vence"]
                    and cache_metricas["revision"] == revision[0]):
                return cache_metricas["datos"]
            with candado:
                usuarios, eventos = analitica.cargar(ruta_datos)
                excluidos = analitica.ids_excluidos(usuarios, analitica.CORREOS_DEMO | set(excluir))
                excluidos |= {u.id for u in store.users.values() if u.role == Role.ADMIN}  # la moderación no es uso
                r = analitica.calcular(eventos, excluidos)
                reales = {u.id for u in store.users.values() if u.id not in excluidos}
                agentes = {u.id for u in store.users.values() if u.email.endswith("@" + analitica.DOMINIO_SIMULADO)}
                activos = {e.actor_id for e in store.activity}
                origen = {"agentes_simulados": len(agentes & reales & activos), "personas": len((reales - agentes) & activos)}
                solicitudes = [q for q in store.requests.values() if q.reader_id in reales]
                desglose = {k: [{"grupo": g, **v} for g, v in grupos.items()]
                            for k, grupos in analitica.desglose(  # misma población que los KPIs
                                solicitudes, [o for o in store.offers.values() if o.seller_id not in excluidos]).items()}
                actividad = deque(maxlen=12)
                for e in store.activity:
                    if e.action in ETIQUETAS and e.actor_id in reales:
                        numero = analitica.numero(analitica.SOLICITUD, {"detail": e.detail})
                        q = store.requests.get(numero)
                        # solo una comuna del catálogo: el panel es público y la ubicación es texto libre
                        detalle = " · ".join(filter(None, [store.book(q.book_id).title, known_location(q.location)])) if q else ""
                        actividad.append({"hora": e.at.isoformat(timespec="minutes"), "tipo": ETIQUETAS[e.action], "detalle": detalle})
                tipos = r["eventos_por_tipo"]
                resultado = {
                    "simulado": False,
                    "aviso": (f"Demo en vivo: {origen['agentes_simulados']} agentes simulados (cuentas del dominio bookwho.test) "
                              f"y {origen['personas']} personas usan la app con datos de prueba." if origen["agentes_simulados"]
                              else "Datos reales de la prueba en vivo: personas que usan la app con datos de prueba."),
                    "origen": origen,
                    "generado": datetime.now().isoformat(timespec="seconds"),
                    "en_vivo": True,
                    "periodo": {"desde": r["periodo"][0], "hasta": r["periodo"][1]} if r["periodo"] else None,
                    "agentes": {"lectores": sum(store.users[i].role == Role.READER for i in reales),
                                "vendedores": sum(store.users[i].role == Role.SELLER for i in reales)},
                    "kpis": {"resolucion_pct": r["kpi_tasa_resolucion"], "respuesta_pct": r["kpi_tasa_respuesta"],
                             "horas_primera_oferta": r["kpi_horas_primera_oferta"]},
                    "totales": {"eventos": r["eventos_reales"], "usuarios_activos": r["usuarios_activos"],
                                "solicitudes": r["solicitudes_publicadas"], "ofertas": tipos.get("oferta_publicada", 0),
                                "aceptadas_para_coordinar": tipos.get("oferta_por_concretar", 0),
                                "compras_confirmadas": tipos.get("trato_concretado", 0), "descargas_apk": descargas[0]},
                    "uso_diario": [{"dia": d, "eventos": r["uso_diario"].get(d, 0)} for d in dias_seguidos(r["uso_diario"])],
                    "solicitudes_por_estado": dict(sorted(Counter(RequestStatus.LABELS[q.status] for q in solicitudes).items())),
                    "desglose": desglose,
                    "verificacion": None,  # solo existe en la simulación
                    "actividad": list(reversed(actividad)),
                }
                cache_metricas.update(datos=resultado, vence=time.monotonic() + 3, revision=revision[0])
                return resultado

    @app.get("/api/metricas")
    def metricas():
        return metricas_reales()

    def de_publico(nombre):  # archivo que el equipo subió a BOOKWHO_PUBLICO, si existe
        ruta = os.path.join(publico, nombre) if publico else ""
        return ruta if ruta and os.path.isfile(ruta) else None

    def metricas_simuladas():
        ruta = de_publico("metricas.json")
        if not ruta:
            return error(NotFound("Todavía no hay métricas simuladas."))
        return FileResponse(ruta, headers={"Cache-Control": "no-store"})

    # Paneles (SPEC-004), directo del repositorio: /simulacion/ con la simulación del informe y /en-vivo/ con los
    # datos del servidor (agentes simulados y personas, SPEC-006). /reales/ es el nombre anterior de /en-vivo/.
    def redirigir_a(destino):  # sin parámetros: nadie puede usar la redirección para mandar a otro sitio
        return lambda: RedirectResponse(destino)

    def panel():
        return FileResponse(os.path.join(RAIZ, "panel", "index.html"))

    for ruta, datos in (("/simulacion", metricas_simuladas), ("/en-vivo", metricas_reales), ("/reales", metricas_reales)):
        app.add_api_route(ruta, redirigir_a(f"{ruta}/"), methods=["GET"], include_in_schema=False)
        app.add_api_route(f"{ruta}/", panel, methods=["GET"], include_in_schema=False)
        app.add_api_route(f"{ruta}/metricas.json", datos, methods=["GET"], include_in_schema=False)

    # Sitio público (SPEC-008)
    @app.api_route("/descargar", methods=["GET", "HEAD"], include_in_schema=False)  # HEAD: lectores de QR que revisan el enlace
    def descargar(request: Request):
        apk = de_publico("bookwho.apk")
        if not apk:
            return PlainTextResponse("La app todavía no está publicada. Vuelve a intentarlo en un rato.", 404)
        if request.method == "GET" and request.headers.get("range", "bytes=0-").startswith("bytes=0-"):
            with candado:  # una por descarga: no cuentan HEAD ni la continuación de una descarga cortada
                descargas[0] += 1
                revision[0] += 1
        return FileResponse(apk, media_type="application/vnd.android.package-archive", filename="BookWho.apk")

    @app.get("/config.json", include_in_schema=False)
    def configuracion():  # el equipo la cambia en vivo editando BOOKWHO_PUBLICO/config.json, sin reiniciar
        ruta = de_publico("config.json") or os.path.join(RAIZ, "data", "remote_config.json")
        return FileResponse(ruta, media_type="application/json", headers={"Cache-Control": "no-store"})

    app.mount("/fuentes", StaticFiles(directory=os.path.join(RAIZ, "assets", "fonts"), check_dir=False), name="fuentes")
    app.mount("/", StaticFiles(directory=os.path.join(RAIZ, "sitio"), html=True, check_dir=False), name="sitio")  # al final
    return app


def app_desde_entorno() -> FastAPI:
    """Fábrica para uvicorn (--factory): importar este módulo no crea ni toca datos."""
    admin = (os.environ.get("BOOKWHO_ADMIN_CORREO"), os.environ.get("BOOKWHO_ADMIN_CLAVE"))
    return crear_app(
        os.environ.get("BOOKWHO_DATOS", os.path.expanduser("~/bookwho/datos/bookwho.json")),
        admin=admin if all(admin) else None,
        publico=os.environ.get("BOOKWHO_PUBLICO", os.path.expanduser("~/bookwho/publico")),
        excluir=[c.strip().lower() for c in os.environ.get("BOOKWHO_EXCLUIR", "").split(",") if c.strip()],
    )

