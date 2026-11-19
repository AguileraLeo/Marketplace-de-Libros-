# Declaración de uso de Inteligencia Artificial

## 1. IA usada

- **Herramienta:** Claude Code (Anthropic), CLI de asistencia para desarrollo de software.

## 2. Modelo

- **E2:** Claude Sonnet 5; en la sesión de revisión final, Claude Sonnet 5 y Claude Opus 5.5.
- **E3:** Claude Opus 5.5 (`claude-opus-5-5`).

- **E4:** Claude Opus 5.5 (Claude Code) y GPT-6.1 Sol (Codex en VS Code).

## 3. Prompts realizados

### E2 (maqueta)
- **Alcance de esta declaración:** trabajo de pulido y ajustes sobre la maqueta `BookWho?` (Kivy/KivyMD), correspondiente a una sesión de trabajo previa a la presentación de la evaluación E2. El dominio, las pantallas base y el flujo principal de la app ya existían de un trabajo anterior del equipo; en esta sesión se usó IA para revisar, corregir y pulir esa base.

1. "Antes de escribir código, haz una auditoría completa del repositorio y del material del ramo. Quiero entender qué está hecho, qué falta y qué tecnología corresponde usar antes de definir los próximos pasos del MVP."
2. "Quiero definirle un nombre a la aplicación. Dame opciones que combinen la idea de búsqueda, hallazgo o cacería de un libro, algo original y con identidad propia."
3. "Evalúa 'BookWho?' como nombre para la app: ventajas, riesgos y si calza con el modelo de negocio. Si te convence, lo dejamos como definitivo."
4. "Quiero una pasada de pulido general: revisa el código, el estilo visual, las funcionalidades y la experiencia de usuario, y sugiere mejoras concretas antes de aplicarlas."
5. "Ejecuta la aplicación real en pantalla en cada cambio importante, para que yo pueda revisar visualmente el resultado antes de aprobarlo."
6. "Actualiza el subtítulo de la pantalla de inicio de sesión para que comunique mejor la propuesta de valor de la app."
7. "Renueva la identidad visual de la app (iconografía y tipografía) para que se vea menos genérica y menos parecida a una plantilla estándar."
8. "Explícame cómo funciona el flujo de publicación de libros desde ambos roles, lector y vendedor. No encuentro una opción para publicar un libro como vendedor y quiero entender si es una omisión o una decisión de diseño."
9. "Propón una forma de mostrarle al vendedor qué tan cerca está del lector, sin pedirle a este último su dirección real; puede ser un punto de referencia o zona aproximada."
10. "El selector de ubicación no me muestra todas las comunas que esperaba (por ejemplo Temuco). Revisa si el catálogo está incompleto o si es un problema de la interfaz."
11. "El último cambio de interfaz no me convenció. Revierte específicamente esa parte y deja el resto del trabajo tal como estaba."
12. "Haz un balance honesto de qué porcentaje de la rúbrica de evaluación estamos cubriendo hasta este punto, y qué falta para completarla."
13. "Dejé los resultados de la encuesta en la carpeta del ramo; hay un nombre en broma dentro, lo demás es correcto." / "Revisa que no quede nada más en inglés o mal codificado."
14. "Mi compañero me dio esta información junto con el archivo de las respuestas. ¿Con esa información cumplimos toda la rúbrica? Si no falta nada, hagamos una revisión del código: que no haya agujeros, funciones inventadas ni código muerto."
15. "Abre la app y empecemos a reparar todo, desde lo más importante a lo más simple."
16. "Vamos con la opción B" (fundamentación sin afirmar una reputación de vendedor que la app no tiene).
17. "Arregla el texto de mi compañero; después lo reescribiremos con nuestra voz." / "¿Todos los documentos están actualizados?"
18. "Dejé un HTML con un diseño para la aplicación." (Primero aplicamos solo la paleta y las fuentes.)
19. "Hagamos el diseño que te pasé; no me gusta cómo se ve sin la reestructuración de las pantallas."
20. "Aplica el diseño que te compartí." / "Espera, te compartí un PDF, a ese diseño me refería." (Maqueta de la pantalla "Solicitud publicada".)
21. "Entonces continúa y aplícalo a todas las pantallas; arregla los ajustes que afectan a otras pantallas."

### E3 (servicios integrados y Android)

