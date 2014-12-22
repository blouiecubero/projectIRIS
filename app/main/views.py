from datetime import datetime
from flask import render_template, session,send_from_directory, redirect, url_for, current_app, flash, request
from . import main
from .forms import NameForm, EditProfileForm, PostForm, EditProfileAdminForm, EditUserNameForm, FinanceForm
from .. import db
from ..models import Permission, Role, User, Post, FileBase
from flask.ext.login import login_user, logout_user, login_required, current_user
from ..decorators import admin_required
from werkzeug import secure_filename
import os
from config import Config
from flask.ext.storage import get_default_storage_class
from flask.ext.uploads import init
from flask.ext.uploads import delete, save, Upload
import sys
c = Config()

ALLOWED_PICTURES = set(['png', 'jpg', 'jpeg', 'gif', 'JPG', 'ico'])
ALLOWED_DOCUMENTS = set(['pdf','PDF'])

def allowed_pic(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_PICTURES

def allowed_files(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_DOCUMENTS

@main.route('/', methods=['GET', 'POST'])
def homepage():
    return render_template('home.html')


@main.route('/index', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.picture is None:
        current_user.picture = 'images.jpg'
    picture = 'http://127.0.0.1:5000/uploads/photos/' + current_user.picture
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', form=form, posts=posts, filename=picture)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user.picture is None:
        user.picture = 'images.jpg'
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    picture = 'http://127.0.0.1:5000/uploads/photos/' + user.picture
    return render_template('user.html', user=user,posts=posts, filename=picture)

@main.route('/edit-profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data= current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@main.route('/edit-username', methods=['GET','POST'])
@login_required
def edit_username():
    form = EditUserNameForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.add(current_user)
        flash('Your username has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.username.data= current_user.username
    return render_template('edit_username.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
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
        return redirect(url_for('.user', username = user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)
    

@main.route('/edit-picture/', methods=['GET', 'POST'])
@login_required
def upload_picture():
    user = User.query.filter_by(username=current_user.username).first()
    if request.method == 'POST':
        file = request.files['upload']
        if file and allowed_pic(file.filename):
            filename = secure_filename(file.filename)
            user.picture = filename
            file.save(os.path.join(c.PICTURE_FOLDER, filename))
            db.session.add(user)
            return redirect(url_for('.user', username=user.username))
    return render_template('upload_picture.html')

@main.route('/upload-finance', methods = ['GET', 'POST'])
@login_required
@admin_required
def upload_finance():
    user = User.query.all()
    if request.method == 'POST':
        file = request.files['upload']
        wcuser = request.form['users']
        desc = request.form['description']
        if file and allowed_files(file.filename):
            file_name = secure_filename(file.filename)
            userid = user = User.query.filter_by(username=wcuser).first()
            user = FileBase(owner = userid, filename = file_name, description = desc)
            db.session.add(user)
            file.save(os.path.join(c.FILES_FOLDER, file_name))
            return redirect(url_for('.user', username=current_user.username))
    return render_template('upload_finance.html', userquery=user)

@main.route('/filebase-user/', methods=['GET', 'POST'])
@login_required
def list_of_finance():
    user = User.query.filter_by(username=current_user.username).first()
    finance = user.stored_file.order_by(FileBase.date.desc()).all()
    return render_template('_filebase.html', finance = finance)
    

@main.route('/uploads/photos/<filename>')
def send_photo(filename):
    return send_from_directory(c.PICTURE_FOLDER, filename)

@main.route('/uploads/files/<filename>')
def send_file(filename):
    return send_from_directory(c.FILES_FOLDER, filename)



