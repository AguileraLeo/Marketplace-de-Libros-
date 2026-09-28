# Contexto del proyecto: dónde estamos

Punto de partida para quien clona el repositorio. Resume lo que existe hoy, qué está decidido y qué falta decidir.

Documentos relacionados:

- [`AGENTS.md`](AGENTS.md): visión completa del producto, actores, flujos, alcance del MVP y reglas de trabajo. **Es la fuente de verdad.**
- [`CLAUDE.md`](CLAUDE.md): instrucciones para asistentes de IA (Claude Code, Codex, Copilot, etc.).
- [`README.md`](README.md): instalación, cuentas de demo y estructura de archivos.

---

## 1. Qué es

Plataforma de libros **bajo demanda**: un lector publica el libro que busca, los vendedores responden con ofertas y, cuando el lector acepta una, ambos coordinan la compra por fuera (teléfono, correo o punto de encuentro). En el MVP no hay pagos, envíos ni chat.

## 2. Estado actual (septiembre 2026)

Hay un **demo funcional de punta a punta** hecho en Python + KivyMD 2.0. Cubre el happy path del MVP:

```text
Buscar libro -> crear solicitud -> publicar -> vendedor ve solicitud
-> crea oferta -> lector acepta -> ve datos de contacto
```

| Área | Estado |
|------|--------|
| Login, registro (lector/vendedor), recuperar contraseña (simulado) | Hecho |
| Búsqueda de libros (Google Books → Open Library → catálogo local) | Hecho |
| Lector: crear, ver y cancelar solicitudes; ver y aceptar ofertas | Hecho |
| Vendedor: feed con filtros, detalle, crear/cancelar oferta, mis ofertas | Hecho |
| Admin: estadísticas, usuarios (suspender), solicitudes, ofertas, actividad | Hecho (básico) |
| Máquinas de estado de solicitud y oferta | Hecho, en `store.py` |
| Permisos por rol en la capa de dominio (no solo en la UI) | Hecho |
| Pruebas del flujo crítico y permisos (13 tests) | Pasan |
| Persistencia (base de datos o archivo) | **No existe**: todo vive en memoria |
| Documentación SDD en `docs/` (specs, casos de uso, ADR) | **Pendiente** |
| Reportes, auditoría formal, notificaciones | Fuera del demo |

### Pantallas implementadas (`main.py` + `libros.kv`)

- **Comunes:** Login, Registro.
- **Lector:** Inicio, Buscar libro, Crear solicitud, Solicitud publicada, Mis solicitudes, Detalle de solicitud, Detalle de oferta, Oferta aceptada.
- **Vendedor:** Inicio (solicitudes disponibles y filtros), Detalle de solicitud, Crear oferta, Mis ofertas.
- **Admin:** Panel con estadísticas, usuarios, solicitudes, ofertas y actividad.

## 3. Arquitectura del demo

```text
libros.kv      UI declarativa (KV language)
   │
main.py        Pantallas y navegación. No contiene reglas de negocio.
   │
store.py       Dominio: entidades, estados, validaciones, permisos.
   │           Repositorio en memoria + datos de ejemplo (build_demo_store).
   │
books_api.py   Proveedores externos de libros con fallback.
```

Regla: **toda regla de negocio y todo chequeo de permisos va en `store.py`**, y la UI solo llama a sus métodos. Así se puede probar sin interfaz y cambiar la UI o la persistencia sin romper el dominio.

### Estados

```text
Solicitud:  BORRADOR -> PUBLICADA -> CON_OFERTAS -> EN_COORDINACION -> RESUELTA
            PUBLICADA | CON_OFERTAS | EN_COORDINACION -> CANCELADA

Oferta:     PUBLICADA -> POR_CONCRETAR -> ACEPTADA
            PUBLICADA -> EN_ESPERA -> RECHAZADA | PUBLICADA
            PUBLICADA | POR_CONCRETAR | EN_ESPERA -> CANCELADA
```

## 4. Decisiones tomadas para el demo (todavía no son specs)

Se tomaron para que el demo funcionara y se actualizaron con la Fase 1 del plan de fixes:

1. Al aceptar una oferta inicialmente para coordinar, la oferta pasa a `POR_CONCRETAR`, la solicitud a `EN_COORDINACION` y las demás ofertas activas quedan `EN_ESPERA`.
2. Una vez coordinada y realizada la entrega/pago, el lector confirma el trato (`confirm_deal`), pasando la oferta a `ACEPTADA`, la solicitud a `RESUELTA` y rechazando definitivamente las ofertas `EN_ESPERA`.
3. Si el lector o vendedor desiste de la coordinación (`cancel_deal`), la oferta en trato se rechaza/cancela y las ofertas `EN_ESPERA` vuelven a estar activas (`PUBLICADA`).
4. El contacto del vendedor se revela cuando la oferta entra en coordinación (`POR_CONCRETAR`) o es aceptada (`ACEPTADA`).
5. Cancelar una solicitud cancela sus ofertas activas y registra el rol (`ADMIN` / `READER`) y el motivo de moderación/cancelación.
6. El vendedor puede ofertar cualquier condición (nuevo o usado) y método de entrega; el lector evalúa la oferta al revisarla.
7. Un vendedor tiene como máximo una oferta activa por solicitud.
8. Cada cuenta tiene un solo rol. Un usuario suspendido no puede iniciar sesión ni operar.
9. No hay base de datos: los usuarios de demo están hardcodeados y los datos se pierden al cerrar la app.
10. Stack del demo: Python 3.10/3.11 + Kivy 2.3.1 + KivyMD 2.0.1.dev0.

## 5. Próximos pasos sugeridos

En orden aproximado (ajustar en equipo):

1. Crear la estructura `docs/` de AGENTS.md §13 y pasar las decisiones de la sección 4 a `BUSINESS_RULES.md` y `STATE_MACHINES.md`.
2. Decidir la persistencia (JSON local, SQLite u otra) y registrarla en un ADR.
3. Escribir specs pequeñas (`SPEC-00X`) para cada cambio antes de implementarlo.
4. Definir la política de privacidad de datos de contacto y el significado exacto de `RESUELTA`.
5. Prototipo en Figma de las pantallas prioritarias (AGENTS.md §15).

## 6. Cómo trabajar en equipo

- **Rama principal:** `main`. No hacer push directo; trabajar en ramas y abrir Pull Request.
- **Nombre de ramas:** `spec/SPEC-00X-descripcion`, `docs/...`, `fix/...`.
- **Antes de abrir un PR:** correr `python -m unittest discover -s tests -v` y verificar que pasa todo.
- **Cambios de comportamiento:** primero la spec o la actualización de docs, después el código (Spec-Driven Development).
- **Al usar IA:** pedirle que lea `AGENTS.md` y la spec concreta. Ver `CLAUDE.md`.
- **Al terminar algo importante:** actualizar este archivo (secciones 2, 4 y 5) para que el resto del equipo sepa dónde estamos.
