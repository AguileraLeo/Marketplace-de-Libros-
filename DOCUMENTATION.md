# BookWho? — Medición y evaluación de funcionalidad (RA3)

Este archivo documenta lo que pide el curso para la Evaluación 4: el registro de eventos, los
KPIs, cómo se calculan y cómo se aplica el método MJV App. La documentación técnica completa
del código (pantallas, dominio, servicios, pruebas) está en [`docs/04-architecture/DOCUMENTACION.md`](docs/04-architecture/DOCUMENTACION.md).

## 1. Estado actual

| Parte | Estado |
|---|---|
| Registro de eventos (`Store._log` en `models/store.py` → `data.json`) | Implementado |
| Cálculo de KPIs y gráfico (`analitica.py`) | Implementado y verificado con pruebas automáticas (`tests/test_analitica.py`) usando datos de prueba |
| Metas de KPIs | Definidas el 19-11-2026 para el próximo ciclo de evaluación de 14 días; criterios y alcance en la sección 4.1. |
| **Datos reales de uso** | **Prueba en vivo mínima** el 18-11-2026: 4 cuentas que no son del equipo publicaron 3 solicitudes en el servidor compartido. No alcanza para evaluar los KPIs (sección 7.4). |
| **Datos simulados** (autorizados por el docente) | Generados con `simulador.py` (SPEC-003): 14 días, 24 lectores y 10 vendedores ficticios. Resultados en la sección 7.1, siempre rotulados como simulados. |

## 2. Del problema (RA1) a los KPIs: método MJV App

La encuesta del diagnóstico ([`FUNDAMENTACION-UX-UI.md`](docs/01-requirements/FUNDAMENTACION-UX-UI.md), 18 respuestas)
mostró que 17 de 18 personas (94,4 %) buscaron un libro sin encontrarlo, que 14 de 18 (77,8 %)
tardaron 15 minutos o más y que 14 de 16 (87,5 %) usarían el modelo "pido y me ofrecen". Los
KPIs miden si la app responde a esas tres hipótesis.

| Paso | En BookWho? |
|---|---|
| **Medir** | Los 3 KPIs de la sección 4, definidos a partir de la encuesta, y los eventos que los alimentan (sección 3). Las metas de la sección 4.1 se fijan antes de la próxima recolección. La simulación histórica se generó cuando aún no había metas documentadas. |
| **Jugar** | Periodo **simulado** del 3 al 16 de noviembre de 2026: 24 lectores y 10 vendedores ficticios (`simulador.py`, semilla 42). Periodo de uso real: **por definir por el equipo** (fechas, participantes y dispositivos). |
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
| `login` | Inicio de sesión | `El usuario inició sesión` |
| `registro` | Cuenta nueva | `Nuevo lector registrado` / `Nuevo vendedor registrado` |
| `solicitud_publicada` | El lector publica | `Solicitud #N · <título>` |
| `solicitud_cancelada` | Cancela el lector o modera el admin | `Solicitud #N cancelada (lector)` |
| `oferta_publicada` | El vendedor oferta | `Oferta #M para solicitud #N · $precio` |
| `oferta_cancelada` | El vendedor retira una oferta | `Oferta #M cancelada` |
| `oferta_por_concretar` | El lector acepta para coordinar | `Oferta #M por concretar · solicitud #N en coordinación` |
| `trato_concretado` | El lector confirma la compra | `Oferta #M concretada · solicitud #N resuelta` |
| `trato_desistido` | Lector o vendedor desiste | `Coordinación de oferta #M cancelada · solicitud #N reactivada` |
| `usuario_suspendido` / `usuario_reactivado` | Moderación del admin | `<correo> suspendido` |

**Privacidad:** En los eventos nuevos, solo `usuario_suspendido` y `usuario_reactivado` guardan el correo en `detail`. Los históricos pueden conservar correos de versiones anteriores. Por eso `data.json`
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

### 4.1 Metas del próximo ciclo de evaluación

**Fecha de definición: 19-11-2026.** Estas metas iniciales se establecen para el próximo ciclo
de **14 días consecutivos**. Sus fechas de inicio y cierre, participantes y fuente de datos
deben registrarse antes de comenzar. Las metas son objetivos de evaluación del MVP; no son
compromisos de servicio ni resultados obtenidos.

