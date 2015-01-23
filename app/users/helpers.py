from app.database import db_session
from app.users.models import Role, User

class Role_Determinator():
    role = {}
    
    def define_permissions(self, rolename, permission, boolean):
        self.role[rolename] = (permission,boolean)

    def show_permissions(self):
        return self.role

    def record_roles(self):
        Role.insert_roles(self.role)
        
        
