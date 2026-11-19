# SPEC-010 — Suspender una cuenta la saca del mercado

## Objetivo

Que un usuario suspendido desaparezca del mercado de inmediato, sin borrar datos que otras
personas, la auditoría o los KPIs necesitan.

## Decisión

Decidido por el equipo el 19-11-2026 (AGENTS.md §19, «eliminación lógica vs física»): suspender
**no borra** la cuenta. El borrado físico deja referencias rotas: al quitar las cuentas demo, una
solicitud quedó `EN_COORDINACION` sin ofertas y sin forma de destrabarla. Además, la app consulta
a los usuarios por id, y se perderían la reactivación y el registro de la moderación.

## Alcance

Cuando el administrador suspende una cuenta:

1. La cuenta no puede iniciar sesión ni operar (regla existente). En el servidor, una sesión que
   ya estaba abierta deja de servir para **cualquier** método, también los que no llevan actor.
2. Sus solicitudes `PUBLICADA`, `CON_OFERTAS` o `EN_COORDINACION` pasan a `CANCELADA`, por
   moderación y con el motivo «Cuenta suspendida». Sus ofertas activas se cancelan (regla existente
   de cancelar solicitud).
3. Sus ofertas `PUBLICADA` o `EN_ESPERA` pasan a `CANCELADA`. Si una solicitud queda sin ofertas
   activas, vuelve a `PUBLICADA` (regla existente de cancelar oferta).
4. Si tenía una oferta `POR_CONCRETAR`, el trato se desiste: la oferta pasa a `CANCELADA`, las
   ofertas `EN_ESPERA` de esa solicitud vuelven a `PUBLICADA` y la solicitud a `CON_OFERTAS` o
   `PUBLICADA` (regla existente de desistir).
5. Cada cancelación queda en el registro de actividad, además del evento `usuario_suspendido`.
6. Reactivar devuelve el acceso, **no** el contenido cancelado.

Fuera de alcance: eliminar o anonimizar una cuenta a pedido de la persona (spec aparte),
notificar a terceros y suspensiones temporales.

## Criterios de aceptación

1. Tras suspender a un vendedor con ofertas activas, en espera y por concretar, ninguna sigue
   activa y las solicitudes afectadas quedan en un estado válido de la máquina de estados.
2. Tras suspender a un lector, sus solicitudes no aparecen en el feed de ningún vendedor.
3. Un lector no puede aceptar una oferta de un vendedor suspendido, porque ya no existe una
   oferta activa de esa cuenta.
4. Una sesión abierta antes de la suspensión recibe 403 en todos los métodos de `/api/rpc`.
5. Reactivar no reabre lo cancelado.
6. Pruebas automáticas en `tests/test_store.py` y `tests/test_backend.py`.
