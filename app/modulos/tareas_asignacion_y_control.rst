.. _tareas:

====================
Lógica de las Tareas
====================

Este documento describe la lógica de asignación, control y visibilidad de las tareas en el contexto de los grupos y grupos base.

-----------------------------
1. Asignación de Tareas
-----------------------------
- **Mismo Grupo Base**:  
  Una tarea solo puede asignarse a usuarios que pertenezcan a grupos del mismo grupo base.
- **Restricción de Estado del Usuario**:  
  No se puede asignar la tarea a usuarios eliminados o suspendidos.

-----------------------------
2. Control de Tareas
-----------------------------
- **Control Total dentro del Grupo Base**:  
  Una tarea tiene control total para un grupo base determinado y los grupos que formen parte de él, siempre que los usuarios pertenezcan a esos grupos.
- **Pérdida de Control al Reasignar**:  
  Si la tarea se reasigna a un grupo que está fuera de ese grupo base, los usuarios que previamente tuvieron acceso pierden el control de la tarea.  
  - **Excepción**:  
    En este caso, la única acción que permanece disponible para dichos usuarios es la creación de notas.

-----------------------------
3. Visibilidad de Tareas en la Bandeja del Usuario
-----------------------------
- **Visibilidad de Tareas**:  
  Un usuario verá en su bandeja todas las tareas, sin importar a qué grupo pertenezcan, siempre y cuando él pertenezca al menos a uno de los grupos asociados a la tarea.

-----------------------------
Índice de Contenidos
-----------------------------
- :ref:`tareas`
