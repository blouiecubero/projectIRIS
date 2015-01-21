# Import the database object (db) from the main application module
from sqlalchemy import Table, Column, ForeignKey, Integer, Float, String, Boolean, DateTime, Text
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.orm import relationship, backref
from app.database import Base
from datetime import datetime
from app.projects.models import Project

# @definition - Creates a table for the pivot table for users-projects relationship
user_projects = Table('user_projects',Base.metadata,
    Column('id',Integer,primary_key=True,autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('project_id', Integer, ForeignKey(Project.id))
)


class User(Base):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True,autoincrement=True)
    first_name = Column(String(50), unique=True)
    middle_name = Column(String(50), unique=True)
    last_name = Column(String(50), unique=True)
    email = Column(String(255), nullable=False, unique=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False, default='')

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
