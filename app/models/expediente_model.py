import uuid

from datetime import datetime
from alchemy_db import db
from flask import current_app

from models.alch_model import ExpedienteExt


def get_all_expedientes():
    
    return db.session.query(ExpedienteExt).all()
