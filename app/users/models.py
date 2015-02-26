# Import the database object (db) from the main application module
from sqlalchemy import Table, Column, ForeignKey, Integer, Float, String, Boolean, DateTime, Text
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import PickleType
from flask.ext.login import UserMixin, AnonymousUserMixin
from app.database import Base, db_session
from datetime import datetime, date
from flask import current_app
from app import login_manager
from app.projects.models import Project
from sqlalchemy.ext.mutable import Mutable

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
    user_leaves = relationship('UserStatistics', backref='users',lazy='dynamic')

    #One-to-many
    images = relationship('ProfileImage', backref='users',lazy='dynamic')
    #comments = relationship('Comment', backref='users',lazy='dynamic')
    logs = relationship('Log',backref='users',lazy='dynamic')

    #Many-to-many
    projects = relationship('Project', secondary=user_projects, backref=backref('users', lazy='dynamic'))
    
    #Many-to-many
    role = relationship('Role', secondary='user_roles')

    ## Stores the supervisor of the user.
    supervisor = Column(String(255))    

    ## Checks if the current user is a supervisor
    is_supervisor = Column(Boolean)    

    ## Stores the supervisee of the user.
    supervisee = Column(String(255))    

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
        print user
        u = User.query.filter_by(username=user).first()
        r = Role.query.filter_by(name='Administrator').first()
        if r in u.role:
            return True
        return False

    def return_user(self,user):
        print user
        u = User.query.filter_by(username=user).first()
        print u
        return u

    def return_userstatistics(self,user):
        print user
        u = User.query.filter_by(username=user).first()
        us = UserStatistics.query.filter_by(userId=u.id).first()
        print us
        return us

    def return_sickLeaves(self, user):
        print user
        u = User.query.filter_by(username=user).first()
        us = UserStatistics.query.filter_by(userId=u.id).first()
        print us
        ## If the user has no UserStatistics id yet, this block would 
        ## instantiate the user in the UserStatistics table.
        if us is None:
            temp = UserStatistics(userId=u.id)
            temp.slDates = {}
            temp.slDatesRecord = {}
            db_session.add(temp)
            db_session.commit()
            return temp.slDatesRecord

        if us.slDates is None:
            us.slDates = {}
            us.slDatesRecord = {}
            db_session.add(us)
            db_session.commit()
            print 'OK'
            return us.slDatesRecord

        return us.slDatesRecord

    def return_vacationLeaves(self, user):
        print user
        u = User.query.filter_by(username=user).first()
        us = UserStatistics.query.filter_by(userId=u.id).first()
        print us
        ## If the user has no UserStatistics id yet, this block would 
        ## instantiate the user in the UserStatistics table.
        if us is None:
            temp = UserStatistics(userId=u.id)
            temp.vlDates = {}
            temp.vlDatesRecord = {}
            db_session.add(temp)
            db_session.commit()
            return temp.vlDatesRecord

        if us.vlDates is None:
            us.vlDates = {}
            us.vlDatesRecord = {}
            db_session.add(us)
            db_session.commit()
            return us.vlDatesRecord
        return us.vlDatesRecord

    def return_offsetDates(self, user):
        print user
        u = User.query.filter_by(username=user).first()
        us = UserStatistics.query.filter_by(userId=u.id).first()
        print us
        ## If the user has no UserStatistics id yet, this block would 
        ## instantiate the user in the UserStatistics table.
        if us is None:
            temp = UserStatistics(userId=u.id)
            temp.offsetDates = {}
            temp.offsetDatesRecord = {}
            db_session.add(temp)
            db_session.commit()
            return temp.offsetDatesRecord

        if us.offsetDates is None:
            us.offsetDates = {}
            us.offsetDatesRecord = {}
            db_session.add(us)
            db_session.commit()
            return us.offsetDatesRecord

        return us.offsetDatesRecord

    def return_date_decided(self, user, date, whatLeave):
        u = User.query.filter_by(username=user).first()
        us = UserStatistics.query.filter_by(userId=u.id).first()
        
        if whatLeave == 'sickleave':
            alldateconf = us.slDatesDecidedDates
            if alldateconf is None:
                return None

            dateconf = alldateconf[date]
            return dateconf

        elif whatLeave == 'vacationleave':
            alldateconf = us.vlDatesDecidedDates

            if alldateconf is None:
                return None

            dateconf = alldateconf[date]
            return dateconf

        elif whatLeave == 'offsetleave':
            alldateconf = us.offsetDatesDecidedDates
            if alldateconf is None:
                return None
            
            dateconf = alldateconf[date]
            return dateconf

    def return_date_pending(self, user, date, whatLeave):
        u = User.query.filter_by(username=user).first()
        us = UserStatistics.query.filter_by(userId=u.id).first()
        print 'Records for sickleave: ' + str(us.slDatesRecord)
        print 'Records for vacationleave: ' + str(us.vlDatesRecord)
        print 'Records for offsetleave: ' + str(us.offsetDatesRecord)
        if whatLeave == 'sickleave':
            print 'sickleave'
            print 'DATE: ' + str(date)
            alldateconf = us.slDatesAppliedDates
            print 'ALL DATES: ' + str(alldateconf)

            if alldateconf is None:
                return None

            dateconf = alldateconf[date]
            print 'DATECONF: ' + str(dateconf)
            return dateconf

        elif whatLeave == 'vacationleave':
            print 'vleave'
            print 'DATE: ' + str(date)
            alldateconf = us.vlDatesAppliedDates
            print 'ALL DATES: ' + str(alldateconf)

            if alldateconf is None:
                return None

            dateconf = alldateconf[date]
            return dateconf

        elif whatLeave == 'offsetleave':
            print 'offset'
            alldateconf = us.offsetDatesAppliedDates
            if alldateconf is None:
                return None
            
            dateconf = alldateconf[date]
            return dateconf

    def return_date_pending_cancellation(self, user, date, whatLeave):
        u = User.query.filter_by(username=user).first()
        us = UserStatistics.query.filter_by(userId=u.id).first()
        print 'Records: ' + str(us.slDatesRecord)
        if whatLeave == 'sickleave':
            print 'DATE: ' + str(date)
            alldateconf = us.slDatesCancelled
            print 'ALL DATES: ' + str(alldateconf)

            if alldateconf is None:
                return None

            dateconf = alldateconf[date]
            print 'DATECONF: ' + str(dateconf)
            return dateconf

        elif whatLeave == 'vacationleave':
            alldateconf = us.vlDatesCancelled

            if alldateconf is None:
                return None

            dateconf = alldateconf[date]
            return dateconf

        elif whatLeave == 'offsetleave':
            alldateconf = us.offestDatesCancelled
            if alldateconf is None:
                return None
            
            dateconf = alldateconf[date]
            return dateconf

    def return_date_confirmed_cancellation(self, user, date, whatLeave):
        u = User.query.filter_by(username=user).first()
        us = UserStatistics.query.filter_by(userId=u.id).first()
        print 'Records: ' + str(us.slDatesRecord)
        if whatLeave == 'sickleave':
            print 'DATE: ' + str(date)
            alldateconf = us.slDatesConfirmedCancelled
            print 'ALL DATES: ' + str(alldateconf)

            if alldateconf is None:
                return None

            dateconf = alldateconf[date]
            print 'DATECONF: ' + str(dateconf)
            return dateconf

        elif whatLeave == 'vacationleave':
            alldateconf = us.vlDatesConfirmedCancelled

            if alldateconf is None:
                return None

            dateconf = alldateconf[date]
            return dateconf

        elif whatLeave == 'offsetleave':
            alldateconf = us.offestDatesConfirmedCancelled
            if alldateconf is None:
                return None
            
            dateconf = alldateconf[date]
            return dateconf

    def format_dates(self,given_date):
        dates = given_date.split(';')
        list_of_dates = []
        for i in dates:
            new_date = i.split('-')
            print new_date
            store_date =  date(int(2000 + int(new_date[2])), int(new_date[0]), int( int(new_date[1])))
            temp = store_date.strftime('%B %d, %Y')
            print temp
            list_of_dates.append(temp)
        return list_of_dates

    def format_one_date(self,given_date):
        new_date = given_date.split('-')
        print new_date
        store_date =  date(int(2000 + int(new_date[2])), int(new_date[0]), int( int(new_date[1])))
        temp = store_date.strftime('%B %d, %Y')
        print temp
        return temp

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
## This class enables a mutable dictionary for UserStatistics Table.
class MutableDict(Mutable, dict):

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)
            return Mutable.coerce(key, value)
        else:
            return value

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.changed()

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.changed()

    def __getstate__(self):
        return dict(self)

    def __setstate__(self, state):
        self.update(self)

