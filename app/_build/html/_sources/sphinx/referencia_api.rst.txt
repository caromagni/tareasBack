Referencia de la API
====================

Esta sección proporciona información detallada sobre los endpoints de API disponibles en el sistema back-end de Tareas.

Autenticación
-------------

Todas las solicitudes de API requieren autenticación usando JWT (JSON Web Tokens).

URL Base: ``https://api.tareas.com/v1``

Endpoints
---------

Tareas
^^^^^^

.. http:get:: /tasks

   Recupera una lista de tareas.

   **Ejemplo de solicitud**:

   .. sourcecode:: http

      GET /tasks HTTP/1.1
      Host: api.tareas.com
      Authorization: Bearer <su_token_aqui>

   **Ejemplo de respuesta**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "tareas": [
          {
            "id": 1,
            "titulo": "Completar documentación del proyecto",
            "descripcion": "Escribir y revisar toda la documentación del proyecto",
            "estado": "en_progreso",
            "fecha_vencimiento": "2023-06-30"
          },
          {
            "id": 2,
            "titulo": "Implementar nueva característica",
            "descripcion": "Desarrollar y probar el nuevo panel de usuario",
            "estado": "no_iniciado",
            "fecha_vencimiento": "2023-07-15"
          }
        ]
      }

.. http:post:: /tasks

   Crea una nueva tarea.

   **Ejemplo de solicitud**:

   .. sourcecode:: http

      POST /tasks HTTP/1.1
      Host: api.tareas.com
      Authorization: Bearer <su_token_aqui>
      Content-Type: application/json

      {
        "titulo": "Revisar cambios de código",
        "descripcion": "Revisar y aprobar solicitudes de extracción para el último sprint",
        "estado": "no_iniciado",
        "fecha_vencimiento": "2023-06-25"
      }

   **Ejemplo de respuesta**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 3,
        "titulo": "Revisar cambios de código",
        "descripcion": "Revisar y aprobar solicitudes de extracción para el último sprint",
        "estado": "no_iniciado",
        "fecha_vencimiento": "2023-06-25"
      }

Para obtener información más detallada sobre otros endpoints y formatos de solicitud/respuesta, consulte la documentación completa de la API.