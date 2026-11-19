# BookWho? — Guion de presentación E4

**Duración prevista: 9 minutos**, incluyendo una demo de **2 minutos y 45 segundos**. Los tiempos son una propuesta de exposición, no resultados medidos. Las preguntas del cierre se preparan aparte y no se incluyen en ese tiempo.

Regla de exposición: distinguir **encuesta real**, **resultados simulados** y **demostración con cuentas de prueba**. Una oferta aceptada o un trato confirmado no son una venta verificada. Las cifras históricas de este guion proceden del escenario base, sin mezclarlo con la extensión simulada en vivo.

## Distribución del tiempo y responsables

| Sección de la rúbrica | Intervalo | Duración | Diapositivas | Presenta |
|---|---|---|---|---|
| 1. Problema resuelto (RA1) | 00:00–01:15 | 01:15 | 1–2 | [COMPLETAR: integrante] |
| 2. Solución desarrollada (RA2), incluida demo | 01:15–05:15 | 04:00 | 3–5 | [COMPLETAR: integrante] |
| 3. Metodología de medición (RA3) | 05:15–06:35 | 01:20 | 6–7 | [COMPLETAR: integrante] |
| 4. Resultados y propuesta de mejora | 06:35–08:10 | 01:35 | 8–10 | [COMPLETAR: integrante] |
| 5. Conclusión social y ética | 08:10–09:00 | 00:50 | 11 | [COMPLETAR: integrante] |
| **Total** | **00:00–09:00** | **09:00** | | |

## 1. Problema resuelto (RA1)

### Diapositiva 1 — BookWho?: pedir un libro en vez de recorrer catálogos

**00:00–00:30 · 30 segundos**

- El lector publica qué libro busca; el vendedor responde con una oferta.
- Usuarios objetivo: lectores, librerías pequeñas y vendedores particulares.
- Propósito social: facilitar acceso a libros y visibilidad de pequeños vendedores.
- La coordinación final ocurre fuera de la plataforma.

**Qué decir:** «Partimos de una necesidad concreta: encontrar quién tiene ese libro. El beneficio social es una propuesta que debemos validar, no un impacto que ya podamos dar por demostrado».

**Fuentes:** [README.md, Problema y Solución](../../README.md); [fundamentación UX/UI, apartados b–c](../01-requirements/FUNDAMENTACION-UX-UI.md).

### Diapositiva 2 — Evidencia de la encuesta real

**00:30–01:15 · 45 segundos**

- Encuesta real: 18 respuestas, del 27 al 28 de septiembre de 2026.
- 17 de 18 (94,4 %) buscaron un libro específico sin encontrarlo.
- 14 de 18 (77,8 %) dedicaron 15 minutos o más.
- 14 de 16 (87,5 %) usarían el modelo de pedir y recibir ofertas.
- 16 de 18 creen que ayudaría a vendedores pequeños o independientes.

**Qué decir:** «El interés tiene un denominador distinto porque esa pregunta fue opcional. Esta muestra justifica explorar la solución, pero no representa a toda la población».

**Fuente de todas las cifras:** [fundamentación UX/UI, apartados a–b](../01-requirements/FUNDAMENTACION-UX-UI.md). No atribuir estas respuestas a la simulación.

## 2. Solución desarrollada (RA2)

### Diapositiva 3 — MVC y reglas verificadas en el modelo

**01:15–02:00 · 45 segundos**

- `models/store.py`: entidades, permisos, validaciones, estados y eventos; sin Kivy.
- `controllers/`: navegación, ciclo de vida y coordinación de pantallas y servicios.
- `views/libros.kv`: interfaz declarativa; componentes reutilizables en `views/components.py`.
- POO: clases de datos, herencia de `BaseScreen` y excepciones de dominio.

**Qué decir y mostrar:** tener los archivos abiertos previamente. Dedicar aproximadamente 20 segundos a `Store.create_request()`, `accept_offer()` y `offer_contact()`; 15 segundos a `controllers/app_controller.py`, especialmente `safe()`; 10 segundos a una regla de pantalla en `views/libros.kv`. No recorrer archivos enteros. Explicar que ocultar un botón no sustituye comprobar permisos.

