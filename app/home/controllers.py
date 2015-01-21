from flask import Blueprint, Response , request, render_template, \
                flash, g, session, redirect, url_for, \
				jsonify, json, abort, make_response

from flask.ext.login import login_user , logout_user , current_user , login_required
from app.users.forms import UploadProfilePictureForm
from app.users.models import User, FileBase
from app.users.controllers import getProfilePicture, getUtilization


# @define - blueprint for home
Home = Blueprint('Home', __name__,)


# @function - Renders the home page
@Home.route('/')
@Home.route('/home')
@login_required
def show_home():
	print "Home"
	upload_picture_form = UploadProfilePictureForm(request.form)
	url_for_profile_picture = getProfilePicture()
##	utilizationProject = getUtilization(current_user)
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
			feedbackFile.write(request.form['feedback']+"\n\n")
		return redirect(url_for('Home.show_home'))

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
