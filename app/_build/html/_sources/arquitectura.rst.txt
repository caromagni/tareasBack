Arquitectura
============

Visión General del Sistema
--------------------------

El sistema back-end de Tareas está construido utilizando una arquitectura de microservicios, lo que permite escalabilidad y modularidad.

.. image:: https://example.com/path/to/architecture_diagram.png
   :alt: Diagrama de Arquitectura del Back-end de Tareas
   :width: 600px

Componentes Clave
-----------------

1. Puerta de Enlace API
   Maneja las solicitudes entrantes y las dirige a los servicios apropiados.

2. Servicio de Autenticación
   Gestiona la autenticación de usuarios y la generación de tokens.

3. Servicio de Tareas
   Responsable de las operaciones CRUD en tareas y datos relacionados con tareas.

4. Servicio de Usuarios
   Gestiona los perfiles de usuario y los permisos.

5. Base de Datos
   Almacena todos los datos persistentes de la aplicación.

Flujo de Comunicación
---------------------

1. El cliente envía una solicitud a la Puerta de Enlace API.
2. La Puerta de Enlace API autentica la solicitud con el Servicio de Autenticación.
3. Si está autenticada, la solicitud se reenvía al servicio apropiado.
4. El servicio procesa la solicitud, interactuando con la base de datos si es necesario.
5. La respuesta se envía de vuelta a través de la Puerta de Enlace API al cliente.

Esta arquitectura asegura una separación de responsabilidades y permite el escalado independiente de diferentes componentes según sea necesario.