# SPEC-006 — Agentes simulados en vivo

## Objetivo

Mostrar durante la presentación cómo suben los datos en vivo: lectores y vendedores simulados
usan la app **por la misma API que un teléfono** (SPEC-005), y el panel `/en-vivo/` lo refleja.

## Alcance

- `python3 -m backend.agentes --minutos N` crea los agentes con los perfiles de `simulador.py`.
  Cada uno tiene su propia sesión (`services/remoto.RemoteStore`). Cada turno es una sesión en la
  app: el agente inicia sesión (o se registra, si es nuevo) y hace de 1 a 3 cosas según su
  situación: publica, oferta, acepta, confirma, desiste, retira una oferta antigua o cancela una
  solicitud sin respuesta. Durante la demo llegan algunas personas simuladas nuevas. Se detiene
  solo al cumplir los minutos, o con Ctrl+C.
- Para que el panel no parta vacío, el servidor puede partir con el historial de la simulación del
  informe (`simulador.py --salida`, con el servicio detenido). Al arrancar elimina las cuentas demo,
  y los agentes siguen con las cuentas del historial.
- Los agentes también interactúan con las personas: ofertan a solicitudes publicadas desde los
  teléfonos y aceptan ofertas que reciben de ellos.
- La API informa cuántos agentes simulados y cuántas personas hay activos. El
  panel identifica la demo con una fuente discreta al pie, sin advertencia
  superior, por solicitud del usuario; el equipo explica el detalle en vivo.

Fuera de alcance: agentes con modelos de lenguaje, y correr los agentes en forma permanente.

## Criterios de aceptación

1. Las cuentas de los agentes son del dominio `bookwho.test`, sus nombres terminan en "(sim)" y
   sus contactos son ficticios.
2. Cada acción pasa por la API con la sesión del propio agente: ninguno puede actuar como otro.
3. El panel nunca presenta a los agentes como personas: el pie identifica los
   "agentes simulados" cuando hay datos mixtos, sin un aviso de advertencia.
4. Un error de negocio (por ejemplo, una oferta que otro aceptó antes) o una caída de red no
   detiene a los agentes: se informa y siguen.
5. Prueba automática contra un servidor real levantado en la prueba.
6. El servidor elimina las cuentas demo de cualquier archivo que cargue.
