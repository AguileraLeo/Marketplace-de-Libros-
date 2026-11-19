"""Analítica RA3 (método MJV App): lee el registro de eventos de un data.json y calcula los KPIs.

Uso, en el PC:   python analitica.py [ruta/data.json]
- Sin ruta usa data/user/data.json (los datos de la app en escritorio).
- Analiza UN archivo por dispositivo: no mezcles data.json de teléfonos distintos
  (cada uno numera sus solicitudes desde 1, así que los ids se repetirían).
- Excluye las cuentas demo y las del equipo (CORREOS_EQUIPO): mide solo a usuarios reales.
  Si los datos vienen de simulador.py (cuentas @bookwho.test), lo rotula como DATOS SIMULADOS.
- Imprime solo conteos: nunca el detalle de los eventos (puede traer correos).
- Genera kpis.png si matplotlib está instalado (no es parte del APK).
Fórmulas y limitaciones: DOCUMENTATION.md.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from statistics import median

from models.store import DEMO_USERS, Delivery
from services.locations import known_location

DATA_ESCRITORIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "user", "data.json")

# Población real = todas las cuentas menos estas. Se compara el correo exacto, nunca "parecidos".
CORREOS_DEMO = {email for _nombre, email, *_ in DEMO_USERS}
CORREOS_EQUIPO = set()  # el equipo agrega aquí los correos con que probó la app, p. ej. {"ana@uct.cl"}
DOMINIO_SIMULADO = "bookwho.test"  # cuentas de simulador.py: datos ficticios, nunca personas reales

CAMPOS = {"at", "actor_id", "action", "detail"}
SOLICITUD = re.compile(r"[Ss]olicitud #(\d+)")
OFERTA = re.compile(r"Oferta #(\d+)")
EVENTOS_KPI = ("solicitud_publicada", "oferta_publicada", "trato_concretado")


def cargar(ruta):
    """Devuelve (usuarios, eventos) del data.json, o dos listas vacías si no se puede leer."""
    try:
        with open(ruta, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"No se pudo leer {ruta}: {exc}")
        return [], []
    if not isinstance(data, dict):
        print(f"{ruta} no tiene el formato de un data.json de BookWho?")
        return [], []
    return data.get("users", []), data.get("activity", [])


def ids_excluidos(usuarios, correos):
    return {u.get("id") for u in usuarios if str(u.get("email", "")).lower() in correos}


def numero(patron, evento):
    m = patron.search(str(evento["detail"]))
    return int(m.group(1)) if m else None


def pct(parte, total):
    return round(parte / total * 100, 1) if total else 0.0


def calcular(eventos, excluidos=frozenset()):
    """KPIs sobre los eventos de la población real (fórmulas en DOCUMENTATION.md)."""
    completos = [e for e in eventos if isinstance(e, dict) and CAMPOS <= e.keys()]
    reales = [e for e in completos if e["actor_id"] not in excluidos]
    # Vendedor de cada oferta (aunque sea una cuenta excluida): un trato con una cuenta excluida
    # no es una resolución real.
    vendedor = {numero(OFERTA, e): e["actor_id"] for e in completos if e["action"] == "oferta_publicada"}

    publicadas, primera_oferta, resueltas, no_procesados = {}, {}, set(), 0
    for e in reales:  # el registro está en orden cronológico
        if e["action"] not in EVENTOS_KPI:
            continue
        sol = numero(SOLICITUD, e)
        if sol is None:  # redacción inesperada: se cuenta y se avisa, en vez de calcular mal en silencio
            no_procesados += 1
        elif e["action"] == "solicitud_publicada":
            publicadas[sol] = e["at"]
        elif e["action"] == "oferta_publicada":
            primera_oferta.setdefault(sol, e["at"])
        else:  # trato_concretado
            oferta = numero(OFERTA, e)
            if oferta is None:
                no_procesados += 1
            elif vendedor.get(oferta) not in excluidos:
                resueltas.add(sol)

    horas = []
    for sol in publicadas.keys() & primera_oferta.keys():
        try:
            espera = datetime.fromisoformat(primera_oferta[sol]) - datetime.fromisoformat(publicadas[sol])
            horas.append(espera.total_seconds() / 3600)
        except (TypeError, ValueError):  # fecha ilegible
            no_procesados += 1

    return {
        "eventos_reales": len(reales),
        "eventos_excluidos": len(completos) - len(reales),
        "cuentas_excluidas": len({e["actor_id"] for e in completos} & set(excluidos)),
        "mal_formados": len(eventos) - len(completos),
        "no_procesados": no_procesados,
        "periodo": (str(reales[0]["at"])[:10], str(reales[-1]["at"])[:10]) if reales else None,
        "eventos_por_tipo": dict(Counter(e["action"] for e in reales)),
        "uso_diario": dict(sorted(Counter(str(e["at"])[:10] for e in reales).items())),
        "usuarios_activos": len({e["actor_id"] for e in reales if e["actor_id"] is not None}),
        "solicitudes_publicadas": len(publicadas),
        # KPI 1: ¿el lector consiguió su libro?
        "kpi_tasa_resolucion": pct(len(resueltas & publicadas.keys()), len(publicadas)),
        # KPI 2: ¿los vendedores responden?
        "kpi_tasa_respuesta": pct(len(primera_oferta.keys() & publicadas.keys()), len(publicadas)),
        # KPI 3: ¿cuánto espera el lector? (solo solicitudes que recibieron oferta)
        "kpi_horas_primera_oferta": round(median(horas), 1) if horas else None,
    }


def region(ubicacion):
    """Región de una comuna del catálogo. Un texto libre (podría ser una dirección) nunca sale tal cual."""
    conocida = known_location(ubicacion)
    return conocida[conocida.find("(") + 1:-1] if conocida else "Sin clasificar"


def desglose(solicitudes, ofertas):
    """Solicitudes, % con oferta y mediana de horas hasta la 1.ª oferta, por región, entrega y precio máximo."""
    primera = {}
    for o in ofertas:
        primera[o.request_id] = min(primera.get(o.request_id, o.created_at), o.created_at)
    claves = {"region": lambda q: region(q.location), "entrega": lambda q: Delivery.LABELS[q.delivery_preference],
              "precio_maximo": lambda q: "con precio máximo" if q.max_price else "sin precio máximo"}
    salida = {}
    for nombre, clave in claves.items():
        grupos = defaultdict(list)
        for q in solicitudes:
            grupos[clave(q)].append(q)
        salida[nombre] = {}
        for grupo, qs in sorted(grupos.items()):
            horas = [(primera[q.id] - q.created_at).total_seconds() / 3600 for q in qs if q.id in primera]
            salida[nombre][grupo] = {"solicitudes": len(qs), "con_oferta_pct": round(100 * len(horas) / len(qs), 1),
                                     "horas_primera_oferta_mediana": round(median(horas), 1) if horas else None}
    return salida


def poblacion(usuarios, eventos, excluidos=frozenset()):
    """'simulados' si todo lo analizado viene de simulador.py, 'reales' si no hay cuentas simuladas
    y 'mezclados' si hay de ambas (no se deben analizar juntas)."""
    simulados = {u.get("id") for u in usuarios if str(u.get("email", "")).lower().endswith("@" + DOMINIO_SIMULADO)}
    actores = {e.get("actor_id") for e in eventos if isinstance(e, dict)} - set(excluidos) - {None}
    if not actores & simulados:
        return "reales"
    return "simulados" if actores <= simulados else "mezclados"


def grafico(r, tipo="reales", salida="kpis.png"):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("(sin matplotlib no se genera kpis.png: pip install matplotlib)")
        return
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.4))
    dias = r["uso_diario"]
    a.bar(list(dias), list(dias.values()), color="#3b6ea5")
    a.set_title(f"Eventos por día (usuarios {tipo})")
    a.tick_params(axis="x", rotation=45)
    nombres = ["Respuesta\n(recibió oferta)", "Resolución\n(trato concretado)"]
    valores = [r["kpi_tasa_respuesta"], r["kpi_tasa_resolucion"]]
    b.bar(nombres, valores, color=["#3b6ea5", "#2e8b57"])
    b.set_ylim(0, 105)
    b.set_title(f"KPIs sobre {r['solicitudes_publicadas']} solicitudes (%)")
    for i, v in enumerate(valores):
        b.text(i, v + 2, f"{v}%", ha="center")
    desde, hasta = r["periodo"]
    horas = r["kpi_horas_primera_oferta"]
    aviso = "" if tipo == "reales" else "DATOS SIMULADOS · "
    fig.suptitle(f"{aviso}BookWho? · {desde} a {hasta} · {r['usuarios_activos']} usuarios · "
                 f"mediana hasta la 1.ª oferta: {'—' if horas is None else f'{horas} h'}")
    fig.tight_layout()
    fig.savefig(salida, dpi=120)
    print(f"Gráfico guardado en {salida}")


def main(ruta):
    usuarios, eventos = cargar(ruta)
    excluidos = ids_excluidos(usuarios, CORREOS_DEMO | CORREOS_EQUIPO)
    r = calcular(eventos, excluidos)
    tipo = poblacion(usuarios, eventos, excluidos)
    if tipo == "simulados":
        print("DATOS SIMULADOS (simulador.py, cuentas del dominio bookwho.test): no son usuarios reales.")
    elif tipo == "mezclados":
        print("ADVERTENCIA: el archivo mezcla cuentas simuladas y reales; analízalas por separado.")
    print(f"Excluidos (cuentas demo/equipo): {r['eventos_excluidos']} evento(s) de {r['cuentas_excluidas']} cuenta(s)")
    if r["mal_formados"] or r["no_procesados"]:
        print(f"ADVERTENCIA: {r['mal_formados']} evento(s) incompleto(s) y {r['no_procesados']} que no se pudieron "
              "interpretar quedaron fuera del cálculo. ¿Cambió la redacción de store._log?")
    if not r["eventos_reales"]:
        print(f"No hay eventos de usuarios {tipo}: todavía no hay datos para calcular KPIs.")
        return
    print(f"Periodo: {r['periodo'][0]} a {r['periodo'][1]} · {r['eventos_reales']} eventos de usuarios {tipo}")
    print("Eventos por tipo:", r["eventos_por_tipo"])
    print("Uso diario:", r["uso_diario"])
    print("Usuarios activos:", r["usuarios_activos"])
    print(f"KPI 1 · Tasa de resolución:  {r['kpi_tasa_resolucion']}%")
    print(f"KPI 2 · Tasa de respuesta:   {r['kpi_tasa_respuesta']}%")
    print(f"KPI 3 · Horas hasta 1.ª oferta (mediana): {r['kpi_horas_primera_oferta']}")
    if r["solicitudes_publicadas"]:
        grafico(r, tipo)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DATA_ESCRITORIO)
