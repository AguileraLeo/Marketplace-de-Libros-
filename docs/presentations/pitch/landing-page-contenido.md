# BookWho? — Estrategia de contenido para la landing page

> **Documento de trabajo · versión 1.0 · octubre 2026**
> Base analizada: `AGENTS.md`, `DOCUMENTACION.md`, `FUNDAMENTACION-UX-UI.md`, `README.md`, `pitch/id_visual_icono.md`, las capturas de `screenshots/` y la página `presentacion.html`.
> No contiene código: define **qué se dice, en qué orden y con qué prueba visual**. Es la base para diseñar la landing.

---

## 0. Punto de partida y decisión previa

### 0.1 Qué es hoy la página y qué debe llegar a ser

`presentacion.html` es una **página de proyecto académico**: explica el stack, las pruebas, la arquitectura y el estado del MVP. Le habla a quien evalúa el trabajo, no a quien tiene el problema. La nueva landing debe invertir el destinatario: hablarle al lector y al vendedor, y usar la evidencia y las capturas **como prueba**, no como argumento central.

| Activo existente | Cómo está hoy | Cómo se reutiliza |
|---|---|---|
| `presentacion.html` | Relato técnico y académico, buen sistema visual | Se conserva la estética editorial; se reescribe el relato de producto |
| Encuesta propia (18 respuestas) | Sección de evidencia con gráficos | Se convierte en la prueba del problema, en la sección "No falta el libro" |
| 4 capturas (`screenshots/`) | Tomas de ventana de 800×600 | Se reemplazan por capturas en formato teléfono y alta densidad |
| Marca actual (cuadrado + libro + insignia "?") | Resuelta en CSS, sin archivo vectorial | Se necesita un lockup SVG horizontal antes de diseñar |
| `pitch/id_visual_icono.md` | Brief creativo consolidado | Define los criterios de tono, símbolo y paleta |

### 0.2 La idea rectora

> **La búsqueda se invierte.**
> El lector deja de recorrer catálogos y publica lo que busca; el libro llega como respuesta.

Todo el contenido de la página se ordena alrededor de ese cambio de dirección. Si una sección no ayuda a entenderlo o a creerlo, no pertenece a la landing.

### 0.3 La pregunta de marca

El nombre ya contiene el brief: **BookWho?** significa *¿quién tiene el libro que buscas?* La página puede usar esa pregunta como hilo conductor: abre con ella, la responde en "Cómo funciona" y la cierra con la acción.

### 0.4 Decisión que hay que tomar antes de escribir el hero

La landing no puede prometer lo mismo en dos etapas distintas. Hay que elegir un modo y no mezclarlos:

| Modo | Cuándo aplica | CTA principal | Qué debe quedar claro |
|---|---|---|---|
| **A · Presentación (hoy)** | Evaluación, portafolio, demo con el equipo | "Ver la demo" | Es una maqueta funcional, con cuentas de prueba |
| **B · Lanzamiento** | Cuando exista app pública y registro real | "Publicar mi búsqueda" | Cualquiera puede publicar y recibir ofertas |

**Recomendación:** diseñar la estructura del modo B (que es la que vende), pero dejar el CTA del modo A hasta que exista producto público. El botón cambia de texto, no de lugar ni de jerarquía. Así la página no se rediseña dos veces.

### 0.5 La promesa

> Encontrar un libro deja de ser una recorrida y pasa a ser una respuesta.

---

## 1. Propuesta de valor y posicionamiento

### 1.1 El producto en una frase

**Versión principal (para la landing):**

> **BookWho? es el marketplace de libros donde publicas lo que buscas y los vendedores que lo tienen te responden con una oferta.**

**Versión corta (para titulares y presentaciones):**

> Publicas el libro que buscas. Quien lo tiene, te responde.

**Versión de categoría (para prensa, pitch o footer):**

> Plataforma de búsqueda de libros bajo demanda: la demanda se publica y la oferta llega.

**Versión de una línea para el equipo:**

> Es un clasificado al revés: en vez de que el vendedor publique y el lector recorra, el lector publica y el vendedor responde.

### 1.2 El problema

La landing debe nombrar el problema mejor de lo que el usuario podría hacerlo. No es "faltan libros": es que **la oferta y la demanda no se ven**.

| Capa | Qué pasa en la realidad | Cómo se siente |
|---|---|---|
| **El libro no aparece** | Está agotado, descatalogado, es una edición puntual o de segunda mano | "Ese libro no existe" |
| **Encontrarlo cuesta** | Tienda por tienda, grupo por grupo, feria por feria | "Se me va la tarde" |
| **No se sabe quién lo tiene** | La oferta existe, pero está dispersa y fuera de catálogo | "No sé a quién preguntar" |

