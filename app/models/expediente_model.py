import uuid
from sqlalchemy.orm import scoped_session
from datetime import datetime

from flask import current_app

from .alch_model import ExpedienteExt


def get_all_expedientes():
    session: scoped_session = current_app.session
    return session.query(ExpedienteExt).all()
