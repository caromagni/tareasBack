Gestión de Grupos
================

¿Qué es y para qué sirve?
-------------------------

El módulo de **Grupos** es la herramienta que te permite organizar tu institución judicial o administrativa de manera jerárquica. Es como crear un organigrama digital donde puedes:

- Crear áreas de trabajo (grupos)
- Organizar áreas dentro de cada grupo
- Asignar personas a cada grupo
- Gestionar quién hace qué en tu organización

**Grupo Base**: corresponde a un organismo dentro de la institución, y contendrá los grupos que representan las diferentes áreas de trabajo.

Índice de Contenidos
--------------------

.. contents::
   :local:
   :depth: 2

**Navegación Rápida:**

- `Componentes Principales`_ - Tabla principal, crear, editar, eliminar grupos
- `Flujos de Trabajo Típicos`_ - Casos de uso comunes
- `Consideraciones Importantes`_ - Validaciones y comportamiento del sistema
- `Interfaz de Usuario`_ - Elementos visuales y accesibilidad
- `Casos de Uso Comunes`_ - Por tipo de usuario
- `Consejos útiles`_ - Recomendaciones prácticas
- `¿Necesitas ayuda?`_ - Soporte y mensajes del sistema

Componentes Principales
-----------------------

Tabla Principal - ¿Qué ves aquí?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Funcionalidades que tienes disponibles:**

- Ver todos los grupos de tu organización en una tabla organizada
- Navegar la jerarquía con breadcrumbs que muestran la ruta completa
- Filtrar y buscar grupos por nombre y estado
- Acciones rápidas con botones intuitivos:
  - Ver detalles - Información completa del grupo
  - Editar - Modificar datos del grupo
  - Suspender - Desactivar temporalmente
  - Eliminar - Marcar como eliminado
  - Restaurar - Recuperar grupos eliminados
  - Crear nuevo - Agregar nuevo grupo

**Información que se muestra:**

- **Niveles Grupo** - Jerarquía completa con breadcrumbs usando path_name
- **Estado** - Activo (verde), Suspendido (amarillo), Eliminado (rojo)
- **Nivel jerárquico** - Posición en la estructura (0 = raíz, 1 = primer nivel, etc.)
- **Fecha de actualización** - Cuándo se modificó por última vez
- **Usuario que actualizó** - Quién hizo el último cambio
- **Usuario por defecto** - Quién se asigna automáticamente
- **Descripción** - Información adicional del grupo

**Características técnicas que facilitan tu trabajo:**

- Paginación automática (10 grupos por página)
- Búsqueda en tiempo real
- Estados de carga con spinner
- Notificaciones de éxito/error
- Visualización jerárquica con breadcrumbs

Crear Nuevo Grupo - ¿Cómo hacerlo?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**¿Qué puedes hacer aquí?**

- Crear grupo principal (sin padre) o dependiente (con padre)
- Seleccionar grupo padre para crear jerarquías
- Asignar usuario por defecto al grupo
- El sistema valida automáticamente la estructura

**Proceso paso a paso:**

1. **Definir tipo de grupo:**
   - Grupo principal - Si es una nueva área (ej: nueva sede)
   - Grupo dependiente - Si es un departamento dentro de un área existente

2. **Completar información básica:**
   - Nombre del grupo (obligatorio) - Ej: "Departamento Civil"
   - Descripción (opcional) - Ej: "Maneja casos civiles"
   - Grupo padre (si es dependiente) - Elige de qué grupo depende

3. **Configurar usuario por defecto:**
   - Selecciona quién será el responsable por defecto de ese grupo
   - Opcional para grupos dependientes

**Campos del formulario:**

- **Nombre** - Campo obligatorio (mínimo 6 caracteres)
- **Descripción** - Campo opcional para detalles adicionales
- **Grupo padre** - Para crear jerarquías (opcional)
- **Usuario por defecto** - Se asigna automáticamente a nuevas tareas

**Validaciones que se protegen:**

- Nombre obligatorio (mínimo 6 caracteres)
- Sin símbolos especiales al inicio
- Sin números al inicio
- Estructura jerárquica válida
- Usuario asignado por defecto (un grupo puede o no tener un responsable)

