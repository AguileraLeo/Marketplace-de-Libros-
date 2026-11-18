# SPEC-005 — Backend compartido (modelo remoto)

## Objetivo

Que lectores y vendedores en teléfonos Android distintos usen los mismos datos y que el panel
muestre actividad **real** en vivo. El servidor corre en el Z40 y se publica por el túnel
existente en `https://bookwho.quadcorestore.com`.

## Diseño: proxy remoto

- **El modelo se queda igual y se muda al servidor.** `backend/servidor.py` (FastAPI, un solo
  proceso) tiene el único `Store` real, protegido con un candado (`threading.Lock`), y lo guarda
  con `services/persistence.save_store` después de cada acción que cambia datos, en
  `BOOKWHO_DATOS` (por defecto `~/bookwho/datos/bookwho.json`). Son datos reales: van separados
  de la simulación.
- **La app no cambia sus pantallas.** `services/remoto.py` define `RemoteStore`, con los mismos
  métodos y diccionarios (`requests`, `offers`, `users`) que usan los controladores, pero cada
  llamada viaja al servidor. `controllers/app_controller.py` elige el modelo al iniciar: si hay
  servidor configurado y responde, usa `RemoteStore`; si no, el `Store` local de siempre y avisa
  "Modo sin conexión".
- **El actor lo pone el servidor.** El cliente nunca envía quién es: el servidor identifica al
  usuario por su token y lo pasa como `actor`. Los permisos siguen en `models/store.py`.

## Contrato

| Método y ruta | Cuerpo → respuesta |
|---|---|
| `POST /api/sesion` | `{correo, clave}` → `{token, usuario}` (llama a `authenticate`) |
| `POST /api/registro` | `{nombre, correo, clave, rol, comuna}` → `{token, usuario}` |
| `DELETE /api/sesion` | → 204 |
| `POST /api/rpc` | `{metodo, args}` con `Authorization: Bearer <token>` → `{resultado}` |
| `GET /api/metricas` | público → formato de `metricas.json` (SPEC-004) con `"simulado": false` |
| `GET /api/salud` | público → `{ok: true}` (la app lo usa para decidir el modo) |

Métodos permitidos en `/api/rpc` (cualquier otro → 404):

- **Con actor** (el servidor lo agrega como primer argumento): `reader_requests`,
  `offers_for_request`, `get_request`, `cancel_request`, `cancel_deal`, `set_user_status`,
  `seller_offers`, `seller_contact`, `seller_active_offer`, `open_requests`, `offer_contact`,
  `get_offer`, `create_request`, `create_offer`, `accept_offer`, `confirm_deal`, `cancel_offer`,
  `admin_users`, `admin_stats`, `admin_requests`, `admin_offers`, `admin_activity`.
- **Sin actor:** `book`, `user`, `active_offer_count`, `upsert_book`, `recover_password`.
- **Especial:** `export_activity_log` devuelve el texto del registro (solo admin) y la app lo
  guarda en el teléfono.

Serialización: las entidades viajan como diccionarios con `"_tipo"` (`User`, `Book`,
`BookRequest`, `Offer`, `SellerContact`, `ActivityEntry`) y fechas ISO; el cliente las
reconstruye como las mismas dataclasses.

Errores: `{"error": mensaje, "tipo": clase}` con 400 (`ValidationError`), 401 (token ausente o
vencido), 403 (`PermissionDenied`), 404 (`NotFound` o método no permitido) y 409
(`InvalidTransition`). La app los convierte en la misma excepción de dominio, así que
`app.safe()` los muestra como siempre.

## Seguridad y privacidad

- Ninguna respuesta incluye la contraseña. El correo de un `User` solo viaja si es el propio
  usuario o si quien consulta es admin; el contacto del vendedor, solo por los métodos que lo
  autorizan.
- Sin cuentas demo: el servidor arranca con un `Store()` vacío. El admin se crea al iniciar con
  `BOOKWHO_ADMIN_CORREO` y `BOOKWHO_ADMIN_CLAVE`.
- Sesiones con `secrets.token_urlsafe(32)` en memoria, válidas por 12 horas.
- Cuerpos de hasta 16 KB. HTTPS y límites de uso los da Cloudflare.

## Criterios de aceptación

1. Las 19 pantallas funcionan con `RemoteStore` sin cambiar `controllers/screen_controllers.py`
   ni `views/`.
2. Ninguna regla de negocio se duplica: el servidor solo traduce HTTP a métodos del `Store`.
3. El cliente no puede actuar como otro usuario (el actor sale del token).
4. Ninguna respuesta filtra contraseñas, ni correos o contactos no autorizados.
5. Dos teléfonos ven los mismos datos: lo que publica uno le aparece al otro al refrescar.
6. Si el servidor no responde, la app arranca en modo local y lo avisa; una pérdida de conexión
   durante el uso muestra un mensaje y no cierra la app.
7. El panel muestra "datos reales" o "datos simulados" según el campo `simulado`.
8. Pruebas automáticas en `tests/test_backend.py`.

Fuera de esta etapa: publicar en Play Store, migrar contraseñas a PBKDF2 y la app web.
