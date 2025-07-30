Tipos y Subtipos de Tarea
=========================

Descripción General
------------------

El módulo de **Tipos de Tarea** permite administrar las categorías de tipos de tareas que se pueden crear en el sistema o venir de sistemas externos como el Sistema Expediente. Cada tipo de tarea puede tener subtipos asociados para mayor especificidad.

Índice de Contenidos
--------------------

.. contents::
   :local:
   :depth: 2

**Navegación Rápida:**

1. `Componentes Principales`_ - Tabla principal, crear, editar tipos
2. `Flujos de Trabajo Típicos`_ - Casos de uso comunes
3. `Consideraciones Importantes`_ - Validaciones y comportamiento del sistema
4. `Interfaz de Usuario`_ - Elementos visuales y accesibilidad
5. `Casos de Uso Comunes`_ - Por tipo de usuario
6. `Gestión de Tipos Externos`_ - Manejo de tipos importados

1. Componentes Principales
--------------------------

1.1. Tabla Principal
^^^^^^^^^^^^^^^^^^^^

**Funcionalidades:**

- Visualizar todos los tipos de tarea existentes
- Filtrar por nombre y estado (activo/inactivo)
- Acciones rápidas con botones de acción:
  - Ver detalles - Información completa del tipo
  - Editar - Modificar datos del tipo
  - Restaurar - Recuperar tipos eliminados
  - Crear nuevo - Agregar nuevo tipo
  - Puede agregarse o no un subtipo

**Información mostrada en la tabla:**

- **Nombre del tipo** - Ej: "Acta", "Auto", "Escrito"
- **Origen** - Externo o Interno (indica si el tipo proviene de sistemas externos)
- **Estado** - Activo (verde) o Inactivo (gris)
- **Cantidad de subtipos** - Cuántos subtipos tiene asociados
- **Fecha de actualización** - Cuándo se modificó por última vez
- **Usuario que actualizó** - Quién hizo el último cambio

**Características técnicas:**

- Paginación automática
- Búsqueda en tiempo real
- Estados de carga con spinner
- Notificaciones de éxito/error

1.2. Crear Nuevo Tipo
^^^^^^^^^^^^^^^^^^^^^

**Funcionalidades:**

- Crear desde cero - Nuevo tipo con nombre personalizado
- Copiar existente - Duplicar tipo existente con sus subtipos
- Gestión de subtipos - Agregar/quitar subtipos asociados a tarea existente
- Validaciones - Nombre obligatorio, sin caracteres especiales

**Proceso de creación:**

1. **Seleccionar modo**: "Nuevo" o "Copiar existente"
2. **Ingresar nombre del tipo** (mínimo 4 caracteres)
3. **Si es copia**: seleccionar tipo base
4. **Agregar subtipos opcionales**
5. **Confirmar creación**

**Validaciones:**

- Nombre obligatorio
- Sin espacios al inicio
- Sin números al inicio
- Sin caracteres especiales
- Mínimo 4 caracteres

1.3. Editar Tipo Existente
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Funcionalidades:**

- Modificar nombre del tipo de tarea
- Cambiar estado (activo/inactivo)
- Gestionar subtipos - Agregar, editar, eliminar subtipos
- Validaciones en tiempo real
- Detección de cambios - Solo guarda si hay modificaciones

**Restricciones por origen:**

- **Tipos de origen externo** - No se pueden editar (nombre, estado, subtipos)
- **Tipos de origen interno** - Completamente editables
- **Subtipos de origen externo** - No se pueden modificar individualmente

**Características avanzadas:**

- Gestión individual de subtipos - Cada subtipo se puede editar/eliminar por separado mientras no sean de origen externo
- Estados de subtipos - Activar/desactivar subtipos específicos
- Validación inteligente - Detecta cambios reales antes de permitir guardar
- Confirmación de cambios - Previene guardados accidentales

**Proceso de edición:**

1. **Modificar nombre** (solo si es origen interno)
2. **Cambiar estado activo/inactivo** (solo si es origen interno)
3. **Editar subtipos existentes** (solo subtipos de origen interno)
4. **Agregar nuevos subtipos**
5. **Eliminar subtipos no deseados** (solo subtipos de origen interno)
6. **Guardar cambios**

**Indicadores visuales:**

- "ACTIVO (Origen externo)" - Tipo externo que no se puede desactivar
- "Origen externo. No editable." - Subtipo externo que no se puede modificar
- Campos deshabilitados - Para tipos y subtipos de origen externo

1.4. Ver Detalles
^^^^^^^^^^^^^^^^

**Funcionalidades:**

- Información completa - Nombre, fechas, usuario que actualizó
- Subtipos asociados - Lista de subtipos con estado
- Avatar visual - Representación gráfica del tipo
- Formato de fechas - Fechas legibles para el usuario

**Información mostrada:**

- Nombre del tipo
- Fecha de última actualización
- Usuario que realizó la actualización
- Lista de subtipos asociados
- Estado de cada subtipo (base/normal)
- Información de origen (interno/externo)

1.5. Filtros de Búsqueda
^^^^^^^^^^^^^^^^^^^^^^^

**Funcionalidades:**

