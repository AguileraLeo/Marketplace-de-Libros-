"""Simulador de uso de BookWho? con datos FICTICIOS (RA3, SPEC-003).

Agentes lectores y vendedores usan la lógica real de la app (models/store.py) con un reloj
simulado: se registran, inician sesión, publican, ofertan, aceptan para coordinar, confirman,
desisten y cancelan. Todo queda marcado como simulado:
- cuentas del dominio reservado bookwho.test (RFC 2606: no existe) y contactos ficticios;
- escribe solo en --salida (por defecto data/simulacion/), nunca en data/user/.
Misma semilla y mismos parámetros => mismo archivo de datos.

Los KPIs que resultan reflejan los supuestos de los agentes (perfiles y probabilidades de abajo),
no la conducta de usuarios reales: validan la medición y la app, no el mercado.

Uso:   python simulador.py [--semilla 42] [--dias 14] [--inicio 2026-11-03] [--salida RUTA.json]
Luego: python analitica.py data/simulacion/simulacion.json
Panel (SPEC-004): --panel CARPETA escribe CARPETA/metricas.json para panel/index.html, y
--en-vivo MINUTOS sigue la simulación un día más repartido en esos minutos reales.
"""
import argparse
import heapq
import json
import os
import random
import statistics
import sys
import time
import unicodedata
from collections import Counter, defaultdict, deque
from contextlib import contextmanager
from datetime import datetime, timedelta
from types import SimpleNamespace

import analitica
import models.store as modelo
from models.store import (
    Condition, Delivery, DomainError, OfferStatus, RequestStatus, Role, build_demo_store, format_price,
)
from services.books_api import catalog_lookup
from services.locations import normalize_location_name, proximity_label
from services.persistence import save_store

RAIZ = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(RAIZ, "data", "simulacion", "simulacion.json")
DOMINIO = "bookwho.test"  # reservado (RFC 2606): ningún correo simulado puede ser de una persona real
CLAVE = "sim1234"  # contraseña de todas las cuentas simuladas
INICIO = "2026-11-03"

