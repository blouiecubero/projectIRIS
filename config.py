<<<<<<< HEAD
# Statement for enabling the development environment
DEBUG = True
##TRAP_BAD_REQUEST_ERRORS = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'iris.db')
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

ADMIN = 'seer'

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"

UPLOADS_DEFAULT_DEST = os.path.join(BASE_DIR, 'app\\var\\uploads')
UPLOADS_FILES_DEST = os.path.join(BASE_DIR, 'app\\var\\uploads\\files')
UPLOADED_FILES_ALLOW = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
ALLOWED_DOCUMENTS = set(['pdf','PDF'])
=======
import os
basedir = os.path.abspath(os.path.dirname(__file__))

## All configurations are organized in this py file.
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'blouiecubero@gmail.com'
    FLASKY_ADMIN = 'blouiecubero@gmail.com'
    FILES_FOLDER = '/Users/LouieCubero/My Documents/GitHub/Flasky5/static/FILES/'
    PICTURE_FOLDER = '/Users/LouieCubero/My Documents/GitHub/Flasky5/static/PICTURES/'
    FILE_SYSTEM_STORAGE_FILE_VIEW = 'static'
    DEFAULT_FILE_STORAGE = 'filesystem'
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'JPG'])
    ALLOWED_PICTURES = set(['png', 'jpg', 'jpeg', 'gif', 'JPG', 'ico'])
    ALLOWED_DOCUMENTS = set(['pdf','PDF'])
    @staticmethod
    def init_app(app):
        pass

 

#Initialization of the database.

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
>>>>>>> cee9d0b2da1d3dbeac36bfe675438c30487e7305
