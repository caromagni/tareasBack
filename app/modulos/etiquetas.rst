.. _etiquetas:

=======================
Lógica de las Etiquetas
=======================

Este documento describe la lógica de creación, visibilidad y eliminación de las etiquetas en el contexto de grupos base y tareas.

-----------------------------
1. Creación y Nivel de Almacenamiento
-----------------------------
- **Creación**: Una etiqueta se crea a partir de una tarea.
- **Nivel de Almacenamiento**:  
  Las etiquetas se guardan a nivel de *grupo base*. Esto significa que cualquier grupo (y usuario) que pertenezca a ese mismo grupo base puede ver y utilizar la etiqueta.

-----------------------------
2. Visibilidad en el Filtro de Etiquetas
-----------------------------
- **Filtro por Grupo Base**:  
  En el filtro de etiquetas, cada usuario solo podrá ver aquellas etiquetas correspondientes a los grupos base a los cuales pertenece el grupo del usuario logueado.

-----------------------------
3. Eliminación de Etiquetas
-----------------------------
- **Condición de Eliminación**:  
  Una etiqueta puede eliminarse únicamente si **no** está asociada a ninguna tarea.  
  En términos de estado, esto implica que la etiqueta debe tener su campo de “activa” en falso en todos sus registros, es decir, no debe estar vigente en ninguna tarea.

-----------------------------
4. Visibilidad de Etiquetas en las Tareas
-----------------------------
- **Asignación Original**:  
  Las etiquetas de las tareas solo se muestran dentro del grupo base en el cual fueron originalmente asignadas.
- **Reasignación de Tarea**:  
  Si la tarea se reasigna a un grupo que no pertenece al grupo base original, las etiquetas dejan de ser visibles para el nuevo grupo.

-----------------------------
Índice de Contenidos
-----------------------------
- :ref:`etiquetas`
