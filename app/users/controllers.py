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
from app.users.forms import LoginForm, ChangePasswordForm, AddRolesForm, AddUserForms, UploadProfilePictureForm
from app.users.models import User, ProfileImage, Role, Permission, UserStatistics
from app.projects.models import Project
from app.users.helpers import Role_Determinator
from config import ADMIN

##from app.decorators.controllers import admin_required
from app import login_manager, oid, imageUploadSet

# @define - blueprint for users
Users = Blueprint('Users', __name__,)

# Initializing helper class for handling role modification
role_change = Role_Determinator()

## This enables permissions to run on all functions.
@Users.app_context_processor
def inject_permissions():
    ## If user hasn't no active role yet:

    if current_user.active_role is None:
        return dict(user_perms = current_user.init_active_roles(current_user.username),
                    user = current_user, role=current_user.load_roles(current_user.username))
    ## However, if there is an active role set:
    elif current_user.active_role == 'None':
        return dict(user_perms =[ ],
                    user = current_user, role=current_user.load_roles(current_user.username))

    return dict(user_perms = current_user.load_perms(current_user.active_role),
                    user = current_user,role=current_user.load_roles(current_user.username))

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

@Users.route('/admin/add_users', methods=['GET','POST'])
def add_users():
    form = AddUserForms(request.form)
    all_users = User.query.all()
    form.select_role.choices = [(role.id, role.name)        ## Loads up choices
                                for role in Role.query.all()] 
    ## load roles that had supervisor roles in it:
 

    form.select_supervisor.choices = [(user.username, user.username)
                                     for user in User.query.all() if user.is_supervisor]

    print form.select_role.choices 
    if form.validate_on_submit():
        password = generate_password_hash('seer')       
        u = User (form.fname.data,form.midname.data,form.lname.data,    ## Load user
                  form.email.data,form.username.data,password)
        print form.select_role.data

        for i in form.select_role.data:  ## Loads up the selected choices of the user
            print i 
            u.role.append(Role.query.get(i))
        print u.role

        ##Checks if the user is a supervisor
        if form.check_if_supervisor.data:
            u.is_supervisor = True

        ## Loads up the supervisor of the user, and loads up the user to its supervisor
        u.supervisor = form.select_supervisor.data
        print form.select_supervisor.data

        supervisor = User.query.filter_by(username=form.select_supervisor.data).first()
        if supervisor.supervisee is None or '': 
            
            supervisor.supervisee = u.username
            print supervisor.supervisee
        else:
            supervisor.supervisee = supervisor.supervisee + ' ' + u.username
            print supervisor.supervisee

        db_session.add(u)
        db_session.add(supervisor)
        db_session.commit()

        us = UserStatistics(userId=u.id)
        us.sl = form.number_of_sick_leaves.data
        us.vl = form.number_of_vacation_leaves.data
        us.offset = 0
        db_session.add(us)
        db_session.commit()
        flash('User Created')
        return redirect(url_for('Users.add_users'))
    return render_template('admin/add_user.html', form = form)

@Users.route('/delete_users/<user>', methods=['GET','POST'])
def delete_users(user):
    print user
    ## Checks if the user is an admin
    if current_user.is_admin(current_user.username):
        u = User.query.filter_by(username=user).first()
        us = UserStatistics.query.filter_by(userId=u.id).first()

        # loads the supervisor and deletes the user
        load_supervisor = u.supervisor
        supervisor = User.query.filter_by(username=load_supervisor).first()
        load_supervisees = supervisor.supervisee
        print "Load supervisee before split: " + str(load_supervisees)
        load_supervisees = load_supervisees.split(' ')
        print "Load supervisee after split: " + str(load_supervisees)
        load_supervisees.remove(u.username)
        supervisor.supervisee = ' '.join(load_supervisees)
        print supervisor.supervisee
        db_session.delete(u)
        db_session.add(supervisor)
        db_session.commit()
        flash('User Deleted')
        return redirect(url_for('Users.set_roles'))
    flash('USER UNAUTHORIZED')
    return redirect(url_for('Home.show_home'))
    

@Users.route('/admin/add_roles', methods=['GET','POST'])
def add_roles():
    form = AddRolesForm(request.form)
    admin = Permission.query.filter_by(permission_name='Administrator').first()
    types_of_permissions = Permission.query.all()
    types_of_permissions.remove(admin) ## Remove admin permission in assignment of permssions
    roles = Role.query.all()

    if request.method == 'POST':

        role = form.rolename.data
        rolename = str(role)
        print type(rolename)

        if rolename.isspace() or not rolename: ## Checks if the rolename is empty
            flash('Insert name!')
            return redirect(url_for('Users.add_roles'))

        for r in roles: ## Checks if the rolename is currently existing
            temp_role = str(r.name)
            if temp_role.lower() == rolename.lower(): ## Checks if the rolename has a lowercase/uppercase counterpart
                flash('Role Currently Exists!')
                return redirect(url_for('Users.add_roles'))

        ## Creation of roles proper
        r = Role(rolename)

        ## Assigns all permissions checked to the created role
        ## The loop checks each checkboxes if it was checked or not
        for p in types_of_permissions: 
            perm = p.permission_name
            get_val = request.form.get(str(perm))
            if get_val is not None:
                p = Permission.query.filter_by(permission_name=get_val).first()
                print p
                r.permissions.append(p)     
        print r.permissions
        db_session.add(r)
        db_session.commit()
        flash('Role Created')
        return redirect(url_for('Users.add_roles'))
    return render_template('admin/add_roles.html', form = form, types_of_permissions = types_of_permissions)

