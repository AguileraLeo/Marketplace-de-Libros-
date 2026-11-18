"""Backend compartido de BookWho? (SPEC-005): el mismo models/store.py, ahora en el servidor.

El servidor solo traduce HTTP a métodos del Store: reglas, permisos y estados siguen en el modelo.
El actor de cada llamada sale del token de sesión, nunca de lo que envía el cliente.

En el Z40, desde la raíz del repositorio:
    BOOKWHO_ADMIN_CORREO=... BOOKWHO_ADMIN_CLAVE=... \
    python3 -m uvicorn backend.servidor:app_desde_entorno --factory --host 127.0.0.1 --port 8080
Variables: BOOKWHO_DATOS (datos reales), BOOKWHO_PUBLICO (carpeta del metricas.json simulado),
BOOKWHO_EXCLUIR (correos del equipo, separados por comas, fuera de los KPIs).
"""
import dataclasses
import os
import secrets
import tempfile
import threading
import time
from collections import Counter, defaultdict, deque
from datetime import datetime
from statistics import median
from typing import Optional

from fastapi import Body, FastAPI, Header
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response

import analitica
from models.store import (
    Delivery, DomainError, InvalidTransition, NotFound, PermissionDenied, RequestStatus, Role, Store, User,
    ValidationError,
)
from services import persistence

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DURACION_SESION = 12 * 3600
LIMITE_CUERPO = 16 * 1024