# ------------------------------------------------------------ supuestos (se declaran en el informe)
# Perfiles ficticios redactados con IA (Claude Code) para esta simulación.
LECTORES = [  # (nombre, comuna, perfil)
    ("Camila Rojas", "Temuco", "estudiante"),
    ("Diego Muñoz", "Temuco", "lector"),
    ("Valentina Soto", "Padre Las Casas", "regalo"),
    ("Matías Contreras", "Villarrica", "lector"),
    ("Fernanda Silva", "Temuco", "coleccionista"),
    ("Benjamín Morales", "Concepción", "estudiante"),
    ("Antonia Fuentes", "Concepción", "regalo"),
    ("Joaquín Araya", "Talcahuano", "lector"),
    ("Isidora Castillo", "Concepción", "estudiante"),
    ("Tomás Espinoza", "Santiago", "lector"),
    ("Catalina Reyes", "Santiago", "coleccionista"),
    ("Vicente Herrera", "Providencia", "regalo"),
    ("Martina Díaz", "Ñuñoa", "estudiante"),
    ("Agustín Vargas", "Santiago", "lector"),
    ("Josefa Tapia", "Valparaíso", "estudiante"),
    ("Lucas Sepúlveda", "Viña del Mar", "lector"),
    ("Florencia Cortés", "Viña del Mar", "regalo"),
    ("Gaspar Núñez", "Valparaíso", "coleccionista"),
    ("Emilia Pizarro", "Puerto Montt", "lector"),
    ("Maximiliano Jara", "Osorno", "estudiante"),
    ("Sofía Carrasco", "Temuco", "regalo"),
    ("Cristóbal Vera", "Concepción", "lector"),
    ("Amanda Bravo", "Santiago", "estudiante"),
    ("Renato Lagos", "Coyhaique", "coleccionista"),
]
VENDEDORES = [  # (nombre, comuna, tipo, libros que tiene)
    ("Librería Raíces", "Temuco", "libreria",
     ["hobbit", "cien-anos", "1984", "principito", "sapiens", "casa-espiritus", "rayuela"]),
    ("Librería Biobío", "Concepción", "libreria",
     ["hobbit", "cien-anos", "1984", "quijote", "sapiens", "ficciones", "pedro-paramo"]),
    ("Librería Mapocho", "Santiago", "libreria",
     ["hobbit", "cien-anos", "quijote", "principito", "rayuela", "casa-espiritus", "sapiens", "ficciones"]),
    ("Ignacio Paredes", "Padre Las Casas", "particular", ["rayuela", "ficciones", "principito"]),
    ("Libros Usados Bellavista", "Providencia", "usados",
     ["1984", "quijote", "rayuela", "pedro-paramo", "cien-anos", "ficciones"]),
    ("Carla Medina", "Talcahuano", "particular", ["principito", "1984", "casa-espiritus"]),
    ("Librería Puerto", "Valparaíso", "libreria", ["hobbit", "1984", "principito", "sapiens", "pedro-paramo"]),
    ("Javier Riquelme", "Ñuñoa", "particular", ["sapiens", "hobbit", "ficciones"]),
    ("Libros del Sur", "Temuco", "usados", ["quijote", "ficciones", "pedro-paramo", "hobbit", "1984"]),
    ("Paula Alarcón", "Viña del Mar", "particular", ["cien-anos", "rayuela", "casa-espiritus"]),
]
PRECIO_REF = {  # precios de referencia ficticios (CLP), libros del catálogo local de la app
    "hobbit": 14990, "cien-anos": 15990, "1984": 11990, "quijote": 18990, "principito": 8990,
    "rayuela": 16990, "casa-espiritus": 15990, "sapiens": 21990, "ficciones": 12990, "pedro-paramo": 10990,
}
TIPOS = {  # condición que ofrece, precio sobre la referencia, revisiones del feed por día, horario, disposición
    "libreria": dict(condicion=Condition.NEW, precio=(0.95, 1.10), revisiones=3, horario=(10, 20), disposicion=1.0),
    "usados": dict(condicion=Condition.USED, precio=(0.50, 0.75), revisiones=2, horario=(11, 19), disposicion=0.9),
    "particular": dict(condicion=Condition.USED, precio=(0.45, 0.70), revisiones=1, horario=(19, 23),
                       disposicion=0.6),
}
PERFILES = {  # condición aceptada y entrega (con pesos), (prob. de poner precio máximo, rango sobre la referencia)
    "estudiante": dict(condicion=((Condition.USED, 6), (Condition.ANY, 4)), tope=(0.85, 0.50, 0.80),
                       entrega=((Delivery.IN_PERSON, 6), (Delivery.ANY, 4)),
                       notas=("Lo necesito para un ramo de la universidad.", "Me sirve aunque esté subrayado.", "")),
    "regalo": dict(condicion=((Condition.NEW, 9), (Condition.ANY, 1)), tope=(0.70, 1.00, 1.30),
                   entrega=((Delivery.ANY, 5), (Delivery.SHIPPING, 3), (Delivery.IN_PERSON, 2)),
                   notas=("Es para un regalo, idealmente nuevo.", "Que venga sin marcas, es para regalar.", "")),
    "coleccionista": dict(condicion=((Condition.ANY, 7), (Condition.NEW, 3)), tope=(0.30, 1.10, 1.60),
                          entrega=((Delivery.ANY, 8), (Delivery.SHIPPING, 2)),
                          notas=("Busco una edición en tapa dura.", "Me interesa una edición antigua en buen estado.", "")),
    "lector": dict(condicion=((Condition.ANY, 8), (Condition.USED, 2)), tope=(0.50, 0.70, 1.10),
                   entrega=((Delivery.IN_PERSON, 5), (Delivery.ANY, 5)),
                   notas=("Cualquier edición me sirve.", "Puedo retirarlo en el centro.", "")),
}
DESCRIPCIONES = {
    Condition.NEW: ("Nuevo, sellado.", "Nuevo, edición actual."),
    Condition.USED: ("Usado, buen estado.", "Usado, tapas con algo de desgaste.", "Usado, sin subrayar."),
}
NOTAS_OFERTA = ("", "Lo puedo reservar unos días.", "Coordinamos la entrega por teléfono.")
P_OFERTA = {"Misma comuna": 0.85, "Misma región": 0.60, "lejos con envío": 0.25}
P_ACEPTAR = (0.60, 0.90)  # con una oferta / con dos o más
HORAS_PARA_CERRAR = (6, 72)
P_CONFIRMAR, P_DESISTIR_LECTOR = 0.72, 0.20  # el resto queda en coordinación
P_DESISTIR_VENDEDOR, P_CANCELAR_OFERTA = 0.03, 0.05
DIAS_PARA_RENDIRSE, P_CANCELAR_SOLICITUD = 5, 0.35
P_SONDA = 0.08  # probabilidad de intentar algo inválido en una sesión


