# SPEC-006 — Agentes simulados en vivo

## Objetivo

Mostrar durante la presentación cómo suben los datos en vivo: lectores y vendedores simulados
usan la app **por la misma API que un teléfono** (SPEC-005), y el panel `/reales/` lo refleja.

## Alcance

- `python3 -m backend.agentes --minutos N` crea los agentes con los perfiles de `simulador.py`.
  Cada uno tiene su propia sesión (`services/remoto.RemoteStore`), entra de a poco y actúa
  cada pocos segundos: publica, oferta, acepta, confirma o desiste. Se detiene solo al cumplir
  los minutos, o con Ctrl+C.
- Los agentes también interactúan con las personas: ofertan a solicitudes publicadas desde los
  teléfonos y aceptan ofertas que reciben de ellos.
- El panel indica cuántos agentes simulados y cuántas personas hay activos.

Fuera de alcance: agentes con modelos de lenguaje, y correr los agentes en forma permanente.

## Criterios de aceptación

1. Las cuentas de los agentes son del dominio `bookwho.test`, sus nombres terminan en "(sim)" y
   sus contactos son ficticios.
2. Cada acción pasa por la API con la sesión del propio agente: ninguno puede actuar como otro.
3. El panel nunca presenta a los agentes como personas: el aviso dice "agentes simulados".
4. Un error de negocio (por ejemplo, una oferta que otro aceptó antes) o una caída de red no
   detiene a los agentes: se informa y siguen.
5. Prueba automática contra un servidor real levantado en la prueba.
