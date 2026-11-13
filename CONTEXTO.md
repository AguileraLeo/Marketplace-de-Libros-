# Contexto del proyecto: dónde estamos

Punto de partida para quien clona el repositorio. Resume lo que existe hoy, qué está decidido y qué falta decidir.

Documentos relacionados:

- [`AGENTS.md`](AGENTS.md): visión completa del producto, actores, flujos, alcance del MVP y reglas de trabajo. **Es la fuente de verdad.**
- [`CLAUDE.md`](CLAUDE.md): instrucciones para asistentes de IA (Claude Code, Codex, Copilot, etc.).
- [`README.md`](README.md): instalación, cuentas de demo y estructura de archivos.

---

## 1. Qué es

Plataforma de libros **bajo demanda**: un lector publica el libro que busca, los vendedores responden con ofertas y, cuando el lector acepta una, ambos coordinan la compra por fuera (teléfono, correo o punto de encuentro). En el MVP no hay pagos, envíos ni chat.

## 2. Estado actual (noviembre 2026)

Hay un **demo funcional de punta a punta** hecho en Python + KivyMD 2.0. Cubre el happy path del MVP:

```text
Buscar libro -> crear solicitud -> publicar -> vendedor ve solicitud
-> crea oferta -> lector acepta -> ve datos de contacto
```

| Área | Estado |
|------|--------|
| Login, registro (lector/vendedor), recuperar contraseña (simulado) | Hecho |
| Búsqueda de libros (Google Books → Open Library → catálogo local) con caché de portadas en disco | Hecho |
| Lector: crear, ver y cancelar solicitudes; selector de comuna/ciudad; ver, coordinar y aceptar ofertas | Hecho |
| Vendedor: feed con filtros (excluye solicitudes ya ofertadas), detalle, crear/cancelar oferta, mis ofertas | Hecho |
| Admin: panel de métricas con accesos rápidos y subpantallas de solicitudes, usuarios, ofertas y auditoría | Hecho |
| Admin: búsqueda y exportación de logs de actividad a `.log` | Hecho |
| Máquinas de estado de solicitud y oferta (estados intermedios) | Hecho, en `models/store.py` |
| Permisos por rol en la capa de dominio (no solo en la UI) | Hecho |
| Pruebas automatizadas (34 tests) | Pasan |
| Fundamentación UX/UI con encuesta real (18 respuestas) | Hecho, en `docs/01-requirements/FUNDAMENTACION-UX-UI.md` |
| Persistencia JSON | Hecha en `services/persistence.py`; escritorio usa `data/user/data.json` y Android su directorio privado |
| Documentación SDD en `docs/` | ADR y specs de MVC y estructura creados; otras specs de producto siguen pendientes |
| Reportes, auditoría formal, notificaciones | Fuera del demo |

### Pantallas implementadas (`controllers/screen_controllers.py` + `views/libros.kv`)

- **Comunes:** Login, Registro.
- **Lector:** Inicio, Buscar libro, Crear solicitud, Solicitud publicada, Mis solicitudes, Detalle de solicitud, Detalle de oferta, Oferta aceptada.
- **Vendedor:** Inicio (solicitudes disponibles y filtros), Detalle de solicitud, Crear oferta, Mis ofertas.
- **Admin:** Inicio con métricas y accesos rápidos; subpantallas de Solicitudes (moderación), Usuarios (suspender), Ofertas y Auditoría/Actividad (búsqueda y exportación de logs).

## 3. Arquitectura del demo

```text
main.py                         Punto de entrada y configuración inicial de ventana.
   │
controllers/app_controller.py   Ciclo de vida, navegación y coordinación de servicios.
controllers/screen_controllers.py
                                Eventos y estado de las pantallas Kivy.
   │
views/libros.kv                 Vistas declarativas (layout y estilo).
views/components.py             Widgets visuales reutilizables.
   │
models/store.py                 Modelo/dominio: entidades, reglas, permisos y estados.
                                Store en memoria + datos de ejemplo.
services/                       Persistencia, notificaciones, búsqueda y ubicaciones.
data/                           Catálogo de comunas y configuración remota.
assets/                         Fuentes tipográficas y capturas.
```

