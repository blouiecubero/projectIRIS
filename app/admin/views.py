import os
from .. import db
from . import admin
from werkzeug import secure_filename
from .forms import EditProfileAdminForm
from ..models import Role, User, FileBase
from .helpers import Store_Users, FileChecker
from app.decorators.decorators import admin_required
from flask.ext.login import login_required, current_user
from flask import render_template, session,send_from_directory, redirect, url_for, current_app, flash, request


## Initializing classes
store_user = Store_Users()
check_file_ext = FileChecker()

@admin.route('/admin-user', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_user():

    ## This code runs the functions of an admin role. It checks the files of
    ## the registered users, uploads files to certain users and deletes the files
    ## of certain users.
    
    user_file = store_user.check_if_none() # Checks the current user in the selection field. (initialized as an admin from the start of the program)
    user = User.query.filter_by(username=current_user.username).first() 
    file_owner = User.query.filter_by(username=user_file).first() #Finds the user that was chosen by the admin 
    all_users = User.query.all() # Loads up all the registered users.
    
    if user.picture is None: # Checks if the user has no image yet.
        user.picture = 'images.jpg'
    if user is None: # This might be a possibility. Kept it here if something might go wrong.
        abort(404)

    finance = file_owner.stored_file.order_by(FileBase.date.desc()).all() # Loads up all the file that were uploaded to the chosen user.

    
    if request.method == 'POST':
        
        # There will be two kinds of request here, since in the template, there'll be two submit buttons.
        
        if request.form['button'] == 'Choose User': # If the admin clicked the "Choose User" button,
            wcuser = request.form['users']          
            store_user.store(wcuser)                # it loads up the chosen user
            return redirect(url_for('.admin_user')) # and it will load back to the admin page with the new chosen user.
        
        elif request.form['button'] == 'Upload':    # If the admin wants to upload a file,
            file = request.files['upload']          # Gets the file
            wcuser = request.form['users']          # Gets who's user will be the recipient of the file.
            desc = request.form['description']      # Gets the description.
            if file and check_file_ext.allowed_files(file.filename): # checks if the file is allowed to upload
                file_name = secure_filename(file.filename)
                userid = User.query.filter_by(username=wcuser).first() # Looks up for the recipient of the file
                user = FileBase(owner = userid, filename = file_name, description = desc) # Defines the file, the owner of the file, and its description
                db.session.add(user)    # And executes a command to store it.
                file.save(os.path.join(current_app.config['FILES_FOLDER'], file_name))  # Then it saves the file to the file storage address defined from the config.py
                return redirect(url_for('.admin_user')) 

        #Footnote: I didn't used WTForms here since I find it complex to use. Therefore I just sticked my guns to the old and manual way of uploading files. 
        
    return render_template('admin/user.html', user=user, filename=user.picture,finance = finance, all_users=all_users, whosuser = user_file)

@admin.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    
    ## The admin has the right to change the information provided by user. This feature
    ## was made to rectify errors provided by the user or provide updated information.
    ## It also has the ability to make users admin if they want to.
    
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.admin_user', username = user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('admin/edit_profile.html', form=form, user=user)

@admin.route('/delete-file/<file_name>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_file(file_name):
    user = FileBase.query.filter_by(filename=file_name).first() # Checks the filename to be deleted
    db.session.delete(user)                                     # and poof
    os.remove(current_app.config['FILES_FOLDER'] +'/'+ file_name)                   # Remove it also from its storage
    return redirect(url_for('.admin_user', username=current_user.username))

@admin.route('/edit-picture/', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_picture():

    ## The algorithm of this code is just the same as uploading a file from the admin_user function.
    ## The only difference is the user is the only one that can upload the picture.
    
    user = User.query.filter_by(username=current_user.username).first()
    if request.method == 'POST':
        file = request.files['upload']
        if file and check_file_ext.allowed_pic(file.filename):
            filename = secure_filename(file.filename)
            user.picture = filename
            file.save(os.path.join(current_app.config['PICTURE_FOLDER'], filename))
            db.session.add(user)
            return redirect(url_for('.admin_user'))
    return render_template('admin/upload_picture.html')
