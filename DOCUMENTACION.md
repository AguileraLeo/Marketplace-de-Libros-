# BookWho? — Documentación completa del proyecto

Este documento explica, de principio a fin, qué es la aplicación, cómo funciona, cómo está
construido el código y cómo ejecutarla. Está pensado para que cualquiera del equipo (o quien
evalúe el proyecto) entienda el sistema completo sin tener que leer todo el código fuente.

Documentos relacionados en este repositorio:

- [`README.md`](README.md) — instalación rápida, cuentas de demo, capturas.
- [`AGENTS.md`](AGENTS.md) — visión de producto y reglas de trabajo (fuente de verdad original).
- [`CONTEXTO.md`](CONTEXTO.md) — estado del proyecto y cómo trabajar en equipo.
- [`uso_ia.md`](uso_ia.md) — declaración de uso de Inteligencia Artificial.

---

## 1. Qué es BookWho?

**BookWho?** es una maqueta funcional (Kivy + KivyMD) de una plataforma de **búsqueda de
libros bajo demanda**. La idea central, resumida en una frase:

> El lector publica qué libro busca. Los vendedores que lo tienen responden con una oferta.
> Cuando el lector acepta una, ambos coordinan la compra fuera de la app (teléfono, correo o
> punto de encuentro).

### 1.1 Problema que resuelve

Encontrar un libro específico —agotado, descatalogado, de segunda mano o simplemente difícil
de ubicar— hoy obliga a recorrer tienda por tienda o grupo por grupo de compraventa, sin
ninguna garantía de encontrarlo. BookWho? invierte el modelo habitual de "catálogo que hay que
revisar" por uno de "pido y me ofrecen": el lector no busca entre miles de libros que nadie
tiene, sino que anuncia lo que necesita y espera a que aparezca.

### 1.2 Usuario objetivo

- **Lectores**: buscan un libro puntual (regalo, colección, estudio, lectura) y no quieren
  perder tiempo comparando tienda por tienda.
- **Vendedores** (librerías pequeñas o personas particulares): quieren vender libros puntuales
  sin mantener ni actualizar un catálogo público permanente.
- **Administrador**: rol interno de supervisión y moderación de la plataforma (no es un
  usuario final del producto).

### 1.3 Qué NO hace (fuera de alcance del MVP)

- No procesa pagos ni gestiona envíos: la coordinación final ocurre **fuera** de la app.
- No hay chat interno (se usan los datos de contacto que el vendedor decide compartir).
- El vendedor no mantiene un catálogo/inventario propio (ver §2.4 más abajo — esto se
  conversó explícitamente durante el desarrollo y se decidió mantenerlo así).
- No hay persistencia real: todo vive en memoria mientras la app está abierta.

---

## 2. Cómo funciona la aplicación (flujo por rol)

Hay tres experiencias completamente separadas según el rol de la cuenta: **Lector**,
**Vendedor** y **Administrador**. Cada cuenta tiene un solo rol (no se puede ser lector y
vendedor con el mismo usuario).

### 2.1 Flujo del lector (comprador)

```
Login/Registro
   |
   v
Inicio del lector -> buscador de libros ("¿Qué libro estás buscando?")
   |
   v
Buscar libro (API externa: título / autor / ISBN)
   |
   v
Seleccionar un resultado
   |
   v
Crear solicitud
   - precio máximo (opcional)
   - condición aceptada (cualquiera / nuevo / usado)
   - ubicación (comuna, con autocompletado)
   - preferencia de entrega (presencial / envío / cualquiera)
   - notas
   |
   v
Solicitud publicada (queda en estado PUBLICADA)
   |
   v
Mis solicitudes -> Detalle de solicitud -> ver ofertas recibidas
   |
   v
Detalle de oferta -> Aceptar oferta (pasa a "por concretar", se revela el contacto del vendedor)
   |
   v
Coordinación fuera de la app -> Confirmar trato concretado (o desistir)
```

El lector también puede **cancelar** sus propias solicitudes mientras estén abiertas
(`PUBLICADA` o `CON_OFERTAS`); esto cancela automáticamente las ofertas activas asociadas.

### 2.2 Flujo del vendedor

El vendedor **no publica libros**: responde a lo que los lectores ya están pidiendo.

