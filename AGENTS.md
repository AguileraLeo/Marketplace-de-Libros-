# AGENTS.md — App de libros

## 1. Propósito del proyecto

Este repositorio implementa una plataforma que conecta **lectores que buscan libros** con **vendedores que pueden ofrecerlos**.

La idea evolucionó desde una wishlist personal de libros y comparación de precios hacia un sistema más escalable basado en demanda:

> Un lector publica una solicitud de uno o más libros que desea conseguir. Los vendedores revisan solicitudes, indican que disponen del libro y entregan una oferta. Si el lector acepta una oferta, ambas partes coordinan la compra o entrega fuera de la plataforma mediante datos de contacto.

La plataforma, en su MVP, **no procesa pagos ni gestiona entregas**. Su función principal es conectar demanda y oferta.

El proyecto debe desarrollarse con enfoque **Spec-Driven Development**: las decisiones de producto y comportamiento se documentan antes de implementar. Los agentes de IA deben implementar especificaciones existentes, no inventar funcionalidades mientras programan.

---

## 2. Actores

### Lector

Usuario que busca uno o más libros.

Puede:

- Buscar libros mediante una API externa.
- Seleccionar el libro correcto.
- Crear y publicar una solicitud.
- Indicar precio máximo opcional.
- Indicar si acepta libro nuevo, usado o cualquiera.
- Indicar ubicación.
- Indicar preferencias de entrega.
- Agregar notas.
- Consultar sus solicitudes.
- Recibir y revisar ofertas.
- Aceptar una oferta.
- Acceder a los datos de contacto del vendedor una vez aceptada la oferta.
- Cancelar sus propias solicitudes cuando las reglas de negocio lo permitan.

### Vendedor

Tiene una experiencia diferente a la del lector. No necesita mantener un catálogo de libros en el MVP.

Puede:

- Ver solicitudes publicadas por lectores.
- Buscar y filtrar solicitudes.
- Consultar el detalle de una solicitud.
- Indicar que dispone del libro.
- Crear una oferta.
- Indicar precio.
- Indicar si el libro es nuevo o usado.
- Describir su condición.
- Agregar información adicional.
- Definir datos de contacto.
- Consultar sus ofertas.
- Cancelar ofertas cuando corresponda.
- Ver cuándo una oferta ha sido aceptada.

El modelo inicial es **request-driven**, no inventory-driven: el vendedor responde a solicitudes existentes en vez de publicar todo su inventario.

### Administrador

Interfaz independiente para administración y moderación.

Puede:

- Ver dashboard de estadísticas.
- Consultar usuarios.
- Consultar historial global de solicitudes.
- Consultar ofertas.
- Ver actividad de la plataforma.
- Cancelar/moderar publicaciones.
- Gestionar reportes.
- Suspender usuarios cuando corresponda.
- Consultar publicaciones canceladas.
- Realizar otras acciones administrativas que se especifiquen posteriormente.

Los usuarios normales no pueden registrarse como administradores.

---

## 3. Principios de producto

### Libro y solicitud son entidades diferentes

Un **Libro** representa una obra/edición identificable y sus metadatos.

Ejemplo:

```text
Libro
- externalId
- ISBN
- título
- autores
- portada
- editorial
- fecha/año de publicación
- descripción
- categorías
```

Una **Solicitud** representa que un lector está buscando ese libro.

Ejemplo:

```text
Solicitud #154
Lector: Juan
Libro: El Hobbit
Precio máximo: $15.000
Ubicación: Concepción
Estado: PUBLICADA
```

Un mismo libro puede estar asociado a muchas solicitudes.

### Los metadatos del libro provienen de una API externa

No pedir al lector que escriba manualmente título, autor, ISBN, portada, editorial, etc. cuando esa información pueda obtenerse desde una API.

APIs consideradas:

1. Google Books API — candidata principal para el MVP.
2. Open Library API — alternativa abierta.
3. ISBNdb — posible alternativa futura.

La búsqueda debería permitir, como mínimo:

- título;
- autor;
- ISBN.

La aplicación debe guardar la referencia externa y los datos mínimos necesarios para mantener consistencia y presentar el libro.

### La plataforma conecta, no ejecuta la transacción

En el MVP no implementar:

