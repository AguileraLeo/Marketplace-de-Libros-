# SPEC-012 — Contraseñas con PBKDF2

## Objetivo

Cerrar S6 de la [auditoría de seguridad](../04-architecture/SEGURIDAD.md) elevando el coste de probar contraseñas contra una copia del JSON.

## Decisión

El 19-11-2026 el equipo eligió PBKDF2-HMAC-SHA256 de la biblioteca estándar, con 600 000 iteraciones (recomendación OWASP de 2023) y 16 bytes de sal aleatoria por usuario. El formato persistido es `pbkdf2_sha256$<iteraciones>$<sal hex>$<hash hex>`.

La medición de referencia del equipo fue de 123 ms por hash en un Ryzen 7 7445HS. Antes del despliegue se medirá en el Z40. Si supera 0,5 s, el equipo decidirá en una spec posterior si reduce las iteraciones.

## Migración y verificación

El login admite el SHA-256 histórico de `correo:clave` (64 dígitos hexadecimales). Tras un acceso correcto de una cuenta activa, se actualiza ese hash o uno PBKDF2 con otro número de iteraciones. El guardado habitual del login persiste el cambio mediante `app.safe()` en la app y `guardar()` en el servidor. La migración requiere la contraseña original.

La verificación compara los derivados en tiempo constante. Para un correo inexistente también se calcula PBKDF2 y se devuelve el error habitual de credenciales.

## Pruebas y simulación

Las cuentas ficticias usan 1 000 iteraciones durante las pruebas y la simulación. El simulador deriva las sales de su semilla mediante un generador independiente para conservar la secuencia de actividad.

## Criterios de aceptación

1. El registro en la app real guarda un hash con prefijo `pbkdf2_sha256$600000$`.
2. El login admite y migra una cuenta antigua. En el servidor el cambio queda en el JSON.
3. Una contraseña incorrecta falla con ambos formatos.
4. Un correo inexistente provoca un cálculo PBKDF2.
5. La suite completa tarda alrededor de 10 s.
6. Con la misma semilla se reproduce el mismo archivo y se conservan los KPIs publicados.
