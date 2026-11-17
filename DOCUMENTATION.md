# BookWho? — Medición y evaluación de funcionalidad (RA3)

Este archivo documenta lo que pide el curso para la Evaluación 4: el registro de eventos, los
KPIs, cómo se calculan y cómo se aplica el método MJV App. La documentación técnica completa
del código (pantallas, dominio, servicios, pruebas) está en [`docs/04-architecture/DOCUMENTACION.md`](docs/04-architecture/DOCUMENTACION.md).

## 1. Estado actual

| Parte | Estado |
|---|---|
| Registro de eventos (`Store._log` en `models/store.py` → `data.json`) | Implementado |
| Cálculo de KPIs y gráfico (`analitica.py`) | Implementado y verificado con pruebas automáticas (`tests/test_analitica.py`) usando datos de prueba |
| **Datos reales de uso** | **Todavía no hay.** Al 17-11-2026 el `data.json` no tiene eventos de usuarios reales. Ninguna cifra de este documento es un resultado: los resultados se completan en la sección 7 después del periodo de recolección. |

## 2. Del problema (RA1) a los KPIs: método MJV App

La encuesta del diagnóstico ([`FUNDAMENTACION-UX-UI.md`](docs/01-requirements/FUNDAMENTACION-UX-UI.md), 18 respuestas)
mostró que 17 de 18 personas (94,4 %) buscaron un libro sin encontrarlo, que 14 de 18 (77,8 %)
tardaron 15 minutos o más y que 14 de 16 (87,5 %) usarían el modelo "pido y me ofrecen". Los
KPIs miden si la app responde a esas tres hipótesis.

| Paso | En BookWho? |
|---|---|
| **Medir** | Los 3 KPIs de la sección 4, definidos a partir de la encuesta, y los eventos que los alimentan (sección 3). Las metas se fijan **antes** de recolectar, para no ajustarlas a los resultados. |
| **Jugar** | Periodo de uso real con lectores y vendedores. **Por definir por el equipo:** fechas, número de participantes y dispositivo(s). |
| **Validar** | Comparar cada KPI con su meta y decidir: mantener, ajustar la app y volver a medir (es un ciclo). |

## 3. Registro de eventos

- **Dónde se registra:** `Store._log()` en `models/store.py`. Se llama dentro de cada caso de uso, después
  de validar, así que solo queda registrado lo que realmente cambió datos.
- **Estructura** (`ActivityEntry`): `at` (fecha y hora local del dispositivo, formato ISO),
  `actor_id` (quién), `action` (nombre del evento) y `detail` (contexto en texto).
- **Dónde se guarda:** en `data.json`, clave `"activity"`. En el PC queda en
  `data/user/data.json`; en Android, en la carpeta privada de la app (`user_data_dir`). `data.json` no se
  sube al repositorio (`.gitignore`) ni se incluye en el APK (`buildozer.spec`).

| Evento (`action`) | Cuándo | `detail` |
|---|---|---|
| `login` | Inicio de sesión | `<correo> inició sesión` |
| `registro` | Cuenta nueva | `Nuevo lector: <correo>` / `Nuevo vendedor: <correo>` |
| `solicitud_publicada` | El lector publica | `Solicitud #N · <título>` |
| `solicitud_cancelada` | Cancela el lector o modera el admin | `Solicitud #N cancelada (lector)` |
| `oferta_publicada` | El vendedor oferta | `Oferta #M para solicitud #N · $precio` |
| `oferta_cancelada` | El vendedor retira una oferta | `Oferta #M cancelada` |
| `oferta_por_concretar` | El lector acepta para coordinar | `Oferta #M por concretar · solicitud #N en coordinación` |
| `trato_concretado` | El lector confirma la compra | `Oferta #M concretada · solicitud #N resuelta` |
| `trato_desistido` | Lector o vendedor desiste | `Coordinación de oferta #M cancelada · solicitud #N reactivada` |
| `usuario_suspendido` / `usuario_reactivado` | Moderación del admin | `<correo> suspendido` |

**Privacidad:** `login`, `registro` y `usuario_*` guardan correos en `detail`. Por eso `data.json`
no se comparte ni se sube; para el informe solo se usan los conteos que imprime `analitica.py`,
que nunca muestra el detalle de los eventos.

**Formato estable:** `analitica.py` obtiene el número de solicitud y de oferta desde `detail`
(`Solicitud #N`, `Oferta #M`). `tests/test_analitica.py` genera eventos con la app real y
comprueba que se interpretan todos: si alguien cambia la redacción en `models/store.py`, la prueba
falla. Si aun así aparece un evento ilegible, el script lo informa en vez de calcular mal sin
avisar.

## 4. KPIs

