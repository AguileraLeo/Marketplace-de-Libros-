# Declaración de uso de Inteligencia Artificial

## Herramienta y modelo

- **Herramienta:** Claude Code (Anthropic), CLI de asistencia para desarrollo de software.
- **Modelo:** Claude Sonnet 5; en la sesión de revisión final se usaron Claude Sonnet 5 y Claude Opus 5.5.
- **Alcance de esta declaración:** trabajo de pulido y ajustes sobre la maqueta `BookWho?` (Kivy/KivyMD), correspondiente a una sesión de trabajo previa a la presentación de la evaluación E2. El dominio, las pantallas base y el flujo principal de la app ya existían de un trabajo anterior del equipo; en esta sesión se usó IA para revisar, corregir y pulir esa base.

## Prompts / instrucciones usados (resumen cronológico)

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

## Outputs relevantes generados con IA

- **Diagnóstico de la rúbrica E2**: lectura del documento de rúbrica del curso y detección de que la fundamentación UX/UI (30% de la nota) dependía de evidencia real de usuarios que aún no existía, y de que el archivo `uso_ia.md` era obligatorio por política general del curso (no solo por la rúbrica de esta evaluación).
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

## Ajustes, correcciones y decisiones tomadas por mí sobre lo entregado por la IA

- Decidí **mantener el modelo de solicitud/oferta** tal como estaba (no agregar catálogo de vendedor), después de que la IA me explicara el trade-off.
- Elegí yo el nombre final **"BookWho?"** en vez de las opciones que propuso la IA (Hallalibro, Bibliocaza, etc.).
- Pedí **revertir** el cambio de "comunas de ejemplo" en Crear solicitud porque no era lo que quería, y la IA deshizo puntualmente solo esos archivos/líneas sin tocar el resto del trabajo.
- Definí el alcance de la función de cercanía (nivel comuna/región, sin coordenadas exactas) en vez de la alternativa con distancia en kilómetros que la IA también ofreció, por menor riesgo de datos incorrectos a un día del ensayo.
- Decidí posponer la encuesta/entrevistas de usuarios (fundamentación UX/UI) para el final, priorizando primero el pulido técnico.
- Revisé visualmente cada cambio importante corriendo la app real antes de aceptarlo.
- Ante la reputación de vendedor que no existía, elegí **no implementarla a última hora** y declararla como próximo paso (opción B), para que la fundamentación coincida con lo que muestra la demo.
- Decidí reescribir con nuestras propias palabras el texto de la presentación, usando como base la versión corregida.
- Hago yo los commits, después de revisar los cambios.

## Reflexión personal

Esta fue la primera vez que usé un asistente de IA de forma tan integrada al flujo de desarrollo, no solo para pedir código suelto sino para iterar sobre una app que ya existía. Lo que más me sirvió fue que la IA no se limitó a "hacer lo que pedí": cuando le pedí un cambio de color se dio cuenta sola de que había un bug real en las tarjetas del panel de administrador (KivyMD estaba ignorando los colores personalizados) y lo arregló antes de seguir. Eso me hizo entender que no basta con mirar la pantalla y decir "se ve bien", hay que entender por qué algo se ve como se ve.

También aprendí que la IA puede equivocarse de foco si uno no la corrige a tiempo: en un momento probó agregar más ciudades de ejemplo en el selector de ubicación y a mí no me convenció el resultado, así que le pedí volver atrás. Que pudiera deshacer justo esa parte sin romper el resto del trabajo me hizo confiar más en pedir cambios sin miedo a "perder" lo que ya estaba bien.

Lo que más tuve que revisar por mi cuenta fueron las decisiones de producto: el nombre de la app, si agregábamos o no un catálogo para vendedores, y hasta qué nivel de precisión le poníamos a la ubicación. La IA proponía alternativas con sus ventajas y riesgos, pero la decisión final siempre fue mía, sobre todo pensando en el tiempo que quedaba antes del ensayo con el profesor.

Mi mayor aprendizaje fue que usar IA bien no es "que te resuelva todo", sino tener claro qué le estoy pidiendo, por qué, y revisar el resultado en la app real antes de darlo por bueno. También me quedó claro que la parte más importante de esta evaluación (la fundamentación con usuarios reales) es algo que la IA no puede inventar por mí, y que la dejé pendiente a propósito para no caer en la tentación de rellenarla con datos que no existen.
