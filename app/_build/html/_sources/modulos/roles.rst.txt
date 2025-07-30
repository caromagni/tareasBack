Roles y Casos de Uso
====================

Se deberán configurar:

* Usuarios del Sistema
* Roles del Sistema
* Casos de Uso del Sistema 
* Casos de Uso asociados a cada Rol
* Roles asociados al usuario

Descripción:
------------

Un usuario deberá tener por lo menos un rol en el Sistema de Tareas. Si el mismo tiene más de un rol, al acceder al sistema seleccionará con qué rol trabajará. Por ejemplo, puede tener un rol Juez y Operador.

Cada funcionalidad del sistema corresponde a uno o más Casos de Uso.

Cada rol de usuario está asociado a diferentes Casos de Uso, según los permisos que se le quieran configurar a ese rol.

Entonces cada vez que el usuario accede a cualquier funcionalidad del sistema, se realiza un control por usuario y rol constatando que, según el rol con el que ingresa al sistema, tenga acceso a dicha funcionalidad. Por ejemplo: Crear Tarea, Crear Grupo, Consultar Tareas, etc.

Los roles se administran en el sistema P-USHER y son importados al Sistema de Tareas en un primer inicio. En los ingresos siguientes de ese usuario se controla el rol y los casos de uso del usuario en el Sistema de Tareas. Los mismos tienen una fecha de vencimiento para estar siempre alineados con los roles ingresados en P-USHER.

En caso que alguno de los registros de roles-casos de uso se encuentre vencido, se importará nuevamente desde P-USHER y se actualizará el registro del usuario en el Sistema de Tareas.

Roles definidos
---------------

El sistema de tareas define cuatro roles de usuario jerárquicos, cada uno con distintos niveles de permisos según su responsabilidad y el alcance asignado dentro del sistema.

**Superadministrador**
~~~~~~~~~~~~~~~~~~~~~~
- Tiene acceso completo a todo el sistema, sin restricciones.
- Puede gestionar cualquier entidad: tareas, usuarios, grupos, tipos, notas, etiquetas, etc.
- No está limitado por grupo o región.

**Administrador**
~~~~~~~~~~~~~~~~~
- Administrador regional, con acceso total pero limitado a una región específica.
- La región se define a través del **grupo base**, que actúa como raíz del árbol jerárquico de grupos.
- Puede gestionar todo lo que esté dentro del grupo base y sus grupos descendientes.

**Operador**
~~~~~~~~~~~~
- Usuario común del sistema con permisos acotados.
- Puede realizar las siguientes acciones dentro del grupo al que pertenece y sus descendientes:
  - Leer tareas
  - Crear tareas
  - Editar tareas
  - Mover tareas entre grupos
  - Agregar notas a tareas
  - Cambiar estado de tareas

**Lector**
~~~~~~~~~~
- Solo puede visualizar tareas dentro del grupo asignado y su jerarquía descendiente.
- No tiene permisos para modificar ni crear elementos.

Casos de Uso del Sistema
------------------------

A continuación, se listan todos los casos de uso que pueden asignarse a los distintos roles:

.. code-block:: javascript

  export const USE_CASES = {
    VER_GRUPOS: 'consultar-grupo',
    VER_ETIQUETAS: 'consultar-label',
    VER_NOTAS: 'consultar-nota',
    VER_TAREAS: 'consultar-tarea',
    VER_TIPOS_NOTA: 'consultar-tipo-nota',
    VER_TIPOS_TAREA: 'consultar-tipo-tarea',
    VER_USUARIOS: 'consultar-usuario',
    CREAR_GRUPOS: 'crear-grupo',
    CREAR_ETIQUETAS: 'crear-label',
    CREAR_NOTAS: 'crear-nota',
    CREAR_TAREAS: 'crear-tarea',
    CREAR_TIPOS_NOTA: 'crear-tipo-nota',
    CREAR_TIPOS_TAREA: 'crear-tipo-tarea',
    CREAR_USUARIOS: 'crear-usuario',
    MODIFICAR_GRUPOS: 'modificar-grupo',
    MODIFICAR_ETIQUETAS: 'modificar-label',
    MODIFICAR_NOTAS: 'modificar-nota',
    MODIFICAR_TAREAS: 'modificar-tarea',
    MODIFICAR_TIPOS_NOTA: 'modificar-tipo-nota',
    MODIFICAR_TIPOS_TAREA: 'modificar-tipo-tarea',
    MODIFICAR_USUARIOS: 'modificar-usuario'
  };

Asignación de Casos de Uso por Rol
----------------------------------

+-------------------+---------------------------------------------------------+
| Rol               | Casos de uso                                            |
+===================+=========================================================+
| Superadministrador| Todos                                                  |
+-------------------+---------------------------------------------------------+
| Administrador      | Todos, limitados al grupo base y su jerarquía         |
+-------------------+---------------------------------------------------------+
| Operador           | `VER_*`, `CREAR_TAREAS`, `MODIFICAR_TAREAS`,          |
|                    | `CREAR_NOTAS`, `MODIFICAR_NOTAS`, `MODIFICAR_GRUPOS`  |
+-------------------+---------------------------------------------------------+
| Lector             | `VER_TAREAS`, `VER_NOTAS`                             |
+-------------------+---------------------------------------------------------+

Notas adicionales
-----------------

- El acceso a tareas y grupos siempre se limita al grupo asignado y sus descendientes.
- Los permisos deben aplicarse respetando la jerarquía de grupos.

.. [#] Editado por M.D.
