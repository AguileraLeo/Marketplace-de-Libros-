# BookWho? — Auditoría de Marca y Dirección Creativa (Fase 1)

> **Documento de dirección estratégica, artística y de movimiento**  
> **Fecha:** Octubre 2026 · **Versión:** 1.0  
> **Framework metodológico:** UI/UX Pro Max Intelligence System  
> **Base documental auditada:** `pitch/index.html`, `presentacion.html`, `pitch/landing-page-contenido.md`, `pitch/id_visual_icono.md`, `FUNDAMENTACION-UX-UI.md`, `CONTEXTO.md`, `AGENTS.md` y activos gráficos en `pitch/`.

---

## 1. Auditoría del Estado Actual

### 1.1 Inspección Técnica y de Arquitectura de Activos

El proyecto cuenta actualmente con una landing page de presentación implementada en [`pitch/index.html`](file:///c:/Proyectos/Marketplace-de-Libros-/pitch/index.html), complementada por la página técnica original [`presentacion.html`](file:///c:/Proyectos/Marketplace-de-Libros-/presentacion.html) y el prototipo funcional en Python + KivyMD (`main.py`, `libros.kv`, `store.py`).

| Capa / Activo | Implementación actual | Diagnóstico técnico |
|---|---|---|
| **Estructura HTML** | HTML5 semántico (`header`, `main`, `section`, `details`, `footer`, `dialog/modal`). | Válido, sin etiquetas rotas ni anidamientos ilegales. |
| **Framework de Estilos** | Tailwind CSS CDN (v3.x en runtime con configuración inline). | Rápido para prototipado, pero depende de script externo; extensible con variables CSS para consistencia de tokens. |
| **Fuentes Tipográficas** | Google Fonts: `Source Serif 4` (titulares) y `IBM Plex Sans` (cuerpo/UI). | Excelente elección editorial; requiere optimización de carga (`font-display: swap`, subconjuntos latinos). |
| **Identidad Vectorial** | `pitch/logo.svg` (1774×887 px) y `pitch/icon.svg` (293×247 px). | Ambos SVG contienen internamente un fondo sólido crema (`#F7F3E5` y `#F7F2E5`). Esto genera una colisión visual si se intentan usar como vectores transparentes sobre fondos oscuros. |
| **Recursos de Demostración** | Tres grabaciones GIF en `pitch/gif/` con resolución idéntica (526×1056 px, ratio ~1:2). | Formato vertical exacto de smartphone moderno. Calidad nítida, peso moderado (2.4 MB a 4.6 MB), aptos para mockups pero demandantes de ancho de banda si cargan en simultáneo. |
| **Accesibilidad Base** | Medidas de foco visible (`focus-visible:ring`), soporte inicial de `prefers-reduced-motion`, etiquetas `aria-label`. | Buena base que requiere profundizar en navegación por teclado de modales y anuncios de estado para lectores de pantalla. |

---

### 1.2 Análisis Sección por Sección de `index.html`

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Barra de aviso demo: contextualiza el modo de evaluación    │
├─────────────────────────────────────────────────────────────────┤
│ 2. Header / Nav: Marca (icono en cápsula) + 5 enlaces + CTA     │
├─────────────────────────────────────────────────────────────────┤
│ 3. Hero: H1 exacto + Subtítulo + CTAs + Mockup Smartphone (GIF) │
├─────────────────────────────────────────────────────────────────┤
│ 4. El Problema: Cifras de encuesta (94,4 %, 77,8 %) + Contraste │
├─────────────────────────────────────────────────────────────────┤
│ 5. Cómo Funciona: 3 pasos (Publica, Recibe, Coordina)           │
├─────────────────────────────────────────────────────────────────┤
│ 6. Características Clave: 4 bloques (Búsqueda, Reglas, Ofertas, │
│    Vendedor) con mockups de teléfono y tarjetas glassmorphism   │
├─────────────────────────────────────────────────────────────────┤
│ 7. Sección Vendedores: Propuesta para librerías y particulares  │
├─────────────────────────────────────────────────────────────────┤
│ 8. Confianza y Privacidad: 3 pilares + matriz de alcance        │
├─────────────────────────────────────────────────────────────────┤
│ 9. FAQ: 7 preguntas en acordeón <details>                       │
├─────────────────────────────────────────────────────────────────┤
│ 10. Cierre (Final CTA): Titular + Botones + Microcopy           │
├─────────────────────────────────────────────────────────────────┤
│ 11. Footer: Logo completo + créditos A+S + uso de IA            │
├─────────────────────────────────────────────────────────────────┤
│ 12. Modal Demo: Visor con pestañas y credenciales de prueba     │
└─────────────────────────────────────────────────────────────────┘
```

#### Lo que funciona y debe conservarse rigurosamente:
1. **Fidelidad al copy de producto:** El texto respeta sin alteraciones los copys definidos en `pitch/landing-page-contenido.md` (titular *"Deja de recorrer tiendas. Publica el libro que buscas"*, subtítulos, microcopys y respuestas del FAQ).
2. **Contraste conceptual del problema:** La frase *"Los catálogos te muestran lo que hay. BookWho? te muestra quién lo tiene"* sintetiza con contundencia la propuesta de valor sin caer en jerga de "marketplace inverso".
3. **Respaldo con datos reales de la encuesta:** El uso del 94,4 % y el 77,8 % otorga credibilidad inmediata y fundamenta por qué existe la plataforma.
4. **Mockup de teléfono móvil con ratio nativo:** El contenedor de smartphone replica fielmente la proporción 526:1056 de la app real, permitiendo apreciar la interfaz sin distorsiones ni cortes artificiales.
5. **Modal con cuentas demo copiables:** Facilita que evaluadores o usuarios prueben la app con un solo clic en las credenciales.

#### Lo que debilita la marca, genera inconsistencias o la hace lucir genérica:
1. **Síndrome de "Dark Mode SaaS / Crypto":**
   * *Diagnóstico:* El diseño actual utiliza un fondo carbón azulado frío (`#0A0D14`, `#111622`) acompañado de sombras difusas en tonos índigo (`shadow-indigo-500/10`) y resplandores esféricos borrosos comunes en plantillas de herramientas de desarrollo o finanzas descentralizadas.
   * *Efecto:* Desconecta de la experiencia cultural, física y táctil del libro. El usuario percibe una herramienta técnica fría en lugar de un punto de encuentro cálido entre lectores y libreros.
2. **Fricción del logo SVG con el fondo oscuro:**
   * *Diagnóstico:* Como `pitch/logo.svg` y `pitch/icon.svg` tienen fondos rectangulares crema horneados en el código vectorial, en la landing se enmarcaron dentro de tarjetas blancas/crema. Aunque funciona como solución de compromiso, genera un parche visual en el encabezado.
   * *Efecto:* Revela falta de integración entre el sistema gráfico vectorial y el tema oscuro de la web.
3. **Fatiga de repetición de mockups (Mockup Fatigue):**
   * *Diagnóstico:* La sección de características presenta tres mockups de teléfono consecutivamente en un patrón alternado (zig-zag). Los tres GIFs se reproducen en bucle simultáneamente.
   * *Efecto:* Sobrecarga la atención visual del usuario, genera distracción por movimiento continuo múltiple y ralentiza dispositivos de gama baja.
4. **Asimetría de protagonismo lector vs. vendedor:**
   * *Diagnóstico:* El lector siente que la app le habla de inmediato, pero el vendedor (librería de viejo o particular) tiene que bajar hasta la sección 5 para sentir que la página también es para él.

---

## 2. Diagnóstico Estratégico de Marca

Para asegurar honestidad y rigor metodológico, separamos de forma explícita los **Hechos Verificables**, las **Hipótesis Estratégicas** y las **Recomendaciones Creativas**.

### 2.1 Hechos Verificables (Evidencia Comprobada en el Proyecto)

1. **Muestra y demografía real (`FUNDAMENTACION-UX-UI.md`):**
   * Encuesta estructurada a 18 personas (27–28 septiembre 2026).
   * 10 de 18 tienen entre 18 y 24 años (estudiantes, lectores jóvenes); 7 de 18 tienen 35 años o más (lectores experimentados, compradores habituales de ferias y librerías tradicionales).
   * 17 de 18 (94,4 %) han buscado un libro específico sin hallarlo.
   * 14 de 18 (77,8 %) dedicaron 15 minutos o más en esa búsqueda infructuosa; 6 de ellos dedicaron más de una hora.
   * La principal exigencia de seguridad declarada es la confianza en el vendedor (13 de 18 calificaciones, 12 de 18 verificación de identidad, 9 de 18 protección de datos).
2. **Capacidades reales del MVP (`AGENTS.md`, `CONTEXTO.md`, `store.py`):**
   * No procesa pagos, logística ni envíos dentro de la plataforma.
   * No dispone de chat interno en el MVP.
   * La coordinación de compra, pago y entrega se realiza directamente entre las partes vía teléfono, correo electrónico o punto de encuentro físico.
   * La app cuenta con un catálogo de 107 comunas chilenas y búsqueda conectada a Google Books y Open Library con fallback local.
   * Los datos de contacto del vendedor permanecen estrictamente ocultos hasta que el lector acepta la oferta.

---

### 2.2 Hipótesis Estratégicas (Supuestos Razonados a Contrastar)

* **Hipótesis H-1 (Estética y Audiencia Madura):** Si la landing page luce como una aplicación tecnológica abstracta con luces de neón e índigo, los compradores mayores de 35 años y los dueños de librerías de barrio (ambos identificados en la investigación) desconfiarán o percibirán la plataforma como ajena a su entorno cultural.
* **Hipótesis H-2 (Doble Rol):** Los lectores con colecciones personales en casa tienen un alto potencial latente de convertirse en vendedores si la plataforma les demuestra que responder a una solicitud toma menos de un minuto y no exige digitalizar todo su librero.
* **Hipótesis H-3 (Claridad de No-Pago):** Declarar abiertamente y sin rodeos que BookWho? no cobra comisión ni intermedia el dinero incrementa la confianza en lugar de reducirla, posicionándola como un facilitador comunitario honesto frente a marketplaces corporativos que cobran tarifas elevadas.

---

### 2.3 Recomendaciones de Posicionamiento

* **Categoría:** *Marketplace de libros bajo demanda (Request-driven book marketplace)*.
* **Contraste con el mercado:**
  * Frente a **Mercado Libre / Grandes cadenas:** No compite por volumen de best sellers ni por logística automatizada de 24 horas; resuelve el libro agotado, la edición de colección, el ejemplar escolar descontinuado y la cercanía de barrio.
  * Frente a **AbeBooks / IberLibro:** AbeBooks posee la función de "Want list", pero orientada a un catálogo global de envíos internacionales caros con interfaces corporativas arcaicas. BookWho? es hiperlocal (por comuna), directo y sin comisiones.
  * Frente a **Grupos de Facebook / Foros:** Elimina la publicación al vacío donde el post caduca en el feed sin respuestas estructuradas. Aquí la solicitud persiste con metadatos reales de ISBN y condición.
* **Declaración de Posicionamiento:**
  > *"Para lectores que ya recorrieron librerías sin éxito y para vendedores con libros sin vitrina digital, BookWho? es el marketplace donde la demanda se publica y la oferta responde. A diferencia de las tiendas tradicionales de catálogo, aquí no buscas entre lo que sobra: recibes ofertas de quien tiene exactamente el libro que necesitas."*

---

### 2.4 Matriz de Percepción: Actual vs. Deseada

| Dimensión | Percepción que genera el diseño actual | Percepción objetivo deseada |
|---|---|---|
| **Ambiente visual** | "Software SaaS moderno / App fintech oscura" | "Librería de autor contemporánea, cálida y de noche" |
| **Tono de voz** | Eficiente, tecnológico, algo distante | Cercano, culto pero accesible, directo y transparente |
| **Materialidad** | Pantallas de vidrio digital y resplandor neón | Tinta de imprenta, papel hueso, terracota de encuadernación, madera oscura |
| **Rol del usuario** | Comprador de e-commerce | Lector en busca de un hallazgo / Librero que conecta con su comunidad |
| **Confianza** | Derivada de "seguridad informática" | Derivada de transparencia humana: datos claros, trato directo, respeto a la privacidad |

---

### 2.5 Incertidumbres y Preguntas Abiertas para Validaciones Futuras

1. **Retención tras el primer contacto:** Dado que la transacción ocurre fuera de la plataforma, ¿qué incentivo mantiene al usuario volviendo a marcar la solicitud como `RESUELTA` en la app? *(Hipótesis de producto a validar en pruebas de campo)*.
2. **Expectativa de pago digital:** Aunque 10 de 18 encuestados pidieron "pago seguro", el MVP no procesa pagos. Se debe vigilar en pruebas de usabilidad si la aclaración de coordinación externa es suficiente o si genera fricción en usuarios habituados a Webpay/MercadoPago.
3. **Dispersión geográfica real:** El catálogo contempla 107 comunas, pero en el lanzamiento inicial la masa crítica de vendedores probablemente se concentrará en comunas específicas (ej. Gran Santiago o Gran Concepción).

---

## 3. Dirección de Arte y Sistema Visual

### 3.1 Concepto Creativo Rector: *"Editorial Contemporáneo en Carbón Cálido y Papel Libro"*

Abandonamos la estética genérica de "Startup SaaS oscura fría" en favor de una **identidad editorial de alta gama**:
* Evoca la atmósfera de una biblioteca personal abierta de noche: maderas profundas, papel marfil envejecido con dignidad, tintas de imprenta tipográfica y acentos en cuero y terracota.
* Une la solvencia contemporánea de un producto digital bien resuelto con la calidez analógica del mundo del libro.

---

### 3.2 Paleta Cromática y Función Semántica

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PALETA SEMÁNTICA "BOOKWHO? WARM EDITORIAL"                              │
├─────────────────────────────────────────────────────────────────────────┤
│  [ #0E1214 ] Fondo Base (Carbón Imprenta Profundo)                      │
│  [ #161D20 ] Superficie / Tarjetas (Pizarra Tinta)                      │
│  [ #222B30 ] Elevación 2 / Bordes sutiles (Grafito de Encuadernación)   │
│  [ #FBFAF7 ] Texto Primario / Títulos (Marfil Hoja de Libro)            │
│  [ #A3B1B8 ] Texto Secundario / Metadatos (Ceniza Neutro)               │
│  [ #D97757 ] Acento Primario / CTAs (Terracota de Guardas y Tapas)      │
│  [ #2D6A4F ] Acento Confianza / Estados (Verde Biblioteca Clásica)      │
│  [ #E5A93C ] Acento Alerta / Pendiente (Ámbar Lámpara de Lectura)       │
└─────────────────────────────────────────────────────────────────────────┘
```

| Token de Color | Valor HEX | Función Semántica en la Interfaz | Justificación de Marca |
|---|---|---|---|
| `--color-canvas` | `#0E1214` | Fondo general de la página | Carbón con matiz orgánico cálido (no negro puro `#000000` ni azul eléctrico). Reduce la fatiga visual y evoca tinta sobre papel oscuro. |
| `--color-surface` | `#161D20` | Tarjetas, contenedores y paneles | Diferencia niveles de elevación sin recurrir a contrastes estridentes. |
| `--color-surface-hover` | `#1F272C` | Estado hover de tarjetas interactivas | Micro-elevación suave y táctil. |
| `--color-border` | `rgba(251, 250, 247, 0.09)` | Bordes de tarjetas y divisores | Simula el filete fino de encuadernación editorial. |
| `--color-text-main` | `#FBFAF7` | Títulos H1-H3 y texto prioritario | Blanco roto / marfil crema (`#FBFAF7`). Evita el encandilamiento del blanco puro `#FFFFFF`. Contraste sobre fondo: **17.8:1** (WCAG AAA). |
| `--color-text-muted` | `#9EADB5` | Descripciones, párrafos secundarios | Lectura descansada y jerarquía tipográfica sin pérdida de legibilidad. Contraste: **7.4:1** (WCAG AAA). |
| `--color-terracotta` | `#D97757` | Botones de acción primaria, enlaces clave | Color cálido de acento estipulado en el brief visual (`pitch/id_visual_icono.md`). Comunica cercanía, trato humano y dinamismo. |
| `--color-terracotta-hover`| `#C56545` | Hover y estados activos de botones | Proporciona feedback táctil inmediato. |
| `--color-forest` | `#2D6A4F` | Insignias de éxito, libro nuevo, verificación | El verde institucional de la app (`#1F4D3A`). Aporta balance, estabilidad y respaldo bibliotecario. |

---

### 3.3 Sistema Tipográfico y Escala de Jerarquía

Mantenemos la dupla tipográfica documentada en la fundamentación del proyecto, elevando su tratamiento compositivo:

1. **Tipografía Display (Titulares y Personalidad):** `Source Serif 4`
   * *Configuración:* Serif humanista con serifas refinadas, remates caligráficos suaves y soporte completo de signos diacríticos en español.
   * *Tratamiento:* `font-optical-sizing: auto`, `letter-spacing: -0.02em` en tamaños grandes (`36px+`), `text-wrap: balance`. Transmite autoridad literaria y prestigio sin rigidez académica.
2. **Tipografía de Contenido y UI:** `IBM Plex Sans`
   * *Configuración:* Sans-serif humanista con orígenes técnicos e industriales que aporta precisión, equilibrio métrico y legibilidad impecable en cuerpos pequeños (chips, inputs, metadatos y botones).
   * *Números tabulares:* Activación de `font-variant-numeric: tabular-nums` para precios (`$15.000 CLP`) y estadísticas (`94,4 %`).

#### Escala Modular de Texto (Desktop / Mobile):
* **H1 (Hero):** Desktop: `56px` / `1.1` · Mobile: `36px` / `1.15` · Weight: `Bold (700)` · Serif.
* **H2 (Secciones):** Desktop: `40px` / `1.2` · Mobile: `28px` / `1.25` · Weight: `Bold (700)` · Serif.
* **H3 (Tarjetas):** Desktop: `22px` / `1.3` · Mobile: `19px` / `1.35` · Weight: `SemiBold (600)` · Serif.
* **Eyebrow / Antetítulo:** `12px` · Weight: `SemiBold (600)` · `letter-spacing: 0.12em` · Uppercase · Sans.
* **Cuerpo Principal:** `16px` / `1.6` · Weight: `Regular (400)` · Sans.
* **Microcopy / Metadatos:** `13px` / `1.5` · Weight: `Medium (500)` · Sans.

---

### 3.4 Composición, Ritmo Visual y Espacios Negativos

* **Rejilla Base:** Sistema responsivo de 12 columnas con ancho máximo contenido de `1200px` (`max-w-7xl` con `padding` horizontal generoso de `24px` a `32px`).
* **Ritmo Vertical:** Secciones con respiración de `96px` a `128px` en escritorio (`py-24` a `py-32`) y `64px` en móviles. Esto evita el abarrotamiento de información y permite que cada argumento se asimile por separado.
* **Alternancia de Planos:**
  * Franja Hero: Expansiva, foco en el título y el mockup interactivo.
  * Franja de Evidencia: Tarjetas compactas de datos en 3 columnas.
  * Franja Proceso: Guía horizontal conectada en 3 pasos.
  * Franja Características: Composición de foco único (evitando el zig-zag repetitivo mediante una narrativa escalonada).
  * Franja Vendedores: Tarjeta envolvente con contraste de superficie que invita a un segundo perfil de usuario.

---

### 3.5 Tratamiento de Recursos Visuales y Mockups

1. **Mockup de Teléfono Móvil:**
   * **Problema a evitar:** Que parezca un "frame" genérico de mockup generator con brillos de plástico irreal.
   * **Tratamiento:** Chasis ultra-fino en aluminio grafito oscuro (`#1E2630`), borde biselado con micro-iluminación cenital de 1 px (`rgba(255,255,255,0.12)`), radio de pantalla exacto a la relación 526:1056 de los GIFs.
   * **Orquestación de GIFs:** En lugar de 3 GIFs reproduciéndose a la vez en la misma pantalla, la landing debe mostrar el GIF clave en el Hero y permitir que en las características el usuario interactúe o que los videos/GIFs se reproduzcan secuencialmente según la sección activa visible en el viewport.
2. **Tratamiento del Logo Vectorial:**
   * Resolver la tensión del fondo crema de `pitch/logo.svg`: en el header se utiliza el isotipo `pitch/icon.svg` montado en una pastilla de identidad editorial que celebra su color institucional marfil sin cortes bruscos, acompañado del wordmark en código HTML tipográfico nativo `BookWho?` con el signo de interrogación en terracota.

---

## 4. Estrategia de Movimiento y Narrativa de Scroll

El movimiento en BookWho? no debe ser decorativo ni buscar impacto circense. Su propósito es **explicar el cambio de dirección del modelo**: demostrar visualmente cómo una búsqueda estancada se convierte en una respuesta activa.

### 4.1 Principios de Movimiento

1. **Calma Literaria (Library Pacing):** Curvas de aceleración suaves (`cubic-bezier(0.16, 1, 0.3, 1)` o `expo.out`). Nada de rebotes bruscos ni animaciones nerviosas.
2. **Intencionalidad Funcional:** Cada animación responde a una causa: revelar datos, guiar la lectura secuencial de los 3 pasos o confirmar una acción de copia.
3. **Respeto Absoluto a la Accesibilidad:** Implementación obligatoria de `@media (prefers-reduced-motion: reduce)` que neutralice traslados y reduzca todo efecto a transiciones sutiles de opacidad o estado final instantáneo.

---

### 4.2 Matriz de Movimiento por Sección

| Sección | Elementos Dinámicos | Elementos Estáticos | Técnica Recomendada | Función Narrativa |
|---|---|---|---|---|
| **01. Hero** | - Entrada stagger del H1 y CTAs.<br>- Aparición suave del teléfono móvil.<br>- Micro-tarjetas flotantes con oscilación sutil (3–4s). | Barra de navegación, fondo general, textos legales. | CSS `@keyframes` o GSAP `power1.out` (desplazamiento vertical ≤ 16px). | Atrae la atención al teléfono sin impedir la lectura inmediata del titular. |
| **02. El Problema** | - Conteo progresivo de cifras (0% &rarr; 94,4%, 0% &rarr; 77,8%) al ingresar al viewport.<br>- Aparición escalonada de las 3 tarjetas de dolor. | Título de sección, textos de evidencia. | `IntersectionObserver` activando clases con transiciones CSS de 400ms. | Enfatiza la contundencia de los datos recopilados en la encuesta real. |
| **03. Cómo Funciona** | - Línea conectora que se "dibuja" conforme el usuario hace scroll.<br>- Activación secuencial de los pasos 1, 2 y 3. | Encabezado de la sección, microcopys. | Scroll-driven progress o clase activa por umbral de scroll (threshold 0.6). | Transmite la sensación de avance guiado y sencillez de proceso. |
| **04. Características** | - Scroll storytelling o Tabs interactivos sincronizados con el teléfono.<br>- Transición cruzada suave entre GIFs según la característica seleccionada. | Textos explicativos principales, títulos. | Tab switcher interactivo o reveal con `cross-fade` de 300ms. | Elimina la fatiga visual de tener 3 GIFs corriendo a la vez; pone el control en manos del usuario. |
| **05. Vendedores** | - Hover cards con iluminación perimetral en terracota.<br>- Efecto sutil al pasar sobre el botón de solicitudes abiertas. | Textos descriptivos, datos de contacto. | CSS `transition: all 200ms ease`. | Sensación de interactividad profesional y directa. |
| **06. Confianza** | - Revelación suave de las 3 columnas de seguridad.<br>- Despliegue de los acordeones del FAQ. | Cuadro de transparencia y alcance. | Transición fluida de altura (`max-height` con `opacity`). | Transmite solidez y tranquilidad sin sobresaltos. |
| **07. Modal Demo** | - Fade-in de fondo oscuro con blur.<br>- Escalamiento suave de la ventana modal (0.96 &rarr; 1.0 en 180ms).<br>- Feedback de "¡Copiado!" en botón de cuentas. | Contenido interno de credenciales. | CSS `transition` con evento de tecla `Escape` y retorno de foco accesible. | Sensación de herramienta lista para ser probada de inmediato. |

---

### 4.3 Especificaciones de Rendimiento y Adaptabilidad Móvil

* **Límite de propiedades animadas:** Restringir animaciones estrictamente a `transform` y `opacity` para garantizar renderizado en GPU a 60 FPS sin provocar repintados (*layout thrashing*).
* **Comportamiento en Móviles (< 768px):**
  * Desactivar efectos parallax y tarjetas flotantes absolutas que puedan desbordar la pantalla (`overflow-x-hidden`).
  * Los GIFs se cargan con `loading="lazy"` para ahorrar datos móviles.
  * Los acordeones del FAQ conservan altura táctil mínima de `48px` para facilitar el toque con el pulgar.

---

## 5. Referencias Visuales y Competitivas Pertinentes

A partir del análisis de mercado y diseño de productos editoriales contemporáneos:

```
┌────────────────────────────────────────────────────────────────────────┐
│ MAPA DE REFERENCIAS VISUALES Y DE EXPERIENCIA                          │
├────────────────────────────────────────────────────────────────────────┤
│  LITERAL.CLUB        ──> Belleza editorial, tarjetas limpias,          │
│                          tratamiento de libros como objetos culturales.│
├────────────────────────────────────────────────────────────────────────┤
│  HARDCOVER.APP       ──> Modo oscuro estructurado, datos legibles,     │
│                          excelente jerarquía de metadatos y portadas.  │
├────────────────────────────────────────────────────────────────────────┤
│  BOOKSHOP.ORG        ──> Enfoque ético y humano, apoyo a librerías     │
│                          locales independientes, tono comunitario.     │
├────────────────────────────────────────────────────────────────────────┤
│  ABEBOOKS (Wants)    ──> Referencia funcional del modelo "Want list",  │
│                          pero superando su interfaz anticuada y lenta. │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Literal Club (`literal.club`):** Referencia en tratamiento visual de portadas, márgenes generosos y estética anti-Goodreads. Demuestra que el software de libros puede ser sofisticado, moderno y respetuoso de la tipografía.
2. **Hardcover (`hardcover.app`):** Referencia en diseño de modo oscuro para lectores: utiliza grises neutros cálidos y acentos suaves en lugar de neones estridentes.
3. **Bookshop.org:** Referencia de tono ético: comunica apoyo al librero independiente y a la economía local sin paternalismos ni excesos corporativos.

---

## 6. Plan de Cambios Recomendados (Priorizados por Impacto)

La siguiente tabla establece la hoja de ruta de diseño para la Fase 2 de implementación, ordenada por impacto en la percepción y esfuerzo técnico:

| Prioridad | Área de Intervención | Acción Específica de Diseño | Impacto Esperado |
|---|---|---|---|
| **P1 · Crítica** | **Afinación Cromática y de Atmósfera** | Reemplazar los tonos fríos/azules e índigos por la paleta *Warm Editorial* (Carbón `#0E1214`, Pizarra `#161D20`, Marfil `#FBFAF7` y resplandores cálidos terracota/ámbar en lugar de azules). | Desmarca la web de plantillas SaaS/cripto genéricas y la posiciona de inmediato como un espacio literario contemporáneo. |
| **P1 · Crítica** | **Armonización de Marca y Logo** | Resolver la integración del logo vectorial en el navbar mediante una pastilla institucional refinada y tipografía nativa consistente con `pitch/id_visual_icono.md`. | Transmite solidez institucional y elimina la sensación de "parche visual". |
| **P2 · Alta** | **Orquestación de las Características** | Reemplazar el patrón repetitivo de 3 teléfonos en zig-zag por un **escaparate interactivo** (Showcase interactivo de 4 módulos o slider sincronizado de características). | Resuelve la fatiga visual, reduce el consumo de datos de 3 GIFs simultáneos y eleva la interactividad a nivel de producto premium. |
| **P2 · Alta** | **Micro-narrativa en el Hero** | Enriquecer el entorno del smartphone en el Hero con elementos visuales que ilustren el momento exacto en que llega una oferta cercana (insignia de comuna, precio acordado). | Claridad instantánea en los primeros 5 segundos de visita. |
| **P3 · Media** | **Interactividad en Cifras de Encuesta** | Añadir contadores progresivos activados por scroll para el 94,4 % y 77,8 % con barras de progreso sutiles. | Mayor dinamismo y fijación del problema en la mente del visitante. |
| **P3 · Media** | **Simulador de Solicitudes para Vendedores** | Incorporar en la sección de vendedores un mini-feed interactivo que simule 3 solicitudes reales de lectores en comunas chilenas (ej. *"Busco El Hobbit en Providencia"*, *"Busco Cien Años de Soledad en Concepción"*). | Permite al vendedor entender su ganancia en 3 segundos: ver que ya hay lectores esperando con dinero en mano. |

---

## 7. Riesgos, Supuestos y Datos Pendientes de Validación

### 7.1 Riesgos Identificados

* **Riesgo R-1 (Peso de Medios):** Tres GIFs de más de 2 MB pueden provocar retardos de renderizado en conexiones móviles lentas.  
  *Mitigación:* Implementar carga diferida estricta (`loading="lazy"`), posters estáticos en formato WebP para el primer cuadro y reproducción bajo demanda o en vista activa.
* **Riesgo R-2 (Equilibrio de Audiencias):** Si la landing parece 90% para lectores, los vendedores no se registrarán; si parece 90% para vendedores, los lectores pensarán que es un panel de administración.  
  *Mitigación:* Mantener la barra superior con el enlace directo *"Tengo libros para vender"* y la sección dedicada 5 con llamada explícita a librerías y particulares.

### 7.2 Supuestos Clave a Verificar en Campo

* **Supuesto S-1:** Los usuarios valoran saber el ISBN y la edición exacta por encima de la inmediatez de una búsqueda difusa.
* **Supuesto S-2:** El público acepta que el pago sea fuera de la plataforma si se garantiza que el vendedor tiene el ejemplar y los datos no se exponen prematuramente.

### 7.3 Checklist de Validación Previa a la Implementación

- [x] Estructura semántica de `index.html` auditada y validada.
- [x] Copys originales de `pitch/landing-page-contenido.md` verificados y protegidos.
- [x] Identidad cromática y tipográfica alineada con `pitch/id_visual_icono.md`.
- [x] Hechos, hipótesis y recomendaciones delimitados rigurosamente.
- [x] Criterios de accesibilidad WCAG AAA y rendimiento móvil definidos.
- [ ] Validación de la dirección creativa por parte del equipo para iniciar la Fase 2 de implementación.

---

*Fin del documento de auditoría y dirección creativa. Este documento queda fijado como la guía estratégica y visual para la siguiente iteración de código.*

