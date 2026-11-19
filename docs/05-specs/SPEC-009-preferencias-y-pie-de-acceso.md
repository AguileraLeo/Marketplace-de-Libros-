# SPEC-009 — Preferencias y pie de acceso

## Solicitud

Incorporar selector de idiomas y condiciones del servicio al pie del acceso.
Por solicitud posterior del usuario, retirar el modo nocturno y conservar la
apariencia clara anterior. Mostrar `soporte@quadcorestore.com` sin configurar correo.

## Decisiones y alcance

- Mantener únicamente la paleta clara de la propuesta C, sin selector de tema
  ni cambios en el logo o el estado de la sesión.
- Mostrar la dirección de soporte como texto, sin envío, vínculo mailto ni buzón.
  Identificarla como dirección aún no habilitada para no prometer atención.
- Abrir un documento desplazable de condiciones, disponible sin iniciar sesión,
  con vuelta al acceso. Describir únicamente capacidades existentes y límites
  del prototipo. Es un borrador para revisión del equipo, no términos legales definitivos.
- No exigir una aceptación contractual ni cambiar el registro, autenticación,
  permisos, tratamiento de datos o reglas de negocio.
- Por elección posterior del usuario, ofrecer español e inglés en toda la app:
  acceso, lector, vendedor y administración, estados, diálogos y errores conocidos.
  Conservar las claves del dominio, los importes en pesos chilenos, títulos de
  libros, nombres, ubicaciones, notas, contactos y registros de auditoría originales.
  Los mensajes remotos desconocidos conservan su texto original.
- Cambiar el idioma antes de iniciar sesión y aplicarlo al navegar, sin vaciar
  formularios ni alterar filtros. No traducir datos persistidos ni llamadas RPC.
- Preferencias de presentación durante la ejecución actual, separadas del Store
  y de los datos del servidor. Al reiniciar se usan español y modo claro.

## Criterios de aceptación

1. No se ofrece modo nocturno ni interruptor de tema.
2. El logo conserva sus colores y geometría. La apariencia clara mantiene legibilidad.
3. Los controles de pie son accesibles mediante desplazamiento a tamaño móvil.
4. El correo aparece, aclarando que no está habilitado; no se realizan acciones de correo.
5. Las condiciones abren y cierran sin modificar datos ni iniciar sesión.
6. La traducción ofrece únicamente los idiomas y pantallas realmente traducidos.
7. El selector de idioma no modifica estados ni formularios ya completados.
8. Probar los cambios con datos de prueba en memoria, sin actividad en el servidor real.

## Pendiente para publicación de condiciones definitivas

Responsable propuesto: Matías Mcintire, que administra el servidor y el dominio `quadcorestore.com` (a confirmar por el equipo). La aprobación del texto de las condiciones queda pendiente del equipo.
