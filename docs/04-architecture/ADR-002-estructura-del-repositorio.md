# ADR-002 — Estructura del repositorio por responsabilidad

## Estado

Aceptada

## Contexto

La primera reorganización MVC separó las vistas y los controladores, pero dejó
el modelo, las integraciones, los recursos y varios documentos en la raíz. La
solicitud de completar la organización requiere reubicar esos archivos sin
romper los comandos habituales, las rutas de recursos ni los datos persistidos.

Esta decisión amplía la ubicación de archivos definida inicialmente en
[ADR-001](./ADR-001-mvc-incremental.md); no altera sus límites de responsabilidad
MVC.

## Decisión

Organizar el proyecto de la siguiente manera:

```text
main.py                         Punto de entrada
models/store.py                 Modelo y reglas de dominio
controllers/                    Coordinación y controladores de pantalla
views/                          Componentes y layout KV
services/                       Persistencia e integraciones
data/                           Catálogos y configuración
data/user/data.json             Persistencia local de escritorio (ignorada)
assets/fonts/                   Fuentes tipográficas
assets/screenshots/             Capturas de la aplicación
docs/                           Documentación y presentación
tests/                          Pruebas automatizadas
```

Los archivos de descubrimiento y configuración de herramientas permanecen en la
raíz: `AGENTS.md`, `CLAUDE.md`, `CONTEXTO.md`, `README.md`, `.gitignore`,
`requirements.txt`, `buildozer.spec` y `main.py`. También se conserva `.agents/`
en su ubicación raíz.

La persistencia de escritorio pasa a `data/user/data.json`. Al iniciar, la
aplicación migra el antiguo `data.json` raíz únicamente si el nuevo destino no
existe. Android continúa guardando en `user_data_dir`.

## Consecuencias

- Las rutas del código dejan de depender de que los módulos estén en la raíz y
  se resuelven desde la raíz del proyecto.
- La URL de configuración remota cambia para reflejar `data/remote_config.json`.
- Buildozer conserva `main.py` como entrada y empaqueta únicamente el código y
  los recursos requeridos por la aplicación.
- Las referencias de documentación se actualizan junto con cada movimiento.
- La decisión es estructural: no introduce cambios funcionales ni de dominio.
