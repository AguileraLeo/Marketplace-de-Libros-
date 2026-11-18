# Auditoría de seguridad de BookWho?

## Alcance y método

Revisión del 18-11-2026 en la rama `feat/backend`, antes de la E4. Se revisaron
`backend/` (incluidos los agentes), `services/remoto.py`, `persistence.py`,
`remote_config.py`, `models/store.py`, `simulador.py`, `sitio/`, `panel/`,
`buildozer.spec`, dependencias y despliegue descrito en `README.md`, contrastados
con AGENTS.md, CLAUDE.md, CONTEXTO.md, SPEC-005 y ADR-004.

Guías: [OWASP API Security Top 10, edición 2023](https://api-security.owasp.org/editions/2023/en/0x11-t10/)
y [OWASP ASVS 5.0.0](https://asvs.owasp.org/), como referencia de autenticación,
sesiones, protección de datos, validación, configuración y registro. Es una revisión
acotada de código y pruebas; no una certificación ASVS ni una prueba de penetración
contra producción. No se han ejecutado ataques, auditorías de dependencias ni comandos
en el Z40. No se afirman CVE sin verificación.

Contexto de confianza aportado por el equipo: uvicorn escucha solamente en
`127.0.0.1:8080`, un proceso, servicio systemd `bookwho`, publicado mediante
Cloudflare Tunnel en `https://bookwho.quadcorestore.com`. Internet llega con
`cf-connecting-ip`; los agentes locales no envían esa cabecera. El servidor confía
en su **presencia** para distinguir internet de conexiones locales: una cabecera
vacía también cuenta como externa. Esta es una precondición de despliegue, no una
propiedad criptográfica de HTTP. Debe impedirse cualquier acceso directo remoto
al origen y cualquier ruta de proxy que omita o acepte sin sobrescribir esa cabecera.

Se completó primero la inspección y esta tabla, sin modificar código. Después se
aplicaron únicamente F1–F8 autorizados; el estado refleja el parche verificado. Las ubicaciones de la tabla corresponden a
la inspección previa a los cambios; las funciones indicadas permiten localizarlas
tras añadir líneas. Las severidades consideran confidencialidad, integridad y
disponibilidad de esta demo, sin puntuaciones CVSS inventadas.

## Hallazgos

| ID | Severidad / guía | Dónde (archivo:línea, antes del parche) | Riesgo verificado | Recomendación | Estado |
|---|---|---|---|---|---|
| S1 | Alta · API2/API6 | `simulador.py:43–44,129–131`, `backend/agentes.py:64–72`, `backend/servidor.py:157–175` | Clave `sim1234` pública y correos deterministas `@bookwho.test`: un tercero puede autenticarse como agente y operar sus recursos. | F1: denegar sesión/registro del dominio simulado desde Cloudflare; mantener loopback. Después rotar secreto y hashes de agentes existentes. | Pendiente (plan): F1 aplicado y probado; falta retirar/rotar la clave pública. |
| S2 | Alta · API2/API4/API6 | `backend/servidor.py:157–175` | Sesión y registro sin límite propio; fuerza bruta y cuentas basura, aun tras la limitación de cuerpo. | F2: ventanas en memoria de fallos por correo/IP y registros por IP, con candado independiente y depuración. Complementar en Cloudflare después. | Corregido: F2, límites en memoria solo para Cloudflare y sin afectar agentes locales. |
| S3 | Media · API4/API8 | `backend/servidor.py:147–151` | El límite de 16 KiB solo usa Content-Length; Transfer-Encoding evita esa comprobación. Un Content-Length inválido también puede provocar una excepción. | F3: rechazar Transfer-Encoding en `/api/` con 411 JSON, permitir DELETE sin cuerpo ni Content-Length y manejar longitud inválida sin 500. Después contar bytes recibidos en streaming. | Corregido: F3 rechaza Transfer-Encoding; conteo de bytes sin longitud queda en el plan. |
| S4 | Alta · API4 | `backend/servidor.py:210–269`, `panel/index.html:534`, `sitio/index.html:141` | Cada visitante recalcula métricas leyendo el JSON completo bajo el candado del Store; compite con los teléfonos. | F4: caché compartida y protegida de hasta 3 s para API y alias; conservar frescura tras escrituras. Después snapshots/incrementales y límites en el borde. | Corregido: F4, caché compartida, serializada y de hasta 3 s; escalado posterior en el plan. |
| S5 | Media · API8 / ASVS configuración | `backend/servidor.py:141–151`, `sitio/index.html:127`, `panel/index.html:204` | Sin cabeceras defensivas propias: clickjacking, MIME sniffing y mayor impacto de inyección. Las páginas requieren scripts/estilos inline. | F5: cabeceras comunes y CSP compatible para HTML, exceptuando `/api/docs`. Después sustituir unsafe-inline por hashes/nonces y revisar Swagger/ReDoc. | Corregido: F5, cabeceras y CSP compatible; eliminación de unsafe-inline en el plan. |
| S6 | Alta · API2 / ASVS autenticación | `models/store.py:247–249`, `models/store.py:340`, `models/store.py:354` | SHA-256 rápido con sal predecible (correo), comparación no constante y claves mínimas de cuatro caracteres. Una copia del JSON permite ataque offline. | F6: compare_digest sin cambiar hashes. Después PBKDF2 versionado con sal aleatoria y migración oportunista; política y recuperación por especificar. | Pendiente (plan): F6 aplicado con compare_digest; hash rápido y política sin migrar. |
| S7 | Media · API3 / ASVS datos y registro | `models/store.py:344`, `models/store.py:363`, `models/store.py:794–807` | Login/registro duplican correos en detail; exportación añade identidad del actor. Acumula información personal en copias del historial. Exportar requiere admin; no es una filtración pública demostrada. | F8: detalles nuevos sin correo, conservando actor_id. Después revisar retención, históricos, exportación y eventos de moderación. | Pendiente (plan): F8 aplicado a detalles nuevos y atribución comprobada; histórico/exportación conservan datos personales. |
| S8 | Media · API4 / ASVS sesiones | `backend/servidor.py:125–135`, `backend/servidor.py:178–179` | Tokens vencidos solo se eliminan cuando se usan; las sesiones abandonadas crecen. DELETE modifica sesiones fuera del candado. | F7: depurar vencidas al crear otra sesión y mantener operaciones de sesión bajo el candado. Después límites de sesiones activas y limpieza periódica. | Corregido: F7, limpieza al crear sesión y cierre protegido; cuotas de tokens vigentes en el plan. |
| S9 | Media · ASVS protección de datos | `services/persistence.py:54–61`, `README.md:152–154` | JSON y temporal con hashes/contactos se crean según umask. No se verificaron permisos reales del host; no se presume que sean públicos. | UMask=0077 en systemd; directorios 0700 y archivos actuales/respaldos 0600; verificar propietario y ruta fuera de las carpetas públicas. | Pendiente (plan): no cambiar persistencia ni servicio hoy. |
| S10 | Media · API2/API3 | `models/store.py:317–318`, `models/store.py:361`, `services/remoto.py:27`, `backend/servidor.py:46`, `backend/servidor.py:61–70` | Mensaje de correo duplicado permite enumeración. Con token, user(id) secuencial revela nombre/rol/comuna/estado; se redactan hash y correo ajeno. No demuestra acceso a ofertas/contactos privados. | Después definir campos públicos y DTO de usuario, errores no enumerables y presupuesto de consultas, con transición compatible para la app. | Pendiente (plan): no cambiar contratos hoy. |
| S11 | Media · API6/API10 | `models/store.py:372–395`, `backend/servidor.py:239–244`, `panel/index.html:219` | upsert_book acepta título y metadatos del cliente; contenido ofensivo puede llegar al panel proyectado. textContent evita interpretarlo como HTML, pero no modera el contenido. | Después resolver metadatos desde proveedor permitido y moderar antes de proyectar; no introducir filtros improvisados hoy. | Pendiente (plan). |
| S12 | Baja · API8/API9 | `backend/servidor.py:141`, `README.md:167` | Documentación y OpenAPI públicos facilitan reconocimiento; exposición intencional, no sustituyen autenticación ni prueban un bypass. Revisar también ReDoc por defecto. | Después inventariar y restringir documentación con Cloudflare Access o deshabilitarla fuera del entorno de demostración. | Pendiente (plan): docs deben seguir funcionando. |
| S13 | Media · API8 / ASVS configuración | `README.md:152–154` | No hay unidad systemd endurecida versionada; el contexto dice que existe bookwho, pero no se inspeccionó su configuración real. Loopback es una defensa positiva. | Después usuario dedicado, mínimo acceso, UMask, NoNewPrivileges y sandbox de systemd con pruebas de escritura/lectura y del túnel. | Pendiente (plan): despliegue no verificado. |
| S14 | Media · API8/API10 | `backend/requirements.txt:2–4`, `requirements.txt:3`, `buildozer.spec:16` | Dependencias servidor sin pins y KivyMD master.zip mutable; sin evidencia de auditoría o inventario. No se declara una vulnerabilidad concreta no comprobada. | Después pip-audit aislado, inventario/SBOM, versiones/hashes y revisión de transitivas; fijar commit de KivyMD y probar actualización del APK conservando firma. | Pendiente (plan): sin instalaciones ni actualizaciones hoy. |
| S15 | Alta · API4/API6 | `backend/servidor.py:182–208`, `services/persistence.py:54–61` | RPC autenticado sin cuotas globales: permite crecimiento de libros, solicitudes, ofertas e historial y escrituras completas del JSON. F2 no cubre todos los recursos. | Después cuotas y tamaños de colecciones por actor, paginación compatible y persistencia incremental. | Pendiente (plan). |
| S16 | Media · API8 / ASVS resiliencia | `services/persistence.py:64–80`, `backend/servidor.py:113–116` | Un archivo corrupto se aparta y puede iniciarse Store vacío; guardado atómico no equivale a backup. Sin evidencia de restauración probada o alerta. | Después copias privadas versionadas, ensayo de restauración, monitorización y política explícita ante corrupción del backend. | Pendiente (plan). |
| S17 | Media · API5 | `backend/servidor.py:130–136,185–201`, `models/store.py:372` | Un token emitido antes de suspender al usuario puede seguir invocando métodos SIN_ACTOR sin comprobar estado activo. Los métodos con actor sí aplican sus controles. | Después definir revocación y comprobar estado activo centralmente, con pruebas de suspensión y compatibilidad. | Pendiente (plan): fuera de F1–F8. |

Defensas constatadas: actor obtenido del token; lista explícita de RPC; controles de
rol/propiedad en el Store; hashes y correo ajeno redactados al serializar User;
contacto mediante métodos autorizados; TLS verificado por RemoteStore; guardado
atómico; datos de métricas sin correos de cuenta; textContent en el sitio y panel,
y exportación CSV protegida contra fórmulas. Esto reduce riesgos, pero no certifica
ausencia de fallos de autorización ni moderación de información introducida por usuarios.

## Parche autorizado antes de la E4

- F1: presencia de cf-connecting-ip + correo normalizado terminado en el dominio
  simulado: 403 PermissionDenied con el mensaje acordado. En registro se comprueba
  también el correo efectivo truncado a 120 caracteres por el Store. No cambiar agentes.
- F2: solo con esa cabecera; 8 fallos/correo y 30 fallos/IP en 600 s; éxito borra
  fallos del correo, no de la IP. Registro: 40 registros/IP en 3600 s, compatible
  con la NAT del curso. Contadores protegidos con candado propio y poda de entradas viejas.
- F3: Transfer-Encoding en `/api/` se rechaza con 411 ValidationError JSON; no se
  exige Content-Length. El formato sigue siendo {error, tipo}.
- F4: caché única por app/proceso, mutex independiente y TTL monotónico de 3 s;
  los hits no adquieren el candado del Store. Una escritura/descarga puede invalidarla
  antes para conservar el comportamiento previo de la demo. No añadir workers.
- F5: nosniff, strict-origin-when-cross-origin, DENY, política de cámara/micrófono/
  geolocalización vacía y HSTS max-age=31536000 en respuestas. CSP HTML exactamente
  compatible con inline y recursos locales; excepción `/api/docs` por Swagger.
- F6: hmac.compare_digest conservando el esquema SHA-256 existente.
- F7: al crear un token, borrar tokens vencidos; conservar TTL y formato del token.
- F8: solo eventos nuevos de login/registro con texto sin correo; conservar acción,
  actor_id, historial previo y la identidad que consulta administración.

## Plan después de la E4

1. **Frontera de red y abuso:** verificar en el Z40 `systemctl cat bookwho`,
   `systemctl show bookwho -p User -p UMask -p NoNewPrivileges -p ProtectSystem`
   y `ss -ltnp`. Comprobar loopback y túnel sin publicar 8080. Revisar que Cloudflare
   sobrescriba cf-connecting-ip y no existan rutas que lo omitan; restringir documentación,
   aplicar límites/WAF en sesión, registro y RPC, y presupuestos por usuario. La CSP
   solicitada deja Swagger (/api/docs) exceptuado, pero ReDoc por defecto carga
   recursos CDN y puede quedar bloqueado; decidir su retirada o alojamiento local
   después de la E4, sin afectar las rutas del teléfono. Diseñar
   contadores compartidos si se migra a varios procesos. Estas verificaciones no se ejecutaron hoy.
2. **Credenciales de agentes y humanos:** introducir en una spec una variable
   `BOOKWHO_AGENTE_CLAVE` sin valor público por defecto, leída por agentes y herramienta
   de carga. Guardarla en EnvironmentFile privado 0600 fuera del repositorio; rotar
   también las cuentas ya guardadas (cambiar solo la variable no cambia los hashes).
   Retirar/revocar sesiones previas en un reinicio coordinado. Mantener la denegación
   pública del dominio reservado. Tokens de agentes emitidos antes del parche seguirán
   válidos hasta vencer o reiniciar el servicio; programar ese reinicio en el despliegue.
   No registrar ni publicar la variable.
3. **Hash versionado:** definir formato `pbkdf2_sha256$iteraciones$sal$derivado`, con
   sal criptográfica aleatoria por usuario y pbkdf2_hmac de biblioteca estándar.
   Calibrar coste en el Z40 con concurrencia real y referencia actual de OWASP; no
   fijar un coste sin medir. Detectar hash SHA-256 legado, verificarlo con compare_digest
   y rehashear tras un login correcto bajo el candado, guardando atómicamente.
   Nunca convertir hashes sin la contraseña original. Probar coexistencia, reinicio,
   restauración y clientes instalados antes de activar. Diseñar claves más robustas,
   recuperación y errores no enumerables mediante spec aparte.
4. **Servicio y permisos:** drop-in revisado de bookwho con usuario/grupo dedicados,
   `UMask=0077`, `NoNewPrivileges=true`, `PrivateTmp=true`, `ProtectSystem=strict`,
   `ProtectHome=read-only` y `ReadWritePaths` limitado al directorio de datos y al
   público si el proceso realmente lo necesita. Ajustar WorkingDirectory, lectura
   de fuentes/código/APK y acceso a secretos sin abrir todo /home. Probar primero con
   una copia y revertir drop-in si impide arrancar; ejecutar daemon-reload/restart solo
   en ventana acordada. cloudflared debe tener permisos independientes. Cambiar
   propietario y permisos de datos actuales, .tmp, .corrupto y backups; un UMask nuevo
   no protege copias ya existentes. No guardar datos privados bajo sitio/ o público.
5. **Dependencias y cadena de suministro:** inventariar versiones del servidor y APK,
   crear entorno aislado de auditoría y ejecutar `python -m pip_audit` con las dependencias
   inventariadas; revisar CVE/avisos y rutas de explotación antes de actualizar. Generar
   SBOM, fijar versiones/commit y hashes, probar toda la suite en copia, conservar APK,
   firma y entorno anterior para rollback. No actualizar el teléfono a horas de la demo.
6. **Datos y contenidos:** definir metadatos permitidos y resolución desde proveedor,
   moderación previa del feed proyectado, privacidad de user(id), minimización y retención
   de eventos/exportaciones. Revisar históricos sin eliminar evidencia a ciegas y mantener
   atribución por actor_id. Revocar sesiones y denegar también métodos sin actor a
   usuarios suspendidos. Registrar decisiones en specs pequeñas y migraciones reversibles.
7. **Disponibilidad y cuerpos:** contar bytes de cada fragmento ASGI antes de parsear,
   incluyendo solicitudes sin Content-Length/Transfer-Encoding; probar transportes reales,
   límites de conexiones/timeout en el borde y RPC. Medir caché invalidada por agentes,
   separar snapshots de analítica y escrituras si el volumen crece. La limpieza oportunista
   de sesiones no limita tokens activos ni reemplaza una limpieza periódica.
8. **Respaldos y operación:** copiar datos bajo el candado o con el servicio detenido,
   mantener versiones privadas cifradas fuera del directorio público, definir retención y
   responsables, y restaurar en un entorno aislado comprobando cuentas/solicitudes/ofertas.
   Alertar ante corrupción, errores de guardado y disco lleno; diseñar arranque seguro del
   backend para no sustituir silenciosamente datos por un Store vacío.

## Verificación y límites

- 21 pruebas nuevas con TestClient en `tests/test_backend.py`: reserva del dominio,
  normalización y truncamiento, 8 fallos por correo, 30 por IP, reinicio del correo
  tras éxito, 40 registros por hora, caducidad y eliminación de claves viejas,
  exclusión local y solicitudes concurrentes (12 intentos: 8 fallos y 4 rechazos).
- Transfer-Encoding rechazado antes de leer fragmentos; límite de tamaño y longitud
  inválida; cierre 204 sin Content-Length. Cabeceras también en 411/413/429/500 y
  errores internos sin detalle sensible en la respuesta.
- Caché compartida entre `/api/metricas`, `/en-vivo/metricas.json` y `/reales/metricas.json`,
  caducidad con reloj controlado y ocho lecturas concurrentes con un solo cálculo.
- Uso de compare_digest con hash previo intacto; depuración real de sesiones vencidas;
  búsqueda por actor, consulta del nombre y exportación administrativa conservadas.
- Comprobación focalizada en Chromium contra backend temporal: scripts inline,
  fetch, fuentes, video, QR y descarga CSV mediante URL blob funcionan sin infracciones
  CSP. `/api/docs` responde 200 sin CSP, conservando las otras cinco cabeceras.
- Suite completa: **121 pruebas aprobadas**, ejecutadas con el Python del entorno
  virtual mediante `python -m unittest discover -s tests`; sin pruebas omitidas.

Todos los ensayos usan TestClient o servidores locales con datos temporales, nunca
cuentas de producción. Los límites cuentan registros exitosos; los intentos de registro
inválidos no consumen ese cupo. Los contadores y sesiones son de un proceso, se pierden
al reiniciar y la poda es oportunista al recibir otra petición protegida o crear sesión.
La caché puede invalidarse antes de tres segundos por cambios del Store/descargas:
si los agentes escriben continuamente, su beneficio debe medirse tras la E4.
No se cambiaron rutas, esquemas JSON, cliente instalado, APK, UI, algoritmo de hash,
unidad systemd, dependencias ni credenciales de agentes durante este parche.
La corrección en código no implica que el servicio Z40 se haya actualizado o reiniciado.