Editar Grupo Existente - ¿Qué puedes cambiar?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Funcionalidades disponibles:**

- Modificar nombre y descripción del grupo
- Cambiar usuario asignado por defecto
- Gestionar estado activo/inactivo
- El sistema valida en tiempo real

**Características avanzadas que facilitan tu trabajo:**

- Gestión de usuarios - Asignar/quitar usuarios del grupo
- Validación de cambios - Solo guarda si hay modificaciones reales
- Confirmación visual - Muestra avatar y datos del grupo
- Protección de integridad - Previene cambios que rompan la jerarquía

**Campos que puedes editar:**

- **Nombre** - Se puede modificar
- **Descripción** - Se puede modificar
- **Usuario por defecto** - Se puede cambiar
- **Estado** - Activo/suspendido (no eliminado)

**Proceso de edición:**

1. **Modificar información básica:**
   - Nombre del grupo
   - Descripción
   - Usuario asignado por defecto

2. **Gestionar usuarios:**
   - Agregar usuarios al grupo
   - Quitar usuarios del grupo
   - Ver usuarios actuales

3. **Guardar cambios:**
   - Solo si hay modificaciones reales
   - Confirmación antes de guardar

Eliminar Grupo
^^^^^^^^^^^^^

**Funcionalidades:**

- Validación de jerarquía - No permite eliminar grupos con hijos
- Confirmación visual - Muestra avatar y datos del grupo
- Mensajes informativos - Te explica restricciones y consecuencias

**Restricciones importantes que te protegen:**

- No se puede eliminar si tiene grupos hijos
- No se puede eliminar si tiene tareas asignadas
- Eliminación temporal - Se puede restaurar más tarde

**Proceso de eliminación:**

1. Seleccionar grupo a eliminar
2. El sistema valida automáticamente las restricciones
3. Confirmar acción en diálogo
4. Grupo se marca como eliminado
5. Desaparece de la lista principal (pero se puede restaurar)

Suspender Grupo - ¿Cuándo usar?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Funcionalidades:**

- Suspensión temporal - Desactiva el grupo sin eliminarlo
- Confirmación visual - Muestra información del grupo
- Reversibilidad - Se puede reactivar fácilmente
- Preservación de datos - Mantiene toda la información

**¿Cuándo suspender un grupo?**

- Cuando un departamento está temporalmente cerrado
- Durante reorganizaciones
- Cuando no hay personal disponible
- Para mantenimiento del sistema

**Proceso de suspensión:**

1. Seleccionar grupo a suspender
2. Confirmar acción en diálogo
3. Grupo se marca como suspendido
4. Cambia de color en la tabla (amarillo)
5. Se puede reactivar desde la misma tabla

Reactivar Grupo Suspendido
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Funcionalidades:**

- Reactivación inmediata - Restaura el grupo a estado activo
- Confirmación visual - Muestra datos del grupo
- Notificaciones - Confirma éxito de la operación

**Proceso de reactivación:**

1. Buscar grupo suspendido en la tabla (aparece en amarillo)
2. Click en botón "Reactivar"
3. Confirmar acción
4. Grupo vuelve a estado activo

Restaurar Grupo Eliminado
^^^^^^^^^^^^^^^^^^^^^^^^^

**Funcionalidades:**

- Recuperar grupos eliminados - Restaura grupos marcados como eliminados
- Confirmación visual - Muestra información del grupo
- Notificaciones - Confirma éxito o error de la operación

**Proceso de restauración:**

1. Activar filtro "Ver eliminados"
2. Buscar grupo eliminado
3. Click en botón "Restaurar"
4. Confirmar acción
5. Grupo vuelve a estar activo

Ver Detalles del Grupo - Información completa
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Funcionalidades:**

- Información completa - Nombre, descripción, fechas, usuarios
- Avatar visual - Representación gráfica del grupo
- Jerarquía completa - Muestra la estructura organizacional
- Usuarios asignados - Lista de miembros del grupo

**Información que se muestra:**