@Users.route('/delete_roles/<whatrole>', methods=['GET','POST'])
def delete_roles(whatrole):
    print whatrole
    if current_user.is_admin(current_user.username):
        role = Role.query.filter_by(name=whatrole).first()
        db_session.delete(role)
        db_session.commit()
        flash('Role deleted.')
        return redirect(url_for('Users.change_permissions'))
    flash('USER UNAUTHORIZED')
    return redirect(url_for('Home.show_home'))

@Users.route('/admin/set_roles', methods=['GET','POST'])
##@admin_required
def set_roles():
    all_users = User.query.all()
    roles = Role.query.all()

    ## FILTER SUPERADMIN USER
    for i in all_users:
        if i.username == ADMIN:
            all_users.remove(User.query.filter_by(username=ADMIN).first())


    if request.method == 'POST':

        ## This loop checks all the users and assign all the roles assigned by the administrator
        ## Like the previous checking loop, this loop does the same, checking each checkboxes, 
        ## and assign the checked values to the User roles.
        for user in all_users:
            u = User.query.filter_by(username=user.username).first()
            u.role = []
            for r in roles: 
                type = u.username + ' ' + r.name
                print type
                get_val = request.form.get(str(type))
                if get_val is not None:
                    erole = Role.query.filter_by(name=str(get_val)).first() ##Entered role
                    print 'ENTERED! ' + str(erole)
                    u.role.append(erole)
            print str(u.username) + ' ' + str(u.role)
            db_session.add(u)
            u.init_active_roles(u.username)
        db_session.commit()
        flash('Role changed.')
        return redirect(url_for('Users.set_roles'))
    return render_template('admin/set_roles.html', all_users=all_users, roles=roles, ADMIN=ADMIN)       


@Users.route('/admin/edit_permissions', methods=['GET','POST'])
##@admin_required
def change_permissions():
    ## This block filters the admin role and permissions

    all_users = User.query.all()
    list_of_roles = Role.query.all()
    list_of_perms = Permission.query.all()
    admin_role = Role.query.filter_by(name='Administrator').first()
    admin_perms = Permission.query.filter_by(permission_name='Administrator').first()
    list_of_roles.remove(admin_role)
    list_of_perms.remove(admin_perms)

    ## Endblock
    print list_of_perms
    if request.method == 'POST':        
        for roles in list_of_roles:
            role = Role.query.filter_by(name=roles.name).first()
            role.permissions = []
            for perms in list_of_perms: ## number of permissions
                type = roles.name + ' ' + perms.permission_name 
                print type
                get_val = request.form.get(str(type))
                if get_val is not None:
                    p = Permission.query.filter_by(permission_name=str(get_val)).first()
                    print 'ENTERED! ' + str(p)
                    role.permissions.append(p)
            print role.permissions
            db_session.add(role)
        db_session.commit()
        flash('Permissions changed.')
        return redirect(url_for('Users.change_permissions'))
    return render_template('admin/edit_permissions.html',list_of_roles=list_of_roles, 
                            list_of_perms=list_of_perms, all_users=all_users)

## This function changes the permissions upon entering the new role chosen by the user.
@Users.route('/change_active_role/<role>', methods=['GET','POST'])
def change_active_role(role):
    prev_role = Role.query.filter_by(name=current_user.active_role).first()
    r = Role.query.filter_by(name=role).first()
    if prev_role == r:
        return redirect(url_for('Home.show_home'))
    current_user.active_role = r.name
    flash('ACTIVE ROLE CHANGED')
    return redirect(url_for('Home.show_home'))


@Users.route('/profile/<user>', methods=['GET','POST'])
def profile(user):
    upload_picture_form = UploadProfilePictureForm(request.form)
    url_for_profile_picture = getProfilePicture()
    u = User.query.filter_by(username=user).first()
    us = UserStatistics.query.filter_by(userId=u.id).first()
    return render_template('users/profile.html', user = u, userleaves=us, upload_picture_form = upload_picture_form,
                            profile_picture=url_for_profile_picture)


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
    return render_template("users/change_password.html", form=form)

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