| KPI | Meta al cierre del ciclo | Criterio de elección |
|---|---|---|
| **1. Tasa de resolución** | **≥ 50 %** de las solicitudes publicadas | Que al menos la mitad termine con un trato confirmado por el lector, para evaluar si el circuito aporta una solución a la necesidad. |
| **2. Tasa de respuesta** | **≥ 80 %** de las solicitudes publicadas | Que al menos cuatro de cada cinco solicitudes reciban una oferta; permite detectar demanda sin atención de vendedores. |
| **3. Horas hasta la primera oferta** | **≤ 24 h** de mediana, entre solicitudes con oferta | Buscar una primera respuesta dentro de un día para la solicitud típica que recibe oferta, sin exigir atención inmediata a pequeños vendedores. |

Se conservan las fórmulas y exclusiones existentes: las solicitudes canceladas siguen en el
denominador y cada solicitud cuenta una vez. La mediana de espera se interpreta junto con la
tasa de respuesta; no garantiza respuesta para todas las solicitudes ni demuestra una mejora
frente a los 15 minutos de búsqueda manual de la encuesta, que miden otra actividad.

Al cierre se informa para cada KPI su valor, numerador y denominador (o cantidad de solicitudes
con oferta para la mediana), meta y resultado de la comparación. Si no hay solicitudes, se
declara **sin datos para evaluar**, aunque el script imprima tasas de 0 %. Si no hay ofertas,
la mediana queda **sin datos**. No se modifican los umbrales durante el ciclo; los ajustes se
documentan para un ciclo posterior. Los datos reales y simulados se evalúan por separado,
con las cuentas demo y del equipo excluidas del análisis real.

La simulación del 3 al 16 de noviembre precede a estas metas. Como referencia retrospectiva,
31,1 % de resolución queda bajo 50 %, 62,2 % de respuesta queda bajo 80 % y 2,4 h de mediana
queda dentro de 24 h. **Esta comparación no acredita cumplimiento de metas previas ni
validación con usuarios reales.** Se conservan intactos sus datos y el gráfico histórico.

### 4.2 Estimación de lanzamiento y proyección mensual

**Escenario de planificación elaborado el 19-11-2026, sin datos reales de lanzamiento.**
Se estima el primer mes y los tres meses posteriores. Como no hay una fecha de lanzamiento
documentada, «mes» representa un bloque de 30 días desde el inicio: M1 = días 1–30,
M2 = 31–60, M3 = 61–90 y M4 = 91–120. Cada columna corresponde a ese mes, sin acumular
los resultados de meses anteriores.

Las cifras son **supuestos orientativos**, no una predicción estadística ni resultados de una
nueva simulación. La encuesta acredita interés declarado en una muestra pequeña; no permite
estimar captación, retención o conversiones reales. Los resultados simulados de la sección 7.1
sirven para comprobar el instrumento y tampoco calibran esta proyección.

#### Supuestos del escenario base

- Lanzamiento acotado a una comunidad inicial, con lectores y vendedores capaces de usar el
  backend compartido. No se supone cobertura nacional ni nuevas funciones fuera del MVP.
- Lectores activos por mes: **25, 50, 75 y 100**; cada uno publica en promedio **dos solicitudes
  mensuales**. La captación neta de 25 lectores activos adicionales por mes es un supuesto de
  planificación, sin campaña ni tasa de retención demostradas.
- Vendedores activos por mes: **5, 8, 12 y 15**. «Activo» en este escenario significa que
  publica al menos una oferta durante el mes; registrarse por sí solo no basta.
- La disponibilidad de títulos y la revisión del feed mejoran conforme crece la participación
  de vendedores. Se supone un aumento de respuesta de 10 puntos porcentuales mensuales hasta
  M3 y de 5 puntos en M4; entre las solicitudes con oferta, la proporción que se concreta pasa
  de 50 % a aproximadamente 65 %. Son hipótesis, no efectos demostrados del crecimiento.
- La espera mediana se supone de **24, 18, 12 y 8 horas**. No se deduce de las tasas ni de los
  conteos; depende de que los vendedores revisen y atiendan solicitudes con mayor frecuencia.

| Indicador mensual estimado | M1 · lanzamiento | M2 | M3 | M4 |
|---|---|---|---|---|
| Lectores activos (supuesto) | 25 | 50 | 75 | 100 |
| Vendedores activos (supuesto) | 5 | 8 | 12 | 15 |
| Solicitudes publicadas (supuesto) | 50 | 100 | 150 | 200 |
| Solicitudes con al menos una oferta | 30 | 70 | 120 | 170 |
| Solicitudes con trato confirmado por el lector | 15 | 40 | 75 | 110 |
| **KPI 1 · Tasa de resolución esperada** | **30 %** | **40 %** | **50 %** | **55 %** |
| **KPI 2 · Tasa de respuesta esperada** | **60 %** | **70 %** | **80 %** | **85 %** |
| **KPI 3 · Mediana hasta la primera oferta** | **24 h** | **18 h** | **12 h** | **8 h** |

