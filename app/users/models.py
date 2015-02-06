# Import the database object (db) from the main application module
from sqlalchemy import Table, Column, ForeignKey, Integer, Float, String, Boolean, DateTime, Text
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.orm import relationship, backref
from flask.ext.login import UserMixin, AnonymousUserMixin
from app.database import Base, db_session
from datetime import datetime
from flask import current_app
from app import login_manager
from app.projects.models import Project

########################## ASSOCIATION TABLES ################################

# @definition - Creates a table for the pivot table for users-projects relationship
user_projects = Table('user_projects',Base.metadata,
    Column('id',Integer,primary_key=True,autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('project_id', Integer, ForeignKey(Project.id))
)

# @definition - Creates a table for the pivot table for roles-permissions relationship
class Role_Permission_Link(Base):
    __tablename__ = 'role_perms'
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id'), primary_key=True)

# @definition - Creates a table for the pivot table for user-roles relationship
class User_Role_Link(Base):
    __tablename__ = 'user_roles'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)

######################### ASSOCIATION TABLES END ###########################



############################# TABLES PROPER ################################
class User(UserMixin, Base):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True,autoincrement=True)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False, default='')
    active_role = Column(String(255)) ##Stores the active role of the user
    #One-to-many
    stored_file = relationship('Payslip', backref='users',lazy='dynamic')

    #One-to-many
    images = relationship('ProfileImage', backref='users',lazy='dynamic')
    #comments = relationship('Comment', backref='users',lazy='dynamic')
    logs = relationship('Log',backref='users',lazy='dynamic')

    #Many-to-many
    projects = relationship('Project', secondary=user_projects, backref=backref('users', lazy='dynamic'))
    
    #Many-to-many
    role = relationship('Role', secondary='user_roles')

    

    def __init__(self, fname=None,mname=None,lname=None, email=None, username=None, password=None):
        self.first_name = fname
        self.middle_name = mname
        self.last_name = lname
        self.email = email
        self.username = username
        self.password = password

    ## This function initializes all the permissions of the user.

    def init_active_roles(self, username):
        ## If user hasn't no active role yet:
        u = User.query.filter_by(username=username).first()
        role = u.role
        if not role:
            u.active_role = 'None'
            db_session.add(u)
            db_session.commit()
            return []
        r = role[0]
        role_stored = Role.query.filter_by(name=r.name).first()
        u.active_role = role_stored.name
        db_session.add(u)
        db_session.commit()
        based_permissions = role_stored.permissions
        return based_permissions

    def load_perms(self, role):
        r = Role.query.filter_by(name=role).first()
        return r.permissions

    ## This function checks the permissions of the user if it has the permission 
    ## looking for by the function
    def check_perms(self, perms, setofperms):
        p = Permission.query.filter_by(permission_name=str(perms)).first()
        check = p in setofperms
        return check
    
    ## This function loads up the roles of the user
    def load_roles(self, username):
        u = User.query.filter_by(username=username).first()
        return u.role
   
    ## This function changes the active role of the user
    def change_active_role(self, user, role):
        r = Role.query.filter_by(name=role).first()
        u = User.query.filter_by(username=user).first()
        u.active_role = r.name
        if not u.active_role:
            u.active_role = ''
        db_session.add(u)
        db_session.commit()
    
    ## Checks if the user is an admin
    def is_admin(self, user):
        u = User.query.filter_by(username=user).first()
        r = Role.query.filter_by(name='Administrator').first()
        if r in u.role:
            return True
        return False

    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)

class Role(Base):

    ## This *Role* class serves as the table that initializes all the Roles that
    ## has been established in this program. The permission of all its Role are based from the Permission class.
    
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), unique=True)
    #Many-to-many
    user = relationship('User', secondary='user_roles')
    permissions = relationship('Permission', secondary='role_perms')
    
    def __init__(self,name):
        self.name = name

    def load_perms(self, role_name):
        r = Role.query.filter_by(name=role_name).first()
        return r.permissions


    def __repr__(self):
        return '<Role %r>' % self.name


class Permission(Base):

    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True)
    permission_name = Column(String(50), nullable = False, unique=True)
    #Many-to-many
    roles = relationship('Role', secondary='role_perms')

    def __init__(self,permission_name):
        self.permission_name = permission_name

    def __repr__(self):
        return self.permission_name



class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True,autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date = Column(DateTime)
    description = Column(Text)
    hours = Column(Float, nullable=False, unique=True)

    def __init__(self, user_id=None,date=None,description=None, hours=None):
        self.user_id = user_id
        self.date = date
        self.description = description
        self.hours = hours

    # Return object data in easily serializeable format
    @property
    def serialize(self):
        return {
            'id'                : self.id,
            'user_id'           : self.user_id,
            'date'              : self.date,
            'description'       : self.description,
            'hours'             : self.hours
        }
    
class ProfileImage(Base):
    __tablename__ = 'profileImages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    is_active = Column(Integer)
    image = Column(String(200))

    def __init__(self, user_id=None,is_active=None,image=None):
        self.user_id = user_id
        self.is_active = is_active
        self.image = image

    # Return object data in easily serializeable format
    @property
    def serialize(self):
        return {
            'id'                : self.id,
            'user_id'           : self.user_id,
            'is_active'         : self.is_active,
            'image'             : self.image
        }

class Payslip(Base):
    __tablename__ = 'Payslip'
    id =Column(Integer, primary_key=True)
    description = Column(Text)
    date = Column(DateTime, index=True, default=datetime.utcnow)
    user = Column(Integer, ForeignKey('users.id'))
    filename = Column(String(64))

        
    def __repr__(self):
        return self.filename


class AnonymousUser(AnonymousUserMixin):

    ## This class sets permissions upon anonymous users. This is to prevent outside access easily.
    active_role = None
    username = None

    def init_active_roles(self,username):
        return []

    def load_perms(self):
        return []

    def load_roles(self, username):
        return []

    def check_perms(self, perms, setofperms):
        return False

    
    
login_manager.anonymous_user = AnonymousUser 


# Added by Ann

class UserStatistics(Base):
    __tablename__ = 'userstatistics'
    id = Column(Integer, primary_key = True)
    userId = Column(Integer, ForeignKey('users.id'))
    vl = Column(Integer)
    vlDates = Column(String(330)) # not sure with the rules yet but assumed a max 30-day leave
    sl = Column(Integer) 
    slDates = Column(String(330))
    offset = Column(Integer)
    offsetDates = Column(String(330))

    def __init__(self, id, userId, vl, vlDates, sl, slDates, offset, offsetDates):
        self.id = id
        self.userId = userId
        self.vl = vl
        self.vlDates = vlDates
        self.sl = sl
        self.slDates = slDates
        self.offset = offset
        self.offsetDates = offsetDates
