from sqlalchemy.exc import NoResultFound
from models.alch_model import HerarquiaGrupoGrupo
from flask import current_app

def find_parent_id(db, id_hijo: str):
    print("find parent id function")
    print('db.session:', db)
    print('id_hijo:', id_hijo)
    try:
            # query_usr = db.session.query(Usuario).filter(Usuario.email == nombre_usuario).first()

        # Query the HerarquiaGrupoGrupo table to find the parent
        hierarchy = db.query(HerarquiaGrupoGrupo).filter(HerarquiaGrupoGrupo.id_hijo == id_hijo).one()
        
        # If a parent is found, return its id
        return hierarchy.id_padre
    except NoResultFound:
        # If no parent is found, this might be a root node
        return None
    except Exception as e:
        # Log the error and re-raise it
        current_app.logger.error(f"Error finding parent for id_hijo {id_hijo}: {str(e)}")
        raise

def find_parent_id_recursive(db, id_hijo: str):
    print("find parent id recursive function")
    print('db.session:', db)

    parent_id = find_parent_id(db, id_hijo)
    
    if parent_id is None:
        # This is a root node, return None
        return id_hijo
    else:
        # Recursively find the parent of this parent
        grandparent_id = find_parent_id_recursive(db, parent_id)
        
        if grandparent_id is None:
            # If there's no grandparent, this parent is the root
            return parent_id
        else:
            # Continue up the tree
            return grandparent_id

# Usage example:
# from flask import current_app
# 
# def get_root_parent(id_hijo: str):
#     with current_app.db.session() as db.session:
#         try:
#             root_parent_id = find_parent_id_recursive(db.session, id_hijo)
#             return root_parent_id
#         except Exception as e:
#             current_app.logger.error(f"Error finding root parent for id_hijo {id_hijo}: {str(e)}")
#             return None