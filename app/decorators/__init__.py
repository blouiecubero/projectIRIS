from flask import Blueprint

decorators = Blueprint('decorator', __name__)

from . import decorators
