==============================
Actualización de Tareas en Lote
==============================

¿Qué es y para qué sirve?
-------------------------

El módulo de **Actualización de Tareas en Lote** te permite modificar muchas tareas a la vez de forma rápida, segura y consistente. Podés actualizar campos clave como grupo, usuario asignado, prioridad y fecha de fin (y, si corresponde, plazo), con validaciones en tiempo real que te evitan errores y aseguran coherencia con las reglas del sistema.

.. important::
   Ámbito del lote: las tareas que se actualizarán son las que están actualmente filtradas mediante el panel de filtros (a la derecha). Si cambiás los filtros, cambia el conjunto de tareas afectadas. Verificá los filtros antes de presionar Guardar.

Índice de Contenidos
--------------------

.. contents::
   :local:
   :depth: 2

**Navegación Rápida:**

1. `¿Qué podés hacer?`_ - Funcionalidades principales
2. `¿Cómo usarlo?`_ - Pasos para actualizar tareas
3. `Reglas importantes`_ - Qué tener en cuenta
4. `Ejemplos prácticos`_ - Situaciones comunes
5. `Consejos útiles`_ - Recomendaciones prácticas

1. ¿Qué podés hacer?
--------------------

Con esta herramienta podés actualizar muchas tareas al mismo tiempo. Es útil cuando necesitás:

- Cambiar el grupo o persona responsable de varias tareas
- Actualizar la prioridad (Alta, Media o Baja)
- Modificar la fecha de fin de múltiples tareas
- Quitar la asignación de usuario (dejar solo el grupo)

**Campos que podés actualizar:**

- **Grupo** - A qué área pertenecen las tareas
- **Usuario asignado** - Quién es responsable (o dejarlo sin asignar)
- **Prioridad** - Qué tan urgente es (Alta, Media o Baja)
- **Fecha de fin** - Cuándo deben estar terminadas

**Importante saber:**

- Primero elegí el Grupo, y luego vas a ver los usuarios de ese grupo
- Si elegís "Sin asignar", las tareas quedan solo con grupo (sin usuario específico)
- Solo se actualizan los campos que modificás, el resto queda igual

2. ¿Cómo usarlo?
------------------------------

2.1. Cambiar responsable y prioridad de muchas tareas
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Seleccioná Grupo
2. Elegí Usuario asignado (o "Sin asignar")
3. Cambiá Prioridad (Alta/Media/Baja)
4. (Opcional) Definí Fecha de fin
5. Guardar

2.2. Solo actualizar la fecha de fin en lote
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Dejá Grupo y Usuario sin cambios
2. Elegí una Fecha de fin válida para todas
3. Guardar

2.3. Mover tareas a otro grupo y quitar asignación
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Elegí Grupo destino
2. En Usuario asignado, seleccioná "Sin asignar"
3. (Opcional) Ajustá Prioridad o Fecha de fin
4. Guardar

3. Reglas importantes
----------------------

¿Qué tareas se van a actualizar?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Importante**: Se actualizan TODAS las tareas que aparecen según el filtro que tengas activo
- No importa en qué página estés, afecta a todas las tareas filtradas
- **Recomendación**: Antes de guardar, verificá el contador de tareas y revisá que sean las correctas

Restricciones de fechas
^^^^^^^^^^^^^^^^^^^^^^^^

La fecha de fin que pongas debe ser:

- Posterior a hoy (no podés poner una fecha pasada)
- Posterior a la fecha de inicio de las tareas

Si intentás poner una fecha inválida, el sistema te va a avisar y no te va a dejar guardar.

Grupos y usuarios
^^^^^^^^^^^^^^^^^

- Para asignar una persona, primero tenés que elegir el Grupo
- Si querés dejar las tareas sin persona asignada, elegí "Sin asignar"
- Solo se muestran las personas que pertenecen al grupo que elegiste

¿Cuándo NO se puede guardar?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

El botón de Guardar se desactiva cuando:

- No hiciste ningún cambio
- Hay errores en las fechas
- Ya se está guardando (para evitar duplicados)

4. Ejemplos prácticos
----------------------

Situación 1: Reasignar tareas a otra persona
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Caso:** Necesitás pasar todas las tareas de Juan a María.

1. Filtrá las tareas de Juan usando el panel de filtros
2. Abrí "Actualizar en Lote"
3. Elegí el Grupo (si hace falta)
4. Seleccioná a María como Usuario asignado
5. Guardar

Situación 2: Hacer todas las tareas urgentes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Caso:** Hay un grupo de tareas que necesitan mayor prioridad.

1. Filtrá las tareas que querés actualizar
2. Abrí "Actualizar en Lote"
3. Cambiá la Prioridad a "Alta"
4. Guardar

Situación 3: Extender plazos
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Caso:** Se extendieron los plazos y necesitás actualizar la fecha de fin.

1. Filtrá las tareas afectadas
2. Abrí "Actualizar en Lote"
3. Elegí la nueva Fecha de fin
4. Guardar

Situación 4: Liberar tareas de asignación personal
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Caso:** Querés que las tareas queden disponibles para que cualquiera del grupo las tome.

1. Filtrá las tareas
2. Abrí "Actualizar en Lote"
3. En Usuario asignado, elegí "Sin asignar"
4. Guardar

5. Consejos útiles
----------------------------------

Antes de guardar
^^^^^^^^^^^^^^^^

- **Revisá el filtro**: Asegurate de que las tareas filtradas son las que querés actualizar


Al usar la herramienta
^^^^^^^^^^^^^^^^^^^^^^^

- **Primero el Grupo, después el Usuario**: Elegí el grupo para ver las personas de ese grupo
- **"Sin asignar" es útil**: Usalo cuando querés liberar tareas para que otros las tomen
- **Solo cambiá lo necesario**: No hace falta tocar todos los campos, solo los que querés actualizar

Si hay problemas
^^^^^^^^^^^^^^^^

- **Fechas inválidas**: Si no te deja elegir una fecha, fijate el mensaje que aparece debajo
- **Botón deshabilitado**: Si no podés guardar, revisá que hayas hecho cambios y que no haya errores
- **Mensajes de error**: Leé el texto que aparece debajo de los campos, te dice qué corregir

Después de guardar
^^^^^^^^^^^^^^^^^^

- Vas a ver un mensaje confirmando que las tareas se actualizaron
- Si algo falló, el mensaje te va a decir qué pasó
- Podés verificar los cambios viendo las tareas actualizadas

.. [#] Editado por M.B.