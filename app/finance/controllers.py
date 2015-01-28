import os.path
import random
import requests
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, current_app, send_from_directory
from flask.ext.login import login_user , logout_user , current_user , login_required
from flask.ext.uploads import UploadSet, IMAGES, configure_uploads
from werkzeug import secure_filename
from app.database import db_session, Base,init_db
from app.projects.models import Project
from app.users.models import Payslip, User, Permission
from app import login_manager, oid, imageUploadSet
from app.finance.helpers import Store_Users, FileChecker
from app.finance.forms import UploadFileForm
from config import UPLOADS_FILES_DEST
from sqlalchemy.exc import DatabaseError, IntegrityError
from app.decorators.controllers import admin_required,upload_permission_required, HR_required, view_files_required

PaySlip = Blueprint('PaySlip', __name__,)

## This enables permissions to run on all functions.
@PaySlip.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

# Initializing class for temporary storage
store_user = Store_Users()
check_file_ext = FileChecker()
# @function - Used to add an object to a database [Could be move to another class to make this more reusable by other objects]
def add_to_db(object):
    try:
        db_session.add(object)
        db_session.flush()
        return True
    except sqlalchemy.exc.IntegrityError as err:
        print "IntegrityError"
        db_session.rollback()
        return False

# @function - Shows and uploads files for a specified user
@PaySlip.route('/payslip', methods=['GET', 'POST'])
@view_files_required
def payslip_base():
    all_users = User.query.all()
    whosuser = store_user.check_if_none()
    upload_file_form = UploadFileForm(request.form)
    chosen_user = User.query.filter_by(username=whosuser).first() #Finds the user that was chosen by the admin
    finance = Payslip.query.filter_by(user = chosen_user.username).order_by(Payslip.date.desc()).all() #Loads up the files of the chosen_user
    present_user = User.query.filter_by(username=current_user.username).first() #Loads up the present user
    files_of_the_current_user = Payslip.query.filter_by(user = present_user.username).order_by(Payslip.date.desc()).all() # Loads up the files of the present user
    if request.method == 'POST':
        wcuser = request.form['users']          
        store_user.store(wcuser)                # it loads up the chosen user
        return redirect(url_for('.payslip_base'))  # and it will load back to the admin page with the new chosen user.
    
    return render_template('finance/home.html',user=current_user,files_of_the_current_user=files_of_the_current_user, whosuser = whosuser, filebase=finance, upload_file_form=upload_file_form, all_users=all_users)

@PaySlip.route('/upload_payslip', methods=['GET','POST'])
@upload_permission_required
def upload_payslip():
    if request.method == 'POST' and 'files' in request.files:
        file = request.files['files']
        wcuser = request.form['users']
        print wcuser
        userid = User.query.filter_by(username=wcuser).first()
        if file and check_file_ext.allowed_files(file.filename):
            filename = secure_filename(file.filename)        
            user = Payslip(user = userid.username, filename = filename)
            print user
            file.save(os.path.join(current_app.config['UPLOADS_FILES_DEST'], filename))  # Then it saves the file to the file storage address defined from the config.py
            #DONT FORGET TO UPDATE is_active
            if(add_to_db(user)):
                db_session.commit()
                flash("Payslip Uploaded.")
    return redirect(url_for('PaySlip.payslip_base')+"#uploadComplete")

@PaySlip.route('/delete-payslip/<file_name>', methods=['GET', 'POST'])
def delete_payslip(file_name):
    user = Payslip.query.filter_by(filename=file_name).first()                           # Checks the filename to be deleted
    db_session.delete(user)
    db_session.commit()# and poof
    os.remove(current_app.config['UPLOADS_FILES_DEST'] +'\\'+ file_name)                   # Remove it also from its storage
    return redirect(url_for('.payslip_base'))

@PaySlip.route('/uploads/payslip/<filename>')
def send_file(filename):
    ## This function loads up the file to the browser. Thanks to this, we can see uploaded pictures in the webpage.
    return send_from_directory(current_app.config['UPLOADS_FILES_DEST'], filename)
