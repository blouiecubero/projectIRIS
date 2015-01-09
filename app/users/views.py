import os
import sys 
from .. import db
from . import users
from .helpers import FileChecker
from ..models import User, FileBase
from werkzeug import secure_filename
from .forms import EditProfileForm, EditUserNameForm
from flask.ext.login import login_required, current_user
from flask import render_template, session,send_from_directory, redirect, url_for, current_app, flash, request

## Initializing classes
check_file_ext = FileChecker()

@users.route('/', methods=['GET', 'POST'])
@login_required
def user():

    ## This is the function for loading up user's profiles. The user can just view the files
    ## that the admin uploaded to their account. There are repeated algorithm here from the
    ## admin profile. Specifically, the loading of the user, checking of picture and displaying
    ## the files.
    
    if current_user.is_administrator(): # redirects the admin to the admin profile page.
        return redirect(url_for('admin.admin_user'))
    
    ## This is the same code from the admin profile page.
    user = User.query.filter_by(username=current_user.username).first()
    if user.picture is None:
        user.picture = 'images.jpg'
    if user is None:
        abort(404)
    finance = user.stored_file.order_by(FileBase.date.desc()).all()
    return render_template('users/user.html', user=user, filename=user.picture, finance = finance, whosuser = user.username)

@users.route('/edit-profile', methods=['GET','POST'])
@login_required
def edit_profile():

    ## The reason for this feature is to establish uniqueness and to provide more information regarding the user.
    
    form = EditProfileForm()
    
    if form.validate_on_submit(): # If the user submitted all the entered data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)    # It loads the provided entries to the db.
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))

    # Loads up all the former data before submitting.
    form.name.data= current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('users/edit_profile.html', form=form)

@users.route('/edit-username', methods=['GET','POST'])
@login_required
def edit_username():

    ## There may be cases that the user must change it's username for consistency. E.g Marriage
    ## Therefore, this feature was integrated.
    
    form = EditUserNameForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.add(current_user)
        flash('Your username has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.username.data= current_user.username
    return render_template('users/edit_username.html', form=form)
    

@users.route('/edit-picture/', methods=['GET', 'POST'])
@login_required
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
            return redirect(url_for('.user', username=user.username))
    return render_template('users/upload_picture.html')
    

@users.route('/uploads/photos/<filename>')
def send_photo(filename):
    ## This function loads up the file to the browser. Thanks to this, we can see uploaded pictures in the webpage.
    return send_from_directory(current_app.config['PICTURE_FOLDER'], filename)

@users.route('/uploads/files/<filename>')
def send_file(filename):
    ## Has the same reason from the former, however to provide organization, files and pictures were categorized. Therefore, this.
    return send_from_directory(current_app.config['FILES_FOLDER'], filename)
