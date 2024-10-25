from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from models.alch_model import HerarquiaGrupoGrupo
from flask import current_app

def find_parent_id(session: Session, id_hijo: str):
    try:
        # Query the HerarquiaGrupoGrupo table to find the parent
        hierarchy = session.query(HerarquiaGrupoGrupo).filter(HerarquiaGrupoGrupo.id_hijo == id_hijo).one()
        
        # If a parent is found, return its id
        return hierarchy.id_padre
    except NoResultFound:
        # If no parent is found, this might be a root node
        return None
    except Exception as e:
        # Log the error and re-raise it
        current_app.logger.error(f"Error finding parent for id_hijo {id_hijo}: {str(e)}")
        raise

def find_parent_id_recursive(session: Session, id_hijo: str):
    parent_id = find_parent_id(session, id_hijo)
    
    if parent_id is None:
        # This is a root node, return None
        return None
    else:
        # Recursively find the parent of this parent
        grandparent_id = find_parent_id_recursive(session, parent_id)
        
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
#     with current_app.session() as session:
#         try:
#             root_parent_id = find_parent_id_recursive(session, id_hijo)
#             return root_parent_id
#         except Exception as e:
#             current_app.logger.error(f"Error finding root parent for id_hijo {id_hijo}: {str(e)}")
#             return None