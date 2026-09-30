# Declaración de uso de Inteligencia Artificial

## Herramienta y modelo

- **Herramienta:** Claude Code (Anthropic), CLI de asistencia para desarrollo de software.
- **Modelo:** Claude Sonnet 5.
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

## Outputs relevantes generados con IA

- **Diagnóstico de la rúbrica E2**: lectura del documento de rúbrica del curso y detección de que la fundamentación UX/UI (30% de la nota) dependía de evidencia real de usuarios que aún no existía, y de que el archivo `uso_ia.md` era obligatorio por política general del curso (no solo por la rúbrica de esta evaluación).
- **Corrección de un bug real de interfaz**: las tarjetas de métricas del panel de administrador no mostraban colores diferenciados por falta de `theme_bg_color: "Custom"` en KivyMD 2.0; se corrigió en `libros.kv` y se verificó con capturas antes/después.
- **Rediseño visual**: cambio de paleta de color (Teal → dorado envejecido/"darkgoldenrod", derivado con Material You), tipografía serif (Lora, con licencia OFL) para títulos y encabezados, y una marca propia (ícono de libro + insignia "?") para reemplazar el ícono genérico inicial.
- **Función de cercanía vendedor–lector**: `proximity_label()` en `locations.py`, que compara comuna/región del vendedor con la de la solicitud (sin exponer direcciones exactas), más el campo "comuna" agregado al registro de vendedores.
- **Aclaraciones de texto en la interfaz** para que quede explícito que el modelo es "el lector publica lo que busca, el vendedor responde" (no un catálogo de inventario).
- Ejecución de la suite de pruebas (`python -m unittest discover -s tests -v`) después de cada cambio relevante.

## Ajustes, correcciones y decisiones tomadas por mí sobre lo entregado por la IA

- Decidí **mantener el modelo de solicitud/oferta** tal como estaba (no agregar catálogo de vendedor), después de que la IA me explicara el trade-off.
- Elegí yo el nombre final **"BookWho?"** en vez de las opciones que propuso la IA (Hallalibro, Bibliocaza, etc.).
- Pedí **revertir** el cambio de "comunas de ejemplo" en Crear solicitud porque no era lo que quería, y la IA deshizo puntualmente solo esos archivos/líneas sin tocar el resto del trabajo.
- Definí el alcance de la función de cercanía (nivel comuna/región, sin coordenadas exactas) en vez de la alternativa con distancia en kilómetros que la IA también ofreció, por menor riesgo de datos incorrectos a un día del ensayo.
- Decidí posponer la encuesta/entrevistas de usuarios (fundamentación UX/UI) para el final, priorizando primero el pulido técnico.
- Revisé visualmente cada cambio importante corriendo la app real antes de aceptarlo.

## Reflexión personal

Esta fue la primera vez que usé un asistente de IA de forma tan integrada al flujo de desarrollo, no solo para pedir código suelto sino para iterar sobre una app que ya existía. Lo que más me sirvió fue que la IA no se limitó a "hacer lo que pedí": cuando le pedí un cambio de color se dio cuenta sola de que había un bug real en las tarjetas del panel de administrador (KivyMD estaba ignorando los colores personalizados) y lo arregló antes de seguir. Eso me hizo entender que no basta con mirar la pantalla y decir "se ve bien", hay que entender por qué algo se ve como se ve.

También aprendí que la IA puede equivocarse de foco si uno no la corrige a tiempo: en un momento probó agregar más ciudades de ejemplo en el selector de ubicación y a mí no me convenció el resultado, así que le pedí volver atrás. Que pudiera deshacer justo esa parte sin romper el resto del trabajo me hizo confiar más en pedir cambios sin miedo a "perder" lo que ya estaba bien.

Lo que más tuve que revisar por mi cuenta fueron las decisiones de producto: el nombre de la app, si agregábamos o no un catálogo para vendedores, y hasta qué nivel de precisión le poníamos a la ubicación. La IA proponía alternativas con sus ventajas y riesgos, pero la decisión final siempre fue mía, sobre todo pensando en el tiempo que quedaba antes del ensayo con el profesor.

Mi mayor aprendizaje fue que usar IA bien no es "que te resuelva todo", sino tener claro qué le estoy pidiendo, por qué, y revisar el resultado en la app real antes de darlo por bueno. También me quedó claro que la parte más importante de esta evaluación (la fundamentación con usuarios reales) es algo que la IA no puede inventar por mí, y que la dejé pendiente a propósito para no caer en la tentación de rellenarla con datos que no existen.
