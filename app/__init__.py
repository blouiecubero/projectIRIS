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

 