| KPI | Fórmula | Eventos | Pregunta (hipótesis de la encuesta) |
|---|---|---|---|
| **1. Tasa de resolución** (principal) | solicitudes con `trato_concretado` ÷ solicitudes publicadas × 100 | `solicitud_publicada`, `trato_concretado` | ¿El lector consigue el libro que no encontraba? |
| **2. Tasa de respuesta** | solicitudes con al menos una `oferta_publicada` ÷ solicitudes publicadas × 100 | `solicitud_publicada`, `oferta_publicada` | ¿Los vendedores responden? Sin respuesta, el modelo "pido y me ofrecen" no funciona. |
| **3. Horas hasta la primera oferta** | mediana de (hora de la primera `oferta_publicada` − hora de `solicitud_publicada`), solo solicitudes que recibieron oferta | los mismos, con su hora | ¿Se acorta la búsqueda que hoy toma 15 minutos o más? |

Métricas descriptivas, que **no** son KPI: eventos por día, eventos por tipo y usuarios activos.

Reglas de cálculo:

- La unidad es la **solicitud**. El denominador son las solicitudes publicadas por usuarios reales
  (incluye las que después se cancelaron).
- Solo cuentan las ofertas de vendedores reales, y un trato concretado con una cuenta excluida no
  cuenta como resuelto.
- Si no hay solicitudes, los KPI 1 y 2 valen 0 % (no se divide por cero) y el KPI 3 queda vacío.

## 5. Cómo calcularlos: `analitica.py`

Se ejecuta en el PC:

```bash
python analitica.py                    # usa data/user/data.json (los datos de la app en el PC)
python analitica.py ruta/a/data.json   # otro archivo (uno por dispositivo)
```

- **Excluye** las 5 cuentas demo (`DEMO_USERS` en `models/store.py`, por correo exacto) y las del equipo:
  antes de analizar, agreguen a `CORREOS_EQUIPO` (en `analitica.py`) los correos con que probaron
  la app. Informa cuántos eventos y cuentas excluyó.
- **Imprime** el periodo, los eventos por tipo, el uso diario, los usuarios activos y los 3 KPIs,
  más una advertencia si algún evento no se pudo interpretar.
- **Genera `kpis.png`** (eventos por día y KPIs 1 y 2; el título indica periodo, usuarios y
  mediana del KPI 3) si `matplotlib` está instalado en el PC (`pip install matplotlib`). No forma
  parte de `requirements.txt` ni del APK porque la app no lo usa.
- **Sacar el `data.json` del teléfono** (APK de depuración y depuración USB activada):

  ```bash
  adb exec-out run-as cl.uct.bookwho cat files/data.json > data_telefono.json
  python analitica.py data_telefono.json
  ```

  **Importante:** desinstalar la app, o tener que hacerlo para instalar un APK firmado con otra
  llave, **borra este archivo**. Respáldenlo antes de reinstalar durante el periodo de recolección
  (ver la nota de firma en el `README.md`).

## 6. Limitaciones metodológicas (declarar en el informe)

1. **Muestra pequeña y periodo corto:** los resultados son indicativos, no estadísticamente
   significativos.
2. **Corte al final del periodo:** las solicitudes publicadas poco antes del cierre no alcanzan
   a recibir respuesta, lo que hace bajar los KPI 1 y 2.
3. **El KPI 3 no incluye las solicitudes sin ofertas:** hay que leerlo junto al KPI 2.
4. **"Trato concretado" lo declara el lector:** la app no verifica que la entrega ocurrió.
5. **Un archivo por dispositivo:** cada teléfono numera sus solicitudes desde 1. Se analiza cada
   `data.json` por separado; no se juntan ni se suman.
6. **Hora local del dispositivo, sin zona horaria:** las diferencias de tiempo son válidas dentro
   de un mismo teléfono.
7. **Datos demo vs. reales:** la semilla de demo no genera eventos (`build_demo_store` vacía el
   registro), pero cualquier uso posterior de las cuentas demo sí queda registrado; `analitica.py`
   lo excluye. Los ensayos del equipo con cuentas propias se excluyen con `CORREOS_EQUIPO`.
8. **No se registran pantallas vistas ni errores de validación:** no se puede medir el abandono
   antes de publicar ni la frecuencia de errores.
9. **Una oferta cuenta como respuesta aunque después se cancele:** el vendedor sí respondió.

## 7. Resultados

**Pendiente: completar con los datos reales después del periodo de recolección.**

| Dato | Valor |
|---|---|
| Periodo de recolección | — |
| Dispositivo(s) analizado(s) | — |
| Usuarios reales activos | — |
| Solicitudes publicadas | — |
| KPI 1 · Tasa de resolución (meta: —) | — |
| KPI 2 · Tasa de respuesta (meta: —) | — |
| KPI 3 · Horas hasta la primera oferta (meta: —) | — |

Gráfico: `kpis.png`, generado con `analitica.py` a partir de esos mismos datos.
