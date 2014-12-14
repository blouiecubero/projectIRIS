from datetime import datetime
from flask import render_template, session,send_from_directory, redirect, url_for, current_app, flash, request
from . import main
from .forms import NameForm, EditProfileForm, PostForm, EditProfileAdminForm, EditUserNameForm, FinanceForm
from .. import db
from ..models import Permission, Role, User, Post
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

class Store_Image():
    filename = 'images.jpg'
    DictUsers = {'TestName':'testname'}
    name = 'TestName'
    
    def return_image(self, current_user):
        for i in self.DictUsers:
            if i == current_user:
                filename = self.DictUsers[i]
                return filename
        return 'images.jpg'

    def authenticate_user(self, current_user):
        for i in self.DictUsers:
            if i == current_user:
                return i
            else:
                return self.name

    def put_image(self,user, filename):
        self.DictUsers[user] = filename

class Store_File():
    filename = 'Nofile.html'
    DictUsers = {'None':'None as of now'}
    name = 'None'
    
    def return_file(self, current_user):
        for i in self.DictUsers:
            if i == current_user:
                filename = self.DictUsers[i]
                return filename
        return 'Nofile.html'
            

    def put_file(self,user, filename):
        self.DictUsers[user] = filename

    

store = Store_Image()
financials = Store_File()

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
    filename = 'http://127.0.0.1:5000/uploads/' + store.return_image(current_user.username)
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', form=form, posts=posts, filename=filename)


@main.route('/user/<username>')
def user(username):
    if Exception:
        filename = 'images.jpg'
    user = User.query.filter_by(username=username).first()
    store.name = username
    store.filename = store.return_image(username)
    financials.name = username
    financials.filename = financials.return_file(username)
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    filename = 'http://127.0.0.1:5000/uploads/' + store.return_image(username)
    financefile = financials.return_file(username)
    finance = 'http://127.0.0.1:5000/uploads/' + financials.return_file(username)
    return render_template('user.html', user=user,posts=posts, filename=filename, financefile=financefile, finance= finance)

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
    user = current_user.username
    if request.method == 'POST':
##        print 'saving'
##        save(request.files['upload'])
##        return redirect(url_for('.user', username = user))
        file = request.files['upload']
        if file and allowed_pic(file.filename):
            filename = secure_filename(file.filename)
            store.filename = filename
            store.name = current_user.username
            store.put_image(store.name, store.filename)
            file.save(os.path.join(c.PICTURE_FOLDER, filename))
            return redirect(url_for('.user', username=user))
    return render_template('upload_picture.html')


##@main.route('/delete-picture/<int:id>', methods=['GET', 'POST'])
##@login_required
##def remove(id):
##    """Delete an uploaded file."""
##    upload = Upload.query.get_or_404(id)
##    delete(upload)
##    return redirect(url_for('index'))


@main.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(c.UPLOAD_FOLDER, filename)

@main.route('/upload-finance', methods = ['GET', 'POST'])
@login_required
@admin_required
def upload_finance():
    user = User.query.all()
    if request.method == 'POST':
        file = request.files['upload']
        wcuser = request.form['users']
        if file and allowed_files(file.filename):
            filename = secure_filename(file.filename)
            financials.filename = filename
            financials.name = wcuser
            file.save(os.path.join(c.FILES_FOLDER, filename))
            financials.put_file(financials.name, financials.filename)
            user = current_user.username
            return redirect(url_for('.user', username=user))
    return render_template('upload_finance.html', userquery=user)