**Hallazgo que sostiene todo el relato:** el problema no es la falta de oferta, es la falta de encuentro. Las razones que dieron los encuestados apuntan a la visibilidad más que al stock: "no encuentro el libro" (6), "no sé qué vendedores lo tienen" (5) y "hay demasiados resultados" (5).

**Titular recomendado para esta sección:**

> **No falta el libro. Falta saber quién lo tiene.**

**Evidencia que se puede mostrar (real, de la encuesta propia):**

> En una encuesta a 18 lectores y vendedores (septiembre de 2026), **17 de 18 (94,4 %)** buscaron un libro específico y no lo encontraron. **14 de 18 (77,8 %)** dedicaron 15 minutos o más, y 6 de ellos más de una hora.

*Nota de honestidad:* es una muestra pequeña y exploratoria. Presentarla como "lo que escuchamos", nunca como "estudio de mercado" ni como porcentaje de la población.

### 1.3 A quién va dirigido

La página habla a dos personas con el mismo problema visto desde lados opuestos. El error más común sería escribir solo para el lector.

|  | **Lector** | **Vendedor** |
|---|---|---|
| **Quién es** | Jóvenes y adultos: 10 de 18 tienen entre 18 y 24 años y 7 tienen 35 o más; estudiantes, lectores frecuentes, quien busca un regalo o completa una colección | Librería de viejo, feria, particular con libros en casa |
| **Lo que dice** | "Lo vi una vez y no lo vuelvo a encontrar" | "Tengo libros que nadie ve" |
| **Lo que necesita** | Que alguien le diga "lo tengo" | Que alguien le diga "lo busco" |
| **Lo que teme** | Perder tiempo y exponer sus datos | Publicar y que nadie lo vea |
| **Qué valora** | Precio, estado, cercanía | Que la solicitud sea real y concreta |
| **CTA que le corresponde** | Publicar mi búsqueda | Ver solicitudes abiertas |

**A quién no le habla la página (y está bien):**

- Quien busca un best seller que está en cualquier tienda: no necesita el modelo.
- Quien quiere pagar con tarjeta dentro de la app: no es lo que hace el MVP.
- Quien espera chat, envío y seguimiento: eso llega en una etapa posterior.

### 1.4 Posicionamiento

**Declaración de posicionamiento:**

> Para lectores que ya recorrieron catálogos y para vendedores con libros sin vitrina, BookWho? es el lugar donde la búsqueda se publica y la oferta llega. A diferencia de los marketplaces de catálogo, aquí no revisas inventario: recibes respuestas de quien tiene el libro.

**Marco competitivo:**

| Alternativa | Lo que ofrece | Por qué no basta |
|---|---|---|
| Catálogos y grandes tiendas | Stock amplio y compra inmediata | Solo existe lo que está en catálogo; el libro puntual no aparece |
| Clasificados y grupos de compraventa | Oferta de particulares | El vendedor publica al vacío; el aviso caduca y el lector no lo encuentra |
| Ferias y librerías de viejo | Probabilidad real de hallazgo | Es presencial, sin búsqueda ni visibilidad |
| **BookWho?** | La demanda se publica y activa la oferta | No procesa pagos ni envíos: el trato es directo entre las partes |

**Frase de contraste para usar en la página:**

> Los catálogos te muestran lo que hay. BookWho? te muestra **quién lo tiene**.

### 1.5 Los tres pilares del mensaje

| Pilar | Mensaje | Prueba dentro del producto |
|---|---|---|
| **Encuentro** | "El libro correcto, con la persona que lo tiene." | Búsqueda por API, solicitud publicada, ofertas reales |
| **Control** | "Tú decides el precio, el estado y la entrega." | Precio máximo, condición aceptada, preferencia de entrega |
| **Confianza** | "Tu contacto aparece cuando tú decides." | Contacto oculto hasta coordinar, moderación con motivo |

### 1.6 Lo que el producto no hace (y cómo decirlo sin que suene a carencia)

| No hace | Cómo se dice en la página |
|---|---|
| No procesa pagos | "La compra se coordina directamente entre lector y vendedor." |
| No tiene chat interno | "Hablas con la persona: teléfono, correo o punto de encuentro." |
| No gestiona envíos | "Tú eliges cómo recibirlo: presencial o envío." |
| No exige catálogo al vendedor | "No necesitas inventario: respondes a lo que ya están buscando." |
| No tiene reputación ni calificaciones (aún) | **No se menciona.** Queda como próximo paso, no como promesa |