class UserStatistics(Base):
    __tablename__ = 'userstatistics'
    id = Column(Integer, primary_key = True)
    userId = Column(Integer, ForeignKey('users.id'))
    proposed_offset = Column(Integer)

    ## To shorten the explanation, I'll just explain the differences of the last 
    ## words and what does it mean.

    ## The "Dates" is the basis of the User's applied dates
    ## The "DatesRecord" records all the previous transactions, like pending, cancelled, confirm and denied dates to list some.
    ## The "DatesCancelled" records when a certain date to be cancelled is applied
    ## The "DatesConfirmedCancelled" records when the certain date to be cancelled is confirmed to cancel
    ## The "DatesAppliedDates" records all the dates when was the leave applied
    ## The "DatesDecidedDates" records all the decided (confirmed, denied, cancelled) dates when was the leave has received a decision

    ## My format for all recording dates is a dictionary. Simply because in each date recorded, there'll be a counterpart value. For example:
    ## vlDates = {'date1': 1, 'date2': 2} (The dates stored represent the value of it's decision. 0 is for pending for approval, 
    ## 1 is for confirmed, 2 is for denied, 3 is for pending cancellation, and 4 is for cancelled.)


    vl = Column(Integer) ## Number of dates remaining
    vlDates = Column(MutableDict.as_mutable(PickleType))              
    vlDatesRecord = Column(MutableDict.as_mutable(PickleType))
    vlDatesCancelled = Column(MutableDict.as_mutable(PickleType))
    vlDatesConfirmedCancelled = Column(MutableDict.as_mutable(PickleType))
    vlDatesAppliedDates = Column(MutableDict.as_mutable(PickleType))
    vlDatesDecidedDates = Column(MutableDict.as_mutable(PickleType))

    sl = Column(Integer) ## Number of dates remaining
    slDates = Column(MutableDict.as_mutable(PickleType))
    slDatesRecord = Column(MutableDict.as_mutable(PickleType))
    slDatesCancelled = Column(MutableDict.as_mutable(PickleType))
    slDatesConfirmedCancelled = Column(MutableDict.as_mutable(PickleType))
    slDatesAppliedDates = Column(MutableDict.as_mutable(PickleType))
    slDatesDecidedDates = Column(MutableDict.as_mutable(PickleType))

    offset = Column(Integer) ## Number of dates remaining
    offsetDates = Column(MutableDict.as_mutable(PickleType))
    offsetDatesRecord = Column(MutableDict.as_mutable(PickleType))
    offestDatesCancelled = Column(MutableDict.as_mutable(PickleType))
    offestDatesConfirmedCancelled = Column(MutableDict.as_mutable(PickleType))
    offsetDatesAppliedDates = Column(MutableDict.as_mutable(PickleType))
    offsetDatesDecidedDates = Column(MutableDict.as_mutable(PickleType))


    def __repr__(self):
        return str(self.userId)


   


    