- Filtro por nombre - Búsqueda textual
- Filtro por estado - Activos/inactivos
- Filtro por origen - Internos/externos
- Búsqueda avanzada - Combinar múltiples criterios
- Limpiar filtros - Resetear búsqueda

**Opciones de filtrado:**

- **Nombre**: Búsqueda parcial por nombre
- **Ver inactivos**: Mostrar tipos desactivados
- **Origen**: Filtrar por interno/externo
- **Combinaciones**: Nombre + estado + origen

2. Flujos de Trabajo Típicos
------------------------------

2.1. Crear Nuevo Tipo de Tarea
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Abrir tabla de tipos
2. Click en botón "Crear"
3. Elegir modo: "Nuevo" o "Copiar existente"
4. Completar formulario
5. Agregar subtipos (opcional)
6. Confirmar creación

2.2. Editar Tipo Existente
^^^^^^^^^^^^^^^^^^^^^^^^^^

1. En la tabla, click en "Editar"
2. Verificar origen del tipo (externo/interno)
3. Modificar campos permitidos según origen
4. Gestionar subtipos (respetando restricciones de origen)
5. Guardar cambios

2.3. Restaurar Tipo Inactivo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Activar filtro "Ver inactivos"
2. Buscar tipo eliminado
3. Click en "Restaurar"
4. Confirmar restauración

3. Consideraciones Importantes
------------------------------

3.1. Origen de los Tipos
^^^^^^^^^^^^^^^^^^^^^^^^^

- **Origen Interno** - Tipos creados dentro del sistema, completamente editables
- **Origen Externo** - Tipos importados de sistemas externos, no editables
- **Indicadores visuales** - La tabla muestra claramente el origen de cada tipo
- **Restricciones automáticas** - Los tipos externos no se pueden modificar

3.2. Validaciones de Seguridad
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Nombres únicos** - No se permiten duplicados
- **Caracteres especiales** - Solo letras, números y espacios
- **Longitud mínima** - 4 caracteres mínimo
- **Estados coherentes** - Subtipos activos solo en tipos activos
- **Protección de origen** - Tipos externos no se pueden modificar

3.3. Comportamiento del Sistema
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Eliminación lógica** - Los tipos no se borran físicamente
- **Cascada de estados** - Al desactivar tipo, subtipos se desactivan
- **Auditoría** - Se registra quién y cuándo realizó cambios
- **Integridad** - No se pueden eliminar tipos con tareas asociadas
- **Respeto al origen** - Los tipos externos mantienen su integridad

3.4. Rendimiento
^^^^^^^^^^^^^^^

- **Paginación** - 10 elementos por página por defecto
- **Búsqueda optimizada** - Filtros en tiempo real
- **Carga diferida** - Subtipos se cargan bajo demanda
- **Cache inteligente** - Datos recientes se mantienen en memoria

4. Interfaz de Usuario
-----------------------

4.1. Elementos Visuales
^^^^^^^^^^^^^^^^^^^^^^^

- **Avatares** - Representación gráfica de cada tipo
- **Chips de estado** - Indicadores visuales de estado
- **Iconos intuitivos** - Acciones claramente identificadas
- **Colores semánticos** - Verde (activo), Rojo (eliminado), Gris (inactivo)
- **Indicadores de origen** - Externo/Interno claramente marcados

4.2. Responsividad
^^^^^^^^^^^^^^^^^

- **Móvil** - Filtros en drawer lateral
- **Desktop** - Filtros en sidebar fijo
- **Tablet** - Adaptación automática de layout

4.3. Accesibilidad
^^^^^^^^^^^^^^^^^^

- **Navegación por teclado** - Todas las acciones accesibles
- **Contraste adecuado** - Cumple estándares WCAG
- **Textos descriptivos** - Labels claros y comprensibles

5. Casos de Uso Comunes
------------------------

5.1. Administrador del Sistema
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Crear tipos base para la organización
- Configurar subtipos específicos por área
- Mantener tipos actualizados y organizados
- Gestionar estados activo/inactivo
- Diferenciar entre tipos internos y externos

5.2. Usuario Final
^^^^^^^^^^^^^^^^^

- Ver tipos disponibles para crear tareas
- Entender la estructura de subtipos
- Identificar tipos activos vs inactivos
- Comprender la jerarquía de categorías
- Reconocer tipos que no se pueden modificar

6. Gestión de Tipos Externos
------------------------------

6.1. Visualización
^^^^^^^^^^^^^^^^^

- Los tipos externos se muestran claramente
- Indicadores visuales de origen externo
- Diferenciación en la tabla principal

6.2. Protección
^^^^^^^^^^^^^^

- No se pueden modificar ni eliminar
- Campos deshabilitados automáticamente
- Validaciones que previenen cambios

6.3. Integración
^^^^^^^^^^^^^^^

- Se pueden usar para crear tareas normalmente
- Mantienen funcionalidad completa
- Compatibilidad con flujos de trabajo

6.4. Auditoría
^^^^^^^^^^^^^

- Se mantiene registro de su origen
- Trazabilidad completa de cambios
- Historial de integraciones

Esta documentación proporciona una guía completa para entender y utilizar el módulo de Tipos y Subtipos de Tarea de manera efectiva, combinando información técnica con orientación práctica para el usuario.