- pagos;
- logística;
- envíos;
- checkout;
- escrow;
- chat interno;
- inventario completo de vendedores.

Cuando una oferta es aceptada, la aplicación muestra los datos de contacto permitidos por el vendedor, por ejemplo:

- teléfono;
- correo electrónico;
- dirección o lugar de entrega/librería.

La coordinación ocurre fuera de la plataforma.

---

## 4. Flujo principal del producto

```text
LECTOR
   |
   v
Busca libro en API
   |
   v
Selecciona libro
   |
   v
Crea solicitud
   |
   v
Publica solicitud
   |
   +----------------------+
                          |
                          v
                     VENDEDOR
                          |
                          v
                  Ve solicitudes
                          |
                          v
                  Abre solicitud
                          |
                          v
                    Crea oferta
                          |
   +----------------------+
   |
   v
LECTOR recibe oferta
   |
   v
Revisa oferta
   |
   v
Acepta oferta
   |
   v
Obtiene datos de contacto
   |
   v
Coordinación fuera de la plataforma
```

Este recorrido es el **happy path prioritario del MVP**.

---

## 5. Flujo del lector

### Login / registro

El usuario puede iniciar sesión, registrarse y recuperar contraseña.

En el registro debe escoger un rol permitido, inicialmente:

- Lector
- Vendedor

Administrador no es una opción de registro público.

### Home / dashboard del lector

Objetivo principal:

> “¿Qué libro estoy buscando y qué está pasando con mis solicitudes?”

Elementos principales:

- navegación;
- buscador de libros;
- solicitudes recientes;
- cantidad/estado de ofertas;
- acceso a “Mis solicitudes”.

### Buscar libro

Consultar API externa por título, autor o ISBN.

Cada resultado puede mostrar:

- portada;
- título;
- autor;
- editorial;
- ISBN;
- acción “Seleccionar”.

### Crear solicitud

Campos previstos:

- libro seleccionado;
- precio máximo opcional;
- condición aceptada:
  - cualquiera;
  - nuevo;
  - usado;
- ubicación;
- preferencia de entrega:
  - presencial;
  - envío;
  - cualquiera/ambas;
- información adicional/notas.

Acción principal:

`PUBLICAR SOLICITUD`

### Solicitud publicada

Mostrar confirmación y permitir:

- ver solicitud;
- volver al inicio.

### Detalle de solicitud

Mostrar:

- libro;
- datos de la solicitud;
- estado;
- ofertas recibidas;
- acceso al detalle de cada oferta;
- opción de cancelar cuando corresponda.

### Detalle de oferta

Mostrar:

- libro;
- precio;
- condición;
- vendedor;
- información adicional.

No revelar necesariamente todos los datos privados de contacto antes de la aceptación; esto debe quedar definido por las specs de privacidad.

Acción principal:

`ACEPTAR OFERTA`

### Oferta aceptada

Mostrar los datos de contacto habilitados por el vendedor y dejar explícito que la coordinación de compra/entrega se realiza directamente entre lector y vendedor.

---

## 6. Flujo del vendedor

### Dashboard

Objetivo:

> Encontrar lectores que buscan libros que el vendedor tiene disponibles.

Mostrar:

- buscador de solicitudes;
- filtros;
- solicitudes recientes.

Filtros previstos:

- ubicación;
- precio máximo;
- condición;
- otros que sean definidos por specs posteriores.

### Detalle de solicitud

Mostrar:

- libro;
- ISBN;
- portada;
- ubicación;
- precio máximo;
- condición aceptada;
- notas del lector.

Acción principal:

`PUEDO OFRECERLO`

### Crear oferta

Campos:

- precio;
- estado: nuevo/usado;
- condición;
- información adicional;
- métodos/datos de contacto que recibirá el lector tras aceptar.

Datos de contacto posibles:

- teléfono;
- correo;
- lugar/dirección de entrega.

Acción:

`PUBLICAR OFERTA`

### Mis ofertas

Permitir filtrar, al menos conceptualmente, por:

- todas;
- activas;
- aceptadas;
- finalizadas.

Mostrar libro, precio, condición, estado y acciones permitidas.

---

## 7. Flujo de administrador

La administración debe considerarse una experiencia independiente de lector/vendedor.

### Dashboard

Métricas potenciales:

