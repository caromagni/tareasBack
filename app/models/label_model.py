import uuid
from models.usuario_model import get_grupos_by_usuario
from models.tarea_model import get_tarea_by_id
from sqlalchemy.orm import scoped_session, joinedload
from datetime import datetime, timedelta
from common.functions import controla_fecha
from common.utils import *
from common.error_handling import ValidationError
from common.logger_config  import logger
from models.grupo_hierarchy import find_parent_id_recursive

from flask import current_app
from alchemy_db import db
from .alch_model import Label, Grupo, HerarquiaGrupoGrupo, LabelXTarea, Tarea
from models.alch_model import Label, Grupo, HerarquiaGrupoGrupo

    

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
def insert_label(username=None, nombre='', color= '', eliminado=False, fecha_eliminacion=None, id_user_creacion=None, id_grupo=None, id_tarea=None, ids_labels=[]):
    
    
    if username is not None:
        id_user_creacion = verifica_username(username)
    else:
        raise ValidationError("Usuario no ingresado 0")  
    
    nuevoID_label=uuid.uuid4()
    id_tarea = id_tarea
    # tarea = get_tarea_by_id(id_tarea)
    # id_grupo = tarea[0]['grupos'][0]['id']
    id_grupo = id_grupo
    # print('grupo:', tarea[0]['grupos'][0]['id'], 'usuario ingresante:', id_user_creacion)
    print('db.session:', db.session)
    id_grupo_padre=find_parent_id_recursive(db.session, id_grupo)

    print('id_grupo_padre:', id_grupo_padre)

    nueva_label = Label(
        eliminado=eliminado,
        fecha_eliminacion=fecha_eliminacion,
        fecha_creacion=datetime.now(),
        id_user_creacion=id_user_creacion,
        id=nuevoID_label,
        color=color,
        id_grupo_padre=id_grupo_padre,
        nombre=nombre,
    )

    db.session.add(nueva_label)

    print('ids_labels:', ids_labels)
    print('nuevoID_label:', nuevoID_label)

    ids_labels.append(str(nuevoID_label) )
    print('ids_labels:', ids_labels)

    insert_label_tarea(ids_labels=ids_labels, id_tarea=id_tarea, username=username)

       
    db.session.commit()

    return nueva_label


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
def get_all_label(username=None, page=1, per_page=30, nombre='', id_grupo_padre=None, id_tarea=None, id_user_creacion=None, fecha_desde='01/01/2000', fecha_hasta=datetime.now(), eliminado=None, label_color=''):
       
    """ if username is not None:
        id_user = verifica_username(username)
    else:
        raise ValidationError("Usuario no ingresado") """
   

    query = db.session.query(Label).filter(Label.fecha_creacion.between(fecha_desde, fecha_hasta)).order_by(Label.fecha_creacion.desc())
    if nombre != '':
        query = query.filter(Label.nombre.ilike(f'%{nombre}%'))

    if id_grupo_padre is not None:
        query = query.filter(Label.id_grupo_padre== id_grupo_padre)

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
    
    res = db.session.query(Label).filter(Label.id == id).first()

    if res is not None:
        return res 
    else:
        print("Label no encontrada")
        return None

def delete_label(username=None, id_label=None):    

    if username is not None:
        id_user_actualizacion = verifica_username(username)
    else:
        raise ValidationError("Usuario no ingresado")
    
    label = db.session.query(Label).filter(Label.id == id_label, Label.eliminado==False).first()
    print('label id a borrar:', label)
    if label is not None:
        if(label.id_user_creacion != id_user_actualizacion):
            return "Usuario no autorizado para eliminar la etiqueta" 
        else: 
            labelTarea = db.session.query(LabelXTarea).filter(LabelXTarea.id_label != id_label, LabelXTarea.activa == True).all()       
            if labelTarea is not None:
                result = { "status": "error", "message": "La etiqueta está asociada a una tarea activa"}
                return result
            else:
                label.eliminado=True
                label.fecha_eliminacion=datetime.now()
                label.id_user_actualizacion=id_user_actualizacion
                label.fecha_actualizacion=datetime.now()
                db.session.commit()
                return label        
    else:
        print("Label no encontrada")
        return None

############################## LABELS x GRUPO BASE ########################################
### Busca las etiquetas activas según el grupo base disponibles para todo el árbol de dicho grupo ####