**Fuentes:** [README.md, Arquitectura MVC](../../README.md); [modelo](../../models/store.py); [controlador](../../controllers/app_controller.py); [vista](../../views/libros.kv); [ADR-001](../04-architecture/ADR-001-mvc-incremental.md) y [ADR-002](../04-architecture/ADR-002-estructura-del-repositorio.md). Los tiempos de explicación son planificación del guion.

### Diapositiva 4 — Demo en el teléfono: del lector al contacto

**02:00–04:45 · 2 minutos y 45 segundos**

- Un mismo teléfono en **modo local**, con las cuentas de prueba de la tabla siguiente. Este recorrido demuestra persistencia local; el backend compartido se explica por separado.
- El lector busca y publica; el vendedor responde a esa solicitud.
- El lector acepta para coordinar y entonces accede al contacto autorizado.
- Cerrar y reabrir permite mostrar persistencia, sin desinstalar ni borrar datos.

**Preparación del equipo:** APK instalado, teléfono cargado y proyección lista. Para este ensayo con cuentas demo, cerrar la app, desactivar la conexión antes de abrirla y comprobar que inicia en modo local. El servidor compartido no tiene estas cuentas: las elimina al arrancar. En escritorio se puede forzar el modo local con los comandos del Plan B. Verificar los accesos antes de presentar; si un archivo local anterior no contiene estas cuentas, usar un entorno de ensayo preparado sin borrar datos personales. Revisar que el vendedor no tenga una oferta activa para la nueva solicitud. No mostrar registros con datos personales. Esta preparación y la demo son instrucciones para el equipo: no se ejecutaron al redactar el guion.

**Correos y alias de las cuentas de prueba locales** (existentes en `DEMO_USERS`; no requieren buzones de correo):

| Uso en el ensayo | Alias / nombre visible | Correo de acceso | Clave |
|---|---|---|---|
| Lector principal | Juan Pérez | `lector@demo.cl` | `1234` |
| Vendedor principal | Librería Los Andes | `vendedor@demo.cl` | `1234` |
| Lector de respaldo | María González | `maria@demo.cl` | `1234` |
| Vendedor de respaldo | Pedro Soto | `pedro@demo.cl` | `1234` |
| Administración local, si se muestra | Admin | `admin@demo.cl` | `admin` |

Son identidades ficticias de la demo. `analitica.py` excluye sus correos exactos automáticamente;
no registrar otras cuentas de ensayo ni confundirlas con participantes reales. Las cuentas
`@bookwho.test` pertenecen a los agentes simulados y no se usan para este login público.

**Datos preparados para el recorrido** (propuestos para el ensayo, no resultados medidos):

| Campo | Valor |
|---|---|
| Solicitud | El Hobbit; máximo $10.000 CLP; condición cualquiera; Concepción; entrega presencial |
| Nota del lector | «Ensayo E4: busco un ejemplar para lectura personal». |
| Oferta | $8.000 CLP; usado; «Buen estado, sin páginas faltantes». |
| Nota del vendedor | «Ensayo E4: coordinación externa con contacto ficticio». |
| Correo de contacto | `vendedor@example.test` (ficticio; no enviar correos) |
| Teléfono y dirección | Vacíos; basta con el correo ficticio como contacto |

El correo de contacto se ingresa en el formulario de oferta; es distinto del correo de acceso
`vendedor@demo.cl`. Crear una solicitud nueva en cada ensayo y conservar su identificador para
evitar abrir una oferta anterior.

