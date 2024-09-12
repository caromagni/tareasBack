API de Tareas
==============

Esta sección proporciona información detallada sobre los endpoints de API relacionados con tareas en el sistema back-end de Tareas.

Autenticación
-------------

Todas las solicitudes de API requieren autenticación usando JWT (JSON Web Tokens).

URL Base: ``https://api.tareas.com/v1``

Endpoints
---------

Tipo de Tarea
^^^^^^^^^^^^^

.. http:get:: /tipo_tarea

   Recupera una lista de tipos de tareas.

   **Ejemplo de solicitud**:

   .. sourcecode:: http

      GET /tipo_tarea HTTP/1.1
      Host: api.tareas.com
      Authorization: Bearer <su_token_aqui>

   **Parámetros de consulta**:

   * ``page`` (opcional): Número de página para la paginación.
   * ``per_page`` (opcional): Número de elementos por página.

   **Ejemplo de respuesta**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "count": 10,
        "data": [
          {
            "id": 1,
            "nombre": "Desarrollo",
            "descripcion": "Tareas de desarrollo de software"
          },
          {
            "id": 2,
            "nombre": "Diseño",
            "descripcion": "Tareas de diseño gráfico"
          }
        ]
      }

.. http:post:: /tipo_tarea

   Crea un nuevo tipo de tarea.

   **Ejemplo de solicitud**:

   .. sourcecode:: http

      POST /tipo_tarea HTTP/1.1
      Host: api.tareas.com
      Authorization: Bearer <su_token_aqui>
      Content-Type: application/json

      {
        "nombre": "Testing",
        "descripcion": "Tareas de pruebas de software"
      }

   **Ejemplo de respuesta**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 3,
        "nombre": "Testing",
        "descripcion": "Tareas de pruebas de software"
      }

.. http:delete:: /tipo_tarea/(string:id)

   Elimina un tipo de tarea existente.

   **Ejemplo de solicitud**:

   .. sourcecode:: http

      DELETE /tipo_tarea/3 HTTP/1.1
      Host: api.tareas.com
      Authorization: Bearer <su_token_aqui>

   **Ejemplo de respuesta**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "Msg": "Registro eliminado",
        "Id tipo de tarea": "3",
        "Tipo de tarea": "Testing"
      }

Tareas
^^^^^^

.. http:get:: /tarea

   Recupera una lista de tareas.

   **Ejemplo de solicitud**:

   .. sourcecode:: http

      GET /tarea HTTP/1.1
      Host: api.tareas.com
      Authorization: Bearer <su_token_aqui>

   **Parámetros de consulta**:

   * ``page`` (opcional): Número de página para la paginación.
   * ``per_page`` (opcional): Número de elementos por página.
   * ``titulo`` (opcional): Filtrar por título de tarea.
   * ``id_expediente`` (opcional): Filtrar por ID de expediente.
   * ``id_tipo_tarea`` (opcional): Filtrar por ID de tipo de tarea.
   * ``id_usuario_asignado`` (opcional): Filtrar por ID de usuario asignado.
   * ``id_grupo`` (opcional): Filtrar por ID de grupo.
   * ``fecha_desde`` (opcional): Filtrar por fecha de inicio.
   * ``fecha_hasta`` (opcional): Filtrar por fecha de fin.

   **Ejemplo de respuesta**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "count": 25,
        "data": [
          {
            "id": "1",
            "titulo": "Implementar nueva funcionalidad",
            "descripcion": "Desarrollar la funcionalidad X para el módulo Y",
            "estado": "en_progreso",
            "fecha_creacion": "2023-06-01T10:00:00",
            "fecha_vencimiento": "2023-06-15T18:00:00",
            "id_tipo_tarea": 1,
            "id_usuario_asignado": "user123",
            "id_expediente": "exp456"
          },
          // ... más tareas ...
        ]
      }

.. http:get:: /tarea/(string:id_tarea)

   Recupera los detalles de una tarea específica.

   **Ejemplo de solicitud**:

   .. sourcecode:: http

      GET /tarea/1 HTTP/1.1
      Host: api.tareas.com
      Authorization: Bearer <su_token_aqui>

   **Ejemplo de respuesta**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": "1",
          "titulo": "Implementar nueva funcionalidad",
          "descripcion": "Desarrollar la funcionalidad X para el módulo Y",
          "estado": "en_progreso",
          "fecha_creacion": "2023-06-01T10:00:00",
          "fecha_vencimiento": "2023-06-15T18:00:00",
          "id_tipo_tarea": 1,
          "id_usuario_asignado": "user123",
          "id_expediente": "exp456"
        }
      ]

.. http:post:: /tarea

   Crea una nueva tarea.

   **Ejemplo de solicitud**:

   .. sourcecode:: http

      POST /tarea HTTP/1.1
      Host: api.tareas.com
      Authorization: Bearer <su_token_aqui>
      Content-Type: application/json

      {
        "titulo": "Revisar pull request",
        "descripcion": "Revisar y aprobar el PR #123",
        "estado": "pendiente",
        "fecha_vencimiento": "2023-06-20T18:00:00",
        "id_tipo_tarea": 1,
        "id_usuario_asignado": "user456",
        "id_expediente": "exp789"
      }

   **Ejemplo de respuesta**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": "2",
        "titulo": "Revisar pull request",
        "descripcion": "Revisar y aprobar el PR #123",
        "estado": "pendiente",
        "fecha_creacion": "2023-06-10T09:00:00",
        "fecha_vencimiento": "2023-06-20T18:00:00",
        "id_tipo_tarea": 1,
        "id_usuario_asignado": "user456",
        "id_expediente": "exp789"
      }

.. http:delete:: /tarea/(string:id)

   Elimina una tarea existente.

   **Ejemplo de solicitud**:

   .. sourcecode:: http

      DELETE /tarea/2 HTTP/1.1
      Host: api.tareas.com
      Authorization: Bearer <su_token_aqui>

   **Ejemplo de respuesta**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "Msg": "Registro eliminado",
        "Id tarea": "2"
      }

Usuarios Asignados a Tareas
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. http:get:: /tarea_usr/(string:tarea_id)

   Recupera los usuarios asignados a una tarea específica.

   **Ejemplo de solicitud**:

   .. sourcecode:: http

      GET /tarea_usr/1 HTTP/1.1
      Host: api.tareas.com
      Authorization: Bearer <su_token_aqui>

   **Ejemplo de respuesta**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id_usuario": "user123",
          "nombre": "Juan Pérez",
          "email": "juan@example.com"
        },
        {
          "id_usuario": "user456",
          "nombre": "María García",
          "email": "maria@example.com"
        }
      ]

.. http:post:: /tarea_usr

   Asigna un usuario a una tarea.

   **Ejemplo de solicitud**:

   .. sourcecode:: http

      POST /tarea_usr HTTP/1.1
      Host: api.tareas.com
      Authorization: Bearer <su_token_aqui>
      Content-Type: application/json

      {
        "id_usuario": "user789",
        "id_tarea": "1"
      }

   **Ejemplo de respuesta**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "valido": "true",
        "id_usuario": "user789",
        "id_tarea": "1",
        "Msg": "Tarea asignada"
      }

Para obtener información más detallada sobre otros endpoints y formatos de solicitud/respuesta, consulte la documentación completa de la API.