- usuarios;
- lectores;
- vendedores;
- solicitudes totales;
- solicitudes activas;
- solicitudes con ofertas;
- solicitudes resueltas;
- ofertas;
- actividad reciente.

### Gestión

Secciones previstas:

- usuarios;
- solicitudes;
- ofertas;
- libros;
- historial;
- reportes;
- publicaciones canceladas.

### Moderación

Acciones previstas:

- cancelar solicitud;
- eliminar/moderar contenido;
- suspender usuario;
- revisar reportes.

Toda acción administrativa sensible debe quedar auditada cuando se especifique el sistema de auditoría.

---

## 8. Estados de dominio

Los estados exactos deberán consolidarse en una spec antes de implementar. El diseño conceptual actual es:

### Solicitud

```text
BORRADOR
   |
   v
PUBLICADA
   |
   v
CON_OFERTAS
   |
   v
RESUELTA
```

Transiciones adicionales:

```text
PUBLICADA   -> CANCELADA
CON_OFERTAS -> CANCELADA
PUBLICADA   -> EXPIRADA   (posible versión futura)
```

### Oferta

Modelo conceptual:

```text
PUBLICADA
   |
   +--> ACEPTADA
   |
   +--> RECHAZADA
   |
   +--> CANCELADA
```

Evitar implementar transiciones que no estén expresamente permitidas en las reglas de negocio.

---

## 9. Modelo de dominio inicial

Modelo conceptual, sujeto a refinamiento mediante specs:

```text
User
- id
- name
- email
- password/authIdentity
- role
- status
- createdAt

Book
- id
- externalProvider
- externalId
- isbn
- title
- authors
- coverUrl
- publisher
- publishedDate

BookRequest
- id
- readerId
- bookId
- maxPrice?
- acceptedCondition
- location
- deliveryPreference
- notes?
- status
- createdAt
- updatedAt

Offer
- id
- requestId
- sellerId
- price
- bookCondition
- conditionDescription?
- notes?
- status
- createdAt
- updatedAt

SellerContact
- sellerId
- phone?
- email?
- addressOrMeetingPoint?
```

No asumir que este esquema es definitivo. Las specs de dominio tienen precedencia.

---

## 10. Alcance del MVP

El MVP debe demostrar el circuito completo:

```text
Buscar libro
-> crear solicitud
-> publicar
-> vendedor encuentra solicitud
-> vendedor crea oferta
-> lector recibe oferta
-> lector acepta
-> contacto externo
```

### Incluido

- autenticación;
- roles lector/vendedor/admin;
- búsqueda externa de libros;
- solicitudes;
- ofertas;
- estados básicos;
- datos de contacto;
- administración básica;
- validaciones;
- permisos;
- manejo de errores;
- pruebas del flujo crítico.

### Fuera del MVP salvo spec explícita

- pagos;
- chat interno;
- logística;
- seguimiento de envíos;
- catálogo/inventario completo del vendedor;
- scraping de librerías;
- precios automáticos;
- reservas complejas;
- reputación/calificaciones;
- recomendaciones avanzadas;
- matching automático;
- notificaciones sofisticadas.

---

## 11. Evolución posible

### V2

- matching automático entre solicitudes y vendedores;
- notificaciones;
- mejores filtros;
- expiración de solicitudes;
- reputación/calificaciones.

### V3

```text
Libro
 -> Solicitud
 -> Matching
 -> Oferta
 -> Chat
 -> Reserva
 -> Pago
 -> Entrega
 -> Calificación
```

En el futuro podría soportar tanto librerías como vendedores particulares, pero esto no debe contaminar el alcance del MVP.

---

## 12. Enfoque Spec-Driven Development

Regla principal:

> La IA no diseña el producto mientras programa. Implementa decisiones previamente especificadas.

No utilizar prompts del tipo:

> “Créame una aplicación donde los usuarios puedan buscar libros y venderlos.”

Preferir:

> “Lee SPEC-003. Implementa exclusivamente el caso de uso Crear solicitud de libro. No agregues funcionalidades fuera de la especificación.”

Cada spec debe tener una sola responsabilidad y criterios de aceptación verificables.

### Flujo de trabajo