| Tiempo dentro de la demo | Acción en el teléfono | Frase breve / evidencia visible |
|---|---|---|
| 00:00–00:15 | Iniciar sesión con `lector@demo.cl`, clave `1234`. | «Esta es una cuenta de prueba, excluida de los KPIs de uso real». |
| 00:15–00:40 | Buscar «El Hobbit» y seleccionar el resultado correcto. | «Los metadatos vienen del proveedor externo; existe respaldo local si falla la red». |
| 00:40–01:05 | Completar los datos de solicitud de la tabla y publicar. | Mostrar la confirmación y conservar su identificador. El máximo de $10.000 es opcional en la app. |
| 01:05–01:20 | Salir e iniciar sesión como `vendedor@demo.cl`, clave `1234`. | «Cambiamos de rol en el mismo dispositivo para este ensayo local». |
| 01:20–01:45 | Localizar la nueva solicitud, pulsar «Puedo ofrecerlo» y publicar la oferta preparada. | Mostrar $8.000, usado y contacto `vendedor@example.test`; teléfono y dirección vacíos. |
| 01:45–02:15 | Volver a la cuenta del lector, abrir la oferta y aceptar para coordinar. | Mostrar el contacto. «Aceptar inicia la coordinación; no acredita una venta ni una entrega». |
| 02:15–02:45 | Cerrar la aplicación y reabrirla; si pide login, entrar como lector y abrir la misma solicitud. | Mostrar que solicitud, oferta y estado permanecen. No prometer persistencia de la sesión. |

**Fuentes:** [README.md, cuentas de demo, búsqueda, persistencia y reglas](../../README.md); [documentación técnica, flujo por rol](../04-architecture/DOCUMENTACION.md); [catálogo de respaldo con El Hobbit](../../services/books_api.py). Las duraciones y acciones seleccionadas son planificación, no mediciones.

### Diapositiva 5 — Servicios y límites del MVP

**04:45–05:15 · 30 segundos**

- Persistencia JSON con escritura temporal y reemplazo atómico.
- Autenticación sin recuperación de contraseña: el login indica que todavía no está disponible.
- Notificaciones locales y configuración remota con respaldo sin conexión.
- APK Android; sin pagos, chat ni logística. El backend permite compartir datos; esta demo con cuentas predefinidas usa el modo local.

**Qué decir:** «En este ensayo los datos persisten en el dispositivo. Para compartirlos entre teléfonos se usa el backend de SPEC-005». No presentar una notificación del mismo teléfono como entrega remota al lector.

**Fuente:** [README.md, servicios y reglas del demo](../../README.md).

## 3. Metodología de medición (RA3)

### Diapositiva 6 — De acciones a eventos: MJV App

**05:15–05:50 · 35 segundos**

- Medir: indicadores vinculados al diagnóstico y metas fijadas el 19-11-2026 para el próximo ciclo de 14 días.
- Jugar: recorridos durante un periodo declarado; aquí, actividad simulada.
- Validar: comparar con metas, ajustar y volver a medir.
- `ActivityEntry`: `at`, `actor_id`, `action`, `detail`; se guarda en `activity` del JSON.
- Ejemplos de eventos: `solicitud_publicada`, `oferta_publicada`, `trato_concretado`.

**Qué decir:** «El evento representa una acción aceptada por el modelo, no una pantalla vista. Mostramos agregados. Para el próximo ciclo de 14 días fijamos resolución ≥ 50 %, respuesta ≥ 80 % y mediana hasta la primera oferta ≤ 24 h. Estas metas se documentaron después de la simulación histórica; no eran sus criterios previos».

**Fuentes:** [DOCUMENTATION.md, apartados 2–4](../../DOCUMENTATION.md); [ActivityEntry y Store._log](../../models/store.py).

### Diapositiva 7 — KPIs e instrumentos

**05:50–06:35 · 45 segundos**

- Resolución: solicitudes con `trato_concretado` ÷ publicadas × 100. **Meta: ≥ 50 %.**
- Respuesta: solicitudes con al menos una oferta ÷ publicadas × 100. **Meta: ≥ 80 %.**
- Espera: mediana de horas hasta la primera oferta, solo entre solicitudes con oferta. **Meta: ≤ 24 h.**
- `analitica.py` calcula; `simulador.py` genera actividad ficticia con métodos del dominio.
- Periodo base simulado: 3–16 de noviembre de 2026, 14 días simulados; semilla 42, 24 lectores y 10 vendedores simulados.

**Tabla de apoyo — expectativa de lanzamiento, no resultados medidos:**

