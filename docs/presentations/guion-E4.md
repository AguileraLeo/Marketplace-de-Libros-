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

- Un mismo teléfono y cuentas de prueba: el almacenamiento no está compartido entre dispositivos.
- El lector busca y publica; el vendedor responde a esa solicitud.
- El lector acepta para coordinar y entonces accede al contacto autorizado.
- Cerrar y reabrir permite mostrar persistencia, sin desinstalar ni borrar datos.

**Preparación del equipo:** APK instalado, teléfono cargado y proyección lista. Usar únicamente contactos ficticios. Revisar previamente que el vendedor no tenga una oferta activa para la solicitud del ensayo. No mostrar registros con datos personales. Esta preparación y la demo son instrucciones para el equipo: no se ejecutaron al redactar el guion.

| Tiempo dentro de la demo | Acción en el teléfono | Frase breve / evidencia visible |
|---|---|---|
| 00:00–00:15 | Iniciar sesión con `lector@demo.cl`, clave `1234`. | «Esta es una cuenta de prueba, excluida de los KPIs de uso real». |
| 00:15–00:40 | Buscar «El Hobbit» y seleccionar el resultado correcto. | «Los metadatos vienen del proveedor externo; existe respaldo local si falla la red». |
| 00:40–01:05 | Completar ubicación, condición y entrega; publicar solicitud. | Mostrar la confirmación y conservar su identificador. Precio máximo opcional. |
| 01:05–01:20 | Salir e iniciar sesión como `vendedor@demo.cl`, clave `1234`. | «Cambiamos de rol en el mismo dispositivo porque aún no hay backend compartido». |
| 01:20–01:45 | Localizar la solicitud, pulsar «Puedo ofrecerlo» y publicar una oferta con contacto ficticio. | Mostrar precio y condición. [COMPLETAR: valores y contacto ficticios del ensayo]. |
| 01:45–02:15 | Volver a la cuenta del lector, abrir la oferta y aceptar para coordinar. | Mostrar el contacto. «Aceptar inicia la coordinación; no acredita una venta ni una entrega». |
| 02:15–02:45 | Cerrar la aplicación y reabrirla; si pide login, entrar como lector y abrir la misma solicitud. | Mostrar que solicitud, oferta y estado permanecen. No prometer persistencia de la sesión. |

**Fuentes:** [README.md, cuentas de demo, búsqueda, persistencia y reglas](../../README.md); [documentación técnica, flujo por rol](../04-architecture/DOCUMENTACION.md); [catálogo de respaldo con El Hobbit](../../services/books_api.py). Las duraciones y acciones seleccionadas son planificación, no mediciones.

### Diapositiva 5 — Servicios y límites del MVP

**04:45–05:15 · 30 segundos**

- Persistencia JSON con escritura temporal y reemplazo atómico.
- Autenticación local; recuperación de contraseña simulada, sin envío de correos.
- Notificaciones locales y configuración remota con respaldo sin conexión.
- APK Android; sin pagos, chat, logística ni sincronización entre teléfonos.

**Qué decir:** «Los datos persisten en el dispositivo. Las notificaciones locales y el banner remoto no convierten la aplicación en un servicio multiusuario». No presentar una notificación del mismo teléfono como entrega remota al lector.

**Fuente:** [README.md, servicios y reglas del demo](../../README.md).

## 3. Metodología de medición (RA3)

### Diapositiva 6 — De acciones a eventos: MJV App

**05:15–05:50 · 35 segundos**

- Medir: indicadores vinculados al diagnóstico y metas previas a la recolección.
- Jugar: recorridos durante un periodo declarado; aquí, actividad simulada.
- Validar: comparar con metas, ajustar y volver a medir.
- `ActivityEntry`: `at`, `actor_id`, `action`, `detail`; se guarda en `activity` del JSON.
- Ejemplos de eventos: `solicitud_publicada`, `oferta_publicada`, `trato_concretado`.

**Qué decir:** «El evento representa una acción aceptada por el modelo, no una pantalla vista. El detalle permite asociar ofertas y solicitudes; puede contener correos, por eso mostramos agregados». Las metas siguen pendientes: [COMPLETAR: meta acordada por el equipo para cada KPI].

**Fuentes:** [DOCUMENTATION.md, apartados 2–4](../../DOCUMENTATION.md); [ActivityEntry y Store._log](../../models/store.py).

### Diapositiva 7 — KPIs e instrumentos

**05:50–06:35 · 45 segundos**

- Resolución: solicitudes con `trato_concretado` ÷ publicadas × 100.
- Respuesta: solicitudes con al menos una oferta ÷ publicadas × 100.
- Espera: mediana de horas hasta la primera oferta, solo entre solicitudes con oferta.
- `analitica.py` calcula; `simulador.py` genera actividad ficticia con métodos del dominio.
- Periodo base simulado: 3–16 de noviembre de 2026, 14 días simulados; semilla 42, 24 lectores y 10 vendedores simulados.

**Qué decir:** «Las sesiones son métricas descriptivas. Estos KPIs se relacionan con respuesta, resolución y espera. La mediana debe leerse junto a la tasa de respuesta; deja fuera las solicitudes sin ofertas».

**Fuentes de fórmulas y cifras simuladas:** [DOCUMENTATION.md, apartados 2, 4 y 7.1](../../DOCUMENTATION.md); [SPEC-003](../05-specs/SPEC-003-simulador-de-uso.md). Uso real: [COMPLETAR: periodo, participantes y dispositivos de la recolección real].