**Claims prohibidos hasta que exista respaldo:** "miles de libros", "gratis", "sin comisiones", "vendedores verificados", "pago seguro", "garantizado", testimonios inventados. Si se necesita una cifra, usar solo las de la encuesta y con su base visible.

---

## 2. Copywriting del Hero

### 2.1 Objetivo del hero

Que en cinco segundos el visitante entienda tres cosas: **qué cambia** (tú publicas, ellos responden), **para quién es** (lector y vendedor) y **qué hacer ahora** (un solo botón primario). El hero no explica el producto completo: hace inevitable la siguiente sección.

### 2.2 Versión recomendada (copy listo para usar)

> **Antetítulo**
> ¿QUIÉN TIENE EL LIBRO QUE BUSCAS?
>
> **Titular**
> **Deja de recorrer tiendas. Publica el libro que buscas.**
>
> **Subtítulo**
> BookWho? invierte la búsqueda: cuentas qué libro necesitas y los vendedores que lo tienen te envían una oferta. Comparas precio, estado y cercanía, y coordinas directo con la persona.
>
> **Botón primario**
> Ver la demo
>
> **Botón secundario**
> Cómo funciona
>
> **Enlace terciario**
> Tengo libros para vender →
>
> **Microcopy bajo los botones**
> Demo funcional con cuentas de prueba.

**Por qué funciona:**

- El titular tiene dos frases cortas (cuatro y cinco palabras): una quita el dolor, la otra da la acción. Se lee en una pasada y se recuerda.
- "Tiendas" es concreto; "catálogos" es abstracto y suena a jerga de producto.
- El subtítulo explica el mecanismo en el orden en que ocurre: publicas → recibes → comparas → coordinas.
- El antetítulo usa la pregunta del nombre: conecta marca y mensaje sin explicar el juego de palabras.

### 2.3 Alternativas de titular

| # | Titular | Cuándo usarlo | Riesgo |
|---|---|---|---|
| **A** | **Deja de recorrer tiendas. Publica el libro que buscas.** | Recomendado para la landing | Ninguno relevante |
| B | Publica el libro que buscas. Que te lo ofrezcan a ti. | Continuidad con `presentacion.html` | La segunda frase es pasiva y más larga |
| C | El libro que buscas no está en un catálogo. Está en manos de alguien. | Campañas, anuncios, imagen para redes | Largo para un H1 en móvil |
| D | Tú pides el libro. Alguien lo tiene. | Versión mínima para móvil o publicidad | Puede sonar a pedido de comida a domicilio |
| E | ¿Quién tiene el libro que buscas? | Antetítulo, no titular | No dice qué hacer |
| F | Deja de recorrer tiendas. Cuenta qué libro buscas. | Público mayor o poco técnico; tono más cálido | "Cuenta" suaviza la acción y pierde algo de empuje |

**Recomendación:** A como titular; E como antetítulo. B se conserva como variante de bajo riesgo si se quiere mantener continuidad con la página actual.

### 2.4 Alternativas de subtítulo

| Versión | Texto | Cuándo usarla |
|---|---|---|
| **S1 (recomendada)** | BookWho? invierte la búsqueda: cuentas qué libro necesitas y los vendedores que lo tienen te envían una oferta. Comparas precio, estado y cercanía, y coordinas directo con la persona. | Landing completa |
| S2 | Cuéntanos qué libro buscas. Quien lo tenga, te lo ofrece. Tú eliges con quién coordinar. | Versión corta y más humana, ideal para móvil |
| S3 | Publica el libro que buscas y recibe ofertas de librerías y lectores que lo tienen. Sin catálogos infinitos ni tienda por tienda. | Cuando se quiera nombrar a ambos tipos de vendedor |
| S4 | Alguien está buscando justo el libro que tienes. BookWho? te muestra esas solicitudes y te deja responder con una oferta. | Versión para la audiencia vendedor |

**Regla:** un subtítulo, no dos. Si se necesita explicar más, se hace en la sección "Cómo funciona".

### 2.5 Llamados a la acción (CTAs)

| Nivel | Texto | Destino | Cuándo |
|---|---|---|---|
| **Primario** | Ver la demo | Video de 60–75 segundos | Modo presentación (hoy) |
| **Primario** | Publicar mi búsqueda | Registro de lector | Modo lanzamiento |
| **Secundario** | Cómo funciona | Ancla a la sección de pasos | Siempre |
| **Terciario (enlace)** | Tengo libros para vender → | Sección de vendedores | Siempre |
| **Cierre de página** | Publicar mi búsqueda | Registro / demo | Siempre |

