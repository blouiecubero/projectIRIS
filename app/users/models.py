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

# @definition - Creates a table for the pivot table for users-projects relationship
user_projects = Table('user_projects',Base.metadata,
    Column('id',Integer,primary_key=True,autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('project_id', Integer, ForeignKey(Project.id))
)

class Permission:
    
    ## This class initializes the permissions that will be imposed on specific Roles.
    ## As you can see, the permissions are initialized in a hexadecimal value.

    VIEW_FILES = 0x01
    HR_FUNCTION = 0x02
    SEE_PROJECTS = 0x04
    UPLOAD_FILES = 0x08
    ADMINISTER = 0x80
    

class User(UserMixin, Base):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True,autoincrement=True)
    first_name = Column(String(50), unique=True)
    middle_name = Column(String(50), unique=True)
    last_name = Column(String(50), unique=True)
    email = Column(String(255), nullable=False, unique=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False, default='')
    role_id = Column(Integer, ForeignKey('roles.id'))
    
    #One-to-many
    stored_file = relationship('FileBase', backref='users',lazy='dynamic')

    #One-to-many
    images = relationship('ProfileImage', backref='users',lazy='dynamic')
    #comments = relationship('Comment', backref='users',lazy='dynamic')
    logs = relationship('Log',backref='users',lazy='dynamic')

    #Many-to-many
    projects = relationship('Project', secondary=user_projects, backref=backref('users', lazy='dynamic'))
    

    def __init__(self, fname=None,mname=None,lname=None, email=None, username=None, password=None):
        self.first_name = fname
        self.middle_name = mname
        self.last_name = lname
        self.email = email
        self.username = username
        self.password = password
        if self.role_id is None:
            if self.username == 'louie.cubero':
                self.role_id = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role_id = Role.query.filter_by(default=True).first()

    ## This function will determine if the user is granted a specific permission. It acts like a decorator.
    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    ## This function will determine if the user is an administrator. It acts like a decorator.
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    ## This function will determine if the user is an HR. It acts like a decorator.
    def is_HR(self):
        return self.can(Permission.HR_FUNCTION)

    ## This function will determine if the user is an Employee. It acts like a decorator.
    def can_view_files(self):
        return self.can(Permission.VIEW_FILES)

    def can_upload_files(self):
        return self.can(Permission.UPLOAD_FILES)

    def can_see_projects(self):
        return self.can(Permission.SEE_PROJECTS)
    
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

class FileBase(Base):
    __tablename__ = 'files'
    id =Column(Integer, primary_key=True)
    description = Column(Text)
    date = Column(DateTime, index=True, default=datetime.utcnow)
    user = Column(Integer, ForeignKey('users.id'))
    filename = Column(String(64))

        
    def __repr__(self):
        return self.filename


class Role(Base):

    ## This *Role* class serves as the table that initializes all the Roles that
    ## has been established in this program. The permission of all its Role are based from the Permission class.
    
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    default = Column(Boolean, default=False, index=True)
    permissions = Column(Integer)
    users = relationship('User', backref='role', lazy='dynamic')

    ## There are 5 kinds of role that are used. New_User has no permissions.
    ## Employee can only view files, HR_ONLY can only exercise HR functions
    ## While HR_User is a combination HR and User Functions.
    ## The Administrator function has all the functions. HR, User, and
    ## including assigning roles to certain users.

    @staticmethod
    def insert_roles(roles):

        
    ## The purpose of this for loop is to assign the permission to its specific Roles.
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db_session.add(role)
        db_session.commit()
    
    def __repr__(self):
        return '<Role %r>' % self.name


class AnonymousUser(AnonymousUserMixin):

    ## This class sets permissions upon anonymous users. This is to prevent outside access easily.
    
    def can(self, permissions):
        return False

    def is_administrator(self):
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