- Nombre y descripción del grupo
- Nivel jerárquico - Posición en la estructura organizacional
- Organismo padre - A qué organismo pertenece
- Ruta completa - Path completo en la jerarquía
- Fecha de creación y última actualización
- Usuario que realizó la última actualización
- Usuario asignado por defecto - Quién se asigna automáticamente
- Usuarios asignados al grupo

Filtros de Búsqueda - Encontrar lo que necesitas
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Funcionalidades:**

- Filtro por nombre - Búsqueda textual
- Filtro por descripción - Búsqueda en descripciones
- Filtro por estado - Activos, suspendidos, eliminados
- Búsqueda avanzada - Combinar múltiples criterios
- Limpiar filtros - Resetear búsqueda

**Opciones de filtrado básicas:**

- **Nombre**: Búsqueda parcial por nombre
- **Descripción**: Búsqueda en descripciones
- **Ver suspendidos**: Incluir grupos suspendidos
- **Ver eliminados**: Incluir grupos eliminados
- **Combinaciones**: Nombre + estado + descripción

**Opciones de filtrado avanzadas:**

- **Nivel jerárquico** - Filtrar por nivel específico
- **Organismo** - Filtrar por organismo padre
- **Usuario por defecto** - Buscar por usuario asignado
- **Fecha de creación** - Filtrar por rango de fechas

Mapa de Grupos - Vista de árbol
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**¿Qué es y para qué sirve?**

Es una vista de árbol que te muestra toda la estructura organizacional de tu institución de manera visual.

**Funcionalidades:**

- Visualización gráfica de la estructura organizacional
- Navegación interactiva por niveles
- Acciones directas desde el árbol
- Filtros para mostrar/ocultar elementos

**Características del árbol:**

- **Nodos expandibles** - Mostrar/ocultar subgrupos
- **Colores semánticos** - Verde (activo), Rojo (eliminado), Gris (suspendido)
- **Contador de tareas** - Muestra cuántas tareas tiene cada grupo
- **Acciones rápidas** - Agregar, editar, eliminar desde el árbol

**Información que ves en el árbol:**

- Nivel jerárquico - Posición en la estructura
- Ruta completa - Path completo en tooltips
- Organismo - A qué organismo pertenece
- Usuario por defecto - Quién se asigna automáticamente

**Opciones de visualización:**

- Mostrar eliminados - Switch para incluir grupos eliminados
- Zoom y navegación - Controles para explorar el árbol
- Responsive - Se adapta a diferentes tamaños de pantalla

**Acciones disponibles:**

- Agregar subgrupo - Crear grupo hijo directamente
- Editar grupo - Modificar datos del grupo
- Eliminar grupo - Marcar como eliminado
- Ver detalles - Información completa del grupo

Flujos de Trabajo Típicos
-------------------------

Crear Nueva Estructura Organizacional
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Crear grupo base (organismo principal)
2. Agregar áreas principales como grupos hijos
3. Crear sub grupos dentro de cada área
4. Asignar usuarios a cada grupo según responsabilidades
5. Configurar usuarios por defecto para asignación automática

Reorganizar Estructura Existente
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Analizar jerarquía actual usando el mapa de grupos
2. Crear nuevos grupos donde sea necesario
3. Mover grupos entre padres (si está permitido)
4. Reasignar usuarios según nueva estructura
5. Validar integridad de la jerarquía

Gestionar Estados de Grupos
^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Suspender grupos temporalmente cuando no están operativos
2. Reactivar grupos cuando vuelven a funcionar
3. Eliminar grupos obsoletos (con validaciones)
4. Restaurar grupos eliminados accidentalmente

Asignar Tareas a Grupos
^^^^^^^^^^^^^^^^^^^^^^^

1. Seleccionar grupo apropiado para la tarea
2. Verificar usuarios disponibles en el grupo
3. Asignar tarea al grupo completo o usuario específico
4. Monitorear distribución de carga de trabajo

Consideraciones Importantes
--------------------------