22. "Lee la rúbrica, está en la carpeta Desarrollo Móvil." / "Te puse las sesiones que faltaban, léelas también; estas son las instrucciones para mañana."
23. "Sí, es ese [proyecto], pero creo que necesitamos mejorarlo: tiene que correr en Android. ¿Es posible dejarlo para descargar?"
24. "Tengo un servidor, mi PC viejo Lenovo Z40, y un dominio. ¿Sirven de algo en esta ocasión?".
25. "Mi teléfono es iOS, ¿no podré probarlo entonces?" / "Ya, emulemos Android para revisar."
26. "Configuremos la configuración remota." / "Dame los comandos." 
27. "Hagamos lo que falta." (Release del APK, repositorio personal, esta declaración y guía de defensa.)

### E4

Prompts principales a Claude Code en la sesión del 17-11-2026 (textuales, abreviados con […]):

1. "tienes la rubrica de la ultima evaluacion, la de mañana?"
2. "quiero ordenar el repo […] y quiero saber si fredo subio cambios al git, prioridad ordenar el repo, buena arquitectura, limpia profesional, y acorde a la rubrica"
3. "espera, el repo esta bien, los cambios estan bien?"
4. "el profesor dijo que podemos usar datos ficticios", junto con un plan pegado: "Quiero que me ayudes a planificar una infraestructura para alojar Bookwho en mi servidor y ejecutar agentes que simulen usuarios […]. Por ahora, realiza el diagnóstico y presenta el plan."
5. "que haria el simulador […] que las ias usan la app, que esten el el servidor y usen la app muchos agente o varios, creando cuentas, etc o no se puede? es mas barato otra opcion?"
6. "meditemos hacer un backend compartido […]" y luego "terminemos con lo que estabas haciendo, despues seguimoms con el backend"
7. "podrias divir todo lo que queda por hacer y trabajan los dos en paralelo […] gpt no tiene ponytail aunque le puedes dar intrucciones pero lo que sea mas barato"

Los prompts a Codex (borrador del Informe Final; revisión del informe, guion y esta sección) los redactó Claude Code y el equipo los pegó en Codex.

#### Reconstrucción identificada de los prompts pendientes

**Nota de trazabilidad (19-11-2026):** no se encontró `CIERRE_E4.md` ni la transcripción de
la sesión atribuida al 16-11-2026 en los archivos o en el historial Git revisado. A solicitud
del equipo, se completa el registro con la siguiente **reconstrucción de intenciones y alcance**,
basada en las modificaciones y declaraciones conservadas. Estos textos no son citas literales
ni prueban la fecha, el orden exacto o la redacción de los prompts originales. Los commits
citados son del 17-11-2026; acreditan los cambios, no los mensajes que los originaron.

**Claude Code — trabajo de medición y estabilización previo al cierre E4**
(`e2147a8`, «E4: medición RA3 y correcciones de estabilización»):

1. **Prompt reconstruido:** Revisar la medición RA3 de la app y registrar los eventos de los casos de uso exitosos. Calcular resolución, respuesta y mediana de horas hasta la primera oferta; excluir cuentas demo y del equipo, y documentar fórmulas, reproducción y limitaciones sin inventar uso real.
2. **Prompt reconstruido:** Revisar el desistimiento de la coordinación por parte del vendedor y la cancelación de la última oferta. Mantener consistentes los estados de solicitud y oferta y verificar los permisos con pruebas.
3. **Prompt reconstruido:** Corregir el manejo de errores al guardar y de archivos JSON con estructura inesperada, para informar la falla sin continuar como si los datos se hubieran guardado. Añadir pruebas de persistencia.
4. **Prompt reconstruido:** Ocultar el panel de cuentas demo en Android sin afirmar que eso elimina las cuentas ni constituye una medida de seguridad. Actualizar la documentación del alcance y ejecutar las pruebas.

**Codex — documentación académica de cierre**
(`962a3a0`, «Informe Final, guion de la presentación y declaración de IA E4 (borradores)»):