**Variantes que funcionan:**

- "Explorar la demo" (más exploratorio, menos compromiso).
- "Verlo funcionando" (más conversacional; sirve para un público no técnico).
- "Quiero vender" (directo, para la sección de vendedores).
- "Ver solicitudes abiertas" (específico del vendedor; mucho mejor que "Empezar").

**Reglas de escritura para botones:**

- Verbo + objeto, máximo cuatro palabras, sentence case.
- Un solo botón relleno por pantalla; el secundario va con borde o como enlace.
- Nada de "Haz clic aquí", "Enviar", "Más información".
- El texto del botón debe coincidir con lo que ocurre después. Si dice "Ver la demo", abre un video; si dice "Publicar", abre el formulario.

**Microcopy permitido hoy:** "Demo funcional con cuentas de prueba."
**Microcopy a evitar:** "Es gratis", "Sin registro", "Toma menos de un minuto" (no está verificado y el registro sí existe).

### 2.6 Reglas de implementación del hero

- Titular de 8–12 palabras; máximo dos líneas en escritorio y tres en móvil.
- Sin carrusel y sin video con sonido automático.
- La pregunta del antetítulo no se repite en el titular.
- "BookWho?" siempre con el signo de interrogación; evitar terminar una frase con el nombre (queda "BookWho?.").
- No usar "marketplace inverso" en el hero: es jerga. Reservarlo para prensa o pitch.

---

## 3. Características clave / beneficios

### 3.1 Criterio de selección

Se eligen los cuatro módulos que sostienen el circuito completo y que **se pueden ver en la demo**. La administración y la moderación no son una característica de usuario: son una prueba de confianza y van en una franja aparte.

La página actual tiene seis tarjetas técnicas. La nueva landing las consolida así:

| Hoy (`presentacion.html`) | Nueva landing |
|---|---|
| Búsqueda con respaldo | **01 · La edición exacta** |
| Solicitudes y ofertas + Negociación real | **02 · Tú pones las condiciones** y **03 · Decide con todo a la vista** |
| Cercanía por comuna | **04 · Vende sin mantener un catálogo** |
| Permisos por rol + Panel de administración | **Franja de confianza** (no es feature) |

**Titular de la sección:**

> **Menos búsqueda. Más encuentro.**

### 3.2 Característica 01 — La edición exacta

> **Antetítulo:** BÚSQUEDA CON DATOS REALES
>
> **Nombre:** La edición exacta, no una parecida
>
> **Descripción:**
> Busca por título, autor o ISBN y elige entre portadas y ediciones reales. Los datos vienen de Google Books y Open Library, así que no escribes una ficha a mano ni dudas si es el ejemplar correcto.
>
> **Versión corta (tarjeta):**
> Título, autor o ISBN, con portadas y datos reales. Eliges la edición correcta, no la que se le parece.
>
> **Beneficio en una línea:** Encuentras el libro correcto sin escribir una ficha.

- **Qué la prueba:** la pantalla de búsqueda con el selector Título / Autor / ISBN, el spinner y los resultados con portadas.
- **Qué no prometer:** "todas las ediciones del mundo". Los datos dependen de las APIs y del catálogo de respaldo.

### 3.3 Característica 02 — Tú pones las condiciones

> **Antetítulo:** LA SOLICITUD
>
> **Nombre:** Tú pones las condiciones
>
> **Descripción:**
> Fija un precio máximo si quieres, el estado que aceptas, tu comuna y cómo prefieres recibir el libro. Tu búsqueda se publica con tus reglas, y los vendedores saben exactamente qué necesitas.
>
> **Versión corta (tarjeta):**
> Precio máximo, condición, comuna y entrega. Publicas tu búsqueda con tus reglas, no con las de la tienda.
>
> **Beneficio en una línea:** Pides lo que necesitas, no lo que hay.

- **Qué la prueba:** el formulario de creación con los selectores de condición y comuna, y la confirmación "Tu solicitud está publicada" con los tres pasos de "Qué sigue".
- **Qué no prometer:** que el vendedor respetará el precio máximo. Es una referencia, no una garantía.

### 3.4 Característica 03 — Decide con todo a la vista

> **Antetítulo:** LAS OFERTAS
>
> **Nombre:** Decide con todo a la vista
>
> **Descripción:**
> Cada oferta llega con precio, estado del libro y quién lo vende. Comparas en una sola vista y aceptas cuando te convence: el contacto del vendedor aparece solo en ese momento.
>
> **Versión corta (tarjeta):**
> Precio, condición y vendedor, lado a lado. Aceptas cuando te convence y el contacto aparece recién ahí.
>
> **Beneficio en una línea:** Eliges con información, no por descarte.

