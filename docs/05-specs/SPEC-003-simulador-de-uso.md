# SPEC-003 — Simulador de uso con datos ficticios

## Objetivo

Generar actividad ficticia, reproducible y marcada como simulada para medir los KPIs de RA3
mientras no haya datos reales de uso. El docente autorizó usar datos ficticios en la E4.

## Alcance

- Agentes lectores y vendedores con perfiles ficticios que usan la lógica real de la app
  (`models/store.py`): se registran, inician sesión, publican solicitudes, ofertan, aceptan para
  coordinar, confirman, desisten y cancelan.
- Reloj simulado: la actividad se reparte en un periodo declarado (por defecto, 14 días).
- Verificación del contacto del vendedor en cada aceptación y "sondas": acciones inválidas
  hechas a propósito que la app debe rechazar.
- Resumen técnico: recorridos, tiempos por acción, rechazos esperados y fallas inesperadas.

Fuera de alcance: la interfaz gráfica, la red, modelos de IA durante la ejecución, el modo en vivo
y cualquier cambio a la app.

## Criterios de aceptación

1. No modifica el código de la app: cada acción pasa por los métodos públicos de `Store`. Lo único
   que el simulador ajusta directamente son las fechas de creación, para alinearlas con el reloj
   simulado.
2. Todas las cuentas simuladas usan el dominio reservado `bookwho.test` (RFC 2606) y contactos
   ficticios.
3. Con la misma semilla y los mismos parámetros, el archivo de datos generado es idéntico.
4. Escribe solo en la ruta indicada (por defecto `data/simulacion/`), nunca en `data/user/`.
5. El archivo generado se abre en la app y `analitica.py` lo interpreta sin eventos ilegibles.
6. `analitica.py` rotula como "DATOS SIMULADOS" los resultados de cuentas simuladas.
7. En cada aceptación verifica que el contacto lo vea solo quien corresponde e informa cualquier
   violación.
8. Informa los recorridos completos y abiertos, los rechazos esperados y las fallas inesperadas.
9. Tiene pruebas automáticas en `tests/`.