# Métodos del Store que acepta /api/rpc (SPEC-005). Cualquier otro → 404.
CON_ACTOR = {
    "reader_requests", "offers_for_request", "get_request", "cancel_request", "cancel_deal", "set_user_status",
    "seller_offers", "seller_contact", "seller_active_offer", "open_requests", "offer_contact", "get_offer",
    "create_request", "create_offer", "accept_offer", "confirm_deal", "cancel_offer",
    "admin_users", "admin_stats", "admin_requests", "admin_offers", "admin_activity",
}
SIN_ACTOR = {"book", "user", "active_offer_count", "upsert_book", "recover_password"}
SOLO_LECTURA = {
    "reader_requests", "offers_for_request", "get_request", "seller_offers", "seller_contact", "seller_active_offer",
    "open_requests", "offer_contact", "get_offer", "admin_users", "admin_stats", "admin_requests", "admin_offers",
    "admin_activity", "book", "user", "active_offer_count", "recover_password", "export_activity_log",
}
CODIGOS = {ValidationError: 400, PermissionDenied: 403, NotFound: 404, InvalidTransition: 409}
ETIQUETAS = {  # actividad que el panel puede mostrar: nunca login ni registro (traen correos)
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
                datos["email"] = ""
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


def no_autorizado() -> JSONResponse:
    return JSONResponse({"error": "Tu sesión venció: vuelve a iniciar sesión.", "tipo": "SesionVencida"}, 401)


def crear_app(ruta_datos: str, admin=None, publico: Optional[str] = None, excluir=()) -> FastAPI:
    store = persistence.load_store(ruta_datos) or Store()  # sin cuentas demo: arranca vacío
    if admin and not store.find_user_by_email(admin[0]):
        store.add_user("Administrador", admin[0], admin[1], Role.ADMIN)
    candado = threading.Lock()  # un solo Store y un solo escritor: cada llamada pasa de a una
    sesiones: dict[str, tuple[int, float]] = {}

    def guardar():
        os.makedirs(os.path.dirname(os.path.abspath(ruta_datos)), exist_ok=True)
        persistence.save_store(store, ruta_datos)

    def nueva_sesion(usuario: User) -> dict:
        token = secrets.token_urlsafe(32)
        sesiones[token] = (usuario.id, time.time() + DURACION_SESION)
        return {"token": token, "usuario": a_json(usuario, usuario)}

    def usuario_de(authorization: Optional[str]) -> Optional[User]:
        token = (authorization or "").removeprefix("Bearer ").strip()
        user_id, vence = sesiones.get(token, (None, 0))
        if user_id is None or vence < time.time():
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
        if int(request.headers.get("content-length") or 0) > LIMITE_CUERPO:
            return JSONResponse({"error": "La solicitud es demasiado grande.", "tipo": "ValidationError"}, 413)
        return await call_next(request)

    @app.get("/api/salud")
    def salud():
        return {"ok": True}

    @app.post("/api/sesion")
    def iniciar_sesion(datos: dict = Body(...)):
        with candado:
            try:
                usuario = store.authenticate(str(datos.get("correo", "")), str(datos.get("clave", "")))
            except DomainError as exc:
                return error(exc)
            guardar()  # el login queda en el registro de eventos
            return nueva_sesion(usuario)

    @app.post("/api/registro")
    def registrar(datos: dict = Body(...)):
        with candado:
            try:
                usuario = store.register(*(str(datos.get(k, "")) for k in ("nombre", "correo", "clave", "rol", "comuna")))
            except DomainError as exc:
                return error(exc)
            guardar()
            return nueva_sesion(usuario)

    @app.delete("/api/sesion")
    def cerrar_sesion(authorization: Optional[str] = Header(default=None)):
        sesiones.pop((authorization or "").removeprefix("Bearer ").strip(), None)
        return Response(status_code=204)

    @app.post("/api/rpc")
    def rpc(datos: dict = Body(...), authorization: Optional[str] = Header(default=None)):
        with candado:
            actor = usuario_de(authorization)
            if actor is None:
                return no_autorizado()
            metodo, args = datos.get("metodo"), datos.get("args", [])
            if not isinstance(args, list):
                return error(ValidationError("Los argumentos deben ser una lista."))
            if not isinstance(metodo, str) or metodo not in CON_ACTOR | SIN_ACTOR | {"export_activity_log"}:
                return error(NotFound("Método no permitido."))
            try:
                if metodo == "export_activity_log":  # el archivo se arma en el teléfono, no en el servidor
                    with tempfile.TemporaryDirectory() as carpeta:
                        ruta = store.export_activity_log(actor, os.path.join(carpeta, "registro.log"))
                        with open(ruta, encoding="utf-8") as f:
                            resultado = f.read()
                else:
                    funcion = getattr(store, metodo)
                    resultado = funcion(actor, *args) if metodo in CON_ACTOR else funcion(*args)
            except DomainError as exc:
                return error(exc)
            except (TypeError, ValueError, AttributeError, KeyError):  # argumentos que no calzan con el método
                return error(ValidationError("Los datos enviados no son válidos."))
            if metodo not in SOLO_LECTURA:
                guardar()
            return {"resultado": a_json(resultado, actor)}

    def metricas_reales() -> dict:
        """Mismo formato que metricas.json (SPEC-004), con datos reales y sin datos personales."""
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
            primera = {}
            for o in store.offers.values():
                primera[o.request_id] = min(primera.get(o.request_id, o.created_at), o.created_at)
            # ponytail: repite el desglose de simulador.Simulacion.resumen; si crece, pasarlo a un módulo común
            desglose = {}
            for nombre, clave in (("region", lambda q: q.location[q.location.find("(") + 1:-1] if q.location.endswith(")") else q.location),
                                  ("entrega", lambda q: Delivery.LABELS[q.delivery_preference]),
                                  ("precio_maximo", lambda q: "con precio máximo" if q.max_price else "sin precio máximo")):
                grupos = defaultdict(list)
                for q in solicitudes:
                    grupos[clave(q)].append(q)
                desglose[nombre] = []
                for grupo, qs in sorted(grupos.items()):
                    horas = [(primera[q.id] - q.created_at).total_seconds() / 3600 for q in qs if q.id in primera]
                    desglose[nombre].append({"grupo": grupo, "solicitudes": len(qs),
                                             "con_oferta_pct": round(100 * len(horas) / len(qs), 1),
                                             "horas_primera_oferta_mediana": round(median(horas), 1) if horas else None})
            actividad = deque(maxlen=12)
            for e in store.activity:
                if e.action in ETIQUETAS and e.actor_id in reales:
                    numero = analitica.numero(analitica.SOLICITUD, {"detail": e.detail})
                    q = store.requests.get(numero)
                    detalle = f"{store.book(q.book_id).title} · {q.location}" if q else ""
                    actividad.append({"hora": e.at.isoformat(timespec="minutes"), "tipo": ETIQUETAS[e.action], "detalle": detalle})
            tipos = r["eventos_por_tipo"]
            return {
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
                            "compras_confirmadas": tipos.get("trato_concretado", 0)},
                "uso_diario": [{"dia": d, "eventos": n} for d, n in r["uso_diario"].items()],
                "solicitudes_por_estado": dict(sorted(Counter(RequestStatus.LABELS[q.status] for q in solicitudes).items())),
                "desglose": desglose,
                "verificacion": None,  # solo existe en la simulación
                "actividad": list(reversed(actividad)),
            }

    @app.get("/api/metricas")
    def metricas():
        return metricas_reales()

    # El panel sale directo del repositorio: / con los datos simulados y /reales/ con los reales.
    @app.get("/")
    def panel_simulado():
        return FileResponse(os.path.join(RAIZ, "panel", "index.html"))

    @app.get("/metricas.json")
    def metricas_simuladas():
        ruta = os.path.join(publico or "", "metricas.json")
        if not os.path.isfile(ruta):
            return error(NotFound("Todavía no hay métricas simuladas."))
        return FileResponse(ruta, headers={"Cache-Control": "no-store"})

    @app.get("/reales")
    def reales_sin_barra():
        return RedirectResponse("/reales/")

    @app.get("/reales/")
    def reales():
        return FileResponse(os.path.join(RAIZ, "panel", "index.html"))

    @app.get("/reales/metricas.json")
    def reales_metricas():
        return metricas_reales()

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