| KPI estimado | M1 | M2 | M3 | M4 |
|---|---|---|---|---|
| Resolución | 30 % | 40 % | 50 % | 55 % |
| Respuesta | 60 % | 70 % | 80 % | 85 % |
| Mediana hasta primera oferta | 24 h | 18 h | 12 h | 8 h |

**Qué decir:** «Para el lanzamiento estimamos 30 % de resolución, 60 % de respuesta y 24 horas de espera mediana. Al cuarto mes proyectamos 55 %, 85 % y 8 horas, si crecen la participación y la disponibilidad de vendedores. Es un escenario por validar. La espera solo considera solicitudes con oferta». Mostrar la tabla dentro del tiempo asignado; no añadir otro bloque.

**Supuestos para la defensa:** meses de 30 días; 50, 100, 150 y 200 solicitudes por mes; de 25 a 100 lectores activos y de 5 a 15 vendedores activos. Los umbrales del piloto son metas aspiracionales; la expectativa mensual alcanzaría resolución y respuesta en M3. La fecha de lanzamiento y la captación real no están documentadas. Fuente y protocolo: [DOCUMENTATION.md, apartado 4.2](../../DOCUMENTATION.md).

**Fuentes de fórmulas, metas y cifras simuladas:** [DOCUMENTATION.md, apartados 2, 4, 4.1 y 7.1](../../DOCUMENTATION.md); [SPEC-003](../05-specs/SPEC-003-simulador-de-uso.md). Uso real: periodo, participantes y dispositivos todavía no documentados; se deben registrar antes del próximo ciclo. No presentar el ensayo con cuentas demo como recolección real.

## 4. Resultados y propuesta de mejora

### Diapositiva 8 — Resultados del escenario base simulado

**06:35–07:15 · 40 segundos**

- **SIMULADO:** 45 solicitudes publicadas; 34 usuarios simulados activos.
- **SIMULADO:** resolución 31,1 % (14 de 45); respuesta 62,2 % (28 de 45).
- **SIMULADO:** 2,4 h de mediana hasta la primera oferta.
- **SIMULADO:** 136 verificaciones de contacto sin violaciones y 31 acciones inválidas rechazadas.
- Evidencia técnica limitada al escenario; no demuestra impacto social ni transacciones reales.

**Qué decir:** «Son datos simulados. Frente a las metas nuevas, las tasas quedan bajo el objetivo y la espera dentro de 24 h. Es una referencia retrospectiva: no valida usuarios reales ni metas previas». Mostrar el gráfico sin cambiar sus cifras; las probabilidades del simulador influyen en los resultados.

**Fuente de todos los resultados simulados:** [DOCUMENTATION.md, apartados 7.1–7.2](../../DOCUMENTATION.md). Recurso visual: [kpis_simulados.png](../resultados/kpis_simulados.png).

### Diapositiva 9 — Panel público: simulación visible

**07:15–07:50 · 35 segundos**

