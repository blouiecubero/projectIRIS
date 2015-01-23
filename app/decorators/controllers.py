##These decorators contains decorators that permits a specific authority on
##a decorated function.

from functools import wraps
from flask import abort
from flask.ext.login import current_user
from app.users.models import Permission
from flask import Blueprint

Decorators = Blueprint('decorator', __name__)


##This decorator checks if the user has the permission
##to execute the decorated function.
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

## This decorator checks if the user is granted to run the specific function.

def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)

def HR_required(f):
    return permission_required(Permission.HR_FUNCTION)(f) 

def Employee_required(f):
    return permission_required(Permission.VIEW_FILES)(f) 
