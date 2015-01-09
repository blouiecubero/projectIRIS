from flask import Blueprint

users = Blueprint('users', __name__)

from . import views
from ..models import Permission

@users.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
