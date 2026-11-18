"""Agentes simulados en vivo (SPEC-006): lectores y vendedores ficticios que usan la app por la API.

Cada agente tiene su propia sesión (services/remoto.RemoteStore), igual que un teléfono: pasa por el
mismo servidor, el mismo modelo y los mismos permisos. Usan los perfiles de simulador.py, cuentas del
dominio bookwho.test y contactos ficticios, así que el panel los muestra como agentes simulados.

Cada turno es una sesión: el agente "abre la app" (inicia sesión, o se registra si es nuevo) y hace de
1 a 3 cosas según cómo estén sus solicitudes u ofertas. Si en el servidor ya está cargado el historial
de la simulación, los agentes siguen con esas mismas cuentas. Es una versión simplificada de la
simulación: sirve para la demostración en vivo, no para medir.

En el Z40, desde la raíz del repositorio:
    python3 -m backend.agentes --minutos 180                    # contra el servidor local (127.0.0.1:8080)
    python3 -m backend.agentes --minutos 5 --ritmo 3 8           # prueba corta y más rápida
"""
import argparse
import random
import time
from datetime import datetime, timedelta

import simulador
from models.store import Condition, Delivery, DomainError, OfferStatus, RequestStatus
from services.books_api import catalog_lookup
from services.locations import proximity_label
from services.remoto import RemoteStore, SinConexion

PRECIO_GENERICO = 12990  # libros fuera del catálogo local (p. ej. los que buscan las personas en Google Books)
# Personas ficticias que llegan durante la demo (redactadas con IA, como los perfiles de simulador.py).
NUEVOS_LECTORES = [
    ("Paula Ibarra", "Temuco", "estudiante"), ("Nicolás Fuentes", "Concepción", "lector"),
    ("Javiera Ortiz", "Santiago", "regalo"), ("Felipe Navarro", "Valparaíso", "coleccionista"),
    ("Daniela Muñoz", "Padre Las Casas", "lector"), ("Sebastián Rojas", "Viña del Mar", "estudiante"),
]
NUEVOS_VENDEDORES = [
    ("Librería La Frontera", "Temuco", "libreria", ["rayuela", "1984", "principito", "ficciones", "hobbit"]),
    ("Rodrigo Saavedra", "Concepción", "particular", ["sapiens", "cien-anos", "pedro-paramo"]),
]


class Agente:
    def __init__(self, url, nombre, comuna, rol, **extra):
        datos = simulador.Simulacion.agente(nombre, comuna, rol, **extra)  # "(sim)", @bookwho.test y comuna normalizada
        self.__dict__.update(vars(datos))
        self.cliente = RemoteStore(url)
        self.vistas = set()  # solicitudes que este vendedor ya evaluó

    def entrar(self):
        """Abre la app: inicia sesión; si la cuenta todavía no existe, se registra."""
        try:
            self.usuario = self.cliente.authenticate(self.correo, simulador.CLAVE)
            return False
        except SinConexion:
            raise
        except DomainError:
            self.usuario = self.cliente.register(self.nombre, self.correo, simulador.CLAVE, self.rol, self.comuna)
            return True


def _lector(url, persona):
    nombre, comuna, perfil = persona
    return Agente(url, nombre, comuna, "lector", perfil=perfil)


def _vendedor(url, persona, numero):
    nombre, comuna, tipo, libros = persona
    return Agente(url, nombre, comuna, "vendedor", tipo=simulador.TIPOS[tipo], stock=libros,
                  telefono=f"+56 9 0000 {numero:04d}", punto=f"Punto de encuentro ficticio, {comuna}")