```text
Idea
  |
  v
Product Discovery
  |
  v
Visión / alcance
  |
  v
User Stories
  |
  v
Requisitos y reglas de negocio
  |
  v
Modelo de dominio
  |
  v
Casos de uso
  |
  v
Wireframes / Figma
  |
  v
Arquitectura
  |
  v
Specs
  |
  v
Implementación por IA
  |
  v
Pruebas
  |
  v
Commit
  |
  v
Siguiente spec
```

---

## 13. Estructura documental recomendada

```text
docs/
|
+-- 00-product/
|   +-- VISION.md
|   +-- ACTORES.md
|   +-- ALCANCE_MVP.md
|
+-- 01-requirements/
|   +-- USER_STORIES.md
|   +-- REQUIREMENTS.md
|   +-- BUSINESS_RULES.md
|
+-- 02-domain/
|   +-- DOMAIN_MODEL.md
|   +-- ENTITIES.md
|   +-- STATE_MACHINES.md
|
+-- 03-use-cases/
|   +-- CU-001-registrar-usuario.md
|   +-- CU-002-buscar-libro.md
|   +-- CU-003-crear-solicitud.md
|   +-- CU-004-ver-solicitudes.md
|   +-- CU-005-crear-oferta.md
|   +-- ...
|
+-- 04-architecture/
|   +-- ARCHITECTURE.md
|
+-- 05-specs/
    +-- SPEC-001-auth.md
    +-- SPEC-002-book-search.md
    +-- SPEC-003-create-request.md
    +-- SPEC-004-seller-feed.md
    +-- SPEC-005-create-offer.md
    +-- ...
```

El código fuente debe comenzar cuando la base documental mínima correspondiente esté definida.

---

## 14. Orden de implementación recomendado

### Sprint 1 — Fundaciones

- proyecto;
- base de datos;
- arquitectura;
- autenticación;
- usuarios;
- roles y permisos.

### Sprint 2 — Primer flujo de lector

```text
Buscar libro
-> seleccionar libro
-> crear solicitud
-> publicar
```

### Sprint 3 — Vendedor

```text
Ver solicitudes
-> ver detalle
-> crear oferta
```

### Sprint 4 — Conexión

```text
Lector ve ofertas
-> revisa oferta
-> acepta
-> obtiene contacto
```

Al finalizar este sprint existe un MVP funcional de punta a punta.

### Sprint 5 — Administrador

- dashboard;
- usuarios;
- solicitudes;
- ofertas;
- moderación;
- historial.

### Sprint 6 — Calidad

- validaciones;
- seguridad;
- autorización;
- manejo de errores;
- pruebas;
- UX;
- auditoría donde corresponda.

---

## 15. Pantallas prioritarias para Figma

El primer prototipo navegable debe concentrarse en el flujo principal.

### Lector

1. Login.
2. Registro.
3. Dashboard lector.
4. Buscar libro.
5. Crear solicitud.
6. Solicitud publicada.
7. Detalle de solicitud / ofertas recibidas.
8. Detalle de oferta.
9. Oferta aceptada / contacto.

### Vendedor

10. Dashboard vendedor / solicitudes disponibles.
11. Detalle de solicitud.
12. Crear oferta.
13. Mis ofertas.

### Administrador

14. Dashboard.
15. Gestión de solicitudes.
16. Gestión de usuarios/reportes/moderación según prioridad.

La administración puede diseñarse después del prototipo principal lector-vendedor.

---

## 16. Guía UX

### Lector

La interfaz debe responder rápidamente:

> “¿Qué libros estoy buscando y qué está pasando con ellos?”

La búsqueda de libros debe ser protagonista.

### Vendedor

La interfaz debe responder:

> “¿Qué personas están buscando libros que puedo ofrecer?”

Las solicitudes y filtros son protagonistas.

### Administrador

Priorizar:

- visibilidad del estado del sistema;
- búsqueda;
- filtros;
- tablas;
- moderación;
- trazabilidad.

Las tres experiencias pueden compartir sistema visual, pero no necesitan compartir la misma navegación ni jerarquía de información.

---

## 17. Ejemplo de spec de implementación