5. **Prompt reconstruido:** Leer `AGENTS.md` y las fuentes del repositorio. Redactar el borrador de `INFORME_FINAL.md` siguiendo problema, solución, metodología, resultados y conclusión ética. Citar la evidencia y separar encuesta real, simulación y demo; dejar identificados los datos que el equipo aún no haya proporcionado.
6. **Prompt reconstruido:** Preparar `docs/presentations/guion-E4.md` para una exposición de nueve minutos, incluida una demo de dos minutos y cuarenta y cinco segundos. Proponer tiempos, acciones por rol, fuentes, alternativas ante fallas y preguntas de defensa sin presentar el ensayo como ejecutado.
7. **Prompt reconstruido:** Revisar la coherencia entre informe, guion y documentación. Completar la declaración E4 en `USO_IA.md`, diferenciando herramientas, trabajos asistidos, decisiones humanas y limitaciones; no atribuir pruebas o resultados nuevos a una tarea de redacción.

**Codex — actualización documental actual (19-11-2026):** el encargo fue definir las metas de
los KPIs, completar los prompts de este archivo y completar los datos de cuentas de prueba del
guion. El equipo autorizó expresamente usar una reconstrucción identificada cuando no se
encontraron los prompts originales. Se documentaron metas para el próximo ciclo, sin
atribuirlas retrospectivamente a la simulación histórica, y se reutilizaron los alias locales
existentes en `DEMO_USERS`.

**Seguimiento del encargo (19-11-2026, prompt textual a Codex):** «con respecto a los kpis,
estima cuanto se espera el primer mes de lanzamiento y proyecta al menos dos o tres meses
a futuro». La IA elaboró un escenario condicionado para M1–M4, explicitó sus supuestos de
participación y actividad y lo separó de las metas del piloto y de los datos simulados.

Alcance de los trabajos originales:

- **Claude Code:** integración del refactor MVC con el trabajo E4 y resolución de conflictos; corrección del cierre al suspender usuarios; organización del repositorio; simulador ficticio (SPEC-003), panel público (SPEC-004), diagnóstico de CGNAT y guía de publicación con Cloudflare Tunnel.
- **GPT-6.1 Sol (Codex):** redacción del borrador del Informe Final, del guion de presentación y de este borrador de declaración.
- **Decisiones y ejecución del equipo:** comandos de git y del servidor; uso de datos simulados autorizado por el docente; aprobación de sacar `.agents/` y de postergar el backend hasta después de la presentación.

## 4. Outputs

### E2

- **Diagnóstico de la rúbrica E2**: lectura del documento de rúbrica del curso y detección de que la fundamentación UX/UI (30% de la nota) dependía de evidencia real de usuarios que aún no existía, y de que el archivo `USO_IA.md` era obligatorio por política general del curso (no solo por la rúbrica de esta evaluación).
- **Corrección de un bug real de interfaz**: las tarjetas de métricas del panel de administrador no mostraban colores diferenciados por falta de `theme_bg_color: "Custom"` en KivyMD 2.0; se corrigió en `libros.kv` y se verificó con capturas antes/después.
- **Rediseño visual**: cambio de paleta de color (Teal → dorado envejecido/"darkgoldenrod", derivado con Material You), tipografía serif (Lora, con licencia OFL) para títulos y encabezados, y una marca propia (ícono de libro + insignia "?") para reemplazar el ícono genérico inicial.
- **Función de cercanía vendedor–lector**: `proximity_label()` en `locations.py`, que compara comuna/región del vendedor con la de la solicitud (sin exponer direcciones exactas), más el campo "comuna" agregado al registro de vendedores.
- **Aclaraciones de texto en la interfaz** para que quede explícito que el modelo es "el lector publica lo que busca, el vendedor responde" (no un catálogo de inventario).
- Ejecución de la suite de pruebas (`python -m unittest discover -s tests -v`) después de cada cambio relevante.
- **Limpieza de la encuesta**: se reparó la codificación rota (tildes y ñ) en 227 celdas de la planilla y se reemplazó un nombre en broma.
- **Verificación de cifras**: se recalcularon los porcentajes del texto del equipo contra la planilla. El 94,4 % y el 13 de 18 eran correctos; el 87,5 % requería precisar su base (14 de 16) y la muestra no era solo de 18 a 24 años (10 de 18).
- **Detección de una afirmación sin respaldo**: el texto decía que las tarjetas mostraban la reputación del vendedor, pero esa función no existe en la app y está fuera del MVP según `AGENTS.md`.
- **Revisión de código y 5 correcciones**: búsquedas de libros que podían mostrar resultados viejos (`main.py`), chequeo de permisos de `offer_contact()` que confiaba en el rol enviado por el cliente (`store.py`), código muerto y un precio 0 mal validado en `_parse_price()`, y redimensionado ineficiente de `WideButton`. Se agregaron pruebas que fallan con el código anterior y pasan con el corregido.
- **Redacción de `FUNDAMENTACION-UX-UI.md`** a partir de la encuesta y del texto del equipo, verificando cada pantalla y componente citado contra el código.
- **Paleta y fuentes de la maqueta editorial**: verde `#1F4D3A`, fondo crema `#FBFAF7`, Source Serif 4 en títulos e IBM Plex Sans en el resto. La IA detectó con capturas que un esquema de color dejaba botones invisibles en el inicio del lector y lo corrigió antes de entregarlo. Después se reconstruyó el inicio del lector según la maqueta (selector segmentado, cifras resumen y lista editorial), subiendo el selector a 48 dp por accesibilidad y omitiendo la etiqueta "Nuevas", que la app no puede calcular. Luego se rehízo la confirmación "Solicitud publicada" según su maqueta en PDF, reutilizando la misma fila de solicitud y ajustando el interlineado de los títulos en serif. Finalmente se llevó el estilo a las 19 pantallas restilizando los componentes compartidos (listas planas, estados con punto de color, selector segmentado, paneles y botones), y se revisó cada pantalla con capturas automáticas. En esa revisión la IA detectó y corrigió: huecos dentro de palabras por el *hinting* de Kivy, el estado "Activa" de ofertas en gris, una etiqueta aplastada y botones de comuna que se salían de la pantalla o medían menos de 48 dp.
- **Actualización de documentos desactualizados**: reglas de estados en `README.md`, cantidad de pruebas en `CONTEXTO.md` y estado de la rúbrica en `DOCUMENTACION.md`.

