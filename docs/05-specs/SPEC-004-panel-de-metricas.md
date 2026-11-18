# SPEC-004 — Panel público de métricas

## Objetivo

Mostrar en una página web pública (`bookwho.quadcorestore.com/simulacion/`) los KPIs de RA3 y la
verificación de la app, con los datos del simulador (SPEC-003), y permitir una demostración
"en vivo" durante la presentación.

## Alcance

- `simulador.py --panel CARPETA` escribe `CARPETA/metricas.json`: KPIs (calculados con
  `analitica.py`), uso diario, estado de las solicitudes, desglose, verificaciones y la
  actividad reciente, sin datos personales.
- `simulador.py --en-vivo MINUTOS` continúa la simulación un día más, repartido en esos minutos
  reales, y actualiza el archivo después de cada acción.
- `panel/index.html`: página estática que lee `metricas.json` y se actualiza sola.
- Diseño compacto: los tres KPI, una fila de cifras y tarjetas en pares (gráfico y actividad; desglose y
  estados). Una tarjeta sin datos se oculta y su vecina ocupa el espacio. En vivo, las cifras separan
  personas y agentes simulados, y suman las descargas del APK desde el último reinicio del servidor.
- Los tres KPI se destacan sobre las cifras de apoyo (fondo suave, borde de marca y cifra grande).
- «Descargar CSV» exporta lo que muestra el panel: separador «;», coma decimal y UTF-8, como lo abre Excel en
  español; ningún texto se abre como fórmula. Las tablas de datos van en columnas, con paginación de 8 filas cuando tienen más, y filas alternadas.


- Auditoría UI/UX aprobada del panel:
  - B1: estados de solicitudes con punto, cantidad, porcentaje y barra proporcional;
    gris, verde, ámbar y rojo con variantes claras y oscuras. Nombres y valores en color de texto.
  - B2: cifras agrupadas en «Mercado» y «Uso», con personas, agentes simulados o usuarios
    simulados activos según el origen, y descargas del APK cuando están presentes.
  - B3: destello de 1,6 segundos solo en cifras que cambian respecto al último pintado,
    guardadas por rótulo, y solo con `prefers-reduced-motion: no-preference`.
  - B4: última barra del día actual rotulada «hoy · N» durante el modo en vivo, sin
    duplicar el rótulo si también es el máximo; fecha tomada de `generado`.
  - B5: tablas con paginación de 8 filas solo si superan ese tamaño; la página se conserva
    por título entre actualizaciones. Encabezados destacados, filas alternadas y controles
    accesibles. El CSV conserva todas las filas y las tablas siguen en columnas de 300 px.
  - B6: logo y «BookWho?» del encabezado enlazan al inicio, seguidos por « · Panel de métricas»,
    sin enlace separado de vuelta.

Fuera de alcance: datos reales, inicio de sesión en el panel y el backend (SPEC-005).

## Criterios de aceptación

1. La página identifica los datos **simulados** mediante etiquetas y la fuente al
   pie. Por solicitud del usuario, no muestra una advertencia amarilla superior;
   la explicación detallada se presenta en vivo.
2. `metricas.json` no contiene correos, nombres de personas, teléfonos ni contraseñas.
3. Los KPIs del panel coinciden con los que imprime `analitica.py` sobre los mismos datos.
4. La página no usa librerías externas para los gráficos e inserta todo texto con
   `textContent`, nunca como HTML.
5. Cada gráfico se puede leer sin color y sin pasar el mouse: valores escritos y una tabla con los
   mismos datos.
6. Si `metricas.json` falta o viene mal, la página lo informa sin romperse y mantiene lo último
   que mostró.
7. El modo en vivo no altera el periodo base: sin `--en-vivo`, los datos son idénticos a los de
   SPEC-003.
8. Tiene pruebas automáticas en `tests/`.
