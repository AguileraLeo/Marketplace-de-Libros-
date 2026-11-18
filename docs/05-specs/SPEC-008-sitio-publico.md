# SPEC-008 — Sitio público: landing, descarga del APK y configuración remota

## Objetivo

Que cualquier persona conozca BookWho?, instale la app Android desde el dominio del proyecto
(`bookwho.quadcorestore.com`, también con un código QR) y siga la demo en vivo, y que el equipo
cambie el mensaje de la app sin compilar un APK nuevo.

## Alcance

- `/`: landing con la identidad de SPEC-007 (azul tinta y Manrope): qué es, cómo funciona, botón de
  descarga, código QR (`sitio/qr.svg`; `sitio/qr.png` para las diapositivas), cifras en vivo y cómo instalar.
- `/descargar`: entrega `BOOKWHO_PUBLICO/bookwho.apk` como `BookWho.apk`, con el tipo de archivo de Android.
- `/config.json`: configuración remota de la app. Sale de `BOOKWHO_PUBLICO/config.json`, que el equipo
  edita en el servidor sin reiniciarlo, o, si no existe, de `data/remote_config.json`. La app la pide a su
  servidor y, sin servidor configurado, a GitHub.
- `/privacidad/`: qué datos guarda la app, quién los ve, dónde se guardan y cómo pedir que se borren.
- Paneles de SPEC-004: `/simulacion/` (simulación del informe) y `/en-vivo/` (datos del servidor, con los
  agentes de SPEC-006; `/reales/` sigue funcionando). Un día sin actividad aparece con 0 eventos.

Fuera de alcance: publicar en Google Play, verificar correos y una app para iPhone.

## Criterios de aceptación

1. El sitio no carga recursos externos: la fuente se sirve desde el propio servidor.
2. La landing no explica el correo inventado, los agentes simulados ni el origen de las cifras: el equipo lo
   explica en vivo para defender esas decisiones (guion E4, diapositiva 9). Por escrito queda en el panel
   `/en-vivo/` y en `/privacidad/`.
3. Las cifras en vivo se escriben con `textContent`.
4. Sin APK publicado, `/descargar` responde 404 con un mensaje claro.
5. Cambiar `config.json` en el servidor cambia el banner la próxima vez que se abre la app, y un JSON
   inválido no la rompe: se queda con la configuración local.
6. El sitio no tapa la API: las rutas `/api/...` responden igual que antes.
7. Pruebas automáticas de las rutas en `tests/test_backend.py`.
