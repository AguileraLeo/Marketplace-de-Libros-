# Fundamentación UX/UI — BookWho?

## a) Metodología de investigación

- **Instrumento:** encuesta estructurada en Google Forms (23 preguntas: perfil, hábitos de búsqueda y compra, problemas con plataformas actuales, seguridad e interés en la app).
- **Muestra:** 18 respuestas, recogidas entre el 27 y el 28 de septiembre de 2026.
- **Participantes:** potenciales lectores y vendedores. La mayoría tiene entre 18 y 24 años (10 de 18) y el resto es mayor de 25 años (8 de 18, de los cuales 7 tienen 35 años o más). Se trata de estudiantes, lectores frecuentes y personas que compran en ferias o librerías de segunda mano.
- **Análisis:** recuento y porcentaje por pregunta. En las preguntas de selección múltiple cada opción se cuenta por separado. En las preguntas opcionales, el porcentaje se calcula sobre quienes respondieron.

## b) Resultados principales

| # | Hallazgo | Evidencia |
|---|----------|-----------|
| H1 | Casi todos han buscado un libro específico sin encontrarlo | 17 de 18 (94,4 %) |
| H2 | La búsqueda toma tiempo | 14 de 18 (77,8 %) dedicaron 15 minutos o más; 6 de ellos, más de 1 hora |
| H3 | El problema no es la falta de oferta, sino saber quién tiene el libro | "No encuentro el libro" (6), "No sé qué vendedores lo tienen" (5), "Hay demasiados resultados" (5) |
| H4 | Hay interés en el modelo de "pedir y recibir ofertas" | 14 de 16 (87,5 %) la usaría ("Sí" o "Probablemente sí"); 15 de 18 (83,3 %) la considera útil o muy útil |
| H5 | La confianza en el vendedor es la principal exigencia de seguridad | Calificaciones (13 de 18), verificación de identidad (12), pago seguro (10), protección de datos (9) y reporte de usuarios (9) |
| H6 | Los vendedores pequeños se beneficiarían | 16 de 18 creen que la app ayudaría a vendedores pequeños o independientes; 8 de 18 mencionan a los vendedores de ferias |
| H7 | Los usuarios son diversos en edad y en canales de compra | 7 de 18 tienen 35 años o más; compran en tiendas online (9), librerías tradicionales (8) y ferias (8 entre ambos tipos) |

## c) Matriz hallazgo → decisión de diseño

| Hallazgo | Decisión de interfaz | Dónde está en la app |
|----------|---------------------|----------------------|
| H1, H3 | En lugar de mostrar un catálogo gigante, la pantalla principal del lector es un formulario de búsqueda: "¿Qué libro estás buscando?" con un selector Título / Autor / ISBN, un `MDTextField` y un `MDButton` "Buscar". Debajo, dos cifras resumen (solicitudes activas y ofertas por revisar) y las solicitudes recientes con su estado | `ReaderHomeScreen` |
| H3 | Los metadatos del libro (título, autor, ISBN, portada) se obtienen de Google Books u Open Library; el lector solo elige el resultado correcto en tarjetas (`BookResultCard`) | `BookSearchScreen` |
| H3, H4 | El modelo se invierte: el lector publica una solicitud y son los vendedores quienes llegan con ofertas, para que el lector no tenga que preguntar tienda por tienda | `CreateRequestScreen` → `RequestPublishedScreen` |
| H2 | Publicar una solicitud requiere 3 acciones principales: **Buscar**, **Seleccionar** y **Publicar solicitud**, cada una en su pantalla del `ScreenManager` | Inicio → Buscar libro → Crear solicitud |
| H5 | Cada oferta se presenta en una fila (`ItemCard`, basada en `MDCard`) que muestra el vendedor, el precio y la condición del libro, para que el lector sepa con quién trata antes de decidir | `ReaderRequestDetailScreen`, `OfferDetailScreen` |
| H5 | Los datos de contacto del vendedor quedan ocultos hasta que el lector acepta la oferta para coordinar, y la pantalla lo explica | `OfferDetailScreen` → `OfferAcceptedScreen` |
| H5 | Inicio de sesión con roles, y un administrador que puede suspender usuarios y moderar solicitudes con un motivo | `LoginScreen`, `AdminUsersScreen`, `AdminRequestsScreen` |
| H6 | El vendedor no necesita mantener un catálogo: ve solicitudes reales, las filtra por ubicación, presupuesto y condición, y responde con una oferta | `SellerHomeScreen`, `CreateOfferScreen` |

**Pendientes derivados de la investigación (próximo paso):** el sistema de calificaciones de vendedores (H5, 13 de 18) y el reporte de usuarios quedaron fuera del MVP por alcance (ver `AGENTS.md` §10–11). La app tampoco procesa pagos: la compra se coordina directamente entre las partes y la pantalla lo deja explícito.

## d) Justificación de la estructura y la navegación

La app tiene tres experiencias separadas por rol, cada una con la pregunta principal de su usuario en primer plano:

- **Lector:** "¿Qué libro busco y qué pasa con mis solicitudes?". La búsqueda está arriba y las solicitudes recientes, abajo.
- **Vendedor:** "¿Quién busca un libro que yo pueda ofrecer?". La pantalla muestra un feed de solicitudes con filtros.
- **Administrador:** métricas y moderación.

El orden de las pantallas sigue el recorrido real del problema (H1–H3): buscar → elegir el libro exacto → publicar → recibir ofertas → aceptar → contactar. Así se evita el comportamiento que los usuarios reportaron (13 de 18 buscaban en internet y 7 recorrían otras librerías). La navegación usa `ScreenManager` con transiciones con dirección (avanzar hacia la izquierda y volver hacia la derecha) y una barra superior con botón de volver (`MDTopAppBar`) en las 14 pantallas internas, para que el usuario nunca quede sin salida.

## e) Diversidad y accesibilidad

Como 7 de 18 encuestados tienen 35 años o más (H7), y como la app busca sumar a vendedores de ferias y librerías pequeñas (H6), que suelen estar menos familiarizados con la tecnología:

- **Material Design con KivyMD:** se usan componentes estándar que el usuario ya reconoce de otras apps.
- **Botones grandes:** los botones de acción y las opciones de los selectores miden al menos 48 dp de alto (los principales, 52 dp), que es el mínimo táctil que recomienda Material.
- **Jerarquía tipográfica clara:** títulos en estilo `Title`, contenido en `Body` y etiquetas en `Label`. Hay una sola acción principal por pantalla, destacada como botón relleno.
- **Contraste alto:** tema claro con texto oscuro sobre fondo claro, y estados de solicitud y oferta con un punto de color acompañado de texto (no solo color).
- **Siguiente paso explícito:** al publicar, la confirmación explica en tres pasos numerados qué pasará después (recibir ofertas, comparar y aceptar, ver el contacto), para que nadie quede sin saber qué hacer.
- **Lenguaje simple y en español:** textos de acción explícitos ("Buscar", "Seleccionar", "ACEPTAR PARA COORDINAR"), un texto guía que cambia según lo que se busca ("Título del libro", "Nombre del autor", "ISBN"), mensajes que explican qué pasará (por ejemplo, cuándo se verán los datos de contacto) y validaciones con mensajes concretos ("El precio debe ser mayor que 0").
