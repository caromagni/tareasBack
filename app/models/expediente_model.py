from alchemy_db import db
from cache import cache
from models.alch_model import ExpedienteExt

@cache.memoize(timeout=3600)
def get_all_expedientes():
    
    return db.session.query(ExpedienteExt).all()
