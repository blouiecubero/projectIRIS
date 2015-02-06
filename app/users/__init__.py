<<<<<<< HEAD
from controllers import Users
=======
from flask import Blueprint

users = Blueprint('users', __name__)

from . import views
from ..models import Permission

@users.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
>>>>>>> cee9d0b2da1d3dbeac36bfe675438c30487e7305