- **Qué la prueba:** el detalle de solicitud con varias ofertas, el aviso de contacto oculto y la pantalla de oferta aceptada con los datos revelados.
- **Qué no prometer:** calificaciones, reputación o "vendedores verificados". No existen en el MVP.
- **Matiz que sí conviene contar:** si el lector acepta una oferta y luego desiste, las demás no se pierden: vuelven a estar activas. Es una decisión de producto real y genera confianza.

### 3.5 Característica 04 — Vende sin mantener un catálogo

> **Antetítulo:** PARA QUIEN TIENE LOS LIBROS
>
> **Nombre:** Vende sin mantener un catálogo
>
> **Descripción:**
> Mira las solicitudes abiertas, filtra por comuna, presupuesto y condición, y ofrece el libro que ya tienes. Sin inventario que actualizar ni avisos que nadie ve.
>
> **Versión corta (tarjeta):**
> El feed te muestra qué están buscando cerca de ti. Filtras, ofreces y vendes el libro que ya tienes.
>
> **Beneficio en una línea:** Cada solicitud ya está buscando lo que tienes.

- **Qué la prueba:** el inicio del vendedor con los filtros y la insignia de cercanía ("Misma comuna", "Misma región"), y el formulario de oferta.
- **Qué no prometer:** volumen de solicitudes ni "miles de lectores". Decir "solicitudes abiertas" y, en producción, "solicitudes reales cerca de ti".

### 3.6 Franja de confianza (apoyo, no característica)

> **Antetítulo:** SEGURIDAD
>
> **Titular:** La confianza también se diseña
>
> - **Tu contacto, bajo control.** El teléfono, el correo y el punto de encuentro se revelan cuando aceptas coordinar.
> - **Moderación con motivo.** El equipo administrador puede suspender cuentas y cancelar publicaciones dejando registro.
> - **Todo a la vista.** Cada solicitud y cada oferta muestran en qué paso están.

**Por qué esta franja existe:** la confianza fue la principal exigencia de la encuesta (calificaciones 13 de 18, verificación 12, pago seguro 10, protección de datos 9). La página no puede resolver lo que el producto no tiene, pero sí puede mostrar lo que sí hace: proteger el contacto y moderar.

### 3.7 Traducción de lenguaje técnico a lenguaje de landing

| Hoy suena a ingeniería | En la landing suena a beneficio |
|---|---|
| "Búsqueda con respaldo: Google Books → Open Library → catálogo local" | "La edición exacta, con datos reales" |
| "Máquina de estados completa" | "Sabes en qué paso está cada solicitud" |
| "Negociación real: las demás quedan en espera" | "Si desistes, las otras ofertas no se pierden" |
| "Cercanía por comuna" | "Solicitudes cerca de ti, sin exponer direcciones" |
| "Permisos por rol revalidados en el dominio" | "Cada persona ve y hace solo lo que le corresponde" |
| "Panel de administración con auditoría exportable" | "Moderación activa y registro de lo que pasa" |

**Regla:** ninguna palabra del stack (Kivy, KivyMD, Python, API, dominio, estado) aparece en la landing de producto. Si se necesita para la evaluación, va en una nota al pie o en una sección "Detrás de BookWho?" al final, separada del relato.

---

## 4. Elementos de apoyo visual y narrativo

### 4.1 Arco narrativo de la página

| # | Sección | Pregunta que responde | Mensaje | Prueba visual | CTA |
|---|---|---|---|---|---|
| 1 | **Hero** | ¿Qué es esto? | La búsqueda se invierte | Video en loop del momento en que llega una oferta | Ver la demo |
| 2 | **El problema** | ¿Me pasa a mí? | No falta el libro: falta saber quién lo tiene | Dato 94,4 % + relato breve | — |
| 3 | **Cómo funciona** | ¿Cómo funciona? | Publicas una vez, te responden, coordinas | Tres capturas: solicitud, ofertas, contacto | — |
| 4 | **Para lectores** | ¿Qué gano? | La edición exacta, tus condiciones, todo a la vista | Búsqueda, formulario, ofertas | Publicar mi búsqueda |
| 5 | **Para vendedores** | ¿Y si tengo libros? | Alguien ya está buscando lo que tienes | Feed con cercanía y formulario de oferta | Ver solicitudes abiertas |
| 6 | **Confianza** | ¿Es seguro? | Tu contacto aparece cuando tú decides | Aviso de contacto oculto + panel de admin | — |
| 7 | **Cierre** | ¿Empiezo? | Tu próxima búsqueda empieza publicando | Marca + pregunta | Publicar mi búsqueda |