def correo(nombre):
    texto = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
    return ".".join(texto.lower().split()) + "@" + DOMINIO


def redondear(monto):
    """Precio con terminación 990, como en las librerías (mínimo $990)."""
    return max(990, round(monto / 1000) * 1000 - 10)


def region(ubicacion):
    return ubicacion[ubicacion.find("(") + 1:-1] if ubicacion.endswith(")") else ubicacion


def guardar_json(ruta, datos):
    """Escritura atómica: quien lea el archivo (el panel) nunca ve uno a medio escribir."""
    with open(ruta + ".tmp", "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    os.replace(ruta + ".tmp", ruta)


@contextmanager
def reloj_simulado(sim):
    """La app toma la hora con datetime.now(): durante la simulación responde la hora simulada."""
    real = modelo.datetime

    class _Simulado(real):
        @classmethod
        def now(cls, tz=None):
            return sim.reloj

    modelo.datetime = _Simulado
    try:
        yield
    finally:
        modelo.datetime = real


class Simulacion:
    def __init__(self, semilla, dias, inicio, n_lectores, n_vendedores):
        self.parametros = dict(semilla=semilla, dias=dias, inicio=inicio, lectores=n_lectores, vendedores=n_vendedores)
        self.rnd = random.Random(semilla)
        self.inicio = datetime.fromisoformat(inicio)
        self.fin = self.inicio + timedelta(days=dias)
        self.reloj = self.inicio
        self.cola, self.turno = [], 0
        self.lectores = [self.agente(n, c, Role.READER, perfil=p) for n, c, p in LECTORES[:n_lectores]]
        self.vendedores = [
            self.agente(n, c, Role.SELLER, tipo=TIPOS[t], stock=["demo-" + x for x in libros],
                        telefono=f"+56 9 0000 {i:04d}", punto=f"Punto de encuentro ficticio, {c}")
            for i, (n, c, t, libros) in enumerate(VENDEDORES[:n_vendedores], 1)
        ]
        self.vistas, self.ocultos = set(), set()  # cada vendedor evalúa una vez cada solicitud
        self.tiempos = defaultdict(list)
        self.contacto = {"verificaciones": 0, "violaciones": []}
        self.sondas = {"verificaciones": 0, "violaciones": []}
        self.fallas = []
        self.actividad = deque(maxlen=12)  # para el panel: tipo de acción, libro y comuna; nunca personas

    def anotar(self, tipo, detalle=""):
        self.actividad.append({"hora": self.reloj.isoformat(timespec="minutes"), "tipo": tipo, "detalle": detalle})

    def titulo(self, request_id):
        return self.store.book(self.store.requests[request_id].book_id).title

    @staticmethod
    def agente(nombre, comuna, rol, **extra):
        return SimpleNamespace(nombre=f"{nombre} (sim)", correo=correo(nombre), comuna=normalize_location_name(comuna),
                               rol=rol, usuario=None, **extra)

    # ---------------------------------------------------------------- motor de eventos
    def agendar(self, momento, accion, *args):
        if self.reloj <= momento < self.fin:
            self.turno += 1  # desempate estable: dos eventos a la misma hora salen en el orden agendado
            heapq.heappush(self.cola, (momento, self.turno, accion, args))

    def momento(self, dia, horario):
        return self.inicio + timedelta(days=int(dia), minutes=round(self.rnd.uniform(horario[0] * 60, horario[1] * 60)))

    def en(self, horas):
        return self.reloj + timedelta(minutes=round(self.rnd.uniform(horas[0] * 60, horas[1] * 60)))

    def elegir(self, pares):
        return self.rnd.choices([o for o, _ in pares], weights=[w for _, w in pares])[0]

    def ejecutar(self):
        with reloj_simulado(self):
            self.store = build_demo_store(catalog_lookup)
            for obj in [*self.store.users.values(), *self.store.requests.values(), *self.store.offers.values()]:
                obj.created_at = self.inicio  # los datos de demo se crean con la hora real del equipo
                if hasattr(obj, "updated_at"):
                    obj.updated_at = self.inicio
            self.libros = {f"demo-{k}": self.store.upsert_book(catalog_lookup(f"demo-{k}")).id for k in PRECIO_REF}
            self.libro_ext = {v: k for k, v in self.libros.items()}
            dias = (self.fin - self.inicio).days
            for v in self.vendedores:
                self.agendar(self.momento(self.rnd.uniform(0, 1), v.tipo["horario"]), self.registrar_vendedor, v)
            for lec in self.lectores:
                self.agendar(self.momento(self.rnd.uniform(0, dias * 0.6), (9, 23)), self.registrar_lector, lec)
            while self.cola:
                self.reloj, _, accion, args = heapq.heappop(self.cola)
                accion(*args)
        return self.store

    # ---------------------------------------------------------------- acciones medidas
    def accion(self, nombre, fn, *args):
        """Paso normal: el agente ya revisó el estado, así que cualquier error es inesperado y se informa."""
        t0 = time.perf_counter()
        try:
            resultado = fn(*args)
        except Exception as exc:  # incluye DomainError: un paso válido no debería rechazarse
            self.fallas.append({"accion": nombre, "momento": self.reloj.isoformat(), "error": f"{type(exc).__name__}: {exc}"})
            return None
        self.tiempos[nombre].append((time.perf_counter() - t0) * 1000)
        return resultado

    def esperar_rechazo(self, registro, descripcion, fn, *args):
        """Acción que la app DEBE rechazar: si la acepta, es una violación de sus reglas."""
        registro["verificaciones"] += 1
        try:
            fn(*args)
        except DomainError:
            return
        except Exception as exc:
            self.fallas.append({"accion": descripcion, "momento": self.reloj.isoformat(), "error": f"{type(exc).__name__}: {exc}"})
            return
        registro["violaciones"].append(descripcion)

    def login(self, agente):
        return self.accion("login", self.store.authenticate, agente.correo, CLAVE)

    # ---------------------------------------------------------------- vendedores
    def registrar_vendedor(self, v):
        v.usuario = self.accion("registro", self.store.register, v.nombre, v.correo, CLAVE, Role.SELLER, v.comuna)
        if not v.usuario:
            return
        v.usuario.created_at = self.reloj
        self.anotar("Nueva cuenta de vendedor")
        for d in range((self.reloj - self.inicio).days, (self.fin - self.inicio).days):
            for _ in range(v.tipo["revisiones"]):
                self.agendar(self.momento(d, v.tipo["horario"]), self.sesion_vendedor, v)

    def precio_ofertado(self, v, req):
        ext = self.libro_ext.get(req.book_id)
        if ext not in v.stock:
            return None
        cercania = proximity_label(v.comuna, req.location)
        if cercania in P_OFERTA:
            p = P_OFERTA[cercania]
        elif req.delivery_preference != Delivery.IN_PERSON:
            p = P_OFERTA["lejos con envío"]
        else:
            return None
        if req.accepted_condition not in (Condition.ANY, v.tipo["condicion"]):
            p *= 0.25
        precio = redondear(PRECIO_REF[ext[5:]] * self.rnd.uniform(*v.tipo["precio"]))
        if req.max_price and precio > req.max_price:
            if self.rnd.random() < 0.5:
                precio = req.max_price  # se ajusta al tope del lector
            else:
                p *= 0.3
        return precio if self.rnd.random() < p * v.tipo["disposicion"] else None

    def sesion_vendedor(self, v):
        st = self.store
        if not self.login(v):
            return
        for req in st.open_requests(v.usuario):
            if (v.usuario.id, req.id) in self.vistas:
                continue
            self.vistas.add((v.usuario.id, req.id))
            precio = self.precio_ofertado(v, req)
            if precio is None:
                continue
            condicion = v.tipo["condicion"]
            oferta = self.accion("ofertar", st.create_offer, v.usuario, req.id, str(precio), condicion,
                                 self.rnd.choice(DESCRIPCIONES[condicion]), self.rnd.choice(NOTAS_OFERTA),
                                 v.telefono, v.correo, v.punto)
            if oferta:
                oferta.created_at = oferta.updated_at = self.reloj
                self.anotar("Oferta recibida", f"{self.titulo(req.id)} · {format_price(precio)} · "
                                               f"{Condition.LABELS[condicion].lower()}")
        for o in st.seller_offers(v.usuario):
            if o.status == OfferStatus.IN_DEAL and self.rnd.random() < P_DESISTIR_VENDEDOR:
                if self.accion("desistir (vendedor)", st.cancel_deal, v.usuario, o.id, "Ya no tengo el libro (simulado)"):
                    self.anotar("Trato desistido por el vendedor", self.titulo(o.request_id))
            elif (o.status == OfferStatus.PUBLISHED and self.reloj - o.created_at >= timedelta(days=3)
                  and self.rnd.random() < P_CANCELAR_OFERTA):
                if self.accion("cancelar oferta", st.cancel_offer, v.usuario, o.id):
                    self.anotar("Oferta retirada", self.titulo(o.request_id))
        if self.rnd.random() < P_SONDA:
            self.sonda_vendedor(v)

    def sonda_vendedor(self, v):
        st = self.store
        propias = [o for o in st.seller_offers(v.usuario) if o.status == OfferStatus.PUBLISHED]
        if propias and self.rnd.random() < 0.5:
            o = self.rnd.choice(propias)
            self.esperar_rechazo(self.sondas, "se aceptó una oferta duplicada", st.create_offer,
                                 v.usuario, o.request_id, "5000", Condition.USED, "", "", v.telefono, "", "")
            return
        abiertas = st.open_requests(v.usuario)
        if abiertas:
            self.esperar_rechazo(self.sondas, "se aceptó una oferta con precio 0", st.create_offer,
                                 v.usuario, self.rnd.choice(abiertas).id, "0", Condition.USED, "", "", v.telefono, "", "")

    # ---------------------------------------------------------------- lectores
    def registrar_lector(self, lec):
        lec.usuario = self.accion("registro", self.store.register, lec.nombre, lec.correo, CLAVE, Role.READER, lec.comuna)
        if not lec.usuario:
            return
        lec.usuario.created_at = self.reloj
        self.anotar("Nueva cuenta de lector")
        hoy, dias = (self.reloj - self.inicio).days, (self.fin - self.inicio).days
        libros = self.rnd.sample(list(self.libros), self.rnd.choice((1, 1, 2, 2, 3)))
        self.agendar(self.en((0.1, 0.6)), self.publicar, lec, libros[0])
        for ext in libros[1:]:
            self.agendar(max(self.momento(self.rnd.uniform(hoy, dias), (9, 23)), self.en((1, 2))), self.publicar, lec, ext)
        for d in range(hoy + 1, dias):
            self.agendar(self.momento(d, (9, 23)), self.sesion_lector, lec)

    def publicar(self, lec, ext):
        perfil = PERFILES[lec.perfil]
        if not self.login(lec):
            return
        prob_tope, f0, f1 = perfil["tope"]
        tope = str(redondear(PRECIO_REF[ext[5:]] * self.rnd.uniform(f0, f1))) if self.rnd.random() < prob_tope else ""
        req = self.accion("publicar", self.store.create_request, lec.usuario, self.libros[ext], tope,
                          self.elegir(perfil["condicion"]), lec.comuna, self.elegir(perfil["entrega"]),
                          self.rnd.choice(perfil["notas"]))
        if req:
            req.created_at = self.reloj
            self.anotar("Solicitud publicada", f"{self.store.book(req.book_id).title} · {lec.comuna}")

    def costo(self, req, oferta):
        """Cómo compara el lector: precio, más un castigo si no es la condición que pidió o el vendedor está lejos."""
        castigo = 0
        if req.accepted_condition not in (Condition.ANY, oferta.book_condition):
            castigo += 3000
        if proximity_label(self.store.users[oferta.seller_id].location, req.location).startswith("Otra región"):
            castigo += 2000
        return oferta.price + castigo, oferta.id

    def sesion_lector(self, lec):
        st = self.store
        activas = [r for r in st.reader_requests(lec.usuario) if r.status in RequestStatus.ACTIVE]
        if not activas or not self.login(lec):
            return
        for req in activas:
            if req.status == RequestStatus.IN_DEAL:
                continue  # se cierra con su propio evento
            vivas = [o for o in st.offers_for_request(lec.usuario, req.id) if o.status == OfferStatus.PUBLISHED]
            for o in vivas:
                if o.id not in self.ocultos:  # antes de aceptar, el lector NO debe ver el contacto
                    self.ocultos.add(o.id)
                    self.esperar_rechazo(self.contacto, "el contacto se vio antes de aceptar",
                                         st.offer_contact, lec.usuario, o.id)
            if vivas and self.rnd.random() < P_ACEPTAR[len(vivas) > 1]:
                mejor = min(vivas, key=lambda o: self.costo(req, o))
                if self.accion("aceptar para coordinar", st.accept_offer, lec.usuario, mejor.id):
                    self.anotar("Aceptada para coordinar", self.titulo(req.id))
                    self.verificar_contacto(lec, mejor)
                    self.agendar(self.en(HORAS_PARA_CERRAR), self.cerrar_trato, lec, mejor.id)
            elif (not vivas and req.status == RequestStatus.PUBLISHED
                  and self.reloj - req.created_at >= timedelta(days=DIAS_PARA_RENDIRSE)
                  and self.rnd.random() < P_CANCELAR_SOLICITUD):
                if self.accion("cancelar solicitud", st.cancel_request, lec.usuario, req.id, "Ya no lo necesito (simulado)"):
                    self.anotar("Solicitud cancelada", self.titulo(req.id))
        if self.rnd.random() < P_SONDA:
            ajenas = [o for o in st.offers.values() if o.status == OfferStatus.PUBLISHED
                      and st.requests[o.request_id].reader_id != lec.usuario.id]
            if ajenas:
                self.esperar_rechazo(self.sondas, "un lector aceptó una oferta ajena",
                                     st.accept_offer, lec.usuario, self.rnd.choice(ajenas).id)

    def verificar_contacto(self, lec, oferta):
        """Tras aceptar: el lector ve el contacto del vendedor; otro lector y otro vendedor, no."""
        st = self.store
        self.contacto["verificaciones"] += 1
        visto = self.accion("ver contacto", st.offer_contact, lec.usuario, oferta.id)
        if visto is None or visto.phone != st.contacts[oferta.seller_id].phone:
            self.contacto["violaciones"].append("el lector no ve el contacto de la oferta que aceptó")
        otros_lectores = [x for x in self.lectores if x.usuario and x is not lec]
        otros_vendedores = [x for x in self.vendedores if x.usuario and x.usuario.id != oferta.seller_id]
        for grupo, quien in ((otros_lectores, "otro lector"), (otros_vendedores, "otro vendedor")):
            if grupo:
                self.esperar_rechazo(self.contacto, f"{quien} vio el contacto",
                                     st.offer_contact, self.rnd.choice(grupo).usuario, oferta.id)

    def cerrar_trato(self, lec, oferta_id):
        st = self.store
        if st.offers[oferta_id].status != OfferStatus.IN_DEAL or not self.login(lec):
            return  # el vendedor desistió antes
        r = self.rnd.random()
        titulo = self.titulo(st.offers[oferta_id].request_id)
        if r < P_CONFIRMAR:
            if self.accion("confirmar compra", st.confirm_deal, lec.usuario, oferta_id):
                self.anotar("Compra confirmada por el lector", titulo)
        elif r < P_CONFIRMAR + P_DESISTIR_LECTOR:
            if self.accion("desistir (lector)", st.cancel_deal, lec.usuario, oferta_id, "No nos pusimos de acuerdo (simulado)"):
                self.anotar("Trato desistido por el lector", titulo)

    # ---------------------------------------------------------------- resumen
    def resumen(self):
        st = self.store
        simulados = {u.id for u in st.users.values() if u.email.endswith("@" + DOMINIO)}
        solicitudes = [r for r in st.requests.values() if r.reader_id in simulados]
        primera = {}
        for o in st.offers.values():
            if o.request_id not in primera or o.created_at < primera[o.request_id]:
                primera[o.request_id] = o.created_at

        def desglose(clave):
            grupos = defaultdict(list)
            for r in solicitudes:
                grupos[clave(r)].append(r)
            salida = {}
            for nombre, reqs in sorted(grupos.items()):
                horas = [(primera[r.id] - r.created_at).total_seconds() / 3600 for r in reqs if r.id in primera]
                salida[nombre] = {
                    "solicitudes": len(reqs),
                    "con_oferta_pct": round(100 * len(horas) / len(reqs), 1),
                    "horas_primera_oferta_mediana": round(statistics.median(horas), 1) if horas else None,
                }
            return salida

        return {
            "simulado": True,
            "aviso": "Datos ficticios de simulador.py: reflejan los supuestos de los agentes, no conducta de usuarios reales.",
            "parametros": self.parametros,
            "periodo": [self.inicio.date().isoformat(), (self.fin - timedelta(days=1)).date().isoformat()],
            "agentes": {"lectores": len(self.lectores), "vendedores": len(self.vendedores)},
            "solicitudes_por_estado": dict(sorted(Counter(RequestStatus.LABELS[r.status] for r in solicitudes).items())),
            "ofertas": sum(o.seller_id in simulados for o in st.offers.values()),
            "contacto": self.contacto,
            "sondas": self.sondas,
            "fallas_inesperadas": self.fallas,
            "tiempo_por_accion_ms": {n: {"veces": len(t), "mediana": round(statistics.median(t), 3)}
                                     for n, t in sorted(self.tiempos.items())},
            "desglose": {
                "region": desglose(lambda r: region(r.location)),
                "entrega": desglose(lambda r: Delivery.LABELS[r.delivery_preference]),
                "precio_maximo": desglose(lambda r: "con precio máximo" if r.max_price else "sin precio máximo"),
            },
        }

    # ---------------------------------------------------------------- modo en vivo (SPEC-004)
    def continuar_en_vivo(self, minutos, al_actuar, dias=1):
        """Sigue la simulación `dias` días más, repartidos en `minutos` reales, y avisa tras cada acción."""
        self.rnd = random.Random(self.parametros["semilla"] + 1)  # otra secuencia: el periodo base no cambia
        dia0 = (self.fin - self.inicio).days
        self.reloj, self.fin = self.fin, self.fin + timedelta(days=dias)
        ritmo = dias * 86400 / max(minutos * 60, 0.001)  # segundos simulados por cada segundo real
        lector_de = {lec.usuario.id: lec for lec in self.lectores if lec.usuario}
        with reloj_simulado(self):
            for d in range(dia0, dia0 + dias):
                for v in self.vendedores:
                    for _ in range(v.tipo["revisiones"] if v.usuario else 0):
                        self.agendar(self.momento(d, v.tipo["horario"]), self.sesion_vendedor, v)
                for lec in lector_de.values():
                    self.agendar(self.momento(d, (9, 23)), self.sesion_lector, lec)
                    if self.rnd.random() < 0.3:
                        self.agendar(self.momento(d, (9, 23)), self.publicar, lec, self.rnd.choice(list(self.libros)))
            for o in list(self.store.offers.values()):  # los tratos abiertos se cierran durante la demo
                lec = lector_de.get(self.store.requests[o.request_id].reader_id)
                if o.status == OfferStatus.IN_DEAL and lec:
                    self.agendar(self.en((1, 20)), self.cerrar_trato, lec, o.id)
            while self.cola:
                momento, _, accion, args = heapq.heappop(self.cola)
                time.sleep((momento - self.reloj).total_seconds() / ritmo)
                self.reloj = momento
                accion(*args)
                al_actuar()


def exportar_panel(sim, ruta_datos, carpeta, en_vivo=False):
    """metricas.json para panel/index.html (SPEC-004): conteos y KPIs, nunca datos de personas."""
    usuarios, eventos = analitica.cargar(ruta_datos)
    r = analitica.calcular(eventos, analitica.ids_excluidos(usuarios, analitica.CORREOS_DEMO | analitica.CORREOS_EQUIPO))
    res, tipos = sim.resumen(), r["eventos_por_tipo"]
    os.makedirs(carpeta, exist_ok=True)
    guardar_json(os.path.join(carpeta, "metricas.json"), {
        "simulado": True,
        "aviso": res["aviso"],
        "generado": datetime.now().isoformat(timespec="seconds"),
        "en_vivo": en_vivo,
        "periodo": {"desde": r["periodo"][0], "hasta": r["periodo"][1]} if r["periodo"] else None,
        "agentes": res["agentes"],
        "kpis": {"resolucion_pct": r["kpi_tasa_resolucion"], "respuesta_pct": r["kpi_tasa_respuesta"],
                 "horas_primera_oferta": r["kpi_horas_primera_oferta"]},
        "totales": {"eventos": r["eventos_reales"], "usuarios_activos": r["usuarios_activos"],
                    "solicitudes": r["solicitudes_publicadas"], "ofertas": tipos.get("oferta_publicada", 0),
                    "aceptadas_para_coordinar": tipos.get("oferta_por_concretar", 0),
                    "compras_confirmadas": tipos.get("trato_concretado", 0)},
        "uso_diario": [{"dia": d, "eventos": n} for d, n in r["uso_diario"].items()],
        "solicitudes_por_estado": res["solicitudes_por_estado"],
        "desglose": {k: [{"grupo": g, **v} for g, v in grupos.items()] for k, grupos in res["desglose"].items()},
        "verificacion": {
            "contacto": {"verificaciones": res["contacto"]["verificaciones"],
                         "violaciones": len(res["contacto"]["violaciones"])},
            "acciones_invalidas": {"intentos": res["sondas"]["verificaciones"],
                                   "aceptadas": len(res["sondas"]["violaciones"])},
            "fallas": len(res["fallas_inesperadas"]),
        },
        "actividad": list(reversed(sim.actividad)),  # la más reciente primero
    })


def simular(semilla=42, dias=14, inicio=INICIO, lectores=len(LECTORES), vendedores=len(VENDEDORES), salida=SALIDA,
            panel=None, en_vivo=None):
    """Corre la simulación y guarda el data.json simulado, su resumen y, si se pide, el metricas.json del panel."""
    salida = os.path.abspath(salida)
    if salida.startswith(os.path.join(RAIZ, "data", "user") + os.sep):
        raise SystemExit("La simulación no se escribe en data/user/: ahí están los datos de la app.")
    sim = Simulacion(semilla, dias, inicio, lectores, vendedores)
    sim.ejecutar()
    os.makedirs(os.path.dirname(salida), exist_ok=True)

    def guardar(vivo=False):
        save_store(sim.store, salida)
        guardar_json(os.path.splitext(salida)[0] + "_resumen.json", sim.resumen())
        if panel:
            exportar_panel(sim, salida, panel, vivo)

    guardar()
    if en_vivo:
        print(f"En vivo: un día simulado más en {en_vivo:g} minutos (Ctrl+C para detener).", flush=True)
        try:
            sim.continuar_en_vivo(en_vivo, lambda: guardar(vivo=True))
        finally:
            guardar()  # al terminar, o con Ctrl+C, el panel deja de decir "en vivo"
    return sim.resumen()


def main(argv=None):
    p = argparse.ArgumentParser(description="Simulador de uso de BookWho? con datos ficticios (SPEC-003).")
    p.add_argument("--semilla", type=int, default=42)
    p.add_argument("--dias", type=int, default=14)
    p.add_argument("--inicio", default=INICIO, help="primer día simulado (AAAA-MM-DD)")
    p.add_argument("--lectores", type=int, default=len(LECTORES))
    p.add_argument("--vendedores", type=int, default=len(VENDEDORES))
    p.add_argument("--salida", default=SALIDA)
    p.add_argument("--panel", metavar="CARPETA", help="escribe CARPETA/metricas.json para panel/index.html")
    p.add_argument("--en-vivo", type=float, metavar="MINUTOS", help="sigue un día más, repartido en esos minutos")
    a = p.parse_args(argv)
    try:
        r = simular(a.semilla, a.dias, a.inicio, a.lectores, a.vendedores, a.salida, a.panel, a.en_vivo)
    except KeyboardInterrupt:
        print("Simulación en vivo detenida: los datos y el panel quedaron guardados.")
        return 0
    estados = ", ".join(f"{n} {e.lower()}" for e, n in r["solicitudes_por_estado"].items())
    print(f"SIMULACIÓN (datos ficticios) · semilla {a.semilla} · {r['periodo'][0]} a {r['periodo'][1]} · "
          f"{r['agentes']['lectores']} lectores y {r['agentes']['vendedores']} vendedores simulados")
    print(f"Solicitudes: {sum(r['solicitudes_por_estado'].values())} ({estados}) · ofertas: {r['ofertas']}")
    print(f"Contacto: {r['contacto']['verificaciones']} verificaciones, {len(r['contacto']['violaciones'])} violaciones · "
          f"sondas: {r['sondas']['verificaciones']} acciones inválidas, {len(r['sondas']['violaciones'])} aceptadas por error")
    print(f"Fallas inesperadas: {len(r['fallas_inesperadas'])}")
    print(f"Datos: {os.path.relpath(a.salida)} · siguiente paso: python analitica.py {os.path.relpath(a.salida)}")
    if a.panel:
        print(f"Panel: {os.path.join(a.panel, 'metricas.json')} (se ve con panel/index.html en la misma carpeta)")
    return 1 if (r["contacto"]["violaciones"] or r["sondas"]["violaciones"] or r["fallas_inesperadas"]) else 0


if __name__ == "__main__":
    sys.exit(main())
