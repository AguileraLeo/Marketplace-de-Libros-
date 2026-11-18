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
  español; ningún texto se abre como fórmula. Las tablas de datos van en columnas y sin paginar: tienen pocas filas.

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
