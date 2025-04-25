Referencia de la API
====================

Esta sección proporciona una descripción general de la API para el sistema backend de Tareas. La documentación detallada de la API, que incluye todos los endpoints disponibles, formatos de solicitud y respuesta, y requisitos de autenticación, está disponible a través de nuestra interfaz de Swagger.

Documentación de Swagger
------------------------
La referencia completa de la API es accesible a través de nuestra página de Swagger, donde puedes explorar y probar cada endpoint de manera interactiva. Swagger proporciona información actualizada sobre todos los endpoints, los parámetros requeridos y las estructuras de respuesta.

- **URL de Swagger en entorno de desarrollo:** 
  ``https://dev-backend.tareas.pjm.gob.ar/docs``

- **URL de Swagger en entorno productivo:** 
  ``https://backend.tareas.pjm.gob.ar/docs``

Visita el enlace anterior para acceder a la información detallada de la API y probar los endpoints directamente.

Autenticación
-------------
La API ofrece **dos** métodos de autenticación:

1. **JWT (JSON Web Tokens)**  
   Todas las solicitudes de API pueden requerir autenticación usando JWT.  
   Consulta la documentación de Swagger para obtener detalles sobre la autenticación JWT y ejemplos de solicitudes.

2. **API Keys**  
   El backend también soporta autenticación mediante **API Keys**. Para utilizar este método se deben incluir **dos encabezados** (headers) en cada solicitud:

   - ``x-api-key``  
     Debe contener la clave API provista oportunamente por un administrador del sistema *"pusher"*.
   - ``x-api-system``  
     Debe contener el nombre del servicio que realiza la llamada, también provisto por el administrador de *"pusher"*.

   Es responsabilidad del cliente que consume la API mantener seguras estas credenciales y renovarlas en caso necesario.