Regla: **toda regla de negocio y todo chequeo de permisos va en `models/store.py`**, y la UI solo llama a sus métodos. Así se puede probar sin interfaz y cambiar la UI o la persistencia sin romper el dominio.

### Estados

```text
Solicitud:  BORRADOR -> PUBLICADA -> CON_OFERTAS -> EN_COORDINACION -> RESUELTA
            PUBLICADA | CON_OFERTAS | EN_COORDINACION -> CANCELADA

Oferta:     PUBLICADA -> POR_CONCRETAR -> ACEPTADA
            PUBLICADA -> EN_ESPERA -> RECHAZADA | PUBLICADA
            PUBLICADA | POR_CONCRETAR | EN_ESPERA -> CANCELADA
```

## 4. Decisiones tomadas para el demo (todavía no son specs)

Se tomaron para que el demo funcionara y se actualizaron con las Fases 1 a 4 del plan de fixes:

1. Al aceptar una oferta inicialmente para coordinar, la oferta pasa a `POR_CONCRETAR`, la solicitud a `EN_COORDINACION` y las demás ofertas activas quedan `EN_ESPERA`.
2. Una vez coordinada y realizada la entrega/pago, el lector confirma el trato (`confirm_deal`), pasando la oferta a `ACEPTADA`, la solicitud a `RESUELTA` y rechazando definitivamente las ofertas `EN_ESPERA`.
3. Si el lector o vendedor desiste de la coordinación (`cancel_deal`), la oferta en trato se rechaza/cancela y las ofertas `EN_ESPERA` vuelven a estar activas (`PUBLICADA`).
4. El contacto del vendedor se revela cuando la oferta entra en coordinación (`POR_CONCRETAR`) o es aceptada (`ACEPTADA`).
5. Cancelar una solicitud cancela sus ofertas activas y registra el rol (`ADMIN` / `READER`) y el motivo de moderación/cancelación.
6. El vendedor puede ofertar cualquier condición (nuevo o usado) y método de entrega; el lector evalúa la oferta al revisarla.
7. Un vendedor tiene como máximo una oferta activa por solicitud.
8. Cada cuenta tiene un solo rol. Un usuario suspendido no puede iniciar sesión ni operar.
9. No hay base de datos; la app persiste datos en JSON local. Las cuentas demo se cargan al iniciar si todavía no existe un archivo persistido.
10. Stack del demo: Python 3.10/3.11 + Kivy 2.3.1 + KivyMD 2.0.1.dev0.
11. El feed del vendedor excluye las solicitudes donde ya tiene una oferta activa; esas se gestionan desde "Mis ofertas".
12. El admin consulta la actividad en una subpantalla dedicada (con búsqueda) y puede exportarla a un archivo `.log`.

## 5. Próximos pasos sugeridos

En orden aproximado (ajustar en equipo):

1. Pasar las decisiones de la sección 4 a `BUSINESS_RULES.md` y `STATE_MACHINES.md`.
2. Escribir specs pequeñas (`SPEC-00X`) para cada cambio antes de implementarlo.
3. Definir la política de privacidad de datos de contacto y el significado exacto de `RESUELTA`.
4. Prototipo en Figma de las pantallas prioritarias (AGENTS.md §15).

## 6. Cómo trabajar en equipo

- **Rama principal:** `main`. No hacer push directo; trabajar en ramas y abrir Pull Request.
- **Nombre de ramas:** `spec/SPEC-00X-descripcion`, `docs/...`, `fix/...`.
- **Antes de abrir un PR:** correr `python -m unittest discover -s tests -v` y verificar que pasa todo.
- **Cambios de comportamiento:** primero la spec o la actualización de docs, después el código (Spec-Driven Development).
- **Al usar IA:** pedirle que lea `AGENTS.md` y la spec concreta. Ver `CLAUDE.md`.
- **Al terminar algo importante:** actualizar este archivo (secciones 2, 4 y 5) para que el resto del equipo sepa dónde estamos.
