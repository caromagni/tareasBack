import uuid
from datetime import datetime
import common.utils as utils
import common.logger_config as logger_config
from models.grupo_hierarchy import find_parent_id_recursive
from db.alchemy_db import db
from .alch_model import Label, LabelXTarea, Tarea
import common.cache as cache_common
########################## LABELS #############################################
# def buscar_grupo_padre_recursivo(id):
#     
#     padre = session.query(Grupo.id,
#                   Grupo.eliminado,          
#                   HerarquiaGrupoGrupo.id_padre,
#                   HerarquiaGrupoGrupo.id_hijo
#                   ).join(HerarquiaGrupoGrupo, Grupo.id == HerarquiaGrupoGrupo.id_hijo

#                   ).filter(HerarquiaGrupoGrupo.id_padre).all() 
#     print('padre:', padre)
    
#     if not padre:
#         return id
#     else:
#         return buscar_grupo_padre_recursivo(padre.id)

# Creación de nueva etiqueta (se crea asociada a una tarea y un grupo base específico)
def insert_label(username=None, nombre='', color= '', eliminado=False, fecha_eliminacion=None, id_user_creacion=None, id_grupo=None, id_tarea=None):
    
    ids_labels=[]
    
    if username is not None:
        id_user_actualizacion = utils.get_username_id(username)

    if id_user_actualizacion is not None:
            utils.verifica_usr_id(id_user_actualizacion)
    else:
            raise Exception("Usuario no ingresado")  
    
    nuevoID_label=uuid.uuid4()
    id_tarea = id_tarea
    # tarea = get_tarea_by_id(id_tarea)
    # id_grupo = tarea[0]['grupos'][0]['id']
    id_grupo = id_grupo
    # print('grupo:', tarea[0]['grupos'][0]['id'], 'usuario ingresante:', id_user_creacion)
    print('db.session:', db.session)
    id_grupo_base=find_parent_id_recursive(db.session, id_grupo)

    print('id_grupo_padre:', id_grupo_base)

    nueva_label = Label(
        eliminado=eliminado,
        fecha_eliminacion=fecha_eliminacion,
        fecha_creacion=datetime.now(),
        id_user_creacion=id_user_creacion,
        id_label=nuevoID_label,
        color=color,
        id_grupo_base=id_grupo_base,
        nombre=nombre,
    )

    db.session.add(nueva_label)

    print('ids_labels:', ids_labels)
    print('nuevoID_label:', nuevoID_label)

    ids_labels.append(str(nuevoID_label) )
    print('ids_labels:', ids_labels)

    result = insert_label_tarea(ids_labels=ids_labels, id_tarea=id_tarea, username=username)
    print('result Insert Label:', result)
       
    db.session.commit()

    return result


def update_label(id='', **kwargs):
    
    label = db.session.query(LabelXTarea).filter(Label.id == id, Label.eliminado==False).first()
   
    if label is None:
        return None
    
    if 'eliminado' in kwargs:
        label.eliminado = kwargs['eliminado']
    if 'id_tarea' in kwargs:
        label.id_tarea = kwargs['id_tarea']           
    if 'label' in kwargs:
        label.nombre = kwargs['nombre']
  
        
    label.fecha_actualizacion = datetime.now()
    

    ###################Formatear el resultado####################
    result = {
        "id": label.id,
        "titulo": label.titulo,
        "id_tipo_label": label.id_tipo_label,
        "tipo_label": label.tipo_label,
        "id_tarea": label.id_expediente,
        "label": label.label,
        "eliminado": label.eliminado,
        "fecha_eliminacion": label.fecha_eliminacion,
        "fecha_actualizacion": label.fecha_actualizacion,
        "fecha_creacion": label.fecha_creacion,
        
    }

    db.session.commit()
    return result

# Consulta de etiquetas por parámetros
def get_all_label(username=None, page=1, per_page=30, nombre='', id_grupo_base=None, id_tarea=None, id_user_creacion=None, fecha_desde='01/01/2000', fecha_hasta=datetime.now(), eliminado=None, label_color=''):
       
    """ if username is not None:
        id_user_actualizacion = get_username_id(username)

    if id_user_actualizacion is not None:
            verifica_usr_id(id_user_actualizacion)
    else:
            raise Exception("Usuario no ingresado")
    """

    query = db.session.query(Label).filter(Label.fecha_creacion.between(fecha_desde, fecha_hasta)).order_by(Label.fecha_creacion.desc())
    if nombre != '':
        query = query.filter(Label.nombre.ilike(f'%{nombre}%'))

    if id_grupo_base is not None:
        query = query.filter(Label.id_grupo_base== id_grupo_base)

    if id_tarea is not None:
        query = query.filter(Label.id_tarea== id_tarea)

    if id_user_creacion is not None:
        query = query.filter(Label.id_user_creacion == id_user_creacion)

    if eliminado is not None:
        query = query.filter(Label.eliminado == eliminado)

    #muestra datos
    total= len(query.all()) 
    result = query.order_by(Label.fecha_creacion).offset((page-1)*per_page).limit(per_page).all()

    
    return result, total

