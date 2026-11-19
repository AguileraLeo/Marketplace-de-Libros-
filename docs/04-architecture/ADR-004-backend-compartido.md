# ADR-004 — Backend compartido con modelo remoto

## Estado

Aceptado el 19-11-2026: el backend está desplegado en el Z40 y lo usaron agentes y personas en la E4.
Propuesto el 17-11-2026 (CLAUDE.md, regla 6).
Especificación: [SPEC-005](../05-specs/SPEC-005-backend-compartido.md).

## Contexto

Cada teléfono guardaba sus propios datos, así que lectores y vendedores en teléfonos distintos no
se veían (DOCUMENTATION.md, limitación 5) y no se podía mostrar uso real en vivo. El equipo
decidió construir el backend antes de la presentación de la E4.

## Decisión

- Servidor FastAPI en el Z40 (`backend/servidor.py`), publicado por el túnel de Cloudflare en
  `bookwho.quadcorestore.com`. Un solo proceso con el mismo `models/store.py`, un candado y la
  persistencia JSON atómica de siempre.
- La app usa un proxy remoto (`services/remoto.py`) con la misma interfaz que el `Store`, así
  que las pantallas no cambian. Si el servidor no responde, vuelve al modo local.
- El actor de cada acción sale del token de sesión; los permisos siguen en el modelo.
- El servidor no tiene cuentas demo.

## Alternativas descartadas

- **API REST por caso de uso:** más trabajo y obligaba a reescribir los controladores.
- **Cliente web:** el equipo prefirió la app Android.
- **SQLite:** para el volumen de la prueba alcanza el `Store` en memoria con JSON. Conviene migrar
  cuando haya varios procesos o muchos datos.

## Consecuencias

- Datos compartidos entre teléfonos y métricas reales en vivo (`/en-vivo/`).
- Depende de la red y del Z40: sin conexión, la app trabaja en modo local y esos datos no se
  sincronizan después.
- Un solo proceso: no escala a muchos usuarios, pero alcanza para la prueba.
- Las contraseñas usan SHA-256 con el correo como sal: antes de abrir la app al público general,
  hay que migrarlas a PBKDF2.