Por ejemplo, en M1 se esperan **15 solicitudes resueltas y 30 con oferta de un total de 50**,
si se cumplen los supuestos. Los conteos muestran la coherencia de las tasas; no son ventas
verificadas ni cantidades garantizadas. Con una muestra inicial pequeña, unas pocas solicitudes
pueden cambiar mucho los porcentajes.

#### Relación con las metas y seguimiento

Las metas del piloto de 14 días (sección 4.1) siguen siendo **objetivos aspiracionales**;
esta tabla expresa una **expectativa condicionada** para el lanzamiento. En el escenario base,
M1 quedaría bajo las metas de resolución y respuesta. M3 alcanzaría sus umbrales de 50 % y
80 %, y la mediana cumpliría el umbral de 24 h desde M1. Alcanzar un umbral en un mes no
acredita haberlo cumplido durante el piloto, porque son periodos distintos.

Al cierre de cada bloque se evalúan las solicitudes publicadas dentro de ese bloque y las
ofertas y confirmaciones asociadas registradas hasta ese mismo cierre. Las canceladas permanecen
en el denominador y una solicitud con varias ofertas cuenta una vez como respondida. Las
resoluciones posteriores pueden informarse como seguimiento de su cohorte, sin sumarlas como
resoluciones de solicitudes nuevas del mes siguiente. El corte perjudica a las solicitudes
recientes; se debe declarar esa limitación al comparar meses.

Para esta evaluación se separan personas, cuentas demo/equipo y agentes simulados. Se usa una
fuente compartida o se analiza cada archivo local por separado; no se suman identificadores de
dispositivos distintos. **`analitica.py` calcula sobre todo el archivo recibido y no genera esta
proyección ni separa automáticamente cohortes mensuales.** La automatización de ese seguimiento
requerirá una especificación propia; esta actualización es solo documental.

Al terminar M1 se contrastarán participación, solicitudes, tasas y espera observadas con los
supuestos. Si no se incorporan vendedores con los títulos demandados o no revisan el feed,
las tasas pueden estancarse o bajar y la espera aumentar. El crecimiento no asegura mejora.
Se conservará esta versión y se fecharán las revisiones futuras del escenario, sin alterar
los resultados históricos ni presentar estos valores como observaciones.

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

### Datos simulados: `simulador.py`

Mientras no haya uso real, `simulador.py` genera actividad ficticia con la lógica real de la app
([SPEC-003](docs/05-specs/SPEC-003-simulador-de-uso.md)): 24 lectores y 10 vendedores con
perfiles ficticios se registran, publican, ofertan, aceptan, confirman, desisten y cancelan
durante 14 días simulados.

```bash
python simulador.py                                    # escribe data/simulacion/simulacion.json
python analitica.py data/simulacion/simulacion.json    # KPIs rotulados como DATOS SIMULADOS
```

- **Ficticio y marcado:** cuentas `@bookwho.test` (dominio reservado, RFC 2606), nombres con
  "(sim)", teléfonos `+56 9 0000 …` y puntos de encuentro ficticios. Todas usan la contraseña `sim1234`.
- **Separado:** escribe solo en `data/simulacion/`, que Git ignora y el APK no incluye; nunca en
  `data/user/`.
- **Reproducible:** con la misma semilla y los mismos parámetros, el archivo es idéntico. Para
  reiniciar los datos basta con volver a ejecutarlo.
- **Pone a prueba la app mientras simula:** en cada aceptación comprueba que el contacto lo vea
  solo el lector que aceptó, e intenta acciones inválidas (ofertas duplicadas o con precio 0,
  aceptar ofertas ajenas) que la app debe rechazar. El resultado queda en
  `data/simulacion/simulacion_resumen.json`, con el desglose por región, entrega y precio máximo.
- **Verlo en la app:** respaldar `data/user/data.json`, copiar ahí `data/simulacion/simulacion.json`
  y abrir la app; por ejemplo, con `admin@demo.cl` se ve el panel de métricas.
