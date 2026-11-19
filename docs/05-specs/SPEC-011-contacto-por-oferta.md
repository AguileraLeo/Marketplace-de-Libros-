# SPEC-011 — El contacto se guarda con cada oferta

## Objetivo

Que el lector vea exactamente el contacto que el vendedor ofreció en **esa** oferta.

## Problema

El modelo guardaba un único contacto por vendedor y cada oferta nueva lo sobrescribía. Si el
vendedor ofrecía un punto de encuentro en Temuco y después otro en Concepción, el lector de la
primera oferta, ya en coordinación, pasaba a ver el de Concepción.

## Decisión

Decidido por el equipo el 19-11-2026 (AGENTS.md §19, «política de visibilidad de datos
personales»): el contacto es **por oferta**. El formulario de oferta ya lo pedía así («datos que
recibirá el lector tras aceptar»), y el punto de encuentro depende de cada solicitud.

## Alcance

1. Al publicar una oferta se guarda una copia de su contacto (teléfono, correo, dirección o punto
   de encuentro), asociada a la oferta.
2. El lector que acepta para coordinar ve esa copia. Ofertas posteriores del mismo vendedor no la
   cambian.
3. El contacto del perfil del vendedor guarda el último usado, **solo** para precargar el formulario.
4. La visibilidad no cambia: el contacto se muestra al coordinar o aceptar (`POR_CONCRETAR` o
   `ACEPTADA`), y al administrador. Nunca viaja dentro de la oferta: `get_offer` y las listas de
   ofertas no lo incluyen.
5. La pantalla de contacto se limpia **antes** de cargar, para que un error no deje visible el
   contacto de otra oferta.

## Compatibilidad

- La API sigue devolviendo un `SellerContact`: las apps ya instaladas funcionan sin cambios.
- Los `data.json` existentes cargan sin cambios: la tabla nueva parte vacía.
- Las ofertas creadas antes de este cambio no tienen copia y muestran el contacto actual del
  vendedor, como antes. Los contactos que ya se sobrescribieron no se pueden recuperar.

## Criterios de aceptación

1. Dos ofertas del mismo vendedor con contactos distintos: cada lector ve el suyo, también después
   de guardar y volver a cargar el archivo.
2. Antes de aceptar, el contacto no aparece en ninguna respuesta de la oferta.
3. Una oferta antigua sin copia muestra el contacto del perfil.
4. Pruebas automáticas en `tests/test_store.py`, `tests/test_persistence.py` y `tests/test_backend.py`.
