## This program is run with a blueprint in it to make it more organized.

from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import config
from flask.ext.storage import get_default_storage_class
from flask.ext.uploads import init
import os

## Extensions Defined.
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


## Extensions initialized. (This is the function that initialized and imported
## all the listed configurations and extensions to be used in the program.

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

## The following code is for blueprinting.
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .decorators import decorators as decorators_blueprint
    app.register_blueprint(decorators_blueprint)

    from .email import email as email_blueprint
    app.register_blueprint(email_blueprint)
    

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .users import users as users_blueprint
    app.register_blueprint(users_blueprint, url_prefix='/users')

    return app