### E3

- **Diagnóstico:** la IA comparó el repositorio con la rúbrica E3 y las sesiones 17–24 y detectó que faltaban 3 de los 4 servicios (el login existía, pero solo en memoria; no había JSON, notificaciones ni configuración remota).
- **`services/persistence.py`:** guardar/cargar todo el `Store` en `data.json` (fechas como ISO, escritura atómica con `.tmp`, respaldo si el JSON está corrupto, contadores de id que siguen desde el mayor guardado) y `tests/test_persistence.py`.
- **`services/notifications.py`:** notificación local con plyer y permiso `POST_NOTIFICATIONS` en Android; disparada al publicar una oferta y al entrar un lector con ofertas por revisar.
- **`services/remote_config.py` + `remote_config.json`:** lectura asíncrona con `UrlRequest` desde GitHub, `DEFAULTS` como respaldo sin conexión y validación de claves/tipos.
- **Hash SHA-256 de contraseñas** en `store.py`, porque al persistir quedarían en texto plano en el JSON.
- **Android:** `buildozer.spec`, certificados con `certifi` para que HTTPS funcione en el teléfono, y compilación del APK con Docker.
- **Pruebas en emulador Android 14:** la IA configuró el emulador, instaló el APK y verificó con capturas el login, la notificación, la persistencia tras forzar el cierre y la configuración remota con y sin red. Antes de eso detectó en el contenido del APK dos fallas que lo habrían cerrado al abrir (falta de `pycairo` y una versión vieja de `materialyoucolor`) y una que impedía mostrar notificaciones en Android 12+.
- **Documentación:** secciones nuevas del `README.md` (servicios y dónde están, Android, dificultades) y la reorganización de este archivo en las 6 secciones pedidas.

### E4 (borrador)

Antecedentes proporcionados por el equipo para esta declaración; no constituyen una nueva ejecución ni una verificación independiente de los resultados:

- **Claude Code — integración:** integró el refactor MVC realizado por un integrante con el trabajo E4 y resolvió los conflictos.
- **Claude Code — corrección:** detectó y corrigió un error que cerraba la aplicación al suspender usuarios.
- **Claude Code — organización:** ordenó el repositorio, ajustó el README según la rúbrica, creó ADR-003 y sacó `.agents/`.
- **Claude Code — medición y panel:** creó el simulador de datos ficticios (SPEC-003) y el panel público de métricas (SPEC-004).
- **Claude Code — publicación:** diagnosticó CGNAT y guió la publicación con Cloudflare Tunnel.
- **Pruebas informadas:** pasaron de 50 a 63. Esta evolución se declara según los hechos aportados por el equipo; Codex no ejecutó pruebas durante estas tareas de documentación.
- **GPT-6.1 Sol (Codex) — redacción:** redactó el borrador del Informe Final, el guion de la presentación y este borrador de la parte E4.
- **Codex — actualización documental del 19-11-2026:** definió metas iniciales de resolución ≥ 50 %, respuesta ≥ 80 % y mediana hasta la primera oferta ≤ 24 h para el próximo ciclo de 14 días; sincronizó documentación, informe y guion; completó alias y datos ficticios del ensayo; reconstruyó los prompts pendientes con identificación explícita y referencias al historial. Esta tarea no generó nuevos datos de uso ni ejecutó la demo gráfica.
- **Codex — proyección del lanzamiento:** añadió un escenario M1–M4 en `DOCUMENTATION.md` §4.2 y lo resumió en el informe, el guion y el contexto. Estimó resolución de 30 % a 55 %, respuesta de 60 % a 85 % y mediana de espera de 24 h a 8 h. Son supuestos de planificación solicitados por el equipo; no hay observaciones de lanzamiento ni evidencia de que se cumplirán.
- **Responsabilidad del equipo:** ejecutó todos los comandos de git y del servidor; decidió usar datos simulados con autorización del docente, aprobó sacar `.agents/` y postergó el backend hasta después de la presentación.

## 5. Ajustes

### E2

- Decidí **mantener el modelo de solicitud/oferta** tal como estaba (no agregar catálogo de vendedor), después de que la IA me explicara el trade-off.
- Elegí yo el nombre final **"BookWho?"** en vez de las opciones que propuso la IA (Hallalibro, Bibliocaza, etc.).
- Pedí **revertir** el cambio de "comunas de ejemplo" en Crear solicitud porque no era lo que quería, y la IA deshizo puntualmente solo esos archivos/líneas sin tocar el resto del trabajo.
- Definí el alcance de la función de cercanía (nivel comuna/región, sin coordenadas exactas) en vez de la alternativa con distancia en kilómetros que la IA también ofreció, por menor riesgo de datos incorrectos a un día del ensayo.
- Decidí posponer la encuesta/entrevistas de usuarios (fundamentación UX/UI) para el final, priorizando primero el pulido técnico.
- Revisé visualmente cada cambio importante corriendo la app real antes de aceptarlo.
- Ante la reputación de vendedor que no existía, elegí **no implementarla a última hora** y declararla como próximo paso (opción B), para que la fundamentación coincida con lo que muestra la demo.
- Decidí reescribir con nuestras propias palabras el texto de la presentación, usando como base la versión corregida.
- Hago yo los commits, después de revisar los cambios.

### E3

- Pedí que la app no quedara solo en escritorio: tenía que correr en Android y quedar disponible para descargar (APK en GitHub Releases).
- Revisé que todo funcionara en un emulador Android en el PC: login, notificación al entrar como lector, datos que se mantienen al cerrar y reabrir la app, y el banner de configuración remota con y sin conexión.
- Decidí no portar la app a iOS en esta etapa, aunque mi teléfono es iPhone: requiere Mac, Xcode y firma de Apple, y a esta altura podía ser contraproducente.
- Quería servir la configuración remota y la descarga desde mi propio servidor (un Lenovo Z40 con dominio propio). Como estaba apagado, decidí dejarlo para después de la evaluación y usar GitHub como fuente remota.
- Hice yo los commits y el paso a `main` con un Pull Request, como veníamos trabajando en el equipo.

### E4

