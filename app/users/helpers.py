<<<<<<< HEAD
from app.database import db_session
from app.users.models import Role, User

class Role_Determinator():
    role = {}
    
    def define_permissions(self, rolename, permission):
        self.role[rolename] = (permission)

    def show_permissions(self):
        return self.role

    def record_roles(self):
        Role.insert_roles(self.role)
        
        
=======
from flask import current_app

class FileChecker():
    
    ## Defining functions for filechecking when upload functions are used.
    
    def allowed_pic(self,filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_PICTURES']

    def allowed_files(self,filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_DOCUMENTS']   
>>>>>>> cee9d0b2da1d3dbeac36bfe675438c30487e7305
