## This py file serves as the database of the program. This is where all tables
## and columns are initialized. As you can see, this program utilizes an 
## ORM (Object Relational Mapping), and uses SQLite as the main database.

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from hashlib import md5
import hashlib


class Permission:
    
    ## This class initializes the permissions that will be imposed on specific Roles.
    ## As you can see, the permissions are initialized in a hexadecimal value.
    
    VIEW_FILES = 0x01
    ADMINISTER = 0x80



class Role(db.Model):

    ## This *Role* class serves as the table that initializes all the Roles that
    ## has been established in this program. The permission of all its Role are based from the Permission class.
    
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    ## There are 2 kinds of role that are used. The User and the Administrator.
    ## The permission of the user is to only view files, while the admin can perform
    ## higher duties, such as uploading or deleting a file from a specific user.
    
    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.VIEW_FILES, True),
            'Administrator': (0xff, False)
        }
        
    ## The purpose of this for loop is to assign the permission to its specific Roles.
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name



class User(UserMixin, db.Model):

    ## The function of the User table is to record all the Users registered and its specific attributes.
    
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    filename = db.Column(db.String(64))
    stored_file = db.relationship('FileBase', backref='owner', lazy ='dynamic')
    picture = db.Column(db.String(64))

    ## This function checks if the registered user is an admin. It's reference and basis is listed from the root:/config.py file.
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    ## This function checks if the password is tried to be read. 
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    ## This function generates a password hash so eliminate the chances of
    ## easily getting it.
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    ## This function verifies if the password matches to its generated_hash
    ## Since if the old hash can be used to procured the password, then there's
    ## no point of hashing the password at all. Therefore, it's hash is always
    ## new and unique.
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    ## This function generates a confirmation token.
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    ## This function checks if the user has already confirmed its account.
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    ## This function generates another token. It's different from the first
    ## token generator to eliminate redundancy and maintain clarity.
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    ## This function 
    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False
    
login_manager.anonymous_user = AnonymousUser    
    
                      


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class FileBase(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))
    filename = db.Column(db.String(64))

    def __repr__(self):
        return self.filename + ' '
