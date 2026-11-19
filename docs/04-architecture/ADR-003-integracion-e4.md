# ADR-003 — Integración E4: analítica, documentación entregable y limpieza

## Estado

Aceptada

Complementa [ADR-002](./ADR-002-estructura-del-repositorio.md): conserva su estructura MVC y
ubica lo que se agregó en la Evaluación 4.

## Contexto

En la E4 se unieron dos líneas de trabajo paralelas: la reorganización MVC (ADR-001 y ADR-002)
y la medición RA3 (registro de eventos, KPIs y `analitica.py`), que se había hecho sobre la
estructura anterior. Además, el repositorio tenía archivos que no son parte de la entrega: la
carpeta `.agents/` (skills de un asistente de IA, unas 95.000 líneas) y copias duplicadas en
`pitch/`.

## Decisión

- `simulador.py` (SPEC-003) también queda en la raíz y fuera del APK, por la misma razón que
  `analitica.py`. Sus datos van a `data/simulacion/`, que Git ignora.
- `analitica.py` queda en la raíz, junto a `main.py`: es el punto de entrada de la herramienta
  de medición que se ejecuta en el PC. Lee el modelo (`models/store.py`), pero la app no lo
  importa y `buildozer.spec` lo excluye del APK.
- `DOCUMENTATION.md` queda en la raíz porque el curso lo pide como entregable del repositorio.
  La documentación técnica sigue en `docs/04-architecture/DOCUMENTACION.md`.
- `.agents/` no se versiona (`.gitignore`): es configuración local de herramientas, no código
  de la app. El uso de IA se declara en `docs/06-process/USO_IA.md`.
- La landing del pitch pasa a `docs/presentations/pitch/`, sin sus copias de `presentacion.html`
  y de las capturas (los originales están en `docs/presentations/` y `assets/screenshots/`).
- `docs/05-planning/` se une a `docs/06-process/`: era un solo documento de proceso y repetía el
  número 05 de `docs/05-specs/`.
- Se ignoran los archivos exportados de teléfonos (`data_*.json`) y los respaldos `.corrupto` y
  `.tmp`, porque pueden contener correos de participantes.

## Consecuencias

- La raíz solo tiene puntos de entrada (`main.py`, `analitica.py`), configuración y los
  documentos que piden las herramientas y el curso.
- Quien tenga `.agents/` en su copia local la pierde al actualizar el repositorio y debe
  recuperarla desde el historial si la usa.