```markdown
# SPEC-003 — Crear solicitud de libro

## Objetivo

Permitir que un lector autenticado publique una solicitud para un libro previamente seleccionado.

## Criterios de aceptación

1. El usuario debe estar autenticado.
2. El usuario debe tener permisos de lector.
3. Debe seleccionar un libro válido.
4. Puede ingresar un precio máximo opcional.
5. Debe seleccionar una condición aceptada.
6. Debe indicar ubicación.
7. Puede indicar preferencias de entrega.
8. Puede agregar notas.
9. La solicitud se crea inicialmente con el estado definido por las reglas de negocio.
10. No se puede crear una solicitud sin libro.
11. Un lector solo puede modificar/cancelar sus propias solicitudes salvo intervención administrativa.
```

Al pedir a un agente que implemente una spec:

```text
Lee SPEC-003.

Implementa exclusivamente esta especificación.

No agregues funcionalidades.
No cambies arquitectura sin necesidad.
No inventes nuevas pantallas ni reglas.

Antes de terminar:
- ejecuta las pruebas;
- verifica cada criterio de aceptación;
- informa los archivos modificados;
- informa cualquier criterio que no haya podido cumplirse.
```

---

## 18. Reglas para agentes de IA

1. Leer `AGENTS.md` y las specs relevantes antes de modificar código.
2. Tratar las specs como fuente de verdad.
3. No inventar requisitos.
4. No ampliar el alcance silenciosamente.
5. Si una decisión necesaria no está especificada y afecta comportamiento de negocio, detenerse y pedir aclaración o proponer la actualización de la spec.
6. No introducir pagos, chat, inventario u otras funciones fuera del MVP sin una spec explícita.
7. Respetar roles y autorización en backend, no solo ocultar elementos de UI.
8. Un lector no debe poder modificar recursos de otros lectores.
9. Un vendedor no debe poder modificar ofertas de otros vendedores.
10. Las acciones administrativas deben requerir rol administrativo.
11. Mantener separadas las entidades `Book`, `BookRequest` y `Offer`.
12. No duplicar innecesariamente información proveniente de la API de libros.
13. Validar datos externos antes de persistirlos.
14. Nunca confiar exclusivamente en datos enviados por el cliente para permisos, identidad o estados.
15. Las transiciones de estado deben respetar la máquina de estados definida.
16. Implementar una spec por vez siempre que sea posible.
17. Ejecutar pruebas antes de dar una tarea por terminada.
18. No declarar una spec completada si algún criterio de aceptación sigue incumplido.
19. Documentar decisiones arquitectónicas importantes.
20. Favorecer simplicidad y mantenibilidad por sobre abstracciones prematuras.

---

## 19. Decisiones todavía abiertas

No asumir respuestas a estos puntos sin una spec o ADR:

- stack frontend;
- stack backend;
- base de datos;
- proveedor de autenticación;
- Google Books vs Open Library como proveedor principal;
- estrategia exacta de persistencia/cache de metadatos externos;
- posibilidad de que una misma cuenta sea lector y vendedor;
- política de visibilidad de datos personales;
- qué ocurre exactamente con otras ofertas al aceptar una;
- si una solicitud puede aceptar más de una oferta;
- expiración de solicitudes;
- eliminación lógica vs física;
- notificaciones;
- definición exacta de “RESUELTA”;
- cierre/finalización de la transacción fuera de plataforma;
- sistema de reportes;
- auditoría administrativa.

Estas decisiones deben documentarse antes de que condicionen código importante.

---

## 20. Objetivo pedagógico del proyecto

Además de construir el producto, este proyecto busca enseñar a desarrollar software con IA de manera disciplinada.

El objetivo no es aprender a escribir:

> “Hazme una app.”

El objetivo es aprender a:

1. descubrir el problema;
2. definir el producto;
3. modelar el dominio;
4. escribir requisitos;
5. diseñar casos de uso;
6. crear wireframes;
7. tomar decisiones arquitectónicas;
8. convertir funcionalidades en specs pequeñas;
9. delegar implementación a agentes;
10. revisar, probar e iterar.

El agente de IA es un **implementador y colaborador técnico**, no el sustituto de las decisiones de producto.

---

## 21. Definición resumida del producto

> Plataforma de búsqueda bajo demanda de libros donde lectores publican qué libros necesitan, vendedores responden con ofertas y, tras aceptar una oferta, ambas partes coordinan la compra o entrega mediante contacto externo. El sistema incluye una interfaz administrativa para supervisión, estadísticas y moderación.