**Titulares de sección recomendados:**

1. Hero: *Deja de recorrer tiendas. Publica el libro que buscas.*
2. Problema: *No falta el libro. Falta saber quién lo tiene.*
3. Cómo funciona: *Publicas una vez. Te responden. Coordinas.*
4. Para lectores: *Menos búsqueda. Más encuentro.*
5. Para vendedores: *¿Tienes libros? Alguien ya los está buscando.*
6. Confianza: *Tu contacto aparece cuando tú decides.*
7. Cierre: *Tu próxima búsqueda empieza publicando.*

### 4.2 Capturas recomendadas por sección

| Momento | Pantalla en la app | Qué debe verse | Sección |
|---|---|---|---|
| Inicio del lector | `ReaderHomeScreen` | Saludo, buscador, cifras y solicitudes recientes | Hero |
| Búsqueda | `BookSearchScreen` | Selector Título / Autor / ISBN y resultados con portadas | Para lectores · La edición exacta |
| Crear solicitud | `CreateRequestScreen` | Condición, comuna y preferencia de entrega | Para lectores · Tú pones las condiciones |
| Solicitud publicada | `RequestPublishedScreen` | Check, número y los tres pasos de "Qué sigue" | Cómo funciona |
| Ofertas recibidas | `ReaderRequestDetailScreen` | Dos o tres ofertas con precio y condición | Para lectores · Decide con todo a la vista |
| Detalle de oferta | `OfferDetailScreen` | Aviso de que el contacto se verá al aceptar | Confianza |
| Oferta aceptada | `OfferAcceptedScreen` | Contacto revelado + aviso de coordinación externa | Confianza |
| Inicio del vendedor | `SellerHomeScreen` | Filtros, solicitudes e insignia de cercanía | Para vendedores |
| Crear oferta | `CreateOfferScreen` | Precio, condición y datos de contacto | Para vendedores |
| Panel de admin | `AdminHomeScreen` | Métricas y accesos | Confianza (secundaria) |

**Producción de capturas (importante):**

- Las actuales son tomas de ventana de 800×600; la app corre en 420×860. No sirven como mockup de teléfono en alta densidad.
- Volver a capturar a 3× (1260×2580) o recortar la ventana y montarla en un marco de teléfono fino.
- Fondo crema `#FBFAF7`, sin barra de tareas, sin cursor en las imágenes fijas y sin credenciales de demo visibles.
- Usar portadas reales y títulos reconocibles (El Hobbit, Cien años de soledad, 1984): comunican "esto ya funciona".
- Evitar estados vacíos y placeholders en las capturas del hero.
- Las credenciales de demo van en un bloque aparte, no dentro de la captura.

### 4.3 Micro-interacciones que conviene mostrar

| Interacción | Dónde | Por qué mostrarla |
|---|---|---|
| El selector Título / Autor / ISBN cambia el texto guía | Característica 01 | Demuestra que la búsqueda se adapta, no que es un formulario genérico |
| Spinner real durante la búsqueda | Característica 01 | Honestidad: los datos vienen de una API, no de una lista fija |
| Punto de color + texto en cada estado | Toda la app | Los estados se leen sin depender solo del color |
| Revelado del contacto al aceptar | Confianza | Convierte la privacidad en un gesto visible |
| Check y "Qué sigue" tras publicar | Cómo funciona | Reduce la ansiedad de "¿y ahora qué?" |
| Insignia "Misma comuna / Misma región" | Vendedores | Cercanía sin exponer direcciones |
| Una oferta pasa de "en espera" a "activa" | Característica 03 | Explica que las oportunidades no se pierden |
| Métricas del panel de admin | Confianza | Muestra que hay supervisión real |

### 4.4 Video grabado con OBS

La app es una ventana de 420×860: grabar en vertical es lo natural. Se necesitan **tres clips**, no uno.

#### Clip A — Loop del hero (9–12 segundos, vertical, sin audio)

No mostrar la búsqueda: mostrar **la llegada de la oferta**, que es lo diferencial.

| Tiempo | Acción en pantalla |
|---|---|
| 0–3 s | Detalle de solicitud con tres ofertas; el cursor recorre precio y condición |
| 3–6 s | Abre una oferta; se ve el aviso de que el contacto está oculto |
| 6–9 s | Acepta para coordinar; el contacto aparece |
| 9–12 s | Plano fijo del contacto y el aviso de coordinación externa; fundido al inicio |

