from sqlalchemy.exc import NoResultFound
from models.alch_model import HerarquiaGrupoGrupo
from flask import current_app
from common.cache import *


@cache.memoize(timeout=60 * 60 * 24)  # Cache for 24 hours
def find_parent_id(db, id_hijo: str):
    print("find parent id function")
    print('db.session:', db)
    print('id_hijo:', id_hijo)
    try:

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

@cache.cached(CACHE_TIMEOUT_LONG)
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