```
Login/Registro (como Vendedor, con su comuna)
   |
   v
Inicio del vendedor -> "Solicitudes disponibles"
   (excluye automáticamente las solicitudes donde ya tiene una oferta activa)
   |
   v
Filtrar por texto / ubicación / presupuesto mínimo / condición
   |
   v
Ver detalle de una solicitud (incluye la cercanía: "Misma comuna" / "Misma región" / "Otra región")
   |
   v
"Puedo ofrecerlo" -> Crear oferta
   - precio
   - estado del libro (nuevo/usado) y descripción de condición
   - información adicional
   - datos de contacto que verá el lector si acepta
   |
   v
Oferta publicada -> aparece en "Mis ofertas" (activa / por concretar / en espera / aceptada / finalizada)
```

El vendedor puede **cancelar** su propia oferta mientras esté activa o en espera.

### 2.3 Flujo del administrador

Experiencia completamente separada, pensada para supervisión y moderación:

- **Inicio**: métricas generales (usuarios, lectores, vendedores, solicitudes por estado,
  ofertas) con accesos rápidos a cada sección.
- **Solicitudes**: listado completo con filtro por estado y acción de **moderar/cancelar**
  (queda registrado que fue el admin quien canceló, y por qué — el lector lo ve reflejado en
  el detalle de su solicitud).
- **Usuarios**: listado con acción de **suspender/reactivar** (un usuario suspendido no puede
  iniciar sesión ni operar).
- **Ofertas**: listado global de solo lectura.
- **Auditoría/Actividad**: registro cronológico de eventos relevantes (login, registro,
  publicación de solicitudes/ofertas, cancelaciones, etc.), con búsqueda de texto y **botón
  para exportar el log a un archivo `.log`**.

### 2.4 Por qué "no hay opción para publicar libros como vendedor"

