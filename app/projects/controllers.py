# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
from flask.ext.login import login_user , logout_user , current_user , login_required
from app.database import db_session, Base
from app import login_manager, oid


# @define - blueprint for projects
Projects = Blueprint('Projects', __name__,)

# @function - Assigns current user to g
@Projects.before_request
def before_request():
    g.user = current_user


# @function - Renders the project page
@Projects.route('/project')
def show_project():
	return render_template('project.html')