- Abrir [bookwho.quadcorestore.com/simulacion/](https://bookwho.quadcorestore.com/simulacion/), con rótulo de datos simulados.
- Mismos KPIs que `analitica.py` para el mismo conjunto de datos simulados.
- La página consulta `metricas.json` cada 5 segundos; no expone datos personales.
- El modo en vivo extiende la actividad simulada sin modificar el periodo base.
- Opcional: dejar en pantalla el QR de la landing (`sitio/qr-descarga.png`) para que el curso instale la app. Quienes se registren aparecen en `/en-vivo/` como personas, aparte de los agentes simulados.
  - Decirlo en vivo: que se registren con un correo inventado. La demo no necesita datos personales reales (minimización de datos).
  - Las cuentas «(sim)» son agentes simulados: usan la app por la misma API que un teléfono, con cuentas del dominio reservado `bookwho.test` y contactos ficticios, y el panel las cuenta aparte de las personas. Las cifras de la landing las incluyen.

**Qué decir y mostrar:** señalar tasas, mediana y verificaciones. Si el equipo ya activó el modo en vivo, observar una actualización y aclarar que sus valores pueden diferir del gráfico del periodo base simulado. No afirmar que los cambios corresponden a las acciones realizadas en el teléfono: son fuentes separadas. Si no hay actualización, explicar el mecanismo sin fingir actividad.

**Fuentes:** [README.md, Panel público](../../README.md); [SPEC-004](../05-specs/SPEC-004-panel-de-metricas.md). El 17-11-2026 el sitio respondía con los mismos KPIs; volver a comprobarlo en el ensayo. La configuración del servidor corresponde al equipo.

### Diapositiva 10 — Qué mejorar y con qué cautela

**07:50–08:10 · 20 segundos**

- Backend compartido ya implementado y en prueba (SPEC-005): validar el recorrido entre dispositivos antes de usarlo como evidencia de uso real.
- Avisos sobre entrega y cobertura: impacto medio, esfuerzo bajo, pendientes de validación real.
- Notificar a vendedores y medir abandono: propuestas que requieren especificación y revisión de privacidad.
- Las diferencias territoriales simuladas reflejan supuestos; no diagnósticos de comunidades reales.

**Qué decir:** «La prioridad es validar el circuito compartido con usuarios reales. Las mejoras sugeridas por la simulación son hipótesis, no conclusiones causales».

**Fuente:** [DOCUMENTATION.md, apartados 6 y 7.2–7.3](../../DOCUMENTATION.md).

## 5. Conclusión social y ética

### Diapositiva 11 — Acceso, privacidad y responsabilidad

**08:10–09:00 · 50 segundos**

- Propuesta social: conectar lectores y pequeños vendedores; impacto real pendiente de medir.
- Contactos protegidos por permisos; analítica agregada, sin publicar registros personales.
- Contraseñas con hash; JSON sin cifrado documentado y cuentas demo limitan la seguridad.
- Accesibilidad: español claro, estados con texto y color, controles de al menos 48 dp.
- Uso de IA declarado; revisión humana de producto, documentación y conclusiones.

**Qué decir:** «Entregamos un MVP y un método reproducible de medición. El siguiente paso es validar con usuarios reales y las metas del próximo ciclo: 50 % de resolución, 80 % de respuesta y mediana de espera de hasta 24 h». Indicar que los borradores académicos asistidos por IA deben revisarse por el equipo.

**Fuentes:** [README.md, Privacidad](../../README.md); [fundamentación UX/UI, apartado e](../01-requirements/FUNDAMENTACION-UX-UI.md); [DOCUMENTATION.md, limitaciones](../../DOCUMENTATION.md); [USO_IA.md](../06-process/USO_IA.md).

## Plan B: reemplazar la demo, sin ampliar el tiempo

Aplicar dentro del bloque de demo previsto, sin sumar otra demostración completa:

- **Falla el teléfono o la proyección:** mostrar un video local del mismo recorrido. [COMPLETAR: grabar y ubicar el video local de respaldo]. No se encontró un video de ese recorrido en los recursos revisados; no se presenta como existente. Hay GIF de búsqueda, oferta y aceptación en `docs/presentations/pitch/gif/`, como apoyo parcial.
- **Alternativa de escritorio:** iniciar la app desde la raíz en modo local y repetir el recorrido con las mismas cuentas de prueba. En PowerShell:

  ```powershell
  $env:BOOKWHO_SERVIDOR = 'local'
  python main.py
  ```

  Usar una terminal dedicada al ensayo y cerrarla al terminar. Modo documentado en [README.md, Modo servidor](../../README.md); la interfaz no se ejecutó durante esta actualización documental.
- **Falla internet:** mostrar el catálogo local de respaldo y explicar que la configuración remota usa valores predeterminados. Usar el video si la búsqueda no se completa a tiempo; no prolongar la espera.
- **No carga el panel:** abrir localmente [docs/resultados/kpis_simulados.png](../resultados/kpis_simulados.png). Indicar que es el escenario base simulado; una imagen estática no demuestra actualización en vivo.

Fuentes de las alternativas: [README.md](../../README.md), [DOCUMENTATION.md, apartado 7.1](../../DOCUMENTATION.md) y recursos existentes [búsqueda](pitch/gif/usuario_buscar_libro.gif), [oferta](pitch/gif/vendedor_proponer_oferta.gif), [aceptación](pitch/gif/usuario_aceptar_oferta.gif). El video es un recurso pendiente del equipo.

## Preguntas probables para la defensa

### 1. ¿Qué es un evento y qué estructura tiene?

Es el registro de una acción admitida por el modelo. `ActivityEntry` contiene `at`, `actor_id`, `action` y `detail`, y se persiste bajo `activity` en el JSON. No representa necesariamente una visita a pantalla.  
**Fuente:** [DOCUMENTATION.md, apartado 3](../../DOCUMENTATION.md).

### 2. ¿Cómo relacionan ofertas y solicitudes sin contar varias veces una respuesta?

El analizador interpreta los identificadores del detalle y la unidad de cálculo es la solicitud. Para respuesta basta con que exista una oferta; ofertas posteriores no multiplican solicitudes respondidas.  
**Fuente:** [DOCUMENTATION.md, apartados 3–4](../../DOCUMENTATION.md).

### 3. ¿Qué diferencia hay entre una métrica y un KPI?

Una métrica describe actividad, como eventos diarios o usuarios activos. Un KPI se selecciona por su relación con el objetivo: aquí, resolver solicitudes, recibir respuesta y esperar hasta la primera oferta.  
**Fuente:** [DOCUMENTATION.md, apartado 4](../../DOCUMENTATION.md).

### 4. ¿Cómo aplicaron Medir, Jugar y Validar?

Definieron indicadores desde el diagnóstico, ejecutaron recorridos simulados y analizaron resultados y limitaciones. El 19-11-2026 fijaron las metas del próximo ciclo de 14 días: resolución ≥ 50 %, respuesta ≥ 80 % y mediana hasta la primera oferta ≤ 24 h. La comparación histórica es retrospectiva; la validación del próximo ciclo sigue pendiente.

**Fuente:** [DOCUMENTATION.md, apartado 2](../../DOCUMENTATION.md).

### 5. ¿Cuál fue el periodo de recolección y eran usuarios reales?

El periodo base fue simulado: del 3 al 16 de noviembre de 2026, con 24 lectores y 10 vendedores simulados. El periodo de recolección real sigue pendiente y no debe confundirse con la encuesta real del diagnóstico.  
**Fuente de las cifras simuladas:** [DOCUMENTATION.md, apartados 2 y 7.1](../../DOCUMENTATION.md).

### 6. ¿Por qué usar simulación y qué pueden concluir de ella?

El docente autorizó datos ficticios; el simulador ejercita los métodos públicos del dominio de forma reproducible. Permite revisar instrumentación y recorridos, pero las probabilidades programadas impiden inferir adopción o comportamiento humano real.  
**Fuentes:** [SPEC-003](../05-specs/SPEC-003-simulador-de-uso.md); [DOCUMENTATION.md, apartado 6](../../DOCUMENTATION.md).

### 7. ¿Por qué la mediana de espera no demuestra que todos encontraron su libro?

Solo considera solicitudes con oferta y mide la primera respuesta, no una entrega. Debe leerse con la tasa de respuesta; incluso un `trato_concretado` es declaración del lector, no una venta verificada.  
**Fuente:** [DOCUMENTATION.md, apartados 4 y 6](../../DOCUMENTATION.md).

### 8. ¿El panel en vivo muestra lo que acaba de ocurrir en el teléfono?

Depende de la fuente: `/simulacion/` publica el archivo del escenario simulado y no refleja esta demo local. `/en-vivo/` muestra la actividad del backend compartido, separando personas y agentes; refleja acciones de teléfonos conectados a ese servidor al actualizarse. Las cuentas demo de este guion operan en modo local.

**Fuentes:** [README.md, Panel público y Modo servidor](../../README.md); [SPEC-004](../05-specs/SPEC-004-panel-de-metricas.md); [SPEC-005](../05-specs/SPEC-005-backend-compartido.md).
