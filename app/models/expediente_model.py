from db.alchemy_db import db
from common.cache import *
from models.alch_model import ExpedienteExt

@cache.memoize(CACHE_TIMEOUT_LONG)
def get_all_expedientes():
    
    return db.session.query(ExpedienteExt).all()