- **Verlo en la web:** `python simulador.py --panel CARPETA` escribe `CARPETA/metricas.json`, que
  lee `panel/index.html` ([SPEC-004](docs/05-specs/SPEC-004-panel-de-metricas.md)). Con
  `--en-vivo MINUTOS`, la simulación continúa un día más en tiempo real para la demostración,
  sin alterar el periodo base.

## 6. Limitaciones metodológicas (declarar en el informe)

1. **Muestra pequeña y periodo corto:** los resultados son indicativos, no estadísticamente
   significativos.
2. **Corte al final del periodo:** las solicitudes publicadas poco antes del cierre no alcanzan
   a recibir respuesta, lo que hace bajar los KPI 1 y 2.
3. **El KPI 3 no incluye las solicitudes sin ofertas:** hay que leerlo junto al KPI 2.
4. **"Trato concretado" lo declara el lector:** la app no verifica que la entrega ocurrió.
5. **Un archivo por dispositivo (modo local):** cada teléfono numera sus solicitudes desde 1. Se analiza cada
   `data.json` por separado; no se juntan ni se suman. En modo servidor (SPEC-005) todos los teléfonos
   escriben en un mismo archivo y esta limitación no aplica a esos datos.
6. **Hora local del dispositivo, sin zona horaria:** las diferencias de tiempo son válidas dentro
   de un mismo teléfono.
7. **Datos demo vs. reales:** la semilla de demo no genera eventos (`build_demo_store` vacía el
   registro), pero cualquier uso posterior de las cuentas demo sí queda registrado; `analitica.py`
   lo excluye. Los ensayos del equipo con cuentas propias se excluyen con `CORREOS_EQUIPO`.
8. **No se registran pantallas vistas ni errores de validación:** no se puede medir el abandono
   antes de publicar ni la frecuencia de errores.
9. **Una oferta cuenta como respuesta aunque después se cancele:** el vendedor sí respondió.
10. **Los datos simulados reflejan sus supuestos:** los perfiles y probabilidades de
    `simulador.py` determinan los valores (por ejemplo, la tasa de respuesta depende de
    `P_OFERTA`). Sirven para validar la medición y el funcionamiento de la app, no para afirmar
    cómo se comportan los usuarios.

## 7. Resultados

### 7.1 Datos simulados (3 al 16 de noviembre de 2026)

> **Datos ficticios** generados con `simulador.py` (semilla 42), con autorización del docente.
> Los valores dependen de los supuestos del simulador: no describen a usuarios reales.

| Dato | Valor |
|---|---|
| Periodo | 3 al 16 de noviembre de 2026 (14 días simulados) |
| Fuente | `data/simulacion/simulacion.json`, un solo archivo (como un dispositivo) |
| Usuarios simulados activos | 34 (24 lectores y 10 vendedores) |
| Eventos | 705, de ellos 513 inicios de sesión |
| Solicitudes publicadas | 45 |
| KPI 1 · Tasa de resolución (sin meta previa en esta simulación) | **31,1 %** (14 de 45) |
| KPI 2 · Tasa de respuesta (sin meta previa en esta simulación) | **62,2 %** (28 de 45) |
| KPI 3 · Horas hasta la primera oferta (sin meta previa en esta simulación) | **2,4 h** (mediana) |

![KPIs con datos simulados](docs/resultados/kpis_simulados.png)

Estado de las 45 solicitudes al cierre: 14 resueltas, 9 en coordinación, 1 con ofertas sin
aceptar, 8 publicadas sin ofertas y 13 canceladas.

| Grupo (simulado) | Solicitudes | Con oferta | Mediana hasta la 1.ª oferta |
|---|---|---|---|
| Región: La Araucanía | 11 | 90,9 % | 0,9 h |
| Región: Metropolitana | 12 | 66,7 % | 4,3 h |
| Región: Valparaíso | 7 | 57,1 % | 6,5 h |
| Región: Biobío | 8 | 50,0 % | 5,2 h |
| Región: Aysén | 2 | 50,0 % | 3,2 h |
| Región: Los Lagos (sin vendedores) | 5 | 20,0 % | 14,4 h |
| Entrega: cualquiera | 26 | 69,2 % | 1,3 h |
| Entrega: solo presencial | 16 | 43,8 % | 9,2 h |
| Entrega: solo envío | 3 | 100 % | 13,0 h |
| Con precio máximo | 26 | 57,7 % | 1,1 h |
| Sin precio máximo | 19 | 68,4 % | 2,5 h |

