# ADR-001 — Organización MVC incremental

## Estado

Aceptada

La ubicación inicial de `store.py` y `libros.kv` se amplía posteriormente en
[ADR-002](./ADR-002-estructura-del-repositorio.md); se conservan los límites de
responsabilidad definidos aquí.

## Contexto

La aplicación KivyMD ya separa las reglas de dominio en `store.py` y el layout
declarativo en `libros.kv`, pero `main.py` mezcla el inicio de la aplicación,
widgets reutilizables, pantallas y coordinación de eventos.

## Decisión

Reorganizar la presentación y la coordinación sin alterar el comportamiento:

- `store.py` permanece como modelo/dominio y conserva sus validaciones,
  permisos y transiciones.
- `libros.kv` permanece como vista declarativa.
- `views/components.py` contiene widgets reutilizables de presentación.
- `controllers/screen_controllers.py` contiene las pantallas Kivy que reciben
  eventos, actualizan su estado visual y llaman a los casos de uso del modelo.
- `controllers/app_controller.py` contiene `DemoLibrosApp`, navegación,
  configuración visual y coordinación de servicios.
- `main.py` queda como punto de entrada y configuración inicial de ventana.
- Los servicios e integraciones existentes continúan en sus módulos actuales.

Las pantallas Kivy actúan como adaptadores de controlador para sus vistas KV.
Las reglas de negocio y autorización no se trasladan a las vistas ni a los
controladores.

## Consecuencias

- Los módulos quedan agrupados por responsabilidad y el punto de entrada se
  reduce.
- Los archivos `libros.kv` y `store.py` conservan sus rutas para minimizar
  cambios y evitar introducir una migración de dominio en el mismo paso.
- Una separación posterior de casos de uso/repositorios requerirá una decisión
  y especificación propias.
