<<<<<<< HEAD
import os
from flask import Flask, render_template
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from flask.ext.uploads import UploadSet, IMAGES, configure_uploads
from database import init_db
from config import BASE_DIR
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment

app = Flask(__name__)
app.config.from_object('config')

#configure allowed upload set for images [flask-uploads]
imageUploadSet = UploadSet('images', IMAGES)
configure_uploads(app, imageUploadSet)

#configure login manager, oid and moment
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'Users.login'
oid = OpenID(app, os.path.join(BASE_DIR, 'tmp'))
moment = Moment(app)
bootstrap = Bootstrap(app)
    
# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Import a module / component using its blueprint handler variable
from app.users import Users
from app.users.models import User
from app.home import Home 
from app.projects import Projects
from app.finance import PaySlip
from app.users.models import Payslip
##from app.decorators import Decorators
from app.hr import HR # Added by Ann

app.register_blueprint(Users)
app.register_blueprint(Home)
app.register_blueprint(Projects)
app.register_blueprint(PaySlip)
##app.register_blueprint(Decorators)
app.register_blueprint(HR) # Added by Ann

 
=======
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




>>>>>>> cee9d0b2da1d3dbeac36bfe675438c30487e7305

