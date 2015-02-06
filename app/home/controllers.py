from flask import Blueprint, Response , request, render_template, \
                flash, g, session, redirect, url_for, \
				jsonify, json, abort, make_response

from flask.ext.login import login_user , logout_user , current_user , login_required
from app.users.forms import UploadProfilePictureForm
from app.users.models import User, Payslip, Permission
import datetime
from app.users.controllers import getProfilePicture, getUtilization


# @define - blueprint for home
Home = Blueprint('Home', __name__,)

## This enables permissions to run in every template.
@Home.app_context_processor
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


# @function - Renders the home page
@Home.route('/')
@Home.route('/home')
@login_required
def show_home():
	print "Home"
	upload_picture_form = UploadProfilePictureForm(request.form)
	url_for_profile_picture = getProfilePicture()
##	utilizationProject = getUtilization(current_user)Permission=Permission
	print url_for_profile_picture
##	file_owner = User.query.filter_by(username=current_user.username).first()
##        all_users = User.query.all() # Loads up all the registered users.
	return render_template('home/home.html',user=current_user,upload_picture_form=upload_picture_form, \
		 profile_picture=url_for_profile_picture)


# @function - appends feedbacks to text file [this should be saved on a more organized storage]
@Home.route('/feedback',methods=['GET','POST'])
@login_required
def saveFeedback():
	if request.method == 'POST':
		print request.form['feedback']
		with open("feedback.txt", "a") as feedbackFile:
                        date = datetime.date.today()
                        feedbackFile.write(current_user.username+ ','+ '"'+date.isoformat() +'",')
			feedbackFile.write('"'+request.form['feedback']+'"'+"\n")
		return redirect(url_for('Home.show_home'))


@Home.route('/dl_feedback',methods=['GET','POST'])
@login_required
def downloadFeedback():
    file = open('feedback.txt')
    csv = file.read()
    response = make_response(csv)
    response.headers["Content-Disposition"] = "attachment; filename=feedbacks.csv"
    return response



#@Home.route('/sync')
@login_required
def sync_data(user):
	url='http://www.seerlabs.com:5556/api/getProject'
	payload = {'email': 'claudine.bael@seer-technologies.com'}
	response = requests.post(url, data=payload)
	responseJson = response.json()
	print(responseJson['projects'][0])

	#http://www.seerlabs.com:5556/api/getUtilization
	#http://www.seerlabs.com:5556/api/postNewsfeed
	#http://www.seerlabs.com:5556/api/getNewsfeed
	#http://www.seerlabs.com:5556/api/getProject
