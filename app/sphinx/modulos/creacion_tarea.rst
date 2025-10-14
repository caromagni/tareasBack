==================
Creación de Tarea
==================

¿Qué es y para qué sirve?
-------------------------

El módulo de **Creación de Tarea** es la herramienta que te permite registrar nuevas actividades de forma rápida, clara y segura. Desde aquí definís el tipo de tarea, su prioridad, a quién se asigna, las fechas y la descripción, vinculándola opcionalmente a un expediente. Todo con validaciones en tiempo real para evitar errores y asegurar coherencia con los flujos de trabajo judiciales o administrativos.

Índice de Contenidos
--------------------

.. contents::
   :local:
   :depth: 2

**Navegación Rápida:**

1. `Componentes de la Interfaz`_ - Diálogo, controles y estados
2. `Flujos de Trabajo Típicos`_ - Casos de uso comunes
3. `Consideraciones Importantes`_ - Validaciones y reglas
4. `Interfaz de Usuario`_ - Elementos visuales y accesibilidad
5. `Casos de Uso Comunes`_ - Por tipo de usuario
6. `Consejos útiles`_ - Recomendaciones prácticas
7. `¿Necesitas ayuda?`_ - Soporte y mensajes del sistema

1. Componentes de la Interfaz
------------------------------

1.1. Diálogo "Nueva Tarea" - ¿Qué ves aquí?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Funcionalidades disponibles:**

- Crear una nueva tarea con campos guiados
- Validaciones en tiempo real
- Notificaciones de éxito/error

**Botones de acción:**

- **Guardar** - Crea la tarea (se desactiva si hay errores o durante el envío)
- **Cancelar** - Cierra sin guardar

**Estados del sistema:**

- **Carga inicial** - Se muestran skeletons mientras se obtienen datos (grupos, tipos, expedientes, etc.)
- **Envío** - El botón Guardar muestra un spinner (CircularProgress)
- **Resultado** - Snackbar de confirmación (Tarea creada exitosamente) o error

1.2. Campos del Formulario
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Obligatorios:**

- **Tipo de Tarea** - Define la naturaleza del trabajo (agrupado por nivel: Expediente / Actuación / Interna)
- **Subtipo de Tarea** - Si el tipo seleccionado lo requiere
- **Título** - Nombre claro y descriptivo
- **Grupo** - Área responsable donde "vive" la tarea
- **Prioridad** - Alta (1), Media (2), Baja (3) — por defecto, Baja
- **Fecha de inicio** - Día a partir del cual empieza a correr
- **Fecha de fin** - Fecha límite para completar la tarea

**Opcionales:**

- **Usuario asignado** - Integrante del grupo (se puede definir luego)
- **Expediente** - Vínculo administrativo/judicial
- **Descripción** - Hasta 250 caracteres (mínimo 6 si escribís algo)

**Comportamientos útiles:**

- Al seleccionar Grupo, se cargan los Usuarios de ese grupo
- Contador de caracteres en Descripción

1.3. Fuentes de datos
^^^^^^^^^^^^^^^^^^^^^

- **GrupoService** - Lista de grupos disponibles
- **TaskTypeService** - Tipos de tarea habilitados (y sus subtipos si existen)
- **ActuacionService y ExpedienteService** - Catálogos para vínculos
- **DominioService** - Muestra el dominio actual (informativo)

2. Flujos de Trabajo Típicos
------------------------------

2.1. Crear una tarea simple (rápida)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Elegí Tipo de Tarea (y Subtipo si corresponde)
2. Completá Título
3. Seleccioná Prioridad
4. Elegí Grupo (y, si querés, Usuario asignado)
5. Definí Fecha de inicio y Fecha de fin
6. (Opcional) Agregá Descripción
7. Presioná Guardar

2.2. Asignar una tarea a una persona del grupo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Seleccioná Grupo
2. Elegí Usuario asignado (lista filtrada por el grupo)
3. Completá Tipo, Título, Prioridad y Fechas
4. Guardar

2.3. Vincular una tarea a un expediente
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Completá los datos base (Tipo, Título, Grupo, etc.)
2. En Expediente, seleccioná la carátula correspondiente
3. Guardar

3. Consideraciones Importantes
------------------------------

3.1. Validaciones de Seguridad que te protegen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Fecha de inicio** - No puede ser anterior a hoy
- **Fecha de fin** - Debe ser posterior o igual a Fecha de inicio

**Título obligatorio:**

- No puede comenzar con número ni con caracter especial
- Debe tener al menos 4 caracteres
- No admite ciertos caracteres especiales

**Otras validaciones:**

- **Descripción** (si se completa) - Mínimo 6 y máximo 250 caracteres
- **Grupo obligatorio** - Usuario opcional

3.2. Comportamiento del Sistema que facilita tu trabajo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- El botón Guardar se desactiva si el formulario es inválido o hay errores de fecha
- Se envían solo los campos completos y válidos (payload limpio)
- Si el Tipo de Tarea posee subtipos, el Subtipo pasa a ser obligatorio
- Los Usuarios disponibles dependen del Grupo seleccionado

3.3. Rendimiento optimizado para tu comodidad
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Búsquedas y ordenamientos en listas de selección (tipos, grupos)
- Carga diferida: se consulta lo necesario al abrir el formulario
- Mensajes claros de error y éxito para tomar decisiones rápido

4. Interfaz de Usuario
-----------------------

4.1. Elementos Visuales que facilitan la navegación
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Autocomplete con agrupación por nivel (Expediente / Actuación / Interna)
- Chips/labels y helper texts para indicar estados y errores
- Colores semánticos en mensajes (éxito/error)
- Skeletons de carga para una experiencia fluida

4.2. Accesibilidad para todos los usuarios
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Navegación por teclado en inputs y selectores
- Contraste adecuado y labels claros
- Tooltips y mensajes de ayuda contextual
- Diseño responsive para distintos tamaños de pantalla

5. Casos de Uso Comunes
------------------------

5.1. Administrador del Sistema
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Asegurar que existan Tipos/Subtipos y Grupos correctos
- Monitorear que las tareas se creen con fechas válidas
- Auditar mensajes de error recurrentes para mejorar datos base

5.2. Líder de Equipo
^^^^^^^^^^^^^^^^^^^^

- Crear tareas para su área, asignarlas a miembros del grupo
- Priorizar tareas (Alta/Media/Baja) según urgencia

5.3. Usuario Final
^^^^^^^^^^^^^^^^^^

- Registrar tareas propias o del área
- Elegir Grupo correcto y, si corresponde, Usuario asignado
- Usar Descripción breve y clara (6–250 caracteres)

6. Consejos útiles para el usuario
----------------------------------

**Antes de crear una tarea:**

- **Título** - Usá nombres descriptivos ("Revisar antecedentes", "Cargar informe")
- **Grupo/Usuario** - Si no estás seguro del usuario, seleccioná el Grupo y asigná después
- **Descripción** - Evitá pegar textos extensos; sintetizá en hasta 250 caracteres
- **Errores** - Leé el mensaje que aparece debajo del campo para corregir rápido

7. ¿Necesitas ayuda?
---------------------

- Los mensajes de error te indican qué corregir
- Las validaciones evitan incoherencias (fechas, título, descripción)
- Los tooltips suman contexto en inputs complejos
- El snackbar confirma si la tarea se creó o si hubo un problema

Esta documentación proporciona una guía completa para entender y utilizar el módulo de Creación de Tarea de manera efectiva, combinando información técnica con orientación práctica para el usuario.

.. [#] Editado por M.B.
