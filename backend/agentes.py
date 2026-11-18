"""Agentes simulados en vivo (SPEC-006): lectores y vendedores ficticios que usan la app por la API.

Cada agente tiene su propia sesión (services/remoto.RemoteStore), igual que un teléfono: pasa por el
mismo servidor, el mismo modelo y los mismos permisos. Usan los perfiles de simulador.py, cuentas
del dominio bookwho.test y contactos ficticios, así que el panel los muestra como agentes simulados.
Su comportamiento es una versión simplificada de la simulación: sirve para la demostración en vivo,
no para medir.

En el Z40, desde la raíz del repositorio:
    python3 -m backend.agentes --minutos 5                 # contra el servidor local (127.0.0.1:8080)
    python3 -m backend.agentes --minutos 5 --servidor https://bookwho.quadcorestore.com
"""
import argparse
import random
import time
from datetime import datetime

import simulador
from models.store import Condition, Delivery, DomainError, OfferStatus, RequestStatus
from services.books_api import catalog_lookup
from services.locations import proximity_label
from services.remoto import RemoteStore, SesionVencida, SinConexion

PRECIO_GENERICO = 12990  # libros fuera del catálogo local (p. ej. los que buscan las personas en Google Books)


class Agente:
    def __init__(self, url, nombre, comuna, rol, **extra):
        datos = simulador.Simulacion.agente(nombre, comuna, rol, **extra)  # "(sim)", @bookwho.test y comuna normalizada
        self.__dict__.update(vars(datos))
        self.cliente = RemoteStore(url)
        self.vistas = set()  # solicitudes que este vendedor ya evaluó

    def entrar(self):
        """Se registra; si la cuenta ya existe (otra corrida), inicia sesión."""
        try:
            self.usuario = self.cliente.register(self.nombre, self.correo, simulador.CLAVE, self.rol, self.comuna)
            return "se registró"
        except DomainError:
            self.usuario = self.cliente.authenticate(self.correo, simulador.CLAVE)
            return "inició sesión"


