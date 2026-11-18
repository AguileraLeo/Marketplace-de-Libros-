"""Textos de interfaz ES/EN; los datos de usuarios y libros no se traducen."""

import re
from string import Formatter

SUPPORTED_LANGUAGES = ("es", "en")
ENGLISH = {'Iniciar sesión': 'Sign in',
 '¿No tienes cuenta?': 'New here?',
 'Crear cuenta': 'Create account',
 'Correo electrónico': 'Email address',
 'tu@correo.cl': 'you@example.com',
 'Contraseña': 'Password',
 'Tu contraseña': 'Your password',
 'Recuperación de contraseña': 'Password recovery',
 'Todavía no disponible.': 'Not available yet.',
 'Busca un libro.\nEncuentra quién lo tiene.': 'Find a book.\nFind someone who has it.',
 'Correo informativo · aún no habilitado': 'For reference · mailbox not yet active',
 'Condiciones del servicio': 'Service terms',
 'BookWho? · Proyecto académico': 'BookWho? · Academic project',
 'Condiciones de BookWho?': 'BookWho? service terms',
 'Borrador para revisión del equipo · Prototipo académico': 'Draft for team review · Academic prototype',
 'Coordinación entre las partes': 'Coordinating directly',
 'Datos y acceso': 'Data and access',
 'Límites de esta versión': 'Current limitations',
 'Volver': 'Back',
 'Nombre': 'Name',
 'Correo': 'Email',
 'Mínimo 4 caracteres': 'At least 4 characters',
 '¿Cómo usarás la app?': 'How will you use the app?',
 'Busco libros (Lector)': 'Find books (Reader)',
 'Vendo libros (Vendedor)': 'Offer books (Seller)',
 'Tu comuna (para que los lectores vean qué tan cerca estás)': 'Your municipality (so readers can see how '
                                                               'close you are)',
 'Ej: Concepción, Santiago…': 'E.g. Concepción, Santiago…',
 'Las cuentas de administrador no se pueden crear desde aquí.': 'Administrator accounts cannot be created '
                                                                'here.',
 'BookWho? conecta lectores que buscan libros con vendedores que pueden ofrecerlos. Una solicitud no garantiza recibir una oferta ni conseguir el libro.': 'BookWho? '
                                                                                                                                                           'connects '
                                                                                                                                                           'readers '
                                                                                                                                                           'looking '
                                                                                                                                                           'for '
                                                                                                                                                           'books '
                                                                                                                                                           'with '
                                                                                                                                                           'sellers '
                                                                                                                                                           'who '
                                                                                                                                                           'can '
                                                                                                                                                           'offer '
                                                                                                                                                           'them. '
                                                                                                                                                           'Posting '
                                                                                                                                                           'a '
                                                                                                                                                           'request '
                                                                                                                                                           'does '
                                                                                                                                                           'not '
                                                                                                                                                           'guarantee '
                                                                                                                                                           'an '
                                                                                                                                                           'offer '
                                                                                                                                                           'or '
                                                                                                                                                           'a '
                                                                                                                                                           'book.',
 'Aceptar una oferta inicia la coordinación y permite consultar el contacto autorizado. La compra y la entrega se acuerdan fuera de BookWho?. La aplicación no procesa pagos, no gestiona envíos y no dispone de chat interno.': 'Accepting '
                                                                                                                                                                                                                                 'an '
                                                                                                                                                                                                                                 'offer '
                                                                                                                                                                                                                                 'starts '
                                                                                                                                                                                                                                 'coordination '
                                                                                                                                                                                                                                 'and '
                                                                                                                                                                                                                                 'reveals '
                                                                                                                                                                                                                                 'the '
                                                                                                                                                                                                                                 'authorized '
                                                                                                                                                                                                                                 'contact '
                                                                                                                                                                                                                                 'details. '
                                                                                                                                                                                                                                 'Purchase '
                                                                                                                                                                                                                                 'and '
                                                                                                                                                                                                                                 'delivery '
                                                                                                                                                                                                                                 'are '
                                                                                                                                                                                                                                 'arranged '
                                                                                                                                                                                                                                 'outside '
                                                                                                                                                                                                                                 'BookWho?. '
                                                                                                                                                                                                                                 'The '
                                                                                                                                                                                                                                 'app '
                                                                                                                                                                                                                                 'does '
                                                                                                                                                                                                                                 'not '
                                                                                                                                                                                                                                 'process '
                                                                                                                                                                                                                                 'payments, '
                                                                                                                                                                                                                                 'manage '
                                                                                                                                                                                                                                 'shipping '
                                                                                                                                                                                                                                 'or '
                                                                                                                                                                                                                                 'provide '
                                                                                                                                                                                                                                 'an '
                                                                                                                                                                                                                                 'internal '
                                                                                                                                                                                                                                 'chat.',
 'La aplicación guarda datos de cuenta, solicitudes, ofertas, contactos y actividad. Los permisos se comprueban según el rol y la propiedad del recurso. Los datos de contacto se muestran mediante los métodos autorizados al coordinar una oferta. En modo servidor los datos se guardan en el servidor; en modo sin conexión permanecen en el dispositivo.': 'The '
                                                                                                                                                                                                                                                                                                                                                                'app '
                                                                                                                                                                                                                                                                                                                                                                'stores '
                                                                                                                                                                                                                                                                                                                                                                'account '
                                                                                                                                                                                                                                                                                                                                                                'data, '
                                                                                                                                                                                                                                                                                                                                                                'requests, '
                                                                                                                                                                                                                                                                                                                                                                'offers, '
                                                                                                                                                                                                                                                                                                                                                                'contacts '
                                                                                                                                                                                                                                                                                                                                                                'and '
                                                                                                                                                                                                                                                                                                                                                                'activity. '
                                                                                                                                                                                                                                                                                                                                                                'Permissions '
                                                                                                                                                                                                                                                                                                                                                                'depend '
                                                                                                                                                                                                                                                                                                                                                                'on '
                                                                                                                                                                                                                                                                                                                                                                'the '
                                                                                                                                                                                                                                                                                                                                                                'user '
                                                                                                                                                                                                                                                                                                                                                                'role '
                                                                                                                                                                                                                                                                                                                                                                'and '
                                                                                                                                                                                                                                                                                                                                                                'ownership '
                                                                                                                                                                                                                                                                                                                                                                'of '
                                                                                                                                                                                                                                                                                                                                                                'each '
                                                                                                                                                                                                                                                                                                                                                                'resource. '
                                                                                                                                                                                                                                                                                                                                                                'Contact '
                                                                                                                                                                                                                                                                                                                                                                'details '
                                                                                                                                                                                                                                                                                                                                                                'are '
                                                                                                                                                                                                                                                                                                                                                                'shown '
                                                                                                                                                                                                                                                                                                                                                                'through '
                                                                                                                                                                                                                                                                                                                                                                'authorized '
                                                                                                                                                                                                                                                                                                                                                                'methods '
                                                                                                                                                                                                                                                                                                                                                                'when '
                                                                                                                                                                                                                                                                                                                                                                'coordinating '
                                                                                                                                                                                                                                                                                                                                                                'an '
                                                                                                                                                                                                                                                                                                                                                                'offer. '
                                                                                                                                                                                                                                                                                                                                                                'Server '
                                                                                                                                                                                                                                                                                                                                                                'mode '
                                                                                                                                                                                                                                                                                                                                                                'stores '
                                                                                                                                                                                                                                                                                                                                                                'data '
                                                                                                                                                                                                                                                                                                                                                                'on '
                                                                                                                                                                                                                                                                                                                                                                'the '
                                                                                                                                                                                                                                                                                                                                                                'server; '
                                                                                                                                                                                                                                                                                                                                                                'offline '
                                                                                                                                                                                                                                                                                                                                                                'mode '
                                                                                                                                                                                                                                                                                                                                                                'stores '
                                                                                                                                                                                                                                                                                                                                                                'it '
                                                                                                                                                                                                                                                                                                                                                                'on '
                                                                                                                                                                                                                                                                                                                                                                'the '
                                                                                                                                                                                                                                                                                                                                                                'device.',
 'La recuperación de contraseña no está disponible. El correo soporte@quadcorestore.com se muestra como referencia y aún no está habilitado. No se ofrece inicio de sesión con Google, Apple ni códigos de un solo uso.': 'Password '
                                                                                                                                                                                                                          'recovery '
                                                                                                                                                                                                                          'is '
                                                                                                                                                                                                                          'unavailable. '
                                                                                                                                                                                                                          'soporte@quadcorestore.com '
                                                                                                                                                                                                                          'is '
                                                                                                                                                                                                                          'displayed '
                                                                                                                                                                                                                          'for '
                                                                                                                                                                                                                          'reference '
                                                                                                                                                                                                                          'and '
                                                                                                                                                                                                                          'is '
                                                                                                                                                                                                                          'not '
                                                                                                                                                                                                                          'active '
                                                                                                                                                                                                                          'yet. '
                                                                                                                                                                                                                          'Google, '
                                                                                                                                                                                                                          'Apple '
                                                                                                                                                                                                                          'and '
                                                                                                                                                                                                                          'one-time-code '
                                                                                                                                                                                                                          'sign-in '
                                                                                                                                                                                                                          'are '
                                                                                                                                                                                                                          'not '
                                                                                                                                                                                                                          'offered.',
 'Este texto describe el funcionamiento del prototipo. Las condiciones definitivas y la identificación del responsable del servicio están pendientes de revisión por el equipo.': 'This '
                                                                                                                                                                                  'text '
                                                                                                                                                                                  'describes '
                                                                                                                                                                                  'the '
                                                                                                                                                                                  'prototype. '
                                                                                                                                                                                  'Final '
                                                                                                                                                                                  'terms '
                                                                                                                                                                                  'and '
                                                                                                                                                                                  'identification '
                                                                                                                                                                                  'of '
                                                                                                                                                                                  'the '
                                                                                                                                                                                  'service '
                                                                                                                                                                                  'operator '
                                                                                                                                                                                  'are '
                                                                                                                                                                                  'pending '
                                                                                                                                                                                  'team '
                                                                                                                                                                                  'review.',
 'Cerrar': 'Close',
 'Correo o contraseña incorrectos.': 'Incorrect email or password.',
 'Ingresa tu nombre.': 'Enter your name.',
 'Ingresa un correo válido.': 'Enter a valid email.',
 'La contraseña debe tener al menos 4 caracteres.': 'Password must contain at least 4 characters.',
 'Rol no permitido en el registro.': 'This role is not available for registration.',
 'Ingresa tu comuna para que los lectores sepan qué tan cerca estás.': 'Enter your municipality so readers '
                                                                       'can see how close you are.',
 'Ya existe una cuenta con ese correo.': 'An account with this email already exists.',
 'Tu cuenta está suspendida. Contacta a soporte.': 'Your account is suspended. Contact support.',
 'Idioma de la aplicación': 'Application language',
 'Seleccionar idioma': 'Choose language',
 'Seleccionar': 'Select',
 'Lector': 'Reader',
 'Vendedor': 'Seller',
 'Administrador': 'Administrator',
 'Inicio': 'Home',
 'Mis ofertas': 'My offers',
 'Mis solicitudes': 'My requests',
 'Salir': 'Sign out',
 'Hola, ': 'Hello, ',
 'Busca un libro y recibe ofertas de vendedores que lo tienen.': 'Find a book and receive offers from '
                                                                 'sellers who have it.',
 'Título': 'Title',
 'Autor': 'Author',
 '¿Qué libro estás buscando?': 'Which book are you looking for?',
 '¿Quién lo escribió?': 'Who wrote it?',
 'ISBN del libro': 'Book ISBN',
 'Buscar libro': 'Find a book',
 'Solicitudes activas': 'Active requests',
 'Ofertas por revisar': 'Offers to review',
 'Tus solicitudes': 'Your requests',
 'Ver todas': 'View all',
 'Título, autor o ISBN': 'Title, author or ISBN',
 'Buscar': 'Search',
 'Crear solicitud': 'Create request',
 'Libro seleccionado': 'Selected book',
 'Precio máximo (opcional)': 'Maximum price (optional)',
 'Ej: 15000': 'E.g. 15000',
 'Déjalo vacío si no tienes un máximo': 'Leave blank if you have no maximum',
 '¿En qué estado lo aceptas?': 'Which book conditions do you accept?',
 'Cualquiera': 'Any',
 'Nuevo': 'New',
 'Usado': 'Used',
 '¿Dónde buscas el libro?': 'Where are you looking for the book?',
 'Escribe para buscar tu comuna o ciudad': 'Type to find your municipality or city',
 'Rápido:': 'Quick choice:',
 'Preferencia de entrega': 'Delivery preference',
 'Presencial': 'In person',
 'Envío': 'Shipping',
 '¿Algo más que debamos saber? (opcional)': 'Anything else we should know? (optional)',
 'Por ejemplo, una edición o un idioma en particular': 'For example, a particular edition or language',
 'Publicar solicitud': 'Post request',
 'Tu solicitud está publicada': 'Your request is live',
 'Los vendedores ya pueden verla y enviarte ofertas.': 'Sellers can now see it and send you offers.',
 'Qué pasa ahora': 'What happens next',
 'Los vendedores que tengan el libro te envían una oferta.': 'Sellers who have the book send you an offer.',
 'Comparas precio, estado y ubicación, y aceptas una.': 'Compare price, condition and location, then accept '
                                                        'an offer.',
 'Ves los datos de contacto del vendedor para coordinar.': 'See the seller’s contact details to coordinate.',
 'Ver solicitud': 'View request',
 'Volver al inicio': 'Back to home',
 'Todas': 'All',
 'Activas': 'Active',
 'Resueltas': 'Resolved',
 'Canceladas': 'Cancelled',
 'Detalle de solicitud': 'Request details',
 'Cancelar solicitud': 'Cancel request',
 'Detalle de oferta': 'Offer details',
 'Precio ofrecido · pesos chilenos': 'Offered price · Chilean pesos',
 'El siguiente paso: al aceptar verás el contacto del vendedor. La compra y la entrega se acuerdan directamente entre ustedes.': 'Next: '
                                                                                                                                 'accept '
                                                                                                                                 'to '
                                                                                                                                 'see '
                                                                                                                                 'the '
                                                                                                                                 'seller’s '
                                                                                                                                 'contact '
                                                                                                                                 'details. '
                                                                                                                                 'You '
                                                                                                                                 'arrange '
                                                                                                                                 'purchase '
                                                                                                                                 'and '
                                                                                                                                 'delivery '
                                                                                                                                 'directly '
                                                                                                                                 'with '
                                                                                                                                 'the '
                                                                                                                                 'seller.',
 'Oferta en coordinación. Comunícate con el vendedor mediante sus datos de contacto.': 'Coordination in '
                                                                                       'progress. Reach the '
                                                                                       'seller using their '
                                                                                       'contact details.',
 'Esta oferta está en espera mientras el lector coordina con otra oferta. Si no se concreta, se reactivará.': 'This '
                                                                                                              'offer '
                                                                                                              'is '
                                                                                                              'on '
                                                                                                              'hold '
                                                                                                              'while '
                                                                                                              'the '
                                                                                                              'reader '
                                                                                                              'coordinates '
                                                                                                              'another '
                                                                                                              'offer. '
                                                                                                              'If '
                                                                                                              'that '
                                                                                                              'falls '
                                                                                                              'through, '
                                                                                                              'it '
                                                                                                              'will '
                                                                                                              'become '
                                                                                                              'active '
                                                                                                              'again.',
 'Aceptar para coordinar': 'Accept to coordinate',
 'Ver datos de contacto': 'View contact details',
 'Confirmar compra concretada': 'Confirm completed purchase',
 'Desistir del trato': 'Withdraw from arrangement',
 'Oferta aceptada': 'Offer accepted',
 'Ya pueden ponerse de acuerdo': 'You can now coordinate',
 'Contacto del vendedor': 'Seller’s contact details',
 'La compra y la entrega se coordinan directamente entre tú y el vendedor. La app no procesa pagos ni envíos.': 'You '
                                                                                                                'arrange '
                                                                                                                'purchase '
                                                                                                                'and '
                                                                                                                'delivery '
                                                                                                                'directly '
                                                                                                                'with '
                                                                                                                'the '
                                                                                                                'seller. '
                                                                                                                'The '
                                                                                                                'app '
                                                                                                                'does '
                                                                                                                'not '
                                                                                                                'process '
                                                                                                                'payments '
                                                                                                                'or '
                                                                                                                'shipping.',
 'SOLICITUDES DISPONIBLES': 'AVAILABLE REQUESTS',
 'Encuentra lectores y envía tu oferta.': 'Find readers and send your offer.',
 'Comuna o ciudad': 'Municipality or city',
 'Presupuesto mín.': 'Minimum budget',
 'Búsquedas recientes': 'Recent requests',
 '¿Tienes un libro que alguien busca? Abre su solicitud y cuéntale qué ofreces.': 'Have a book someone is '
                                                                                  'looking for? Open their '
                                                                                  'request and tell them '
                                                                                  'what you can offer.',
 'Solicitud': 'Request',
 'Puedo ofrecerlo': 'I can offer it',
 'Crear oferta': 'Create offer',
 'Precio': 'Price',
 'Ej: 12990': 'E.g. 12990',
 'Estado del libro': 'Book condition',
 'Condición (ej: sin subrayar)': 'Condition (e.g. no highlighting)',
 'Información adicional (opcional)': 'Additional information (optional)',
 'Datos de contacto': 'Contact details',
 'Elige cómo quieres que te contacten. El lector verá estos datos al aceptar tu oferta.': 'Choose how you '
                                                                                          'want to be '
                                                                                          'contacted. The '
                                                                                          'reader will see '
                                                                                          'these details '
                                                                                          'after accepting '
                                                                                          'your offer.',
 'Teléfono': 'Phone',
 'Dirección o punto de entrega': 'Address or meeting point',
 'Publicar oferta': 'Post offer',
 'Aceptadas': 'Accepted',
 'Finalizadas': 'Finished',
 'Administración': 'Administration',
 'Usuarios': 'Users',
 'Lectores': 'Readers',
 'Vendedores': 'Sellers',
 'Solicitudes': 'Requests',
 'Con ofertas': 'With offers',
 'Ofertas': 'Offers',
 'Gestión': 'Management',
 'Ver, filtrar y moderar solicitudes': 'View, filter and moderate requests',
 'Consultar y suspender usuarios': 'View and suspend users',
 'Historial de ofertas de la plataforma': 'Platform offer history',
 'Auditoría / Actividad': 'Audit / Activity',
 'Buscar y exportar logs de actividad': 'Search and export activity logs',
 'Buscar por acción, detalle o actor': 'Search by action, detail or actor',
 'Exportar logs de actividad': 'Export activity logs',
 'Borrador': 'Draft',
 'Publicada': 'Published',
 'En coordinación': 'In coordination',
 'Resuelta': 'Resolved',
 'Cancelada': 'Cancelled',
 'Activa': 'Active',
 'Por concretar': 'To be completed',
 'En espera': 'On hold',
 'Concretada': 'Completed',
 'Rechazada': 'Rejected',
 'Activo': 'Active',
 'Suspendido': 'Suspended',
 'Sin máximo': 'No maximum',
 'Sin ofertas todavía': 'No offers yet',
 ' por revisar': ' to review',
 's': 's',
 'Nuevo o usado': 'New or used',
 '[b]Sin tope[/b]': '[b]No maximum[/b]',
 'Precio máximo': 'Maximum price',
 'Condición aceptada': 'Accepted condition',
 'Ubicación': 'Location',
 'Entrega': 'Delivery',
 'Notas': 'Notes',
 'Entendido': 'Got it',
 'Tienes ofertas por revisar': 'You have offers to review',
 'Modo sin conexión: los datos quedan solo en este teléfono.': 'Offline mode: data stays on this phone only.',
 'Modo sin conexión: mostrando la configuración local.': 'Offline mode: showing local configuration.',
 'No se pudieron guardar los cambios.': 'The changes could not be saved.',
 'Escribe tu correo en el campo de arriba.': 'Enter your email in the field above.',
 'Recuperar contraseña': 'Recover password',
 'Aún no tienes solicitudes. Busca un libro para crear la primera.': 'You have no requests yet. Find a book '
                                                                     'to create your first one.',
 'Escribe al menos 2 caracteres para buscar.': 'Enter at least 2 characters to search.',
 'Buscando…': 'Searching…',
 'catálogo de ejemplo (sin conexión)': 'sample catalog (offline)',
 'Autor desconocido': 'Unknown author',
 'No encontramos libros. Prueba con otro término.': 'No books found. Try another search term.',
 'No hay solicitudes en esta categoría.': 'No requests in this category.',
 'moderación administrativa': 'administrative moderation',
 'el lector': 'the reader',
 'Moderación / Cancelación': 'Moderation / Cancellation',
 'Sin descripción de condición': 'No condition description',
 'Todavía no hay ofertas. Te avisaremos aquí cuando llegue una.': 'No offers yet. New offers will appear '
                                                                  'here.',
 'Solicitud cancelada.': 'Request cancelled.',
 '¿Cancelar solicitud?': 'Cancel request?',
 'Los vendedores dejarán de verla y las ofertas activas se cancelarán.': 'Sellers will no longer see it and '
                                                                         'active offers will be cancelled.',
 'Oferta de ': 'Offer from ',
 'Condición': 'Condition',
 'Información adicional': 'Additional information',
 'Fecha de la oferta': 'Offer date',
 'Atención': 'Please note',
 'Nota de condición': 'Condition note',
 '¿Aceptar esta oferta?': 'Accept this offer?',
 "La oferta pasará a estado 'Por concretar' y verás los datos de contacto del vendedor para coordinar la entrega. Las demás ofertas quedarán en espera.": 'The '
                                                                                                                                                          'offer '
                                                                                                                                                          'will '
                                                                                                                                                          'move '
                                                                                                                                                          'to '
                                                                                                                                                          "'To "
                                                                                                                                                          'be '
                                                                                                                                                          "completed' "
                                                                                                                                                          'and '
                                                                                                                                                          'you '
                                                                                                                                                          'will '
                                                                                                                                                          'see '
                                                                                                                                                          'the '
                                                                                                                                                          'seller’s '
                                                                                                                                                          'contact '
                                                                                                                                                          'details '
                                                                                                                                                          'to '
                                                                                                                                                          'arrange '
                                                                                                                                                          'delivery. '
                                                                                                                                                          'Other '
                                                                                                                                                          'offers '
                                                                                                                                                          'will '
                                                                                                                                                          'be '
                                                                                                                                                          'placed '
                                                                                                                                                          'on '
                                                                                                                                                          'hold.',
 '¡Trato concretado con éxito! La solicitud quedó resuelta.': 'Arrangement completed! The request is now '
                                                              'resolved.',
 '¿Confirmar trato concretado?': 'Confirm completed arrangement?',
 'Confirma que compraste/recibiste el libro. La solicitud quedará resuelta definitivamente y las demás ofertas se cerrarán.': 'Confirm '
                                                                                                                              'that '
                                                                                                                              'you '
                                                                                                                              'purchased/received '
                                                                                                                              'the '
                                                                                                                              'book. '
                                                                                                                              'The '
                                                                                                                              'request '
                                                                                                                              'will '
                                                                                                                              'be '
                                                                                                                              'permanently '
                                                                                                                              'resolved '
                                                                                                                              'and '
                                                                                                                              'other '
                                                                                                                              'offers '
                                                                                                                              'will '
                                                                                                                              'be '
                                                                                                                              'closed.',
 'Confirmar compra': 'Confirm purchase',
 'Se canceló la coordinación. Las demás ofertas vuelven a estar activas.': 'Coordination cancelled. Other '
                                                                           'offers are active again.',
 '¿Desistir de este trato?': 'Withdraw from this arrangement?',
 'Se cancelará la coordinación con este vendedor y las otras ofertas volverán a estar activas para que puedas elegir otra opción.': 'Coordination '
                                                                                                                                    'with '
                                                                                                                                    'this '
                                                                                                                                    'seller '
                                                                                                                                    'will '
                                                                                                                                    'be '
                                                                                                                                    'cancelled '
                                                                                                                                    'and '
                                                                                                                                    'other '
                                                                                                                                    'offers '
                                                                                                                                    'will '
                                                                                                                                    'become '
                                                                                                                                    'active '
                                                                                                                                    'so '
                                                                                                                                    'you '
                                                                                                                                    'can '
                                                                                                                                    'choose '
                                                                                                                                    'another '
                                                                                                                                    'option.',
 'Dirección / punto de entrega': 'Address / meeting point',
 'solicitud disponible': 'available request',
 'solicitudes disponibles': 'available requests',
 'No hay solicitudes que coincidan con los filtros.': 'No requests match these filters.',
 'Esta solicitud ya no recibe ofertas.': 'This request is no longer accepting offers.',
 '¡Oferta publicada! El lector ya puede revisarla.': 'Offer posted! The reader can now review it.',
 'Oferta publicada': 'Offer posted',
 'El lector recibirá tu oferta y podrá aceptarla.': 'The reader will receive your offer and can accept it.',
 '¡En coordinación! El lector está revisando tus datos de contacto para cerrar la compra.': 'Coordination in '
                                                                                            'progress! The '
                                                                                            'reader is '
                                                                                            'reviewing your '
                                                                                            'contact details '
                                                                                            'to complete the '
                                                                                            'purchase.',
 'En espera: el lector está coordinando con otra oferta. Si desiste, tu oferta volverá a activarse.': 'On '
                                                                                                      'hold: '
                                                                                                      'the '
                                                                                                      'reader '
                                                                                                      'is '
                                                                                                      'coordinating '
                                                                                                      'another '
                                                                                                      'offer. '
                                                                                                      'If '
                                                                                                      'they '
                                                                                                      'withdraw, '
                                                                                                      'your '
                                                                                                      'offer '
                                                                                                      'will '
                                                                                                      'become '
                                                                                                      'active '
                                                                                                      'again.',
 '¡Trato concretado! Compra finalizada con éxito.': 'Arrangement completed! Purchase completed successfully.',
 'El lector concretó otra oferta.': 'The reader completed another offer.',
 'Cancelar oferta': 'Cancel offer',
 'No tienes ofertas en esta categoría.': 'You have no offers in this category.',
 'Oferta cancelada.': 'Offer cancelled.',
 '¿Cancelar oferta?': 'Cancel offer?',
 'El lector ya no podrá aceptarla.': 'The reader will no longer be able to accept it.',
 'Desististe del trato. La solicitud vuelve a recibir ofertas.': 'You withdrew from the arrangement. The '
                                                                 'request is accepting offers again.',
 '¿Desistir del trato?': 'Withdraw from arrangement?',
 'Tu oferta se cancelará y el lector podrá elegir otra oferta o recibir nuevas.': 'Your offer will be '
                                                                                  'cancelled and the reader '
                                                                                  'can choose another offer '
                                                                                  'or receive new ones.',
 'Cancelar (moderar)': 'Cancel (moderate)',
 'Sin registros.': 'No records.',
 'Acción de moderación: quedará registrada en la actividad y el lector verá el motivo.': 'Moderation action: '
                                                                                         'it will be logged '
                                                                                         'in the activity '
                                                                                         'and the reader '
                                                                                         'will see the '
                                                                                         'reason.',
 'Cancelar': 'Cancel',
 'Suspender': 'Suspend',
 'Reactivar': 'Reactivate',
 'sistema': 'system',
 'Sin registros de actividad.': 'No activity records.',
 'Logs exportados': 'Logs exported',
 'No se pudo exportar el registro de actividad.': 'The activity log could not be exported.',
 'Debes iniciar sesión.': 'You must sign in.',
 'Tu cuenta está suspendida.': 'Your account is suspended.',
 'No tienes permisos para esta acción.': 'You do not have permission for this action.',
 'El libro seleccionado no es válido.': 'The selected book is invalid.',
 'Debes seleccionar un libro.': 'Select a book.',
 'Selecciona la condición aceptada.': 'Select an accepted condition.',
 'Selecciona una preferencia de entrega.': 'Select a delivery preference.',
 'Indica tu ubicación.': 'Enter your location.',
 'No puedes ver esta solicitud.': 'You cannot view this request.',
 'Solo puedes cancelar tus propias solicitudes.': 'You can only cancel your own requests.',
 'La solicitud ya no recibe ofertas.': 'This request is no longer accepting offers.',
 'Ya tienes una oferta activa para esta solicitud.': 'You already have an active offer for this request.',
 'Indica si el libro es nuevo o usado.': 'Specify whether the book is new or used.',
 'El correo de contacto no es válido.': 'The contact email is invalid.',
 'Agrega al menos un dato de contacto.': 'Add at least one contact detail.',
 'No puedes ver esta oferta.': 'You cannot view this offer.',
 'El contacto se muestra al coordinar o aceptar la oferta.': 'Contact details are shown when coordinating or '
                                                             'accepting an offer.',
 'Solo puedes aceptar ofertas de tus solicitudes.': 'You can only accept offers for your own requests.',
 'Esta oferta ya no está disponible.': 'This offer is no longer available.',
 'Solo puedes confirmar tratos de tus solicitudes.': 'You can only confirm arrangements for your own '
                                                     'requests.',
 'Solo puedes confirmar ofertas que estén en coordinación.': 'You can only confirm offers in coordination.',
 'No puedes desistir de este trato.': 'You cannot withdraw from this arrangement.',
 'Esta oferta no está en coordinación.': 'This offer is not in coordination.',
 'Solo puedes cancelar tus propias ofertas.': 'You can only cancel your own offers.',
 'Esta oferta está en coordinación: usa «Desistir del trato».': 'This offer is in coordination: use '
                                                                '“Withdraw from arrangement”.',
 'No se puede suspender a un administrador.': 'An administrator cannot be suspended.',
 'Estado de usuario inválido.': 'Invalid user status.',
 'Tu sesión venció: vuelve a iniciar sesión.': 'Your session expired: sign in again.',
 'Sin conexión con el servidor. Revisa internet e inténtalo de nuevo.': 'Cannot connect to the server. Check '
                                                                        'your internet connection and try '
                                                                        'again.',
 'Solicitud no encontrada.': 'Request not found.',
 'Oferta no encontrada.': 'Offer not found.',
 'Usuario no encontrada.': 'User not found.',
 'Libro no encontrada.': 'Book not found.',
 'Sin portada': 'No cover',
 'Misma comuna': 'Same municipality',
 'Sin ubicación': 'No location',
 '[size=12sp]Máximo [/size][b]{v1}[/b]': '[size=12sp]Maximum [/size][b]{v1}[/b]',
 '{v0} oferta(s) activa(s) en tus solicitudes.': '{v0} active offer(s) on your requests.',
 '{v0} oferta': '{v0} offer',
 '{v0} resultado(s) · {v2}': '{v0} result(s) · {v2}',
 'Ofertas recibidas ({v1})': 'Offers received ({v1})',
 'Busca: {v1} · Máximo {v3} · {v5}': 'Wanted: {v1} · Maximum {v3} · {v5}',
 'SOLICITUD N.º {v1}': 'REQUEST No. {v1}',
 'Cancelada por {v1}': 'Cancelled by {v1}',
 'Ya tienes una oferta activa de {v1} para esta solicitud.': 'You already have an active offer of {v1} for '
                                                             'this request.',
 'Si existe una cuenta asociada a {v1}, recibirás un enlace para restablecer tu contraseña.\n\n(Simulado: el demo no envía correos.)': 'If '
                                                                                                                                       'an '
                                                                                                                                       'account '
                                                                                                                                       'exists '
                                                                                                                                       'for '
                                                                                                                                       '{v1}, '
                                                                                                                                       'you '
                                                                                                                                       'will '
                                                                                                                                       'receive '
                                                                                                                                       'a '
                                                                                                                                       'password '
                                                                                                                                       'reset '
                                                                                                                                       'link.\n'
                                                                                                                                       '\n'
                                                                                                                                       '(Simulated: '
                                                                                                                                       'the '
                                                                                                                                       'demo '
                                                                                                                                       'does '
                                                                                                                                       'not '
                                                                                                                                       'send '
                                                                                                                                       'emails.)',
 '¡Bienvenido/a, {v1}!': 'Welcome, {v1}!',
 ' · Motivo: {v1}': ' · Reason: {v1}',
 'Se guardó el registro de actividad en:\n\n{v1}': 'The activity log was saved to:\n\n{v1}',
 'Supera tu precio máximo ({v1})': 'Exceeds your maximum price ({v1})',
 'Ofrecido como {v1} (solicitabas {v3})': 'Offered as {v1} (you requested {v3})',
 'Solicitud #{v1} cancelada por moderación.': 'Request #{v1} cancelled by moderation.',
 '{v0} · {v2} · máx. {v4}': '{v0} · {v2} · max. {v4}',
 '{v0} oferta(s) · actualizada {v2}': '{v0} offer(s) · updated {v2}',
 'Alta: {v1}': 'Joined: {v1}',
 'Oferta #{v1} · {v3}': 'Offer #{v1} · {v3}',
 'Solicitud #{v1} · {v3}': 'Request #{v1} · {v3}',
 'Solicitud #{v1} · {v3} · máx. {v5}': 'Request #{v1} · {v3} · max. {v5}',
 '{v0} debe ser un número entero.': '{v0} must be a whole number.',
 '{v0} debe ser mayor que 0.': '{v0} must be greater than 0.',
 '{v0} es demasiado alto.': '{v0} is too high.',
 '{v0} es obligatorio.': '{v0} is required.',
 'No se puede pasar de {v1} a {v3}.': 'Cannot change from {v1} to {v3}.',
 'Error del servidor ({v1}).': 'Server error ({v1}).',
 'Tu próximo libro\nempieza aquí.': 'Your next book\nstarts here.',
 'Alguien busca ese\nlibro que tienes.': 'Someone is looking for\nthat book you have.',
 'Misma región': 'Same region',
 'Otra región ({v0})': 'Other region ({v0})',
 'El precio': 'The price',
 'El precio máximo': 'The maximum price',
 'El presupuesto': 'The budget',
 'BookWho? · Tu próximo libro': 'BookWho? · Your next book'}


def translate(text, language="es", **values):
    localized = ENGLISH.get(text, text) if language == "en" else text
    return localized.format_map(values) if values else localized


def translate_error(text, language="es"):
    """Traduce errores conocidos, conservando mensajes externos desconocidos."""
    if language != "en" or text in ENGLISH:
        return translate(text, language)
    for template in ERROR_TEMPLATES:
        parts = list(Formatter().parse(template))
        pattern = "".join(re.escape(literal) + ("(.+?)" if field else "")
                          for literal, field, _, _ in parts)
        match = re.fullmatch(pattern, text, flags=re.DOTALL)
        if match:
            fields = [field for _, field, _, _ in parts if field]
            values = dict(zip(fields, match.groups()))
            values = {key: translate(value, language) for key, value in values.items()}
            return translate(template, language, **values)
    return text

ERROR_TEMPLATES = (
    "{v0} debe ser un número entero.", "{v0} debe ser mayor que 0.",
    "{v0} es demasiado alto.", "{v0} es obligatorio.",
    "No se puede pasar de {v1} a {v3}.", "Error del servidor ({v1}).",
)
