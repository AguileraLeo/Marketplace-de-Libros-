# SPEC-007 — Propuesta C: Azul tinta

## Objetivo y referencia aprobada

Aplicar a BookWho? la propuesta C seleccionada por el usuario, usando el PNG
«Propuesta C.png» adjunto como referencia. La solicitud autoriza una presentación
amigable, clara y con personalidad, sin introducir funcionalidades ni reglas nuevas.

## Alcance

- Paleta: acento `#284DA6`, fondo `#F5F7FC`, texto `#17243F`, texto secundario
  `#52617B`, borde `#DCE3EF`, destacado suave `#E4EBFB`, superficies blancas.
- Manrope para títulos y cuerpo, empaquetada localmente con licencia OFL.
- Tarjetas legibles con esquinas suaves, controles claros, espacios consistentes
  y una marca tipográfica sencilla. Sin gradientes ni decoración innecesaria.
- Inicio lector: saludo, título «Tu próximo libro empieza aquí», búsqueda protagonista,
  acción de ancho completo, métricas reales y tarjetas de solicitudes.
- Inicio vendedor: título «Alguien busca ese libro que tienes», búsqueda y filtros
  existentes, solicitudes con precio y condición y acceso a sus ofertas.
- Detalle de oferta: libro y autor, precio destacado, datos de la oferta y explicación
  de contacto externo antes de aceptar. Conservar todas las acciones según el estado.
- Aplicar el lenguaje visual compartido a login, formularios, confirmación y administración.
- Reutilizar navegación y componentes existentes; los accesos con texto pueden reemplazar
  iconos sin cambiar su destino. No simular la barra de estado ni el marco del teléfono.

## Criterios de aceptación

1. Fondo, acento y tipografía siguen la propuesta en todas las pantallas existentes.
2. La fuente funciona sin red y se incluye su licencia.
3. El lector puede buscar por título, autor o ISBN y conserva los identificadores de sus controles.
4. Los contadores y las tarjetas se alimentan del modelo, sin cifras ni portadas ficticias.
5. El vendedor conserva todos sus filtros y puede abrir una solicitud y ofertar.
6. El detalle mantiene las condiciones de visibilidad de aceptar, contacto, confirmar y desistir.
7. Los avisos explican que la compra y entrega se coordinan fuera de la plataforma.
8. Botones y selectores ofrecen al menos 48 dp de altura; textos largos se ajustan
   o desplazan sin tapar acciones. El color no es la única señal de estado.
9. El inicio y la navegación ofrecen nombres claros para las acciones existentes.
10. El cambio no modifica entidades, permisos, estados, backend, transporte remoto ni medición.
11. Revisar visualmente lector, vendedor y detalle de oferta a tamaño móvil, y verificar
    formularios y administración mediante los componentes compartidos.
12. Ejecutar las pruebas existentes y comprobar que la app inicia con el KV actualizado.
13. Refinamiento solicitado: agrandar el libro del logo de acceso y marcar su pliegue
    central con una línea de separador dorada, conservando el fondo azul y la insignia.
14. «Iniciar sesión» queda centrado horizontal y verticalmente dentro del botón,
    también después de cargar la fuente, cambiar el texto o redimensionar la ventana.
15. Aplicar la maqueta de acceso aprobada: fondo blanco, logo existente sin cambios,
    título centrado, acceso a registro junto a «¿No tienes cuenta?», etiquetas de
    correo y contraseña y botón principal redondeado. Retirar las cuentas demo de
    esta presentación. La recuperación se muestra como «Todavía no disponible»,
    sin acción que prometa enviar correos; no incluir Google, Apple ni códigos de acceso.
    Conservar el aviso de configuración remota al pie, separado del formulario.

## Validación

Usar datos de demo en memoria y persistencia temporal para las capturas de revisión,
sin registrar cuentas ni publicar solicitudes en el servidor real. La prueba visual no
constituye evidencia de actividad de usuarios ni altera los resultados del informe.