Validaciones de Seguridad que te protegen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Jerarquía coherente** - No se pueden crear ciclos en la estructura
- **Integridad de datos** - No se pueden eliminar grupos con dependencias
- **Permisos de usuario** - Solo usuarios autorizados pueden modificar grupos
- **Auditoría completa** - Se registra quién y cuándo realizó cambios

**Validaciones adicionales:**

- Nivel máximo - No se pueden crear grupos más allá de cierto nivel
- Organismo único - Cada grupo pertenece a un solo organismo
- Usuario por defecto válido - Debe ser un usuario activo del sistema

Comportamiento del Sistema que facilita tu trabajo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Eliminación lógica** - Los grupos no se borran físicamente
- **Cascada de estados** - Al suspender un grupo, se pueden afectar subgrupos
- **Herencia de permisos** - Los subgrupos pueden heredar permisos del padre
- **Protección de datos** - No se pueden eliminar grupos con tareas activas

**Comportamiento adicional:**

- Cálculo automático de level - Se actualiza al cambiar la jerarquía
- Herencia de organismo - Los subgrupos heredan el organismo del padre
- Validación de usuario por defecto - Debe pertenecer al grupo o ser administrador

Rendimiento optimizado para tu comodidad
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Paginación inteligente** - 10 grupos por página por defecto
- **Búsqueda optimizada** - Filtros en tiempo real
- **Carga diferida** - El árbol se expande bajo demanda
- **Cache jerárquico** - Estructura organizacional en memoria

Interfaz de Usuario
-------------------

Elementos Visuales que facilitan la navegación
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Avatares** - Representación gráfica de cada grupo
- **Breadcrumbs** - Navegación jerárquica clara
- **Chips de estado** - Indicadores visuales de estado
- **Colores semánticos** - Verde (activo), Amarillo (suspendido), Rojo (eliminado)
- **Iconos intuitivos** - Acciones claramente identificadas

Accesibilidad para todos los usuarios
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Navegación por teclado** - Todas las acciones accesibles
- **Contraste adecuado** - Cumple estándares WCAG
- **Textos descriptivos** - Labels claros y comprensibles
- **Tooltips informativos** - Ayuda contextual en hover

Casos de Uso Comunes
--------------------

Administrador del Sistema
^^^^^^^^^^^^^^^^^^^^^^^^

- Crear estructura organizacional completa
- Gestionar jerarquías de grupos y subgrupos
- Asignar usuarios a grupos apropiados
- Monitorear estados de grupos y usuarios
- Auditar cambios en la estructura organizacional

Líder de Equipo
^^^^^^^^^^^^^^

- Ver estructura de su área de responsabilidad
- Gestionar subgrupos bajo su control
- Asignar usuarios a grupos específicos
- Monitorear carga de trabajo por grupo

Usuario Final
^^^^^^^^^^^^

- Ver grupos disponibles para asignación de tareas
- Entender jerarquía organizacional
- Identificar grupos activos vs suspendidos
- Comprender estructura de responsabilidades

Gestión de Grupos en distintas situaciones
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Suspender grupos temporalmente durante reorganizaciones
- Reactivar grupos cuando se resuelven problemas
- Restaurar estructura después de cambios accidentales
- Auditar impactos de cambios en la organización

Consejos útiles para el usuario
------------------------------

**Antes de eliminar un grupo:**

- Verifica que no tenga subgrupos
- Verifica que no tenga tareas asignadas
- Considera suspender en lugar de eliminar

**Al crear grupos:**

- Usa nombres descriptivos - "Departamento Civil" en lugar de "DC"
- Agrega descripciones para que otros entiendan su función
- Asigna responsables para que las tareas se asignen automáticamente

**Al buscar grupos:**

- Usa filtros específicos para encontrar lo que necesitas
- Combina filtros para búsquedas más precisas
- Limpia los filtros cuando termines

¿Necesitas ayuda?
^^^^^^^^^^^^^^^^^

- Los mensajes de error te explican qué está mal
- Las validaciones te previenen de cometer errores
- Los tooltips te dan información adicional
- Los colores te indican el estado de cada grupo

Esta documentación proporciona una guía completa para entender y utilizar el módulo de Grupos de manera efectiva, combinando información técnica con orientación práctica para el usuario.