- Retomé lo que quedó pendiente en la E3: llevar BookWho? a mi servidor Z40 con dominio propio. Pedí un backend compartido para que los datos de todos los teléfonos lleguen a un solo lugar y el panel muestre la prueba en vivo.
- Usé datos simulados, autorizados por el docente, con una condición: que siempre se identifiquen como simulados. Los agentes usan cuentas `@bookwho.test` con "(sim)" en el nombre, tienen un panel separado del real y la página de privacidad lo explica.
- Pedí una landing nueva en vez de reutilizar la del pitch anterior. Después hice sacar los avisos y las rotulaciones de las cifras: prefiero explicarlas en vivo y defender ahí las decisiones técnicas.
- Probé el QR y me di cuenta de que abría la página en vez de descargar el APK. Pedí corregirlo para que la descarga fuera directa.
- Filtré las sugerencias de Fredo. Aceptamos logo, favicon, animación, sombras, métricas destacadas, paginación y exportación a CSV; descarté la música.
- Antes de cambiar la interfaz pedí primero una auditoría de UI/UX sin tocar archivos, y solo se implementó cuando la aprobé.
- Repartí el trabajo entre dos IA: Codex implementaba y Claude Code revisaba antes de cada commit. En esas revisiones se descartó una afirmación incorrecta de Codex (que había que recompilar el APK) y se corrigió un estilo suyo que cortaba palabras en las tablas del panel.
- Pedí una auditoría de seguridad antes de presentar. Al entender que la clave de los agentes está a la vista en el repositorio, decidí bloquear esas cuentas desde internet, ya que esconder la clave no era posible.
- Dejé para después de la E4 la validación de correo, el paso a SQLite y un hash de contraseñas más fuerte (PBKDF2). Quedó declarado en `ADR-004` y `SEGURIDAD.md`.
- Hice yo los commits, el despliegue en el Z40 y la subida del APK. La mañana de la presentación el servidor se reinició y perdió la conexión unos minutos. Al volver reprogramé los agentes, porque el reinicio había borrado su temporizador.

## 6. Reflexión en el uso de IA

### E2

Esta fue la primera vez que usé un asistente de IA de forma tan integrada al flujo de desarrollo, no solo para pedir código suelto sino para iterar sobre una app que ya existía. Lo que más me sirvió fue que la IA no se limitó a "hacer lo que pedí": cuando le pedí un cambio de color se dio cuenta sola de que había un bug real en las tarjetas del panel de administrador (KivyMD estaba ignorando los colores personalizados) y lo arregló antes de seguir. Eso me hizo entender que no basta con mirar la pantalla y decir "se ve bien", hay que entender por qué algo se ve como se ve.

También aprendí que la IA puede equivocarse de foco si uno no la corrige a tiempo: en un momento probó agregar más ciudades de ejemplo en el selector de ubicación y a mí no me convenció el resultado, así que le pedí volver atrás. Que pudiera deshacer justo esa parte sin romper el resto del trabajo me hizo confiar más en pedir cambios sin miedo a "perder" lo que ya estaba bien.

Lo que más tuve que revisar por mi cuenta fueron las decisiones de producto: el nombre de la app, si agregábamos o no un catálogo para vendedores, y hasta qué nivel de precisión le poníamos a la ubicación. La IA proponía alternativas con sus ventajas y riesgos, pero la decisión final siempre fue mía, sobre todo pensando en el tiempo que quedaba antes del ensayo con el profesor.

Mi mayor aprendizaje fue que usar IA bien no es "que te resuelva todo", sino tener claro qué le estoy pidiendo, por qué, y revisar el resultado en la app real antes de darlo por bueno. También me quedó claro que la parte más importante de esta evaluación (la fundamentación con usuarios reales) es algo que la IA no puede inventar por mí, y que la dejé pendiente a propósito para no caer en la tentación de rellenarla con datos que no existen.

### E3

La IA nos sirvió principalmente para configurar los servicios y entender cómo funcionan: dónde se guarda el JSON, qué dispara la notificación y de dónde sale el valor remoto.

Nos preocupa no haber podido configurar todo como hubiera querido, desde mi servidor para esta etapa. También nos preocupa entender código escrito a última hora, pero no es una limitante: se entiende la lógica detrás de cada acción.

Aprendí a compilar para Android. Antes lo había hecho para iOS en una aplicación personal, y entender ambos sistemas me aporta al progreso general.

### E4

En esta etapa la Ia se encargó de unificar distintas tareas para luego auditarlas y que todo funcione como debería, existe registro de ello en nuestra forma de trabajar.

Matías montó su servidor local nuevamente, y en conjunto a la IA se logró montar una landing page y una pagina de metricas en un tiempo bastante acotado. La misma mañana de la presentación el Z40 se reinició, el sitio estuvo caído unos minutos y hubo que volver a programar los agentes. 

Lo más delicado fue la honestidad con los datos. La IA puede generar usuarios y actividad que parecen reales, y justamente por eso decidimos que todo lo simulado se vea como simulado. 

Me preocupa la cantidad de código generado en pocos días. Para poder defenderlo habia que revisar cada cambio antes de subirlo, desplegamos solo con las pruebas automáticas en verde (121 al final). Mi aprendizaje es que la IA acelera mucho el trabajo, pero las decisiones siguen siendo nuestras: qué medir, qué mostrar y qué no prometer.