- Formato 1080×2160 (para que la ventana 1:2,05 entre sin recortes), 60 fps, H.264, menos de 5 MB, autoplay silenciado y en loop.
- Sin música ni voz: es un loop de apoyo, no un anuncio.
- Elegir un frame de poster que muestre el momento del contacto.

#### Clip B — Circuito completo (60–75 segundos, horizontal)

| Tramo | Contenido | Recurso |
|---|---|---|
| 0–8 s | Placa de título con la pregunta "¿Quién tiene el libro que buscas?" | Tipografía, sin pantalla |
| 8–20 s | Lector busca "El Hobbit", selecciona y publica la solicitud | Captura real, velocidad 1× |
| 20–35 s | Vendedor filtra por comuna, abre la solicitud y crea la oferta | Corte directo entre roles |
| 35–50 s | Lector recibe la oferta, la acepta y ve el contacto | El momento clave: mantener el ritmo |
| 50–60 s | Confirma el trato; cierre con la marca y el CTA | Placa final |

#### Clip C — Camino del vendedor (20–25 segundos, vertical)

Feed → filtro por comuna → detalle con cercanía → crear oferta → "Mis ofertas". Sirve para la sección de vendedores y para redes.

#### Especificaciones y checklist de grabación

- Resolución: 1080×2160 (vertical, para la ventana 1:2,05) y 1920×1080 (horizontal); grabar a 60 fps y exportar a 30 fps si el peso importa.
- Exportar MP4 H.264 y WebM; nada de GIF.
- Captura de ventana, no de pantalla completa; ocultar barra de tareas y notificaciones.
- Reiniciar la app antes de cada toma: los datos vuelven al estado inicial.
- Usar las mismas cuentas, el mismo libro y el mismo precio en los tres clips.
- Subtítulos en español quemados en el video (se ve sin sonido).
- Sin tiempos muertos de más de un segundo; cortes directos, sin transiciones llamativas.
- No inventar datos: si se muestran tres ofertas, deben existir en la demo.
- Revisar que no aparezcan contraseñas, correos personales ni la consola.

### 4.5 Tono de voz

**Definición:** el de alguien que ya entendió el problema y no necesita gritar. **Cercano y preciso, con la calma de una librería y la claridad de una buena interfaz.**

En los adjetivos de siempre: **profesional** sin ser corporativo, **innovador** sin ser frío, **dinámico** sin ser ansioso y **minimalista** en la forma (nunca en el contenido).

| Atributo | Suena así | No suena así |
|---|---|---|
| **Cercano** | "Cuéntanos qué libro buscas." | "Estimado usuario, ingrese su requerimiento." |
| **Claro** | "El contacto aparece cuando aceptas." | "La revelación de datos se habilita tras la aceptación." |
| **Cálido y editorial** | "Un libro, dos personas, un encuentro." | "Sinergias en el ecosistema del libro." |
| **Optimista sin hype** | "Buscar puede ser más simple." | "Revolucionamos la industria para siempre." |
| **Horizontal** | "Lectores y vendedores." | "Compradores y proveedores." |

**El tono cambia por sección; la voz no:**

| Sección | Registro |
|---|---|
| Hero | Más breve y con algo de imagen: "Deja de recorrer tiendas" |
| Problema | Directo y empático, sin dramatismo |
| Características | Concreto, con verbos de acción |
| Confianza | Sereno y transparente, sin tecnicismos |
| FAQ | Llano, casi conversacional |
| Legal / footer | Preciso y sin adornos |

**Léxico recomendado:** libro, búsqueda, solicitud, oferta, encuentro, coordinar, comuna, vendedor, lector, tener, ofrecer, encontrar, directo.

**Léxico prohibido:** marketplace inverso (en la interfaz), disrupción, revolución, algoritmo, inteligencia artificial, potencia, sinergia, experiencia 360, usuario final, proveedor, SKU, inventario (salvo para negarlo), gratis, garantizado, miles.

**Reglas de estilo:**

- Tuteo neutro; nunca "usted" ni "vos".
- Sentence case en botones y titulares; la app ya usa mayúsculas en algunos botones ("PUBLICAR SOLICITUD"): unificar en la landing.
- Cifras en formato chileno: $15.000, 94,4 %.
- Sin emojis en la landing. La página actual los usa (🔍 📨 🤝 📍 🛡️ 📊) y rompen el tono editorial y el brief de marca.
- Frases de menos de 20 palabras; una idea por párrafo.
- "Vendedor", no "proveedor". "Persona" cuando el rol no importa.

