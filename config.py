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

FLASKY_ADMIN = 'blouiecubero@gmail.com'

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"

UPLOADS_DEFAULT_DEST = os.path.join(BASE_DIR, 'app\\var\\uploads')
UPLOADS_FILES_DEST = os.path.join(BASE_DIR, 'app\\var\\uploads\\files')
UPLOADED_FILES_ALLOW = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
ALLOWED_DOCUMENTS = set(['pdf','PDF'])
