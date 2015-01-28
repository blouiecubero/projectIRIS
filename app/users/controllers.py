import os.path
import random
import requests
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
from flask.ext.login import login_user , logout_user , current_user , login_required
from werkzeug import check_password_hash, generate_password_hash
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.sql import exists
from sqlalchemy import or_
from flask.ext.uploads import UploadSet, IMAGES, configure_uploads
from app.database import db_session, Base,init_db
from app.users.forms import LoginForm, ChangePasswordForm
from app.users.models import User, ProfileImage, Role, Permission
from app.projects.models import Project
from app.users.helpers import Role_Determinator
from app.decorators.controllers import admin_required
from app import login_manager, oid, imageUploadSet

# @define - blueprint for users
Users = Blueprint('Users', __name__,)

# Initializing helper class for handling role modification
role_change = Role_Determinator()

## This enables permissions to run on all functions.
@Users.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

# @function - Used to add an object to a database [Could be move to another class to make this more reusable by other objects]
def add_to_db(object):
    try:
        db_session.add(object)
        db_session.flush()
        return True
    except sqlalchemy.exc.IntegrityError as err:
        print "IntegrityError"
        return False


# @functions - User authentication methods
# @function - Assigns current user to g
@Users.before_request
def before_request():
    g.user = current_user   #current user from flask.ext.login

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@Users.route('/login/', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('Home.show_home'))
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print user.username
        if user and check_password_hash(user.password, form.password.data):
            user.authenticated = True;
            login_user(user);
            return redirect(url_for('Home.show_home'))
        flash('Wrong username or password', 'error-message')
    return render_template("users/login.html", form=form)

@Users.route('/edit_permissions', methods=['GET','POST'])
@admin_required
def change_permissions():
    all_users = User.query.all()
    roles = Role.query.order_by(Role.id).all()
    list_of_emp = ['HR','Finance','OJT','Seer','CD','CPI']
    if request.method == 'POST':
        
            if request.form['button'] == 'Update Role':
                whosuser = request.form['users']
                whatrole = request.form['roles']
                user = User.query.filter_by(username=whosuser).first()
                user.role = Role.query.filter_by(name=whatrole).first()
                db_session.add(user)
                db_session.commit()
                flash('Role changed.')
                return redirect(url_for('Users.change_permissions'))
            
            elif request.form['button'] == 'Save Roles':
                for emp_type in list_of_emp:
                    permit = 0x00
                    for index_num in range(len(list_of_emp)):
                        type = emp_type+ ' ' + str(index_num + 1)
                        print type
                        get_val = request.form.get(str(type))
                        if get_val is not None:
                            permit = permit | int(get_val)
                    default = True
                    print permit
                    if emp_type != 'New_User':
                        default = False
                    role_change.define_permissions(emp_type,permit,default)
                    role_change.record_roles()
                flash('Permissions changed.')
                return redirect(url_for('Users.change_permissions'))
    return render_template('admin/edit_permissions.html',list_of_emp=list_of_emp, all_users=all_users, roles=roles, user=current_user)



@Users.route('/change_password/',methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    user = current_user
    if form.validate_on_submit():
        user = g.user
        print user.username
        if user and check_password_hash(user.password, form.old_password.data):
            if(form.new_password.data == form.confirm_password.data):
                #flash('Password changed ');
                user.password = generate_password_hash(form.new_password.data)
                #if(db_session.commit()):
                flash("Password changed",'error')
                    #return redirect(url_for('Home.show_home'))
                #else:
                    #flash("Password NOT changed",'error')
            else:
                flash("Passwords do not match",'error')
        else:   
            flash('Wrong password', 'error')
    return render_template("users/change_password.html", form=form, user=user)

@Users.route('/logout')
def logout():
    user = g.user
    user.authenticated = False
    logout_user()
    print 'logout success'
    return redirect(url_for('Users.login'))

# @function - Uploads a profile picture and updates the user data
@Users.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'image' in request.files:
        name = str(g.user.id) + "_" + str(ProfileImage.query.filter_by(user_id=g.user.id).count()) + os.path.splitext(request.files['image'].filename)[1].lower()
        print name
        previous_image = ProfileImage.query.filter_by(is_active=1).filter_by(user_id=g.user.id).first()
        try:
            filename = imageUploadSet.save(request.files['image'],name=name)
            image = ProfileImage(user_id=g.user.id,is_active=1,image=filename)
            #image.store()
            if previous_image is not None:
                previous_image.is_active = 0
            #DONT FORGET TO UPDATE is_active
            if(add_to_db(image)):
                current_user.images.append(image);
                db_session.commit()
                flash("Photo saved.")
                print image.id
                print imageUploadSet.url(image.image)
        except:
            print "upload not allowed"
    return redirect(url_for('Home.show_home')+"#uploadComplete")

# @function - Returns the current profile picture of the logged in user
def getProfilePicture():
    #g.user = current_user
    #image = ProfileImage.query.filter_by(is_active=1).filter_by(user_id=g.user.id).first()
    image  = current_user.images.filter_by(is_active=1).first()
    if image is not None:
        print imageUploadSet.url(image.image)
        return imageUploadSet.url(image.image)
    else:
        random_img =  random.randint(1,15)
        url = url_for('static', filename='assets/images/default_profile_image/') + str(random_img) +".jpg"
        return url



# @functions - Basecamp integration methods
@login_required
def syncProjects(username):
    url='http://www.seerlabs.com:5556/api/getProject'
    user = User.query.filter_by(username=username).first()
    payload = {'email': user.email}
    response = requests.post(url, data=payload)
    responseJson = response.json()
    print(responseJson['projects'])

    for projectName in responseJson['projects']:
        print projectName
        (ret, ), = db_session.query(exists().where(Project.project_name==projectName))
        if(ret):
             project = Project.query.filter_by(project_name=projectName).first()
             user.projects.append(project)
             print "Existing"
        else:
            project = Project(projectName)
            if(add_to_db(project)):
                user.projects.append(project)
                db_session.commit()
                print "Project added"
            
def getUtilization(user):
    url='http://www.seerlabs.com:5556/api/getUtilization'
    #user = User.query.filter_by(username=user.username).first() #username is unique
    payload = {'email': user.email}
    response = requests.post(url, data=payload)
    responseJson = response.json()
    return responseJson['projects']

    #http://www.seerlabs.com:5556/api/getUtilization
    #http://www.seerlabs.com:5556/api/postNewsfeed
    #http://www.seerlabs.com:5556/api/getNewsfeed
    #http://www.seerlabs.com:5556/api/getProject

#pragma mark -Test block to install database and add a default user
def add_user(c):
    """try:"""
    db_session.add(c)
    db_session.flush()
    return True
    """except sqlalchemy.exc.IntegrityError as err:
        # @todo: handle as appropriate: return existing instance [session.query(Coupon).filter(Coupon.value==c.value).one()] or re-raise
        #logger.error("Tried to add a duplicate entry for the Coupon value [%s]. Aborting", c.value)
        print "Tried to add a duplicate entry for the Coupon value [%s]. Aborting", c.name
        return False"""
""""
init_db();
u = User('Te','re','suh', 'test@seer-technologies.com', "seer", generate_password_hash("seertech"), )
if(add_user(u)):
    db_session.commit()
else:
    print "aww"
print u.id"""


