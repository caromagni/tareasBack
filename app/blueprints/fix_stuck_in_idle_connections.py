from apiflask import APIBlueprint
from ..models.grupo_model import get_all_herarquia, get_grupos_herarquia_labels, get_grupos_recursivo
from typing import List
from ..schemas.schemas import GrupoHOut, HerarquiaGrupoGrupoOut, HerarquiaOut
from ..common.error_handling import ValidationError
from sqlalchemy.orm import scoped_session, aliased
fix_b = APIBlueprint('fix_b', __name__)
from flask import current_app
from sqlalchemy import text

@fix_b.get('/fix_stuck')
def fix_bb():
    session: scoped_session = current_app.session
        #res=get_grupos_herarquia()
    result_raw = session.execute(text('''SELECT 
    pg_terminate_backend(pid) 
FROM 
    pg_stat_activity 
WHERE 
    -- don't kill my own connection
    pid <> pg_backend_pid()
    -- only affect connections from the user 'developer'
    AND usename = 'developer'
    -- leave the current pgAdmin connection
    AND application_name <> 'pgAdmin 4';
''')) #example of raw query, reusing session pool from sqlalchemy
        
 

    return 'ok' 
    
  
    