def get_active_labels(ids_grupos_base):
    print('entra a get de labels por grupo base aaaahhhhhhhhhhkfhaksfhkasdfhñasdfh')
    print('ids_grupos_base:', ids_grupos_base)
    # id_grupo_base = find_parent_id_recursive(db, id_grupo)
    # print('*********************************************id_grupo_base:', id_grupo_base)
    print("##"*50)
    ids_list = ids_grupos_base.split(',')
    print('ids_list:', ids_list)
    labels_group_array = []
    total = 0
    for id in ids_list:
        print('id_grupos_base:', id)
        print("#"*50)
        labels_group = db.session.query(Label).filter(Label.id_grupo_padre == id, Label.eliminado == False).all()
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
def insert_label_tarea (username=None, **kwargs):
    

    if username is not None:
        id_user_actualizacion = verifica_username(username)
    else:
        raise ValidationError("Usuario no ingresado 1") 
    
    id_tarea = kwargs['id_tarea']
    ids_labels = kwargs['ids_labels']

    labelsTarea = db.session.query(LabelXTarea).filter(LabelXTarea.id_tarea == id_tarea, LabelXTarea.activa == True).all()
    # labelsActivas = db.session.query(LabelXTarea).filter(LabelXTarea.id_tarea == id_tarea, LabelXTarea.activa == True).all()
    # labelsInactivas = db.session.query(LabelXTarea).filter(LabelXTarea.id_tarea == id_tarea, LabelXTarea.activa == False).all()

    taskLabels = []

    # Convertir listas de etiquetas activas e inactivas a conjuntos de IDs para facilitar la comparación
    set_labelsTarea = {str(label.id_label) for label in labelsTarea}
    # set_labelsActivas = {str(label.id_label) for label in labelsActivas}
    # set_labelsInactivas = {str(label.id_label) for label in labelsInactivas}
    set_ids_labels = set(ids_labels)

    # print('set_labelsActivas:', set_labelsActivas)
    # print('set_labelsInactivas:', set_labelsInactivas)
    print('set_ids_labels:', set_ids_labels)
    print('set_labelsTarea:', set_labelsTarea)

    nuevos_labels = set_ids_labels - set_labelsTarea
    viejos_labels = set_ids_labels - nuevos_labels  

    print  ('nuevos_labels:', nuevos_labels)
    print  ('viejos_labels:', len (viejos_labels))

    fecha_actualizacion = datetime.now()

    if len(viejos_labels)!= 0:
        print('entra a actualizar labels')
        for label in labelsTarea:
            for label_viejo in viejos_labels:
                print('entra al bucle de labels viejos'+label_viejo)
                print('entra al bucle de labels de la tarea'+str(label.id_label))
                # if str(label.id_label) == label_viejo:
                #     print(label.activa)
                #     label.activa = True
                #     label.fecha_actualizacion = fecha_actualizacion
                #     label.id_user_actualizacion = id_user_actualizacion
                #     db.session.commit()
                # else:
                if str(label.id_label) not in viejos_labels:
                    label.activa = False
                    label.fecha_actualizacion = fecha_actualizacion
                    label.id_user_actualizacion = id_user_actualizacion
                    db.session.commit()
    # else:
    #     for label in labelsTarea:
    #         label.activa = False
    #         label.fecha_actualizacion = fecha_actualizacion
    #         label.id_user_actualizacion = id_user_actualizacion
    #         db.session.commit()

    if(len(nuevos_labels) != 0):
        for id_label in nuevos_labels:
            print('Creando nuevo registro para label: ', {id_label})
            nuevoID_label_tarea=uuid.uuid4()

            nueva_label = LabelXTarea(
                id=nuevoID_label_tarea,
                id_label=id_label,
                id_tarea=id_tarea,
                activa=True,
                # fecha_creacion=fecha_actualizacion,
                # id_user_creacion=id_user_actualizacion,
                fecha_actualizacion=fecha_actualizacion,
                id_user_actualizacion=id_user_actualizacion
            )
            db.session.add(nueva_label)
            db.session.commit()


    # if not nueva:
    #     # Mantener las etiquetas activas si ya están activas y vienen en ids_labels
    #     for label in labelsActivas:
    #         if str(label.id_label) in set_ids_labels:
    #             print('La etiqueta ya existe activa')
    #         # else:
    #         #     print('La etiqueta no existe activa')
    #         #     label.activa = False
    #         #     label.fecha_actualizacion = fecha_actualizacion
    #         #     label.id_user_actualizacion = id_user_actualizacion
    #         #     db.session.add(label)
    #         #     taskLabels.append(label)

    #     # Activar las etiquetas inactivas si vienen en ids_labels
    #     for label in labelsInactivas:
    #         if str(label.id_label) in set_ids_labels:
    #             print('La etiqueta ya existe inactiva')
    #             label.activa = True
    #             label.fecha_actualizacion = fecha_actualizacion
    #             label.id_user_actualizacion = id_user_actualizacion
    #             db.session.add(label)
    #             taskLabels.append(label)

    # Crear nuevas etiquetas si no existen en las etiquetas activas o inactivas
    # if nueva:
    #     nuevos_labels = set_ids_labels - set_labelsActivas - set_labelsInactivas
    #     for id_label in nuevos_labels:
    #         print('Creando nuevo registro para label: {id_label}')
    #         nuevoID_label_tarea=uuid.uuid4()

    #         nueva_label = LabelXTarea(
    #             id=nuevoID_label_tarea,
    #             id_label=id_label,
    #             id_tarea=id_tarea,
    #             activa=True,
    #             fecha_actualizacion=fecha_actualizacion,
    #             id_user_actualizacion=id_user_actualizacion
    #         )
    #         db.session.add(nueva_label)
    #         taskLabels.append(nueva_label)

    #     db.session.commit()

    ###################Formatear el resultado####################
    response = {
        'status': 'success',
        'message': 'Labels actualizados correctamente',
        'data': [label.id_label for label in taskLabels]
        }
    
    print('response:', response)

    return response
    
    # 
    # # labelsTarea = []

    # # labelsTarea = db.session.query(LabelXTarea).filter(LabelXTarea.id_tarea == id_tarea).all()

    # labelsActivas = db.session.query(LabelXTarea).filter(LabelXTarea.id_tarea == id_tarea, LabelXTarea.activa == True).all()
    # labelsInactivas = db.session.query(LabelXTarea).filter(LabelXTarea.id_tarea == id_tarea, LabelXTarea.activa == False).all()

    # # taskLabels = []
    # updateLabels = []
    # createLabels = []

    # #si vienen labels ya activas, no actualizarlas
    # #si no vienen labels que ya estan activas, actualizarlas (false)
    # #si vienen labels inactivas, actualizarlas (true)

    # if len(labelsInactivas) > 0:
    #     for label in labelsInactivas:
    #         for id_label in ids_labels:
    #             if str(label.id_label) == id_label:
    #                 print('la etiqueta ya existe inactiva')    
    #                 label.activa = True
    #                 label.fecha_actualizacion = fecha_actualizacion
    #                 label.id_user_actualizacion = id_user_actualizacion                                   
    #             else:   
    #                 if len(labelsActivas) > 0:        
    #                     for label in labelsActivas:
    #                         for id_label in ids_labels:
    #                             if str(label.id_label) == id_label:
    #                                 print('la etiqueta ya existe activa') 
    #                             else:
    #                                 print(label)
    #                                 print(id_label)
    #                                 print('la etiqueta no existe activa')
    #                                 createLabels.append(id_label)
    #                 else:
    #                     createLabels.append(id_label)
    # if len(labelsActivas) > 0:
    #     for label in labelsActivas:
    #         for id_label in ids_labels:
    #             if str(label.id_label) == id_label:
    #                 print('la etiqueta ya existe activa') 
    #             else:
    #                 #si solo hay etiquetas activas y no vienen en la lista, se desactivan
    #                 print(label)
    #                 print(id_label)
    #                 print('la etiqueta no existe activa')
    #                 label.activa = False
    #                 label.fecha_actualizacion = fecha_actualizacion
    #                 label.id_user_actualizacion = id_user_actualizacion
    
    #     for label in createLabels:
    #         print('inicia el bucle para CREAR las etiquetas')
    #         print(label)
    #         nuevoID_label_tarea=uuid.uuid4()
        
    #         nueva_label_tarea = LabelXTarea(
    #             activa=True,
    #             fecha_actualizacion=fecha_actualizacion,
    #             id_user_actualizacion=id_user_actualizacion,
    #             id=nuevoID_label_tarea,
    #             id_label=id_label,
    #             id_tarea=id_tarea,        
    #         )
        
    #         db.session.add(nueva_label_tarea)
    #         taskLabels.append(nueva_label_tarea)

    #     for label in updateLabels:
    #         print('inicia el bucle para ACTUALIZAR las etiquetas')
    #         print(label)
    #         label.activa = True
    #         label.fecha_actualizacion = fecha_actualizacion
    #         label.id_user_actualizacion = id_user_actualizacion
            
                    
    #                     db.session.add(nueva_label_tarea)
    #                     taskLabels.append(nueva_label_tarea)

    
   

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
    print('entra a get de labels por tarea')
    
    active_labels = db.session.query(LabelXTarea).filter(LabelXTarea.id_tarea == id_tarea, LabelXTarea.activa == True).all()
    print('consulta labels por id de tarea error')

    if active_labels is not None:
        # ###################Formatear el resultado####################
        # res = {
        #     'status': 'success',
        #     'message': 'Labels obtenidos correctamente',
        #     'data': [label.id_label for label in active_labels]
        # }

        # print('res:', res)
        total = len(active_labels)
    
        return active_labels, total 
    else:
        print("La tarea no tiene labels")
        return None

def delete_label_tarea_model(username, **kwargs):
    print('entra a delete de labels por tarea')
    print('kwargs:', kwargs)
    id = kwargs['id_label']
    id_tarea = kwargs['id_tarea']
    
    
    if username is not None:
        id_user_actualizacion = verifica_username(username)
    else:
        raise ValidationError("Usuario no ingresado")    

   
    active_label = db.session.query(LabelXTarea).filter(LabelXTarea.id_label == uuid.UUID(id), LabelXTarea.id_tarea == uuid.UUID(id_tarea) ).first()
    print('consulta labels por id de tarea')
    print('active_label:', active_label)

    if active_label is not None:
        active_label.activa = False
        active_label.fecha_actualizacion = datetime.now()
        active_label.id_user_actualizacion = id_user_actualizacion
        db.session.commit()
        return active_label       
    else:
        print("La tarea no tiene etiquetas activas")
        return None
  