def get_label_by_id(id):
    
    res = db.session.query(Label).filter(Label.id_label == id).first()

    if res is not None:
        return res 
    else:
        print("Label no encontrada")
        return None

def delete_label(username=None, id_label=None):    

    if username is not None:
        id_user_actualizacion = utils.get_username_id(username)

    if id_user_actualizacion is not None:
            utils.verifica_usr_id(id_user_actualizacion)
    else:
            raise Exception("Usuario no ingresado")
    
    label = db.session.query(Label).filter(Label.id_label == id_label, Label.eliminado==False).first()
    print('label id a borrar:', label.id_label)
    if label is not None:
        if(label.id_user_creacion != id_user_actualizacion):
            return "Usuario no autorizado para eliminar la etiqueta" 
        else: 
            labelTarea = db.session.query(LabelXTarea).filter(LabelXTarea.id_label == id_label, LabelXTarea.activa == True).all()  
            print('labelTarea:', labelTarea)     
            if labelTarea is None:
                result = { "status": "error", "message": "La etiqueta está asociada a una tarea activa"}
                return result
            else:
                
                label.eliminado=True
                label.fecha_eliminacion=datetime.now()
                label.fecha_actualizacion = datetime.now()

                db.session.commit()
                result = {
                    "status": "success",
                    "message": "Etiqueta eliminada correctamente",
                    "id_label": label.id_label,
                    "eliminado": label.eliminado,
                    "fecha_eliminacion": label.fecha_eliminacion,
                    "fecha_actualizacion": label.fecha_actualizacion,
                    "nombre": label.nombre,
                }
                return result        
    else:
        print("Label no encontrada")
        return None

############################## LABELS x GRUPO BASE ########################################
### Busca las etiquetas activas según el grupo base disponibles para todo el árbol de dicho grupo ####
@cache_common.cache.memoize(cache_common.CACHE_TIMEOUT_LONG)
def get_active_labels(ids_grupos_base):
    print('entra a get de labels por grupo base aaaahhhhhhhhhhkfhaksfhkasdfhñasdfh')
    print('ids_grupos_base:', ids_grupos_base)
    # id_grupo_base = find_parent_id_recursive(db, id_grupo)
    # print('*********************************************id_grupo_base:', id_grupo_base)
    print("##"*50)
    ids_list = ids_grupos_base.split(',')
    # ids_list = [ids_grupos_base]
    print('ids_list:', ids_list)
    labels_group_array = []
    total = 0
    for id in ids_list:
        print('id_grupos_base:', id)
        print("#"*50)
        labels_group = db.session.query(Label).filter(Label.id_grupo_base == id, Label.eliminado == False).all()
        print('labels group por id:', labels_group)
        if labels_group is not None:
            print('labels:', labels_group)
            labels_group_array.append(labels_group)
            total = total + len(labels_group)
        
            # total = len(labels_group)
        #     print('saliendo del get_active_labels')   
        # else:
        #     return 'No hay labels para este grupo'
    return labels_group_array, total
    

