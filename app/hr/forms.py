# Forms for leave application

from flask.ext.wtf import Form
from wtforms import TextField, SubmitField
# from flask.ext.login import login_user , logout_user , current_user , login_required
# from wtforms.validators import Required
# from models import db, User, UserStatistics


class datePicking(Form):
	sickDateField = TextField('Pick dates for leave') #, format = '%m/%d/%y')
	vacationDateField = TextField('Pick dates for leave')
	offsetDateField = TextField('Pick dates for leave')
	submitButton = SubmitField('Submit')

	# Parse date then return the number of days
	def dateParser(self, event):
		toString = str(event)

		parsedSickLeave = len(toString.split(';'))
		return parsedSickLeave

		# if not toAddOnCount:
		# 	parsedSickLeave = toString.split(';')
		# 	return parsedSickLeave