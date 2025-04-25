Grupos
======

El módulo de **Grupos** es una componente fundamental del Sistema de Gestión de Tareas, diseñado para facilitar la organización, colaboración y gestión eficiente de equipos dentro del ámbito judicial o administrativo.

Permite la creación y administración de estructuras jerárquicas de grupos, proporcionando una base sólida para la asignación de tareas, control de accesos y coordinación entre unidades o equipos de trabajo.

Grupo Base: corresponde a un organismo dentro de la institución, y contendrá los grupos que representan las diferentes áreas de trabajo.

.. contents::
   :local:
   :depth: 2

1. Introducción general
-----------------------

El módulo de Grupos actúa como la **columna vertebral organizativa** del sistema. Permite representar la complejidad de las estructuras judiciales con precisión, mejorar la asignación de recursos, fortalecer la seguridad a través de permisos, y fomentar la colaboración entre unidades mediante herramientas internas.

2. Características principales
------------------------------

- **Creación flexible de grupos**:
  - Estructuras jerárquicas de múltiples niveles (ej. áreas, departamentos, roles).
  - Plantillas preconfiguradas para crear grupos según modelos comunes.

- **Gestión de membresía**:
  - Asignación de usuarios a grupos de forma intuitiva y predefinida.

- **Permisos y accesos**:
  - Control granular por grupo o subgrupo.
  - Herencia de permisos con personalización opcional.

- **Asignación de tareas**:
  - A nivel de grupo o individual.
  - Reglas de distribución automática según carga u orden.

- **Comunicación interna**:
  - Notificaciones y mensajes internos segmentados por grupo.

- **Dashboards y visualización**:
  - Paneles dinámicos con métricas, tareas pendientes y estado.

- **Reportes y auditoría**:
  - Informes por grupo.
  - Registro detallado de cambios y acciones realizadas.

- **Integración con otros módulos**:
  - Tareas y Usuarios.

3. Casos de uso frecuentes
--------------------------

- Crear un grupo para una nueva unidad judicial.
- Reorganizar áreas o mover miembros entre grupos.
- Asignar tareas a todo un equipo o a un líder de grupo.
- Auditar actividad de un grupo en un periodo determinado.
- Reactivar un grupo eliminado accidentalmente.
- Suspender o activar grupos según necesidades operativas.

4. Uso del servicio 
-------------------

El sistema cuenta con un conjunto de interfaces que permiten a los administradores gestionar completamente la estructura de grupos a través del servicio. Estas operaciones están integradas con validaciones visuales, formularios dinámicos y protección contra errores lógicos como la eliminación de grupos con hijos o asignaciones inválidas.

Acciones habilitadas desde la interfaz:

- Crear un nuevo grupo.
- Modificar los datos de un grupo existente (nombre, estado, jerarquía).
- Eliminar un grupo (de forma lógica, puede recuperarse).
- Restaurar un grupo eliminado o suspendido.
- Consultar jerarquías y niveles organizativos.
- Buscar grupos por nombre, fechas o estado.
- Consultar los usuarios que pertenecen a un grupo específico.

Flujos funcionales disponibles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Creación de grupos**

- Definición de grupo principal o dependiente.
- Validaciones: longitud mínima, sin símbolos ni números iniciales.
- Selección de grupo padre mediante lo que permite crear grupos y sub-grupos.

**Edición de grupos**

- Modificación de nombre, descripción y usuario asignado por defecto.
- Visualización previa con avatar del grupo.
- Confirmación de cambios antes de guardar.

**Eliminación de grupos**

- Eliminación lógica con validación previa de jerarquía (no debe tener hijos).
- Confirmación visual y feedback inmediato.

**Suspensión y restauración**

- Permite suspender temporalmente o reactivar grupos.
- Restauración de grupos eliminados desde la misma tabla.

**Visualización de detalles**

- Datos clave del grupo: nombre, descripción, fecha, usuarios asignados.
- Avatar representativo y estructura jerárquica visual.

**Filtros y búsqueda avanzada**

- Filtros por nombre, descripción, estado, fechas.
- `Switch` para incluir o excluir suspendidos y eliminados.
- Aplicación en tiempo real sobre la tabla.

**Tabla de gestión**

- Vista general de grupos con acciones rápidas.
- Íconos para ver, editar, suspender, eliminar o restaurar.
- Integración con paneles laterales y diálogos contextuales.

**Mensajes del sistema**

- `Snackbars` informan al usuario de forma inmediata.
- Errores y validaciones claras, como:
  - "El grupo tiene hijos asociados."
  - "El nombre debe tener al menos 6 caracteres."
  - "Error al intentar restaurar el grupo."

Beneficios para el usuario funcional
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Previene errores comunes gracias a validaciones automatizadas.
- Facilita la gestión de estructuras complejas en pocos clics.
- Centraliza todas las acciones del módulo en una única vista operativa.
- Mejora la trazabilidad, seguridad y productividad del sistema judicial.

---