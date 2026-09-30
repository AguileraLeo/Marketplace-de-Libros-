# Declaración de uso de Inteligencia Artificial

## Herramienta y modelo

- **Herramienta:** Claude Code (Anthropic), CLI de asistencia para desarrollo de software.
- **Modelo:** Claude Sonnet 5.
- **Alcance de esta declaración:** trabajo de pulido y ajustes sobre la maqueta `BookWho?` (Kivy/KivyMD), correspondiente a una sesión de trabajo previa a la presentación de la evaluación E2. El dominio, las pantallas base y el flujo principal de la app ya existían de un trabajo anterior del equipo; en esta sesión se usó IA para revisar, corregir y pulir esa base.

## Prompts / instrucciones usados (resumen cronológico)

1. Consulta sobre cómo sincronizar la rama `develop` del repositorio (comandos git).
2. Pedido de auditoría inicial del proyecto y del material del ramo, para construir un MVP de compra/venta de libros de forma iterativa.
3. "¿Ponytail está funcionando?" — verificación de que el modo de trabajo minimalista estaba activo.
4. "Hagamos todos los rápidos [arreglos], para el nombre tengo ideas... cacería, cazadores, buscadores de tesoros..." — pedido de nombres para la app siguiendo un concepto de "búsqueda/hallazgo".
5. "¿'BookWho?' qué te parece como nombre?" y confirmación de ese nombre.
6. "Pulamos el código, el estilo de la app, las funciones y la experiencia de usuario, hagamos algo espectacular."
7. "Ábrela para que la vea" (ejecución real de la app en pantalla para revisar visualmente cada cambio).
8. Pedido de cambiar el subtítulo del login a "Ofrece, busca, vende e intercambia".
9. "Usemos íconos de Kivy para darle otro estilo a la app, una tipografía distinta y que no se vea tan IA."
10. "¿Cómo agrego un libro siendo vendedor y siendo comprador? No veo una opción solo para buscar" — duda sobre el modelo de negocio (solicitud vs. catálogo).
11. "¿Podemos agregar la ubicación real [al buscar], para que el vendedor sepa qué tan lejos está el lector? El lector no necesita dar su ubicación exacta, puede ser un punto de referencia."
12. "En el mapa no puedo poner Temuco, Padre Las Casas no me da esa opción, ¿podemos tener todas las opciones o no?"
13. "Volvamos a cómo estábamos" (reversión puntual de un cambio de UI que no convenció).
14. "¿Cuánto de uso [de contexto] te queda?"
15. "¿Cuánto de la rúbrica cubrimos?"

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