class Demo:
    def __init__(self, url, lectores=24, vendedores=10, semilla=None, salida=print):
        self.rnd, self.salida = random.Random(semilla), salida
        self.agentes = [_lector(url, p) for p in simulador.LECTORES[:lectores]]
        self.agentes += [_vendedor(url, p, i) for i, p in enumerate(simulador.VENDEDORES[:vendedores], 1)]
        self.nuevos = [_lector(url, p) for p in NUEVOS_LECTORES]
        self.nuevos += [_vendedor(url, p, 11 + i) for i, p in enumerate(NUEVOS_VENDEDORES)]
        self.rnd.shuffle(self.nuevos)

    def anotar(self, agente, texto):
        """Informa una acción; devuelve True para cortar el turno ("ya hizo algo")."""
        self.salida(f"{datetime.now():%H:%M:%S} · {agente.nombre} {texto}")
        return True

    def titulo(self, agente, book_id):
        return agente.cliente.book(book_id).title

    # ------------------------------------------------------------ una sesión en la app
    def sesion(self, agente):
        if agente.entrar():
            self.anotar(agente, "se registró")
        for _ in range(1 + (self.rnd.random() < 0.5) + (self.rnd.random() < 0.2)):  # de 1 a 3 cosas
            hizo = (self.turno_lector if agente.rol == "lector" else self.turno_vendedor)(agente)
            if not hizo:
                break

    def turno_lector(self, a):
        cli, r = a.cliente, self.rnd
        activas = [q for q in cli.reader_requests(None) if q.status in RequestStatus.ACTIVE]
        for q in activas:  # cerrar un trato en coordinación
            if q.status != RequestStatus.IN_DEAL:
                continue
            trato = next((o for o in cli.offers_for_request(None, q.id) if o.status == OfferStatus.IN_DEAL), None)
            azar = r.random()
            if trato and azar < 0.45:
                cli.confirm_deal(None, trato.id)
                return self.anotar(a, f"confirmó la compra de «{self.titulo(a, q.book_id)}»")
            if trato and azar < 0.55:
                cli.cancel_deal(None, trato.id, "No nos pusimos de acuerdo (simulado)")
                return self.anotar(a, f"desistió del trato por «{self.titulo(a, q.book_id)}»")
        for q in activas:  # aceptar la mejor oferta
            vivas = [o for o in cli.offers_for_request(None, q.id) if o.status == OfferStatus.PUBLISHED]
            if vivas and r.random() < 0.65:
                mejor = min(vivas, key=lambda o: (o.price, o.id))
                cli.accept_offer(None, mejor.id)
                return self.anotar(a, f"aceptó una oferta de ${mejor.price:,} por «{self.titulo(a, q.book_id)}»"
                                   .replace(",", "."))
        for q in activas:  # rendirse con una solicitud vieja que nadie respondió
            if (q.status == RequestStatus.PUBLISHED and datetime.now() - q.created_at > timedelta(hours=6)
                    and r.random() < 0.15):
                cli.cancel_request(None, q.id, "Ya no lo necesito (simulado)")
                return self.anotar(a, f"canceló su solicitud de «{self.titulo(a, q.book_id)}»")
        if len(activas) < 2 and r.random() < 0.5:  # publicar una solicitud nueva
            perfil, clave = simulador.PERFILES[a.perfil], r.choice(list(simulador.PRECIO_REF))
            libro = cli.upsert_book(catalog_lookup(f"demo-{clave}"))
            prob_tope, f0, f1 = perfil["tope"]
            tope = str(simulador.redondear(simulador.PRECIO_REF[clave] * r.uniform(f0, f1))) if r.random() < prob_tope else ""
            elegir = lambda pares: r.choices([o for o, _ in pares], weights=[w for _, w in pares])[0]  # noqa: E731
            cli.create_request(None, libro.id, tope, elegir(perfil["condicion"]), a.comuna, elegir(perfil["entrega"]),
                               r.choice(perfil["notas"]))
            return self.anotar(a, f"publicó una solicitud de «{libro.title}»")
        return False

    def turno_vendedor(self, v):
        cli, r = v.cliente, self.rnd
        for o in cli.seller_offers(None):  # a veces se arrepiente
            if o.status == OfferStatus.IN_DEAL and r.random() < 0.04:
                cli.cancel_deal(None, o.id, "Ya no tengo el libro (simulado)")
                return self.anotar(v, "desistió de un trato: ya no tiene el libro")
            if (o.status == OfferStatus.PUBLISHED and datetime.now() - o.created_at > timedelta(hours=3)
                    and r.random() < 0.05):
                titulo = self.titulo(v, cli.requests[o.request_id].book_id)
                cli.cancel_offer(None, o.id)
                return self.anotar(v, f"retiró su oferta por «{titulo}»")
        for q in cli.open_requests(None):  # revisar solicitudes nuevas y ofertar
            if q.id in v.vistas:
                continue
            v.vistas.add(q.id)
            libro = cli.book(q.book_id)
            clave = libro.external_id.removeprefix("demo-")
            p = simulador.P_OFERTA.get(proximity_label(v.comuna, q.location))
            if p is None:
                p = simulador.P_OFERTA["lejos con envío"] if q.delivery_preference != Delivery.IN_PERSON else 0
            if clave in v.stock:
                base = simulador.PRECIO_REF[clave]
            else:  # un libro que no tiene: a veces lo consigue igual
                p, base = p * 0.4, PRECIO_GENERICO
            condicion = v.tipo["condicion"]
            if q.accepted_condition not in (Condition.ANY, condicion):
                p *= 0.25
            if r.random() >= p * v.tipo["disposicion"]:
                continue
            precio = simulador.redondear(base * r.uniform(*v.tipo["precio"]))
            if q.max_price and precio > q.max_price:
                precio = q.max_price
            cli.create_offer(None, q.id, str(precio), condicion, r.choice(simulador.DESCRIPCIONES[condicion]),
                             r.choice(simulador.NOTAS_OFERTA), v.telefono, v.correo, v.punto)
            return self.anotar(v, f"ofertó ${precio:,} por «{libro.title}»".replace(",", "."))
        return False

    # ------------------------------------------------------------ bucle
    def correr(self, minutos, ritmo=(15, 45)):
        fin = time.monotonic() + minutos * 60
        while time.monotonic() < fin:
            agente = None
            try:
                if self.nuevos and self.rnd.random() < 0.06:  # de vez en cuando llega alguien nuevo
                    agente = self.nuevos.pop()
                    self.agentes.append(agente)
                else:
                    agente = self.rnd.choice(self.agentes)
                self.sesion(agente)
            except SinConexion as exc:
                self.salida(f"{datetime.now():%H:%M:%S} · {exc} Reintento en 10 s.")
                time.sleep(10)
            except DomainError as exc:  # p. ej. otra persona aceptó la oferta antes: se informa y se sigue
                if agente:
                    self.anotar(agente, f"no pudo: {exc}")
            time.sleep(self.rnd.uniform(*ritmo))


def main(argv=None):
    p = argparse.ArgumentParser(description="Agentes simulados en vivo de BookWho? (SPEC-006).")
    p.add_argument("--minutos", type=float, default=180)
    p.add_argument("--ritmo", type=float, nargs=2, default=(15, 45), metavar=("MIN", "MAX"),
                   help="segundos entre una sesión y la siguiente")
    p.add_argument("--servidor", default="http://127.0.0.1:8080")
    a = p.parse_args(argv)
    print(f"Agentes simulados durante {a.minutos:g} minutos contra {a.servidor}, una sesión cada "
          f"{a.ritmo[0]:g}–{a.ritmo[1]:g} s (Ctrl+C para detener).", flush=True)
    try:
        Demo(a.servidor, salida=lambda t: print(t, flush=True)).correr(a.minutos, tuple(a.ritmo))
    except KeyboardInterrupt:
        pass
    print("Agentes detenidos: los datos quedaron en el servidor.", flush=True)


if __name__ == "__main__":
    main()
