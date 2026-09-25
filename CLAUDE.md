# Instrucciones para asistentes de IA

Este archivo lo cargan automáticamente Claude Code y otras herramientas de IA. Las reglas del proyecto están en `AGENTS.md` y el estado actual en `CONTEXTO.md`:

@AGENTS.md
@CONTEXTO.md

## Reglas de trabajo con IA en este repositorio

1. **Idioma:** responder, comentar y documentar en español.
2. **Spec primero:** implementar solo lo que esté en una spec o en `AGENTS.md`. Si falta una decisión de negocio (AGENTS.md §19), detenerse y preguntar; no inventarla.
3. **Dominio en `store.py`:** toda regla de negocio, transición de estado y chequeo de permisos vive en `store.py`. `main.py` y `libros.kv` solo presentan y llaman al dominio.
4. **Pruebas:** agregar o actualizar tests en `tests/` para cada regla nueva y correr `python -m unittest discover -s tests -v` antes de dar algo por terminado.
5. **Stack fijo:** Python 3.10/3.11 + KivyMD 2.0 (API 2.x: `MDButton`, `MDButtonText`, etc.; no usar la API 1.x). No cambiar de stack ni agregar dependencias sin acordarlo con el equipo.
6. **Sin base de datos por ahora:** no introducir persistencia sin un ADR/spec aprobado.
7. **Trabajo en equipo:** varias personas modifican el proyecto. Trabajar en una rama, hacer cambios acotados y no reformatear archivos completos sin necesidad.
8. **Al cerrar una tarea:** informar los archivos modificados, los criterios cumplidos y los no cumplidos, y actualizar `CONTEXTO.md` si cambió el estado del proyecto.

## Comandos

```bash
.venv\Scripts\activate                       # Windows
pip install -r requirements.txt
python main.py                               # ejecutar la app
python -m unittest discover -s tests -v      # pruebas
```