Funcionamiento técnico durante la simulación: 136 verificaciones del contacto del vendedor sin
violaciones, 31 acciones inválidas rechazadas (ninguna aceptada por error), ninguna falla
inesperada, y cada caso de uso del modelo tarda menos de 0,01 ms (sin red ni interfaz).

### 7.2 Qué sostienen los datos y qué es supuesto

| Observación | Qué la explica |
|---|---|
| Ningún error de permisos ni de estados en 705 eventos | **Dato sólido**, porque lo verifica la app real y no depende de los supuestos: el contacto está oculto antes de aceptar, lo ve solo el lector que aceptó, y las acciones inválidas se rechazan. |
| Las regiones sin vendedores casi no reciben ofertas (Los Lagos: 20 %) | **Supuesto + regla de la app:** los vendedores simulados ofertan lejos solo si la solicitud acepta envío, y la app no avisa al lector que no hay vendedores cerca. |
| "Solo presencial" recibe menos ofertas que "cualquiera" (43,8 % frente a 69,2 %) | **Supuesto:** las probabilidades de ofertar según la cercanía (`P_OFERTA`). Hay que confirmarlo con datos reales. |
| De cada dos solicitudes con oferta, una se resuelve (KPI 1 frente a KPI 2) | Supuestos de aceptación y confirmación, más el **corte del periodo**: 9 solicitudes seguían en coordinación el último día. |
| La primera oferta llega en 2,4 h (mediana) | **Supuesto:** cada cuánto revisan los vendedores su feed (1 a 3 veces al día). El lector publica una vez y espera, en vez de buscar tienda por tienda. |

### 7.3 Propuestas de mejora (borrador para revisar en equipo)

Ordenadas por impacto esperado y esfuerzo:

| # | Mejora | Se apoya en | Impacto | Esfuerzo |
|---|---|---|---|---|
| 1 | **Backend compartido** en el servidor del equipo — **implementado en prueba** el 17-11-2026 (SPEC-005): antes cada teléfono guardaba sus datos y lectores y vendedores en teléfonos distintos no se veían | Limitación 5. La simulación pone a todos en un mismo archivo, que es lo que haría el backend | Alto | Alto |
| 2 | Al elegir entrega "Presencial", avisar que aceptar envío aumenta las ofertas | 43,8 % frente a 69,2 % (simulado) | Medio | Bajo |
| 3 | Avisar al lector cuando no hay vendedores en su región y sugerir envío | Los Lagos: 20 % (simulado) | Medio | Bajo |
| 4 | Notificar a los vendedores cuando aparece una solicitud de un libro que suelen ofrecer | El KPI 3 depende de cada cuánto revisan su feed | Medio | Medio |
| 5 | Registrar errores de validación y pantallas vistas, para medir el abandono | Limitación 8 | Medio | Bajo |

Las propuestas 2 a 4 deben validarse con datos reales antes de implementarse, porque en la
simulación esas diferencias salen de los supuestos.

### 7.4 Datos reales: prueba en vivo del 18-11-2026

> Datos del servidor compartido (`~/bookwho/datos/bookwho.json` en el Z40), analizados el 19-11-2026
> con `analitica.calcular()`. Se excluyen los agentes simulados (`@bookwho.test`), la administración,
> las cuentas demo y las dos cuentas del equipo que usa el guion. No se imprimieron correos ni nombres.

| Dato | Valor |
|---|---|
| Periodo | 18-11-2026, entre las 01:52 y las 11:56 (un solo día) |
| Cuentas de personas en el servidor | 6 (4 lectores y 2 vendedores); 2 son del equipo |
| Analizadas, sin el equipo | 4 cuentas activas (3 lectores y 1 vendedor), 23 eventos |
| Solicitudes publicadas | 3 |
| KPI 1 · Tasa de resolución | 0 % (0 de 3) |
| KPI 2 · Tasa de respuesta | 33,3 % (1 de 3) |
| KPI 3 · Horas hasta la primera oferta | 0,0 h (una sola solicitud con oferta) |

**Lectura:** no es el ciclo de 14 días de la sección 4.1 y la muestra es mínima, así que **no se
compara con las metas ni permite conclusiones**. Limitaciones de esta prueba:

- no se puede verificar que las 4 cuentas restantes sean externas al equipo;
- las ofertas de los agentes simulados no cuentan como respuesta de vendedores reales, aunque
  aparecían en el feed de las personas;
- la app no registra el dispositivo usado (APK o escritorio).