class Demo:
    def __init__(self, url, lectores=10, vendedores=5, semilla=None, salida=print):
        self.rnd, self.salida = random.Random(semilla), salida
        self.lectores = [Agente(url, n, c, "lector", perfil=p) for n, c, p in simulador.LECTORES[:lectores]]
        self.vendedores = [
            Agente(url, n, c, "vendedor", tipo=simulador.TIPOS[t], stock=libros,
                   telefono=f"+56 9 0000 {i:04d}", punto=f"Punto de encuentro ficticio, {c}")
            for i, (n, c, t, libros) in enumerate(simulador.VENDEDORES[:vendedores], 1)
        ]
        self.afuera = self.lectores + self.vendedores
        self.rnd.shuffle(self.afuera)
        self.adentro = []

    def anotar(self, agente, texto):
        self.salida(f"{datetime.now():%H:%M:%S} · {agente.nombre} {texto}")

    def titulo(self, agente, book_id):
        return agente.cliente.book(book_id).title

    # ------------------------------------------------------------ turnos
    def entra_uno(self):
        agente = self.afuera.pop()
        try:
            texto = agente.entrar()
        except DomainError:
            self.afuera.append(agente)  # vuelve a la fila: lo intenta en otro turno
            raise
        self.adentro.append(agente)
        self.anotar(agente, texto)

    def turno_lector(self, a):
        cli, r = a.cliente, self.rnd
        activas = [q for q in cli.reader_requests(None) if q.status in RequestStatus.ACTIVE]
        for q in activas:  # 1) cerrar un trato en coordinación
            if q.status == RequestStatus.IN_DEAL:
                trato = next((o for o in cli.offers_for_request(None, q.id) if o.status == OfferStatus.IN_DEAL), None)
                azar = r.random()
                if trato and azar < 0.5:
                    cli.confirm_deal(None, trato.id)
                    return self.anotar(a, f"confirmó la compra de «{self.titulo(a, q.book_id)}»")
                if trato and azar < 0.6:
                    cli.cancel_deal(None, trato.id, "No nos pusimos de acuerdo (simulado)")
                    return self.anotar(a, f"desistió del trato por «{self.titulo(a, q.book_id)}»")
        for q in activas:  # 2) aceptar la mejor oferta
            vivas = [o for o in cli.offers_for_request(None, q.id) if o.status == OfferStatus.PUBLISHED]
            if vivas and r.random() < 0.7:
                mejor = min(vivas, key=lambda o: (o.price, o.id))
                cli.accept_offer(None, mejor.id)
                return self.anotar(a, f"aceptó una oferta por «{self.titulo(a, q.book_id)}»")
        if len(activas) < 2 and r.random() < 0.6:  # 3) publicar una solicitud
            perfil = simulador.PERFILES[a.perfil]
            clave = r.choice(list(simulador.PRECIO_REF))
            libro = cli.upsert_book(catalog_lookup(f"demo-{clave}"))
            prob_tope, f0, f1 = perfil["tope"]
            tope = str(simulador.redondear(simulador.PRECIO_REF[clave] * r.uniform(f0, f1))) if r.random() < prob_tope else ""
            elegir = lambda pares: r.choices([o for o, _ in pares], weights=[w for _, w in pares])[0]  # noqa: E731
            cli.create_request(None, libro.id, tope, elegir(perfil["condicion"]), a.comuna, elegir(perfil["entrega"]),
                               r.choice(perfil["notas"]))
            self.anotar(a, f"publicó una solicitud de «{libro.title}»")

    def turno_vendedor(self, v):
        cli, r = v.cliente, self.rnd
        for q in cli.open_requests(None):
            if q.id in v.vistas:
                continue
            v.vistas.add(q.id)
            libro = cli.book(q.book_id)
            clave = libro.external_id.removeprefix("demo-")
            p = simulador.P_OFERTA.get(proximity_label(v.comuna, q.location))
            if p is None:
                p = simulador.P_OFERTA["lejos con envío"] if q.delivery_preference != Delivery.IN_PERSON else 0
            if clave not in v.stock:  # un libro que no tiene: a veces lo consigue igual
                p, base = p * 0.4, PRECIO_GENERICO
            else:
                base = simulador.PRECIO_REF[clave]
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

    # ------------------------------------------------------------ bucle
    def correr(self, minutos, ritmo=(4, 9)):
        fin = time.monotonic() + minutos * 60
        while time.monotonic() < fin:
            agente = None
            try:
                if self.afuera and (len(self.adentro) < 4 or self.rnd.random() < 0.25):
                    self.entra_uno()  # cuatro entran al tiro y el resto de a poco: el panel muestra cómo crece
                else:
                    agente = self.rnd.choice(self.adentro)
                    (self.turno_lector if agente.rol == "lector" else self.turno_vendedor)(agente)
            except SesionVencida:  # el servidor se reinició: vuelve a entrar
                if agente:
                    self.anotar(agente, agente.entrar())
            except SinConexion as exc:
                self.salida(f"{datetime.now():%H:%M:%S} · {exc} Reintento en 10 s.")
                time.sleep(10)
            except DomainError as exc:  # p. ej. otra persona aceptó la oferta antes: se informa y se sigue
                if agente:
                    self.anotar(agente, f"no pudo: {exc}")
            time.sleep(self.rnd.uniform(*ritmo))


def main(argv=None):
    p = argparse.ArgumentParser(description="Agentes simulados en vivo de BookWho? (SPEC-006).")
    p.add_argument("--minutos", type=float, default=5)
    p.add_argument("--servidor", default="http://127.0.0.1:8080")
    p.add_argument("--lectores", type=int, default=10)
    p.add_argument("--vendedores", type=int, default=5)
    a = p.parse_args(argv)
    print(f"Agentes simulados: {a.lectores} lectores y {a.vendedores} vendedores durante {a.minutos:g} minutos "
          f"contra {a.servidor} (Ctrl+C para detener).", flush=True)
    try:
        Demo(a.servidor, a.lectores, a.vendedores, salida=lambda t: print(t, flush=True)).correr(a.minutos)
    except KeyboardInterrupt:
        pass
    print("Agentes detenidos: los datos quedaron en el servidor.")


if __name__ == "__main__":
    main()
