import uuid

from datetime import datetime
from alchemy_db import db
from flask import current_app
from cache import cache
from models.alch_model import ExpedienteExt

@cache.memoize(timeout=3600)
def get_all_expedientes():
    
    return db.session.query(ExpedienteExt).all()
