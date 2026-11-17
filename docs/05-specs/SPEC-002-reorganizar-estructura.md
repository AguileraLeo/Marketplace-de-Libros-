# SPEC-002 — Reorganizar la estructura del proyecto

## Objetivo

Agrupar los archivos existentes por responsabilidad para completar la organización
MVC, manteniendo el comportamiento de la aplicación y sus instrucciones de
compilación.

## Estructura destino

- `main.py`: punto de entrada requerido por la ejecución y el empaquetado Kivy.
- `models/store.py`: entidades, estados, permisos y reglas de dominio.
- `controllers/`: ciclo de vida, navegación y controladores de pantalla.
- `views/`: widgets reutilizables y `libros.kv`.
- `services/`: persistencia, notificaciones, búsqueda de libros y ubicaciones.
- `data/`: catálogos y configuración remota; `data/user/data.json` para la
  persistencia local de escritorio.
- `assets/`: fuentes tipográficas y capturas.
- `docs/`: documentación de producto, arquitectura, planificación, proceso y
  presentación.
- `tests/`: pruebas automatizadas.

Permanecen en la raíz los archivos de descubrimiento, configuración y entrada
que dependen de esa ubicación: `AGENTS.md`, `CLAUDE.md`, `CONTEXTO.md`,
`README.md`, `.gitignore`, `requirements.txt`, `buildozer.spec` y `main.py`.
También permanecen allí `.agents/` (configuración de agentes) y los archivos
generados/ignorados por herramientas.

## Alcance

- Reubicar los módulos, recursos y documentos existentes según la estructura
  anterior y actualizar todas sus referencias.
- Mantener `python main.py`, `python -m unittest discover -s tests -v` y el
  empaquetado Android como flujos de trabajo soportados.
- Migrar sin pérdida el `data.json` de escritorio que se encuentre en la raíz
  al nuevo directorio `data/user/`; no sobrescribir un archivo de destino ya
  existente.
- Mantener la caché de portadas fuera del código fuente.
- Actualizar la URL remota para que apunte al archivo reubicado en GitHub.
- No modificar reglas de dominio, pantallas, estados ni comportamiento de
  producto.

## Criterios de aceptación

1. Los módulos de modelo, vista, controlador y servicios están ubicados en sus
   carpetas correspondientes y todos los imports se resuelven.
2. Los recursos de comunas, configuración, fuentes y capturas se cargan desde
   sus nuevas rutas.
3. La aplicación conserva `main.py` como punto de entrada y carga las 19
   pantallas.
4. Los datos locales existentes se preservan; si existe el archivo anterior y
   aún no existe el nuevo, se migra sin sobrescritura.
5. Las pruebas automatizadas pasan y no se agregan dependencias.
6. La configuración de Buildozer incluye los recursos necesarios y excluye
   datos locales, pruebas, documentación y capturas.
7. Los documentos y enlaces internos reflejan las rutas nuevas.