### 4.6 Consistencia de marca (revisar antes de diseñar)

| Elemento | Estado actual | Recomendación |
|---|---|---|
| Paleta | La app usa verde `#1F4D3A` y crema `#FBFAF7`; el brief propone `#315C49`, `#F6F1E7` y terracota `#D99573` | Elegir una sola fuente de verdad; se recomienda la de la app y usar terracota solo como acento, verificando contraste |
| Tipografía | Source Serif 4 en títulos e IBM Plex Sans en texto | Mantener: es el diferencial editorial frente a otras apps |
| Logo | Cuadrado redondeado + libro + insignia "?" | Necesita lockup horizontal en SVG para web y favicon |
| Modo oscuro | Ya existe en `presentacion.html` | Conservarlo solo si las capturas y la marca funcionan en oscuro |
| Subtítulo del login | "Ofrece, busca, vende e intercambia." | "Intercambia" no es una función real: reemplazar por "Publica el libro que buscas y recibe ofertas de quienes lo tienen." |

---

## 5. Anexo: copy de producción

### 5.1 Metadatos

- **Title (55 caracteres):** BookWho? | Publica el libro que buscas y recibe ofertas
- **Meta description (133 caracteres):** Deja de recorrer tiendas: publica el libro que buscas y los vendedores que lo tienen te envían una oferta. Compara y coordina directo.
- **OG title:** ¿Quién tiene el libro que buscas? | BookWho?
- **OG description:** Publica lo que buscas y recibe ofertas de quienes tienen el libro. Sin catálogos infinitos.
- **OG image:** teléfono con la pantalla de ofertas + titular, fondo crema, 1200×630.

### 5.2 Navegación

`Cómo funciona · Para vendedores · Confianza · Preguntas` + botón `Ver la demo`

### 5.3 Preguntas frecuentes (respuestas honestas)

1. **¿La plataforma vende los libros?**
   No. BookWho? conecta: la compra y la entrega se coordinan directamente entre lector y vendedor.
2. **¿Cómo pago?**
   Fuera de la app, directo con el vendedor. Esta versión no procesa pagos.
3. **¿Cómo sé con quién hablo?**
   Cada oferta muestra el precio, el estado del libro y quién lo vende. El contacto se revela cuando aceptas coordinar.
4. **¿Puedo vender si soy particular?**
   Sí. No necesitas mantener un catálogo: respondes a las solicitudes que ya están abiertas.
5. **¿En qué ciudades funciona?**
   La demo usa un catálogo de 107 comunas de Chile. La cobertura definitiva se anunciará al lanzar.
6. **¿Mis datos son públicos?**
   No. Tu ubicación es una comuna, no una dirección, y el contacto se comparte solo al coordinar.
7. **¿Hay chat interno?**
   No. Coordinas por teléfono, correo o punto de encuentro, según lo que el vendedor comparta.

### 5.4 Cierre de página

> **Tu próxima búsqueda empieza publicando.**
> Cuéntanos qué libro buscas. Del otro lado, alguien puede tenerlo.
>
> [Publicar mi búsqueda] · [Tengo libros para vender →]

### 5.5 Footer

> BookWho? conecta lectores y vendedores. La compra, el pago y la entrega se coordinan directamente entre las partes.
> Proyecto académico · Desarrollo Móvil (A+S) · Uso de IA declarado en `uso_ia.md`.

---

## 6. Checklist antes de publicar

- [ ] Decidir el modo (presentación o lanzamiento) y no mezclar CTAs.
- [ ] Validar cada claim: nada de "gratis", "miles", "verificado" ni testimonios.
- [ ] Reemplazar las cuatro capturas por tomas en formato teléfono y alta densidad.
- [ ] Grabar los tres clips de OBS con los mismos datos y cuentas.
- [ ] Unificar la paleta y resolver el lockup SVG del logo.
- [ ] Quitar los emojis y el lenguaje técnico de la página de producto.
- [ ] Revisar el tono: tuteo, frases cortas, cero jerga.
- [ ] Medir: clic en el CTA primario, scroll hasta "Cómo funciona" y clic en "Tengo libros para vender".
- [ ] Probar dos titulares (A y F) con la misma página y quedarse con el de mejor clic.
- [ ] Verificar la lectura en móvil: titular en tres líneas, subtítulo en cuatro y un solo botón relleno.

---

*Fin del documento. La siguiente etapa es el wireframe de la landing con este copy fijo, no antes.*