############################## LABELS x TAREA ########################################
def insert_label_tarea(username=None, **kwargs):
    if username is not None:
        id_user_actualizacion = utils.get_username_id(username)

    if id_user_actualizacion is not None:
        utils.verifica_usr_id(id_user_actualizacion)
    else:
        raise Exception("Usuario no ingresado") 
    
    id_tarea = kwargs['id_tarea']
    ids_labels = kwargs['ids_labels']
    
    labelsTarea = db.session.query(LabelXTarea).filter(LabelXTarea.id_tarea == id_tarea).all()
   
    active_labels = []

    # Convertir listas de etiquetas activas e inactivas a conjuntos de IDs para facilitar la comparación
    set_labelsTarea = {str(label.id_label) for label in labelsTarea}
    if len(ids_labels) >= 0:
        set_ids_labels = set(ids_labels)
        nuevos_labels = set_ids_labels - set_labelsTarea  # Todos los labelsXtareas solicitados por el front que no están activos
        viejos_labels = set_ids_labels & set_labelsTarea 
        
        fecha_actualizacion = datetime.now()

        print('set_labelsTarea:', set_labelsTarea)
        print('set_ids_labels:', set_ids_labels)
        print('nuevos_labels:', nuevos_labels)
        print('viejos_labels:', viejos_labels)
        
        if len(viejos_labels) > 0:       
            print('entra a actualizar labels, si no estan en viejos se desactivan')
            # Actualizar etiquetas existentes
            for label in labelsTarea:
                if str(label.id_label) not in viejos_labels:
                    label.activa = False
                    label.fecha_actualizacion = fecha_actualizacion
                    label.id_user_actualizacion = id_user_actualizacion
                    db.session.commit()
                    print('Desactivando label:', label.id_label, label.activa)
                else:
                    # Si la etiqueta ya existe y está activa, actualizar su fecha de actualización
                    print('Label ya existe:', label.id_label)
                    label.activa = True
                    label.fecha_actualizacion = fecha_actualizacion
                    label.id_user_actualizacion = id_user_actualizacion
                    db.session.commit()
                    print('Actualizando label:', label.id_label, label.activa)
                    active_labels.append(label)
     
        if len(nuevos_labels) > 0:
            for id_label in nuevos_labels:
                print('nuevos_labels id_label:', id_label)
                nuevoID_label_tarea = uuid.uuid4()

                nueva_label = LabelXTarea(
                    id=nuevoID_label_tarea,
                    id_label=id_label,
                    id_tarea=id_tarea,
                    activa=True,
                    fecha_actualizacion=fecha_actualizacion,
                    id_user_actualizacion = id_user_actualizacion
                )
                active_labels.append(nueva_label)
                db.session.add(nueva_label)
                db.session.commit()
        
        if(len(set_ids_labels) == 0):
            for label in labelsTarea:
                label.activa = False
                label.fecha_actualizacion = fecha_actualizacion
                label.id_user_actualizacion = id_user_actualizacion
                db.session.commit()
                print('Desactivando label:', label.id_label, label.activa)
    print("#############################################")
    # Formatear el resultado
    result = []
    for l in active_labels:
        labels = db.session.query(Label).filter(Label.id_label == l.id_label).first()
        nombre= labels.nombre
        color= labels.color
        result.append({
            "id": l.id,
            "id_label": l.id_label,
            "id_tarea": l.id_tarea,
            "activa": l.activa,
            "nombre": nombre,
            "color": color,
            "fecha_actualizacion": l.fecha_actualizacion,
            "id_user_actualizacion": l.id_user_actualizacion
        })
    print('result:', result)
    print("#############################################")  
    return result
    

def update_label_tarea(id_label='', id_tarea="", **kwargs):
    
    label_tarea = db.session.query(LabelXTarea).filter(Label.id == id_label, Tarea.id == id_tarea).first()
   
    if label_tarea is None:
        return None
    
    if 'activa' in kwargs:
        label_tarea.activa = kwargs['activa']
        
    label_tarea.fecha_actualizacion = datetime.now()

    ###################Formatear el resultado####################
    
    result = {
        "id": label_tarea.id,
        "activa": label_tarea.activa,
        "id_tarea": label_tarea.id_tarea,
        "id_label": label_tarea.id_label,
        "fecha_actualizacion": label_tarea.fecha_actualizacion,        
    }

    db.session.commit()
    return result

def get_label_by_tarea(id_tarea):
    print('Fetching labels for task ID:', id_tarea)
    active_labels = []

    # Query active labels for the given task
    tasks_labels = db.session.query(LabelXTarea).filter(
        LabelXTarea.id_tarea == id_tarea,
        LabelXTarea.activa == True
    ).all()

    if tasks_labels:
        for row in tasks_labels:
            active_label = db.session.query(
                LabelXTarea.id,
                LabelXTarea.id_label,
                LabelXTarea.id_tarea,
                Label.nombre,
                Label.color
            ).join(
                Label, Label.id_label == LabelXTarea.id_label
            ).filter(
                LabelXTarea.id_tarea == row.id_tarea,
                Label.id_label == row.id_label,
                Label.eliminado == False
            ).first()  

            if active_label:
                label = {
                    "id": active_label.id,
                    "id_label": active_label.id_label,
                    "id_tarea": active_label.id_tarea,
                    "nombre": active_label.nombre,
                    "color": active_label.color
                }
                active_labels.append(label)

    total = len(active_labels)
    print('Total active labels:', total)
    return active_labels, total

def delete_label_tarea_model(username=None, id=None):
    if not username:
        raise Exception("Usuario no ingresado")

    # Verify the username and get the user ID
    id_user_actualizacion = utils.get_username_id(username)
    if not id_user_actualizacion:
        raise Exception("Usuario no ingresado")

    # Query the active label by ID
    try:
        active_label = db.session.query(LabelXTarea).filter(LabelXTarea.id == uuid.UUID(id)).first()
    except ValueError:
        raise Exception("ID inválido proporcionado")

    print('Consulta labels por ID de tarea')
    print('Active label:', active_label)

    if active_label:
        # Mark the label as inactive and update metadata
        active_label.activa = False
        active_label.fecha_actualizacion = datetime.now()
        active_label.id_user_actualizacion = id_user_actualizacion
        db.session.commit()
        print('Etiqueta desactivada correctamente')
        return active_label
    else:
        print("No se encontraron etiquetas activas para la tarea")
        return None