## 4. Resultados y propuesta de mejora

### Diapositiva 8 — Resultados del escenario base simulado

**06:35–07:15 · 40 segundos**

- **SIMULADO:** 45 solicitudes publicadas; 34 usuarios simulados activos.
- **SIMULADO:** resolución 31,1 % (14 de 45); respuesta 62,2 % (28 de 45).
- **SIMULADO:** 2,4 h de mediana hasta la primera oferta.
- **SIMULADO:** 136 verificaciones de contacto sin violaciones y 31 acciones inválidas rechazadas.
- Evidencia técnica limitada al escenario; no demuestra impacto social ni transacciones reales.

**Qué decir:** «Son resultados simulados autorizados por el docente. Las probabilidades del simulador influyen en las tasas. El modelo ejecuta sus controles reales, pero eso no prueba ausencia general de fallos». Mostrar el gráfico sin cambiar sus cifras.

**Fuente de todos los resultados simulados:** [DOCUMENTATION.md, apartados 7.1–7.2](../../DOCUMENTATION.md). Recurso visual: [kpis_simulados.png](../resultados/kpis_simulados.png).

### Diapositiva 9 — Panel público: simulación visible

**07:15–07:50 · 35 segundos**

- Abrir [bookwho.quadcorestore.com](https://bookwho.quadcorestore.com), con rótulo de datos simulados.
- Mismos KPIs que `analitica.py` para el mismo conjunto de datos simulados.
- La página consulta `metricas.json` cada 5 segundos; no expone datos personales.
- El modo en vivo extiende la actividad simulada sin modificar el periodo base.

**Qué decir y mostrar:** señalar tasas, mediana y verificaciones. Si el equipo ya activó el modo en vivo, observar una actualización y aclarar que sus valores pueden diferir del gráfico del periodo base simulado. No afirmar que los cambios corresponden a las acciones realizadas en el teléfono: son fuentes separadas. Si no hay actualización, explicar el mecanismo sin fingir actividad.

**Fuentes:** [README.md, Panel público](../../README.md); [SPEC-004](../05-specs/SPEC-004-panel-de-metricas.md). El 17-11-2026 el sitio respondía con los mismos KPIs; volver a comprobarlo en el ensayo. La configuración del servidor corresponde al equipo.

### Diapositiva 10 — Qué mejorar y con qué cautela

**07:50–08:10 · 20 segundos**

- Backend compartido: impacto alto, esfuerzo alto; requisito para conectar dispositivos distintos.
- Avisos sobre entrega y cobertura: impacto medio, esfuerzo bajo, pendientes de validación real.
- Notificar a vendedores y medir abandono: propuestas que requieren especificación y revisión de privacidad.
- Las diferencias territoriales simuladas reflejan supuestos; no diagnósticos de comunidades reales.

**Qué decir:** «La prioridad es conectar dispositivos. Las mejoras sugeridas por la simulación son hipótesis, no conclusiones causales».

**Fuente:** [DOCUMENTATION.md, apartados 6 y 7.2–7.3](../../DOCUMENTATION.md).

## 5. Conclusión social y ética

### Diapositiva 11 — Acceso, privacidad y responsabilidad

**08:10–09:00 · 50 segundos**

- Propuesta social: conectar lectores y pequeños vendedores; impacto real pendiente de medir.
- Contactos protegidos por permisos; analítica agregada, sin publicar registros personales.
- Contraseñas con hash; JSON sin cifrado documentado y cuentas demo limitan la seguridad.
- Accesibilidad: español claro, estados con texto y color, controles de al menos 48 dp.
- Uso de IA declarado; revisión humana de producto, documentación y conclusiones.

**Qué decir:** «Entregamos un MVP y un método reproducible de medición. No confundimos demostración técnica con eficacia social. El siguiente paso es validar con usuarios reales y metas acordadas». Indicar que los borradores académicos asistidos por IA deben revisarse por el equipo.

**Fuentes:** [README.md, Privacidad](../../README.md); [fundamentación UX/UI, apartado e](../01-requirements/FUNDAMENTACION-UX-UI.md); [DOCUMENTATION.md, limitaciones](../../DOCUMENTATION.md); [USO_IA.md](../06-process/USO_IA.md).

## Plan B: reemplazar la demo, sin ampliar el tiempo

Aplicar dentro del bloque de demo previsto, sin sumar otra demostración completa:

- **Falla el teléfono o la proyección:** mostrar un video local del mismo recorrido. [COMPLETAR: grabar y ubicar el video local de respaldo]. No se encontró un video de ese recorrido en los recursos revisados; no se presenta como existente. Hay GIF de búsqueda, oferta y aceptación en `docs/presentations/pitch/gif/`, como apoyo parcial.
- **Alternativa de escritorio:** el equipo puede iniciar previamente `python main.py` desde la raíz y repetir el recorrido con cuentas de prueba. Comando documentado en [README.md, Escritorio](../../README.md); no se ejecutó al redactar este guion.
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

Definieron indicadores desde el diagnóstico, ejecutaron recorridos simulados y analizaron resultados y limitaciones. Comparar con metas sigue pendiente; sin metas acordadas no se declara cumplimiento.  
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

No: publica agregados de actividad simulada y consulta su archivo cada 5 segundos. La app guarda información local por dispositivo; sin backend compartido no existe esa sincronización.  
**Fuentes:** [README.md, Panel público y Persistencia](../../README.md); [SPEC-004](../05-specs/SPEC-004-panel-de-metricas.md).
