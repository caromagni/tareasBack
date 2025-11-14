===================================
Lógica de Asignación y Control
===================================

¿Qué es y para qué sirve?
-------------------------

Este módulo describe la **lógica de asignación, control y visualización** de las tareas en el contexto de los grupos y grupos base. Define las reglas fundamentales que determinan quién puede asignar, ver y controlar las tareas dentro del sistema, garantizando la seguridad y coherencia en la gestión de actividades.

Índice de Contenidos
--------------------

.. contents::
   :local:
   :depth: 2

**Navegación Rápida:**

1. `Asignación de Tareas`_ - Reglas de asignación
2. `Control de Tareas`_ - Gestión de permisos
3. `Visibilidad de Tareas`_ - Qué ve cada usuario

1. Asignación de Tareas
-----------------------

1.1. Restricción por Grupo Base
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Regla fundamental:**

- Una tarea solo puede asignarse a usuarios que pertenezcan a grupos del **mismo grupo base**
- Esta restricción garantiza que las tareas permanezcan dentro del ámbito organizacional correcto
- No es posible asignar tareas entre diferentes grupos base (diferentes organismos/dominios)

1.2. Restricción por Estado del Usuario
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Validaciones de seguridad:**

- **No se puede asignar** la tarea a usuarios eliminados
- **No se puede asignar** la tarea a usuarios suspendidos
- Solo usuarios activos pueden recibir asignaciones de tareas

1.3. Asignación a Usuarios y Grupos
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Reglas de asignación:**

- **Grupo obligatorio** - Toda tarea debe estar asignada al menos a un grupo
- **Usuario opcional** - La tarea puede asignarse a un usuario específico o quedar disponible para el grupo
- **Usuario por defecto** - Si el grupo tiene configurado un usuario por defecto, la tarea se le asigna automáticamente
- **Sin asignación específica** - Si no hay usuario por defecto, la tarea queda disponible para cualquier miembro del grupo

2. Control de Tareas
--------------------

2.1. Control Total dentro del Grupo Base
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Alcance del control:**

- Una tarea tiene **control total** para un grupo base determinado
- Todos los grupos que formen parte de ese grupo base tienen control
- Los usuarios deben pertenecer a esos grupos para tener acceso
- El control incluye: visualización, edición, reasignación y gestión completa

2.2. Pérdida de Control al Reasignar
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Comportamiento importante:**

- Si la tarea se reasigna a un grupo que está **fuera del grupo base original**, los usuarios que previamente tuvieron acceso **pierden el control** de la tarea
- Esta pérdida de control es automática e inmediata

**Excepción - Creación de Notas:**

- Aunque se pierda el control total, los usuarios que tuvieron acceso previo pueden seguir **creando notas** en la tarea
- Esta funcionalidad permite mantener la trazabilidad y comunicación sobre tareas transferidas

2.3. Implicaciones del Control
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Acciones permitidas con control total:**

- Ver detalles completos de la tarea
- Editar información de la tarea
- Cambiar estado de la tarea
- Reasignar a otros usuarios del mismo grupo base
- Agregar y editar notas
- Gestionar prioridades y fechas

**Acciones sin control total:**

- Solo crear notas (para usuarios que perdieron control por reasignación)

3. Visibilidad de Tareas
------------------------

3.1. Regla de Visibilidad en la Bandeja
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Principio fundamental:**

- Un usuario verá en su bandeja **todas las tareas** asociadas a grupos a los que pertenece
- **No importa** a qué grupo específico esté asignada la tarea
- Solo se requiere que el usuario pertenezca al menos a **uno de los grupos** asociados a la tarea

3.2. Ejemplos de Visibilidad
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Caso 1 - Usuario en un grupo:**

- Usuario "Juan" pertenece al grupo "Secretaría Civil"
- Verá todas las tareas asignadas a "Secretaría Civil"

**Caso 2 - Usuario en múltiples grupos:**

- Usuario "María" pertenece a "Secretaría Civil" y "Mesa de Entradas"
- Verá todas las tareas de ambos grupos en su bandeja unificada

**Caso 3 - Tarea reasignada:**

- Tarea originalmente en "Secretaría Civil" se reasigna a "Secretaría Penal"
- Solo usuarios de "Secretaría Penal" la verán en su bandeja
- Usuarios de "Secretaría Civil" la pierden de vista (excepto para agregar notas)

4. Resumen de Reglas Clave
---------------------------

**Reglas de Asignación:**

1. Mismo grupo base obligatorio
2. Solo usuarios activos
3. Grupo siempre requerido, usuario opcional

**Reglas de Control:**

1. Control total dentro del grupo base
2. Pérdida de control al salir del grupo base
3. Siempre se pueden crear notas (trazabilidad)

**Reglas de Visibilidad:**

1. Se ve si perteneces al grupo de la tarea
2. No importa cuántos grupos tenga la tarea
3. La reasignación cambia la visibilidad inmediatamente

Esta documentación proporciona las reglas fundamentales para entender cómo funciona el sistema de asignación y control de tareas, garantizando una gestión segura y coherente de las actividades.

.. [#] Editado por M.B.
