# Plan de Fixes y Mejoras del Proyecto

Este documento consolida y desglosa las observaciones detectadas en la aplicación ([Observaciones.txt](file:///c:/Proyectos/Marketplace-de-Libros-/Observaciones.txt)), transformándolas en un backlog ordenado de tareas técnicas y funcionales para ser ejecutadas por el equipo de desarrollo.

---

## 📋 Orden de Ejecución Sugerido

El trabajo está estructurado en **4 fases lógicas** para respetar el principio de *Spec-Driven Development* (primero reglas de negocio y dominio en [store.py](file:///c:/Proyectos/Marketplace-de-Libros-/store.py), luego integraciones y finalmente ajustes de interfaz en [main.py](file:///c:/Proyectos/Marketplace-de-Libros-/main.py) y [libros.kv](file:///c:/Proyectos/Marketplace-de-Libros-/libros.kv)):

1. **Fase 1: Dominio y Máquina de Estados (Backend / Store)** — Tareas 1, 2 y 3.
2. **Fase 2: Servicios e Integraciones de Datos** — Tareas 4 y 5.
3. **Fase 3: Experiencia de Usuario y Filtros (Lector / Vendedor)** — Tareas 6 y 7.
4. **Fase 4: Rediseño y Moderación del Panel de Administración** — Tareas 8, 9, 10 y 11.

---

## 🛠️ Detalle de Tareas y Criterios de Aceptación

### 🔹 Fase 1: Dominio, Reglas de Negocio y Estados (`store.py`)

#### [x] Tarea 1: Estados intermedios en aceptación de ofertas y flujo de negociación

- **Observación original:** Al aceptar una oferta, las demás se rechazan automáticamente. Se requiere un estado intermedio para la oferta aceptada (ej. `"POR_CONCRETAR"` / `"EN_REVISION"`) y que las demás queden `"EN_ESPERA"` hasta confirmar el cierre final.
- **Alcance & Archivos:** [store.py](file:///c:/Proyectos/Marketplace-de-Libros-/store.py), [tests/](file:///c:/Proyectos/Marketplace-de-Libros-/tests)
- **Criterios de Aceptación:**
  - [x] Incorporar el estado de oferta `POR_CONCRETAR` (o `EN_TRATO`) y `EN_ESPERA`.
  - [x] Al aceptar una oferta inicialmente, la solicitud pasa a estado intermedio (ej. `EN_PROCESO` o `EN_COORDINACION`).
  - [x] Las otras ofertas pasan a `EN_ESPERA` (sin ser canceladas ni rechazadas definitivamente).
  - [x] Implementar la acción de *Confirmar Compra/Trato Concretado* (pasa la oferta a `ACEPTADA_FINAL`/`CONCRETADA`, la solicitud a `RESUELTA` y las demás ofertas a `RECHAZADA`).
  - [x] Implementar la acción de *Desistir/Cancelar Trato en Curso* (la oferta vuelve a estado previo o `RECHAZADA`, y las ofertas `EN_ESPERA` vuelven a estar activas).
  - [x] Crear tests unitarios que validen estas transiciones y casos límite.

---

#### [x] Tarea 2: Flexibilizar validación de condiciones para ofertas de vendedores

- **Observación original:** El estado del libro y preferencia de entrega indicados por el lector no deben bloquear rígidamente que un vendedor oferte una alternativa distinta.
- **Alcance & Archivos:** [store.py](file:///c:/Proyectos/Marketplace-de-Libros-/store.py), [main.py](file:///c:/Proyectos/Marketplace-de-Libros-/main.py)
- **Criterios de Aceptación:**
  - [x] Modificar la validación en `store.create_offer` para que un vendedor pueda ofertar cualquier condición (nuevo o usado) y método de entrega, incluso si difiere de lo preferido por el lector.
  - [x] En la UI del detalle de oferta, destacar visualmente cuando la condición ofrecida o método difiere de la preferencia original para informar con claridad al lector.
  - [x] Actualizar pruebas unitarias existentes que antes verificaban el bloqueo estricto.

---

#### [x] Tarea 3: Trazabilidad y motivos en cancelaciones administrativas

- **Observación original:** Si un administrador cancela una solicitud, al lector le figura como cancelada sin especificar que fue una moderación administrativa.
- **Alcance & Archivos:** [store.py](file:///c:/Proyectos/Marketplace-de-Libros-/store.py), [libros.kv](file:///c:/Proyectos/Marketplace-de-Libros-/libros.kv), [main.py](file:///c:/Proyectos/Marketplace-de-Libros-/main.py)
- **Criterios de Aceptación:**
  - [x] Agregar a `BookRequest` los campos opcionales `canceled_by_role` (ej. `'ADMIN'` | `'READER'`) y `cancellation_reason` (motivo de moderación).
  - [x] Al cancelar desde el panel de admin, solicitar/registrar un motivo.
  - [x] En la vista de "Detalle de Solicitud" del lector, si fue cancelada por admin, mostrar una alerta informativa: *"Esta solicitud fue cancelada por un administrador (Motivo: ...)"*.

---

### 🔹 Fase 2: Servicios, Búsqueda y Caché

#### [ ] Tarea 4: Caché local persistente para miniaturas y portadas de libros

- **Observación original:** Las miniaturas de los libros se pierden en "Crear solicitud" y en el dashboard principal (a veces cargan y a veces no).
- **Alcance & Archivos:** [books_api.py](file:///c:/Proyectos/Marketplace-de-Libros-/books_api.py), [main.py](file:///c:/Proyectos/Marketplace-de-Libros-/main.py), [libros.kv](file:///c:/Proyectos/Marketplace-de-Libros-/libros.kv)
- **Criterios de Aceptación:**
  - [ ] Implementar un manejador de descarga y caché local en disco (carpeta `.cache/covers/` o similar) para las URLs de portadas.
  - [ ] Si la descarga falla o el libro no tiene imagen, mostrar una portada por defecto / placeholder estilizado.
  - [ ] Garantizar que al seleccionar un libro en "Buscar libro", la referencia de la portada persista correctamente al navegar a "Crear solicitud" y al listarse en el Dashboard.

---

#### [ ] Tarea 5: Normalización de ubicaciones (Selector de Ciudad / Comuna)

- **Observación original:** La ubicación en "Crear solicitud" debe permitir seleccionar ciudades/comunas normalizadas (vía API), en lugar de texto libre con direcciones concretas.
- **Alcance & Archivos:** [store.py](file:///c:/Proyectos/Marketplace-de-Libros-/store.py), [main.py](file:///c:/Proyectos/Marketplace-de-Libros-/main.py), [libros.kv](file:///c:/Proyectos/Marketplace-de-Libros-/libros.kv)
- **Criterios de Aceptación:**
  - [ ] integración con API geográfica liviana catálogo/servicio de regiones y comunas/ciudades principales .
  - [ ] Reemplazar el campo de texto en "Crear solicitud" por un selector/buscador autocompletable de Comuna/Ciudad.
  - [ ] Asegurar que el filtro por ubicación del vendedor coincida exactamente con las ciudades/comunas normalizadas.

---

### 🔹 Fase 3: Experiencia de Usuario y Vistas (Lector y Vendedor)

#### [ ] Tarea 6: Filtrar solicitudes ya ofertadas en el Dashboard del Vendedor

- **Observación original:** En el dashboard del vendedor, los libros/solicitudes donde el vendedor ya envió una oferta deben desaparecer del feed principal.
- **Alcance & Archivos:** [store.py](file:///c:/Proyectos/Marketplace-de-Libros-/store.py), [main.py](file:///c:/Proyectos/Marketplace-de-Libros-/main.py)
- **Criterios de Aceptación:**
  - [ ] En la consulta de solicitudes para el feed del vendedor, excluir aquellas en las que el usuario actual ya posea una oferta activa.
  - [ ] Dichas solicitudes deben ser accesibles y gestionables exclusivamente desde la pantalla **"Mis Ofertas"**.

---

#### [ ] Tarea 7: Fijar cabecera de búsqueda y filtros (Layout Scrollable)

- **Observación original:** Al aplicar filtros, la pantalla se centra y desplaza el buscador y los controles. El buscador y filtros deben permanecer fijos arriba y solo la lista de tarjetas debe desplazarse.
- **Alcance & Archivos:** [libros.kv](file:///c:/Proyectos/Marketplace-de-Libros-/libros.kv), [main.py](file:///c:/Proyectos/Marketplace-de-Libros-/main.py)
- **Criterios de Aceptación:**
  - [ ] Reestructurar el layout KV: contenedor superior con tamaño fijo (`size_hint_y: None`) para buscador y filtros.
  - [ ] Contenedor inferior con `ScrollView` independiente para el listado de resultados.
  - [ ] Prevenir recentrados bruscos al refrescar o filtrar datos.

---

### 🔹 Fase 4: Rediseño y Gestión del Panel de Administración

#### [ ] Tarea 8: Diferenciación visual de tarjetas de métricas en Admin

- **Observación original:** Los resúmenes/métricas superiores en el panel de administración son difíciles de distinguir entre sí.
- **Alcance & Archivos:** [libros.kv](file:///c:/Proyectos/Marketplace-de-Libros-/libros.kv)
- **Criterios de Aceptación:**
  - [ ] Aplicar estilos diferenciados por color/chips (ej. azul para usuarios, verde para solicitudes resueltas, naranja para ofertas activas, etc.).
  - [ ] Mejorar la jerarquía visual de números y etiquetas.

---

#### [ ] Tarea 9: Navegación limpia en Admin (Menú / Tabs / Drawer)

- **Observación original:** Las secciones (Solicitudes, Usuarios, Ofertas, Actividad) sobrecargan la pantalla al estar todo junto.
- **Alcance & Archivos:** [main.py](file:///c:/Proyectos/Marketplace-de-Libros-/main.py), [libros.kv](file:///c:/Proyectos/Marketplace-de-Libros-/libros.kv)
- **Criterios de Aceptación:**
  - [ ] Implementar navegación por pestañas (`MDTabs`), menú desplegable (`MDDropdownMenu`) o barra lateral de navegación para separar cada entidad en su propia subvista.
  - [ ] Descongestionar la pantalla de inicio del Admin dejando únicamente métricas generales y accesos rápidos.

---

#### [ ] Tarea 10: Gestión de logs de actividad y exportación/descarga

- **Observación original:** El registro de actividad satura la interfaz visual; debería registrarse en segundo plano y permitir consulta/descarga bajo demanda.
- **Alcance & Archivos:** [store.py](file:///c:/Proyectos/Marketplace-de-Libros-/store.py), [main.py](file:///c:/Proyectos/Marketplace-de-Libros-/main.py), [libros.kv](file:///c:/Proyectos/Marketplace-de-Libros-/libros.kv)
- **Criterios de Aceptación:**
  - [ ] Remover el bloque de actividad permanente de la vista principal del Admin.
  - [ ] Crear un botón/acción "Exportar Logs de Actividad" (generando archivo `.log` o `.csv`/`.json`).
  - [ ] Vista dedicada de auditoría con paginación/búsqueda si se desea consultar en pantalla.

---

## 📌 Resumen de Dependencias y Pruebas

- Antes de cerrar cada tarea, verificar que todos los tests sigan pasando ejecutando:

  ```bash
  python -m unittest discover -s tests -v
  ```

- Al completar cambios que modifiquen reglas de negocio o estados, actualizar [CONTEXTO.md](file:///c:/Proyectos/Marketplace-de-Libros-/CONTEXTO.md).
