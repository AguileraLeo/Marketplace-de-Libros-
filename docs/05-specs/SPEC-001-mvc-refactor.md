# SPEC-001 — Organización MVC incremental

## Objetivo

Reorganizar la aplicación existente en límites MVC claros, conservando el flujo
actual y sin agregar comportamiento de producto.

La organización física inicial de archivos fue ampliada por
[SPEC-002](./SPEC-002-reorganizar-estructura.md).

**Nota de evolución:** las ubicaciones mencionadas en esta especificación
describen la primera etapa. Actualmente el dominio está en `models/store.py` y
la vista KV en `views/libros.kv`.

## Alcance

- Extraer los widgets Kivy reutilizables desde `main.py` a `views/components.py`.
- Extraer las pantallas y sus adaptadores de eventos a
  `controllers/screen_controllers.py`.
- Mover `DemoLibrosApp` a `controllers/app_controller.py`.
- Mantener `libros.kv`, `store.py`, los servicios y las integraciones en sus
  rutas actuales.
- Dejar `main.py` como punto de entrada.

## Criterios de aceptación

1. `python main.py` continúa siendo el punto de entrada de la aplicación.
2. Las clases referenciadas por `libros.kv` se registran antes de cargar KV.
3. Las reglas de negocio, permisos y transiciones permanecen en `store.py`.
4. Las pantallas conservan sus acciones, navegación y estado visual actuales.
5. No se agregan dependencias ni se cambia el flujo de usuario.
6. La suite existente de pruebas pasa sin cambios de comportamiento.