Esto surgió explícitamente durante el desarrollo: en un marketplace tradicional el vendedor
publica su catálogo y el comprador lo recorre. Acá es al revés (*request-driven*, no
*inventory-driven*): decisión de producto documentada desde el inicio en `AGENTS.md` y
confirmada de nuevo en esta sesión de pulido. Por eso, en el inicio del vendedor y del lector
hay textos explícitos que aclaran el mecanismo ("No publicas libros: elige una solicitud
abierta y ofrécele el libro que buscan").

---

## 3. Modelo de dominio

### 3.1 Entidades (definidas en `store.py`)

| Entidad | Campos clave | Qué representa |
|---|---|---|
| `User` | `id, name, email, password, role, status, location, created_at` | Una cuenta (lector, vendedor o admin). `location` (comuna) solo es obligatoria para vendedores. |
| `Book` | `id, external_provider, external_id, isbn, title, authors, cover_url, publisher, published_date` | Metadatos de una obra, obtenidos de una API externa (o del catálogo local de respaldo). |
| `BookRequest` | `id, reader_id, book_id, max_price, accepted_condition, location, delivery_preference, notes, status, canceled_by_role, cancellation_reason` | La "solicitud" de un lector: qué libro busca y en qué condiciones. |
| `Offer` | `id, request_id, seller_id, price, book_condition, condition_description, notes, status` | La respuesta de un vendedor a una solicitud. |
| `SellerContact` | `seller_id, phone, email, address_or_meeting_point` | Datos de contacto del vendedor, se revelan solo al coordinar/aceptar. |
| `ActivityEntry` | `at, actor_id, action, detail` | Un evento de auditoría (para el panel de admin). |

**Libro y solicitud son entidades distintas**: un mismo libro (por ejemplo "El Hobbit") puede
estar asociado a muchas solicitudes de distintos lectores.

### 3.2 Máquina de estados de la Solicitud (`RequestStatus`)

```
BORRADOR -> PUBLICADA -> CON_OFERTAS -> EN_COORDINACION -> RESUELTA
                |              |               |
                +--------------+---------------+--> CANCELADA
```

- `BORRADOR -> PUBLICADA`: ocurre automáticamente al crear la solicitud (no hay un paso
  intermedio visible para el usuario).
- `PUBLICADA -> CON_OFERTAS`: cuando llega la primera oferta.
- `CON_OFERTAS/EN_COORDINACION -> EN_COORDINACION`: cuando el lector acepta una oferta para
  coordinar (`accept_offer`).
- `EN_COORDINACION -> RESUELTA`: cuando el lector confirma el trato (`confirm_deal`).
- `EN_COORDINACION -> CON_OFERTAS` o `PUBLICADA`: si el trato se desiste (`cancel_deal`),
  vuelve a `CON_OFERTAS` si quedan ofertas en espera, o a `PUBLICADA` si no queda ninguna.
- Cualquier estado abierto puede pasar a `CANCELADA` (por el lector o por moderación admin).

### 3.3 Máquina de estados de la Oferta (`OfferStatus`)

```
PUBLICADA (activa) --acepta el lector--> POR_CONCRETAR --confirma el lector--> ACEPTADA
PUBLICADA --el lector acepta OTRA oferta--> EN_ESPERA --esa otra se desiste--> PUBLICADA
                                                        --esa otra se confirma--> RECHAZADA
Cualquier estado activo (PUBLICADA/POR_CONCRETAR/EN_ESPERA) --el vendedor cancela--> CANCELADA
```

Reglas importantes:

- Un vendedor solo puede tener **una oferta activa** por solicitud.
- El vendedor puede ofertar cualquier condición (nuevo/usado) aunque no coincida exactamente
  con lo que el lector prefería; la UI se lo destaca al lector, pero no lo bloquea (se
  flexibilizó a propósito para no perder ofertas válidas).
- Los datos de contacto del vendedor **solo se revelan** cuando la oferta entra en
  `POR_CONCRETAR` o `ACEPTADA` (`offer_contact()` en `store.py`).

### 3.4 Reglas de permisos (autorización)

Todas las reglas de negocio y de permisos viven en `store.py`, **no en la interfaz**: cada
método del `Store` vuelve a validar el rol, la propiedad del recurso y el estado, sin confiar
en lo que mande la UI. Algunos ejemplos:

- Un lector solo puede ver/cancelar **sus propias** solicitudes.
- Un vendedor solo puede cancelar **sus propias** ofertas.
- Un usuario **suspendido** no puede autenticarse ni operar (se revalida en cada llamada, no
  solo al iniciar sesión).
- Solo el admin puede suspender usuarios, moderar solicitudes o exportar el log de actividad.

---

## 4. Arquitectura del código

```
libros.kv        Interfaz declarativa (KV language): toda la UI y el estilo visual.
   |
main.py          Pantallas (ScreenManager) y navegación. NO contiene reglas de negocio,
   |              solo llama a métodos del Store y reacciona a errores.
store.py         Dominio: entidades, máquinas de estado, validaciones, permisos.
   |              Repositorio en memoria + datos de ejemplo (build_demo_store).
   |
books_api.py     Búsqueda de libros: Google Books -> Open Library -> catálogo local,
   |              con caché de portadas en disco.
locations.py     Catálogo y normalizador de comunas/ciudades de Chile + cercanía
                  aproximada entre vendedor y solicitud.
```

Regla de separación (definida en `CONTEXTO.md` y respetada en todo el código): **toda regla de
negocio y todo chequeo de permisos va en `store.py`**, y la interfaz (`main.py` + `libros.kv`)
solo la invoca y muestra el resultado. Esto permite probar el dominio sin interfaz (ver §6) y
cambiar la UI sin tocar las reglas.

### 4.1 Explicación de `main.py`

Es el punto de entrada (`python main.py`) y define:

- **Configuración de ventana**: en escritorio simula el tamaño de un teléfono (420×860). En
  Android/iOS no aplica ese ajuste.
- **Registro de la tipografía "Lora"** (serif) vía `LabelBase.register(...)`, usada solo en
  títulos/encabezados (ver §7.2).
- **Widgets reutilizables** (su apariencia vive en `libros.kv`, su lógica acá):
  - `BookCover`: portada de un libro, con carga desde caché en disco y *placeholder* mientras
    descarga.
  - `StatusChip`: la píldora de color que muestra el estado de una solicitud/oferta/usuario.
  - `WideButton` / `PrimaryButton`: botón a todo el ancho.
  - `ChoiceRow`: grupo de botones de selección única (usado para elegir condición, rol,
    filtros, etc.).
  - `RequestCard`, `ItemCard`, `BookResultCard`, `StatTile`, `InfoRow`, `EmptyState`: tarjetas
    y filas reutilizadas en casi todas las pantallas.
- **Pantallas** (una clase por pantalla, todas heredan de `BaseScreen`): `LoginScreen`,
  `RegisterScreen`, `ReaderHomeScreen`, `BookSearchScreen`, `CreateRequestScreen`,
  `RequestPublishedScreen`, `ReaderRequestsScreen`, `ReaderRequestDetailScreen`,
  `OfferDetailScreen`, `OfferAcceptedScreen`, `SellerHomeScreen`, `SellerRequestDetailScreen`,
  `CreateOfferScreen`, `SellerOffersScreen`, `AdminHomeScreen`, `AdminRequestsScreen`,
  `AdminUsersScreen`, `AdminOffersScreen`, `AdminActivityScreen`. Cada una implementa
  `refresh()`, que se llama automáticamente al entrar a la pantalla (`on_pre_enter`).
- **`DemoLibrosApp`** (clase principal, `MDApp`): arma el tema (paleta de color, tipografía),
  crea el `Store` de demo, maneja la navegación (`go`, `back`, `go_home`, historial tipo pila),
  el login/logout, diálogos de confirmación/información, *snackbars* de error, y helpers
  compartidos entre pantallas (`request_card`, `request_info_rows`, `fill_book_header`, etc.).
- **`app.safe(fn, *args)`**: envoltorio que llama a un método del `Store` y, si lanza un
  `DomainError`, muestra el mensaje en un *snackbar* en vez de romper la app. Así ningún error
  de negocio se ve como un *crash*.

### 4.2 Explicación de `libros.kv`

Es un archivo [KV language](https://kivy.org/doc/stable/guide/lang.html) de ~1500 líneas.
Contiene **toda** la interfaz: layout, estilos, colores por estado, tipografía y navegación
entre pantallas. Se divide en:

1. **Componentes reutilizables** (arriba del archivo): `Heading`, `Muted`, `FieldLabel`,
   `Panel`, `ListBox`, `BookCover`, `StatusChip`, `RequestCard`, `ItemCard`, `BookResultCard`,
   `StatTile`, `InfoRow`, `EmptyState`, `BookHeader`, `BackBar`, `BrandMark` (el logo de
   BookWho?). Definir estos "átomos" una sola vez evita repetir estilos en cada pantalla.
2. **`MDScreenManager`**: la lista de las 19 pantallas de la app.
3. **Una regla `<NombreDePantalla>:` por pantalla**, con su layout completo.

Detalle técnico importante encontrado y corregido en esta sesión: en KivyMD 2.0, un
`MDCard` **ignora** cualquier `md_bg_color` personalizado a menos que también se le declare
`theme_bg_color: "Custom"` (si no, usa el color que le asigna el tema automáticamente). Esto
afectaba a `Panel` y a `StatTile`, y hacía que las tarjetas de métricas del admin y los
paneles destacados se vieran todas del mismo color en vez de sus colores distintos — se
corrigió agregando esa línea en ambos.

### 4.3 Explicación de `store.py`

Ya cubierto en detalle en la sección 3 (modelo de dominio). Estructuralmente:

- Constantes de dominio arriba (`Role`, `UserStatus`, `RequestStatus`, `OfferStatus`,
  `Condition`, `Delivery`), cada una con sus `TRANSITIONS` (qué cambios de estado son válidos)
  y `LABELS` (texto legible en español).
- Jerarquía de excepciones (`DomainError` y subclases `ValidationError`, `PermissionDenied`,
  `NotFound`, `InvalidTransition`) — todas con mensajes pensados para mostrarse directo al
  usuario.
- Funciones de validación compartidas (`_clean`, `_parse_price`, `format_price`,
  `condition_compatible`).
- La clase `Store`: repositorio en memoria (diccionarios `id -> entidad`) más todos los casos
  de uso como métodos (`register`, `authenticate`, `create_request`, `create_offer`,
  `accept_offer`, `confirm_deal`, `cancel_deal`, `cancel_offer`, `cancel_request`, los métodos
  de admin, etc.). Cada método público empieza revalidando quién es el actor y si tiene
  permiso, antes de tocar cualquier dato.
- `build_demo_store()` + `DEMO_USERS`: arma un `Store` con las 5 cuentas de demo y algunos
  libros/solicitudes/ofertas de ejemplo, para que la app no arranque vacía.

### 4.4 Explicación de `books_api.py`

Resuelve la búsqueda de libros con **tres niveles de respaldo**, en orden:

1. **Google Books API** (necesita internet; sin `GOOGLE_BOOKS_API_KEY` suele responder 429 —
   límite de peticiones — y se pasa al siguiente nivel).
2. **Open Library API** (abierta, sin clave).
3. **Catálogo local** (`LOCAL_CATALOG`, 10 libros hardcodeados) — así la demo funciona sin
   conexión a internet.

Cada proveedor normaliza su respuesta a un mismo formato de diccionario (`title`, `authors`,
`isbn`, `cover_url`, etc.) antes de devolverlo, para que el resto de la app no necesite saber
de qué proveedor vino un libro.

También implementa una **caché de portadas en disco** (`.cache/covers/`, con el nombre de
archivo derivado del hash MD5 de la URL): la primera vez que se ve una portada se descarga en
un hilo aparte y se guarda; las siguientes veces se lee directo del disco, sin volver a pedirla
por red — esto evita el problema original de portadas que "a veces cargan y a veces no".

### 4.5 Explicación de `locations.py`

- `CHILE_LOCATIONS`: catálogo de 107 comunas de Chile con su región.
- `search_locations(query)`: autocompletado tolerante a tildes/mayúsculas (usado en el campo
  de ubicación al crear una solicitud y al registrar un vendedor).
- `normalize_location_name(text)`: convierte lo que escribe el usuario al formato estándar
  `"Comuna (Región)"` si coincide con el catálogo.
- `proximity_label(seller_location, request_location)` **(agregado en esta sesión)**: calcula
  una cercanía aproximada entre la comuna del vendedor y la de una solicitud, **sin usar
  coordenadas ni direcciones exactas** (por privacidad): devuelve `"Misma comuna"`, `"Misma
  región"` u `"Otra región (X)"`. Se muestra como una insignia en las tarjetas de solicitudes
  que ve el vendedor.

### 4.6 Pruebas automatizadas (`tests/`)

```bash
python -m unittest discover -s tests -v
```

- `tests/test_store.py`: flujo feliz completo, permisos (un lector no puede tocar solicitudes
  de otro, etc.), validaciones de formularios, y las máquinas de estado (incluida la
  negociación/desistimiento de un trato y la moderación administrativa).
- `tests/test_locations_and_cache.py`: catálogo de ubicaciones, búsqueda tolerante a tildes,
  normalización, la nueva `proximity_label`, y la caché de portadas de `books_api.py`.

Actualmente hay **30 pruebas**, todas en verde. Se ejecutan después de cada cambio de código
para asegurar que nada se rompió.

---

## 5. Qué se hizo en esta sesión de pulido (resumen)

Partiendo de una app ya funcional (dominio, pantallas, tests — trabajo previo del equipo), en
esta sesión se trabajó específicamente en:

1. **Diagnóstico contra la rúbrica de evaluación** (E2): se detectó que la fundamentación
   UX/UI con evidencia de usuarios (30% de la nota) era el mayor riesgo, y que existe una
   política de curso que exige un archivo `uso_ia.md` separado del README.
2. **Nombre e identidad**: la app pasó de un genérico "App de libros" a **BookWho?**, con una
   marca propia (ícono de libro + insignia "?").
3. **Corrección de un bug real**: las tarjetas de métricas del panel de administrador no
   mostraban colores diferenciados (ver §4.2) — se corrigió con una línea en cada componente
   afectado y se verificó con capturas antes/después.
4. **Rediseño visual**: paleta de color cálida (derivada de "darkgoldenrod" con Material You),
   tipografía serif (Lora, licencia OFL) en títulos/encabezados manteniendo Roboto en el
   cuerpo, íconos por métrica en el panel de admin, spinner real en vez de texto estático
   durante la búsqueda de libros.
5. **Aclaraciones de UX**: textos explícitos en el inicio del lector y del vendedor sobre cómo
   funciona el mecanismo de solicitud/oferta (no es un catálogo).
6. **Función de cercanía vendedor–lector** (`proximity_label`, ver §4.5): además se agregó el
   campo "comuna" al registro de vendedores (obligatorio solo para ese rol).
7. **Pequeñas correcciones de consistencia**: texto en mayúsculas fijas en un botón, quedó en
   formato oración como el resto de la app.

Cada cambio se verificó ejecutando la app real (capturas de pantalla) y corriendo la suite de
tests completa antes de continuar.

---

## 6. Cómo ejecutar el proyecto

### 6.1 Requisitos

- Python 3.10 o 3.11 (probado también en 3.12).
- Kivy 2.3.1 + KivyMD 2.0.1.dev0 (se instala desde GitHub, no está en PyPI todavía).
- En Linux, para compilar KivyMD hace falta `libcairo2-dev` y `pkg-config` instalados a nivel
  de sistema (`sudo apt-get install -y libcairo2-dev pkg-config`).

### 6.2 Instalación y ejecución

```bash
# Windows
py -3.11 -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

Opcional: definir `GOOGLE_BOOKS_API_KEY` como variable de entorno para usar Google Books sin
límite de peticiones. Sin clave, la app cae automáticamente a Open Library y, si tampoco hay
internet, al catálogo local.

### 6.3 Cuentas de demo

| Rol | Correo | Contraseña |
|---|---|---|
| Lector | lector@demo.cl | 1234 |
| Lector | maria@demo.cl | 1234 |
| Vendedor | vendedor@demo.cl | 1234 |
| Vendedor | pedro@demo.cl | 1234 |
| Administrador | admin@demo.cl | admin |

También se pueden registrar cuentas nuevas de lector o vendedor desde la app. **Sin base de
datos:** todo vive en memoria mientras la app está abierta; al cerrarla, los datos vuelven al
estado inicial (excepto la caché de portadas en `.cache/covers/`, que persiste en disco).

### 6.4 Correr las pruebas

```bash
python -m unittest discover -s tests -v
```

---

## 7. Decisiones de diseño visual

### 7.1 Paleta de color

KivyMD 2.0 genera un esquema Material You completo a partir de un solo color "semilla"
(`theme_cls.primary_palette`, definido en `main.py`). Se probaron varias familias de color
(marrón/rojiza, azul/índigo, dorada) y se descartó la familia roja porque su tono resultante
chocaba visualmente con el color ya usado para el estado "cancelada". Se eligió
**`"darkgoldenrod"`**: un dorado envejecido tipo papel/pergamino, que se ve serio y cálido sin
competir con los colores de estado (azul/verde/naranja/rojo/morado que usa `STATUS_COLORS` en
`main.py`).

### 7.2 Tipografía

Se registró la fuente **Lora** (serif, licencia OFL de Google Fonts, archivos en `fonts/`) y
se aplicó únicamente a los estilos tipográficos "Headline" y "Title" del tema de KivyMD (título
de la app, encabezados de sección, nombres de libro en las tarjetas, números del panel de
admin). El cuerpo de texto, botones y campos de formulario siguen en Roboto (la fuente por
defecto de KivyMD), para mantener legibilidad. Es la combinación clásica editorial
serif+sans, y se aplicó modificando el diccionario `theme_cls.font_styles` una sola vez en
`main.py`, sin tocar cada pantalla individualmente.

### 7.3 Marca (`BrandMark`)

En vez de un ícono genérico de Material Icons, se armó un logo propio combinando dos
elementos superpuestos (definido como componente reutilizable en `libros.kv`): un cuadrado
redondeado con un ícono de libro, y una insignia circular con un signo de interrogación
superpuesta en la esquina — literalmente "BookWho?" convertido en símbolo.

---

## 8. Estado frente a la rúbrica de evaluación (E2)

| Criterio | Peso | Estado |
|---|---|---|
| A — Fundamentación UX/UI con evidencia de usuarios | 30% | **Pendiente** — requiere encuesta/entrevistas reales, deliberadamente pospuesto para no inventar datos. |
| B — Maqueta funcional Kivy + KivyMD | 30% | Cubierto: la app ejecuta sin errores, usa componentes KivyMD con coherencia Material Design. |
| C — Estructura del proyecto y navegación | 25% | Cubierto: separación `.py`/`.kv`, `ScreenManager` con 19 pantallas, validaciones, proyecto ordenado. |
| D — Presentación oral y demo en vivo | 15% | Depende de la presentación misma. |

El mayor pendiente sigue siendo el punto A: sin evidencia real de usuarios (encuesta o
entrevistas), ese 30% de la nota no se puede completar honestamente, y es intencional dejarlo
así hasta tener los datos.
