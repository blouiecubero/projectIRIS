# controllers / URL Mapping
# URL Mapping

from flask import Blueprint, render_template, request, redirect, url_for, g, session,flash,current_app
from datetime import date
from flask.ext.login import current_user
from app.database import db_session, Base, init_db
from app.users.models import User, UserStatistics
from app.hr.forms import datePicking
from app.finance.helpers import Store_Users
from jinja2 import Environment, FileSystemLoader
# from forms import signIn, datePicking, dummy
# from app import app
# from models import db, User, UserStatistics, Dummy
HR = Blueprint('HR', __name__,)
store_user = Store_Users()






@HR.route('/leaves', methods=['GET', 'POST'])
def leaves():
	form = datePicking() # datePicking class
	g.user = current_user
	dbQuery = UserStatistics.query.filter_by(userId = g.user.id).first() # get current_user ID
	print dbQuery
	all_users = User.query.all()
	
	userQuery = store_user.check_if_none() 
	userQuery_id = User.query.filter_by(username = userQuery).first() # get ID
	
	statQuery = UserStatistics.query.filter_by(userId = userQuery_id.id).first() # get statistics

	# Output leave dates 
	if not dbQuery:
		user = User.query.filter_by(username=current_user.username).first()
		us = UserStatistics(userId=user.id, sl=15, vl=15)
		print us
		db_session.add(us)
		db_session.commit()
		dbQuery = UserStatistics.query.filter_by(userId = g.user.id).first()	

	# if user has applied for leave
	if request.method == 'POST':

		####### FOR SICK LEAVE ############

		if request.form.get('submitSl', None) == "submitSl":
			addDate = request.form.get('sickDateField')

			## Checkis if the date given was blank.
			if not addDate:
				flash('Please give a specific date.')
				return redirect(url_for('.leaves'))

			
			## Checks if the date entered is already existing
			slList = dbQuery.slDates
			print '\n\n***** SLDATES BASIS 1 ******\n\n :' + str(slList) +'\n\n'
			slListRecord = dbQuery.slDatesRecord
			print '\n\n***** SLDATES RECORD 1 ******\n\n :' + str(slListRecord) + '\n\n'

			if slList is None:
				dbQuery.slDates = {}
				dbQuery.slDatesRecord = {}
				slList = {}
			vlList = dbQuery.vlDates
			vlListRecord = dbQuery.vlDatesRecord
			if vlList is None:
				dbQuery.vlDates = {}
				dbQuery.vlDatesRecord = {}
				vlList = {}
			offsetDates = dbQuery.offsetDates
			offsetDatesRecord = dbQuery.offsetDatesRecord
			if offsetDates is None:
				dbQuery.offsetDates = {}
				offsetDates = {}
				offsetDatesRecord = {}

			check = check_if_existing(slList,vlList,offsetDates,addDate)

			if check:
				flash('Date already picked. Please check your chosen dates again.')
				return redirect(url_for('.leaves'))

			if check_number_of_leaves(current_user.username, addDate, dbQuery.sl, 'sickleave'):
				flash('Insufficient number of days applied.')
				return redirect(url_for('.leaves'))

			dateToAppend = str(addDate)

			slList[dateToAppend] = 0
			print '\n\n***** SLDATES BASIS 2******\n\n:' + str(slList)+'\n\n'
			slListRecord[dateToAppend] = 0
			print '\n\n***** SLDATES RECORD 2 ******\n\n :' + str(slListRecord)+'\n\n'

			dbQuery.slDates = slList
			dbQuery.slDatesRecord = slListRecord
			print '\n\n***** DBQUERY SLDATES BASIS 3 ******\n\n:' + str(dbQuery.slDates)+'\n\n'
			print '\n\n***** DBQUERY SLDATES RECORD 3 ******\n\n :' + str(dbQuery.slDatesRecord)+'\n\n'

			## Record the date when the leave is applied
			slListPendingDate = dbQuery.slDatesAppliedDates
			if slListPendingDate is None:
				slListPendingDate = {}
				today = date.today()
		
				slListPendingDate[dateToAppend] = today.strftime('%m-%d-%y')
				print slListPendingDate
				dbQuery.slDatesAppliedDates = slListPendingDate

			today = date.today()
			slListPendingDate[dateToAppend] = today.strftime('%m-%d-%y')
			print slListPendingDate
			dbQuery.slDatesAppliedDates = slListPendingDate


			db_session.add(dbQuery)
			db_session.commit()
			flash('Sick Leave Application submitted.')
			return redirect(url_for('.leaves'))

		########### FOR VACATION LEAVE ############
		elif request.form.get('submitVl', None) == "submitVl":
			addDate = request.form.get('vacationDateField')
			## Checkis if the date given was blank.
			if not addDate:
				flash('Please give a specific date.')
				return redirect(url_for('.leaves'))
				
		
			## Checks if the date entered is already existing
			slList = dbQuery.slDates
			slListRecord = dbQuery.slDatesRecord
			if slList is None:
				dbQuery.slDates = {}
				dbQuery.slDatesRecord = {}
				slList = {}
			vlList = dbQuery.vlDates
			vlListRecord = dbQuery.vlDatesRecord
			if vlList is None:
				dbQuery.vlDates = {}
				dbQuery.vlDatesRecord = {}
				vlList = {}
			offsetDates = dbQuery.offsetDates
			offsetDatesRecord = dbQuery.offsetDatesRecord
			if offsetDates is None:
				dbQuery.offsetDates = {}
				offsetDates = {}
				offsetDatesRecord = {}

			check = check_if_existing(slList,vlList,offsetDates,addDate)
			if check:
				flash('Date already picked. Please check your chosen dates again.')
				return redirect(url_for('.leaves'))

			if check_number_of_leaves(current_user.username, addDate, dbQuery.vl, 'vacationleave'):
				flash('Insufficient number of days applied.')
				return redirect(url_for('.leaves'))

			dateToAppend = str(addDate)
			vlList[dateToAppend] = 0
			vlListRecord[dateToAppend] = 0

			dbQuery.vlDates = vlList
			dbQuery.vlDates = vlListRecord
			print 'VLDATES BASIS :' + str(dbQuery.vlDates)
			print 'VLDATES RECORD :' + str(dbQuery.vlDatesRecord)

			## Record the date when the leave is applied
			vlListPendingDate = dbQuery.vlDatesAppliedDates
			if vlListPendingDate is None:
				vlListPendingDate = {}
				today = date.today()
				vlListPendingDate[dateToAppend] = today.strftime('%m-%d-%y')
				print vlListPendingDate
				dbQuery.vlDatesAppliedDates = vlListPendingDate

			today = date.today()
			vlListPendingDate[dateToAppend] = today.strftime('%m-%d-%y')
			print vlListPendingDate
			dbQuery.vlDatesAppliedDates = vlListPendingDate

			db_session.add(dbQuery)
			db_session.commit()
			flash('Vacation Leave Application submitted.')
			return redirect(url_for('.leaves'))

		###############FOR OFFSET DATES #############
		elif request.form.get('submitOd', None) == "submitOd":
			addDate = request.form.get('offsetDateField')
			print addDate
			## Checkis if the date given was blank.
			if not addDate:
				flash('Please give a specific date.')
				return redirect(url_for('.leaves'))

			slList = dbQuery.slDates
			slListRecord = dbQuery.slDatesRecord
			if slList is None:
				dbQuery.slDates = {}
				dbQuery.slDatesRecord = {}
				slList = {}
			vlList = dbQuery.vlDates
			vlListRecord = dbQuery.vlDatesRecord
			if vlList is None:
				dbQuery.vlDates = {}
				dbQuery.vlDatesRecord = {}
				vlList = {}
			offsetDates = dbQuery.offsetDates
			offsetDatesRecord = dbQuery.offsetDatesRecord
			if offsetDates is None:
				dbQuery.offsetDates = {}
				offsetDates = {}
				offsetDatesRecord = {}

			check = check_if_existing(slList,vlList,offsetDates,addDate)
			if check:
				flash('Date already picked. Please check your chosen dates again.')
				return redirect(url_for('.leaves'))

			if check_number_of_leaves(current_user.username, addDate, dbQuery.offset, 'offset'):
				flash('Insufficient number of days applied.')
				return redirect(url_for('.leaves'))

			dateToAppend = str(addDate)
			offsetDates[dateToAppend] = 0
			offsetDatesRecord[dateToAppend] = 0
			dbQuery.offsetDates = offsetDates
			dbQuery.offsetDatesRecord = offsetDatesRecord

			## Record the date when the leave is applied
			offsetListPendingDate = dbQuery.offsetDatesAppliedDates
			if offsetListPendingDate is None:
				offsetListPendingDate = {}
				today = date.today()
				offsetListPendingDate[dateToAppend] = today.strftime('%m-%d-%y')
				print offsetListPendingDate
				dbQuery.offsetDatesAppliedDates = offsetListPendingDate

			today = date.today()
			offsetListPendingDate[dateToAppend] = today.strftime('%m-%d-%y')
			print offsetListPendingDate
			dbQuery.offsetDatesAppliedDates = offsetListPendingDate

			db_session.add(dbQuery)
			db_session.commit()
			flash('Offset Dates Application submitted.')
			return redirect(url_for('.leaves'))

		
		elif request.form.get('submitOffsetDays', None) == "submitOffsetDays":
			num_of_days = request.form.get('quantity')
			dbQuery.proposed_offset = int(num_of_days)
			db_session.add(dbQuery)
			db_session.commit()
			print 'NUMBER OF OFFSET DAYS APPLIED' + str(num_of_days)
			flash('Number of offset days confirmed.')
			return redirect(url_for('.leaves'))

	return render_template('hr/leaves.html',
							user=current_user,
							form=form,
							leaveData=dbQuery,		
							) 

# ==========================================================================
@HR.route('/check_if_existing', methods=['GET', 'POST'])
def check_if_existing(dict1, dict2, dict3, input):

	## LOAD ALL DATES
	lod1 = dict1.keys()
	lod2 = dict2.keys()
	lod3 = dict3.keys()
	lod = lod1 + lod2 + lod3
	print 'LOD: '+str(lod)
	## THEN COMPARE
	for a in lod:
		compare = a.split(';')
		print 'COMPARE: '+str(compare)
		add= input.split(';')
		print 'ADD: '+str(add)
		for a in add:
			## If a date was found identical, return true
			if a in compare:
				return True
			

@HR.route('/check_number_of_leaves/<user>/<dates>/<days_remaining>/<what_leave>', methods=['GET', 'POST'])
def check_number_of_leaves(user, date, days_remaining, what_leave):
	u = User.query.filter_by(username=user).first()
	us = UserStatistics.query.filter_by(userId=u.id).first()
	days = date.split(';')
	num_of_days = len(days)
	if what_leave == 'sickleave':
		if us.sl < num_of_days:
			return True
		else:
			return False
	elif what_leave == 'vacationleave':
		if us.vl < num_of_days:
			return True
		else:
			return False
	elif what_leave == 'offset':
		if us.offset < num_of_days:
			return True
		else:
			return False
			

# ==========================================================================

## CONFIRMING FUNCTIONS
@HR.route('/confirm_sickLeave/<confdate>/<user>/<decision>', methods=['GET', 'POST'])
def confirm_sickLeave(confdate,user,decision):
	print confdate
	print user
	u = User.query.filter_by(username=user).first()
	print u
	us = UserStatistics.query.filter_by(userId=u.id).first()
	temp = us.slDates
	temprecord = us.slDatesRecord
	print temp
	dates = temp.keys()
	print dates
	for a in dates:
		print a
		print confdate
		if a == confdate:
			print decision
			if decision == "confirm":
				temp[confdate] = 1
				temprecord[confdate] = 1
				us.slDates = temp
				us.slDatesRecord = temprecord
				print us.slDates
				num_of_days = confdate.split(';')
				subtract = len(num_of_days)
				us.sl = us.sl - subtract
				print us.sl

				## Record the date when the leave is applied
				slListConfirmedDate = us.slDatesDecidedDates
				if slListConfirmedDate is None:
					slListConfirmedDate = {}
					today = date.today()
					slListConfirmedDate[confdate] = today.strftime('%m-%d-%y')
					print slListConfirmedDate
					us.slDatesDecidedDates = slListConfirmedDate

				else:
					today = date.today()
					slListConfirmedDate[confdate] = today.strftime('%m-%d-%y')
					print slListConfirmedDate
					us.slDatesDecidedDates = slListConfirmedDate

				db_session.add(us)
				db_session.commit()
				flash('Date Confirmed.')
				return redirect(url_for('.approval_of_leaves'))

			if decision == "deny":
				temprecord[confdate] = 2
				us.slDatesRecord = temprecord
				print 'SLDATES RECORD AFTER DENYING (FIRST RUN): ' + str(us.slDatesRecord)
				print 'sickleave' 
				dates = us.slDates
				print dates
				del dates[confdate]
				
				us.slDates = dates
				print us.slDates
				print 'SLDATES RECORD AFTER DENYING: ' + str(us.slDatesRecord)
				print 'SLDATES BASIS AFTER DENYING: ' + str(us.slDates)
				## Record the date when the leave is applied

				slListConfirmedDate = us.slDatesDecidedDates
				if slListConfirmedDate is None:
					slListConfirmedDate = {}
					today = date.today()
					slListConfirmedDate[confdate] = today.strftime('%m-%d-%y')
					print slListConfirmedDate
					us.slDatesDecidedDates = slListConfirmedDate

				else:
					today = date.today()
					slListConfirmedDate[confdate] = today.strftime('%m-%d-%y')
					print slListConfirmedDate
					us.slDatesDecidedDates = slListConfirmedDate

				db_session.add(us)
				db_session.commit()
				flash('Date Denied.')
				return redirect(url_for('.approval_of_leaves'))
	
@HR.route('/confirm_vacationLeave/<confdate>/<user>/<decision>', methods=['GET', 'POST'])
def confirm_vacationLeave(confdate,user,decision):
	print confdate
	print user
	u = User.query.filter_by(username=user).first()
	print u
	us = UserStatistics.query.filter_by(userId=u.id).first()
	temp = us.vlDates
	temprecord = us.vlDatesRecord
	print temp
	dates = temp.keys()
	print dates
	for a in dates:
		print a
		print confdate
		if a == confdate:
			print decision
			if decision == "confirm":
				temp[confdate] = 1
				temprecord[confdate] = 1
				us.vlDates = temp
				us.vlDatesRecord = temprecord
				print us.vlDates
				num_of_days = confdate.split(';')
				subtract = len(num_of_days)
				us.vl = us.vl - subtract
				print us.vl

				vlListConfirmedDate = us.vlDatesDecidedDates
				if vlListConfirmedDate is None:
					vlListConfirmedDate = {}
					today = date.today()
					vlListConfirmedDate[confdate] = today.strftime('%m-%d-%y')
					print vlListConfirmedDate
					us.vlDatesDecidedDates = vlListConfirmedDate

				else:
					today = date.today()
					vlListConfirmedDate[confdate] = today.strftime('%m-%d-%y')
					print vlListConfirmedDate
					us.vlDatesDecidedDates = vlListConfirmedDate

				db_session.add(us)
				db_session.commit()
				flash('Date Confirmed.')
				return redirect(url_for('.approval_of_leaves'))
			if decision == "deny":
				temprecord[confdate] = 2
				us.vlDatesRecord = temprecord
				print 'VLDATES RECORD AFTER DENYING (FIRST RUN): ' + str(us.vlDatesRecord)
				print 'sickleave'
				dates = us.vlDates
				print dates
				del dates[confdate]
				
				us.vlDates = dates
				print us.vlDates
				
				print 'VLDATES RECORD AFTER DENYING: ' + str(us.vlDatesRecord)
				print 'VLDATES BASIS AFTER DENYING: ' + str(us.vlDates)

				vlListConfirmedDate = us.vlDatesDecidedDates
				if vlListConfirmedDate is None:
					vlListConfirmedDate = {}
					today = date.today()
					vlListConfirmedDate[confdate] = today.strftime('%m-%d-%y')
					print vlListConfirmedDate
					us.vlDatesDecidedDates = vlListConfirmedDate

				else:
					today = date.today()
					vlListConfirmedDate[confdate] = today.strftime('%m-%d-%y')
					print vlListConfirmedDate
					us.vlDatesDecidedDates = vlListConfirmedDate

				db_session.add(us)
				db_session.commit()
				flash('Date Denied.')
				return redirect(url_for('.approval_of_leaves'))

@HR.route('/confirm_offsetDates/<confdate>/<user>/<decision>', methods=['GET', 'POST'])
def confirm_offsetDates(confdate,user,decision):
	print confdate
	print user
	u = User.query.filter_by(username=user).first()
	print u
	us = UserStatistics.query.filter_by(userId=u.id).first()
	temp = us.offsetDates
	temprecord = us.offsetDatesRecord
	print temp
	dates = temp.keys()
	print dates
	for a in dates:
		print a
		print confdate
		if a == confdate:
			print decision
			if decision == "confirm":
				temp[confdate] = 1
				temprecord[confdate] = 1
				us.offsetDates = temp
				us.offsetDatesRecord = temprecord
				print us.offsetDates

				num_of_days = confdate.split(';')
				subtract = len(num_of_days)
				us.offset = us.offset - subtract
				print us.offset

				## Record the date when the leave is applied
				offsetListConfirmedDate = us.offsetDatesDecidedDates
				if offsetListConfirmedDate is None:
					offsetListConfirmedDate = {}
					today = date.today()
					offsetListConfirmedDate[confdate] = today.strftime('%m-%d-%y')
					print offsetListConfirmedDate
					us.offsetDatesDecidedDates = offsetListConfirmedDate

				else:
					today = date.today()
					offsetListConfirmedDate[confdate] = today.strftime('%m-%d-%y')
					print offsetListConfirmedDate
					us.offsetDatesDecidedDates = offsetListConfirmedDate

				db_session.add(us)
				db_session.commit()
				flash('Date Confirmed.')
				return redirect(url_for('.approval_of_leaves'))

			if decision == "deny":
				temprecord [confdate] = 2
				us.offsetDatesRecord = temprecord

				print 'sickleave'
				dates = us.offsetDates
				print dates
				del dates[confdate]
				
				us.offsetDates = dates
				print us.offsetDates

				## Record the date when the leave is applied
				offsetListConfirmedDate = us.offsetDatesDecidedDates
				if offsetListConfirmedDate is None:
					offsetListConfirmedDate = {}
					today = date.today()
					offsetListConfirmedDate[confdate] = today.strftime('%m-%d-%y')
					print offsetListConfirmedDate
					us.offsetDatesDecidedDates = offsetListConfirmedDate

				else:
					today = date.today()
					offsetListConfirmedDate[confdate] = today.strftime('%m-%d-%y')
					print offsetListConfirmedDate
					us.offsetDatesDecidedDates = offsetListConfirmedDate

				db_session.add(us)
				db_session.commit()
				flash('Date Denied.')
				return redirect(url_for('.approval_of_leaves'))



@HR.route('/confirm_offsetDates/<user>', methods=['GET', 'POST'])
def confirm_offsetDays(user):
	u = User.query.filter_by(username=user).first()
	us = UserStatistics.query.filter_by(userId=u.id).first()
	us.offset = int(us.proposed_offset) + int(us.offset)
	us.proposed_offset = None
	db_session.add(us)
	db_session.commit()
	flash('Number of offset days confirmed.')
	return redirect(url_for('.approval_of_leaves'))
# ==========================================================================
@HR.route('/summary', methods=['GET', 'POST'])
def summary():
	
	g.user = current_user
	dbQuery = UserStatistics.query.filter_by(userId = g.user.id).first() # get current_user ID

	if not dbQuery:
		slSummary = []
	else:
		sickSummary = dbQuery.slDatesRecord
		

	if not dbQuery:
		vacationSummary = []
	else:
		# vl = dbQuery.vlDates
		# vacationSummary = vl.keys()
		vacationSummary = dbQuery.vlDatesRecord
		
		
	if not dbQuery:
		offsetSummary = []
	else:
		offsetSummary = dbQuery.offsetDatesRecord
		# od = dbQuery.offsetDates
		# offsetSummary = od.keys()

	# del slSummary[-1], vacationSummary[-1], offsetSummary[-1],

	if request.method == 'POST':
		session.pop('addDate', None)
		return redirect(url_for('.summary'))

	# print session['addDate']			

	# ==========================================================================

	# g.user = current_user
	# dbQuery = UserStatistics.query.filter_by(userId = g.user.id).first() # query stats of current user

	# slQuery = dbQuery.slDates.split(';')
	# vacationQuery = dbQuery.vlDates.split(';')
	# offsetQuery = dbQuery.offsetDates.split(';')

	# del slQuery[-1], vacationQuery[-1], offsetQuery[-1]

	# slSummary = ', '.join(slQuery)
	# vacationSummary = ', '.join(vacationQuery)
	# offsetSummary = ', '.join(offsetQuery)

	# if request.method == 'POST':
	# 	return redirect(url_for('.leaves'))

	# At start of rendering

	return render_template("hr/summary.html",
							sickSummary=sickSummary,
							vlSummary=vacationSummary,
							offsetSummary=offsetSummary,	
							user=current_user,
							)	
# ==========================================================================

@HR.route('/approval_of_leaves', methods=['GET', 'POST'])
def approval_of_leaves():
	## LOAD ALL DATES
	all_users = current_user.supervisee
	all_users = all_users.split(' ')
	print 'ALL USERS ' + str(all_users)

	if request.method == 'POST':
		if request.form['button'] == 'Confirm':
			print 'CONFIRMED!'
			return redirect(url_for('.approval_of_leaves'))

		elif request.form['button'] == 'Deny':
			print 'DENIED!'
			return redirect(url_for('.approval_of_leaves'))

	return render_template("hr/approve_leaves.html",
							all_users=all_users,
							)	
		

@HR.route('/delete_dates/<user>/<date>/<what_leave>', methods=['GET', 'POST'])
def delete_dates(user,date, what_leave):
	u = User.query.filter_by(username=user).first()
	us = UserStatistics.query.filter_by(userId=u.id).first()
	print 'check'
	if what_leave == 'sickleave':
		print 'sickleave'
		print us.slDates
		dates = us.slDates
		datesrecord = us.slDatesRecord

		print dates
		del dates[date]
		del datesrecord[date]
		
		us.slDates = dates
		us.slDatesRecord = datesrecord

		print us.slDates
		db_session.add(us)
		db_session.commit()
		flash('Date Deleted')
		return redirect(url_for('.summary'))

	elif what_leave == 'vacationleave':
		print 'vacationleave'
		print us.vlDates
		dates = us.vlDates
		datesrecord = us.vlDatesRecord
		del dates[date]
		del datesrecord[date]

		print dates
		us.vlDates = dates
		us.vlDatesRecord = datesrecord
		db_session.add(us)
		db_session.commit()
		flash('Date Deleted')
		return redirect(url_for('.summary'))

	elif what_leave == 'offset':
		print 'offset'
		dates = us.offsetDates
		datesrecord = us.offsetDatesRecord
		del dates[date]
		del datesrecord[date]

		print dates
		us.offsetDates = dates
		us.offsetDatesRecord = datesrecord
		db_session.add(us)
		db_session.commit()
		flash('Date Deleted')
		return redirect(url_for('.summary'))






@HR.route('/request_for_cancellation/<user>/<confdate>/<what_leave>', methods=['GET', 'POST'])
def request_for_cancellation(user,confdate, what_leave):
	u = User.query.filter_by(username=user).first()
	us = UserStatistics.query.filter_by(userId=u.id).first()

	if what_leave == 'sickleave':
		print 'sickleave'
		us.slDatesRecord[confdate] = 3
		print us.slDatesRecord
		print us.slDatesRecord[confdate]

		## Record when the user applied for cancellation
		slCancelDates = us.slDatesCancelled
		if slCancelDates is None:
			slCancelDates = {}
			today = date.today()
	
			slCancelDates[confdate] = today.strftime('%m-%d-%y')
			print slCancelDates
			us.slDatesCancelled = slCancelDates

		today = date.today()
		slCancelDates[confdate] = today.strftime('%m-%d-%y')
		print slCancelDates
		us.slDatesCancelled = slCancelDates

		db_session.add(us)
		db_session.commit()
		flash('Cancellation Requested.')
		return redirect(url_for('.summary'))

	elif what_leave == 'vacationleave':
		print 'vacationleave'
		us.vlDatesRecord[confdate] = 3

		## Record when the user applied for cancellation
		vlCancelDates = us.vlDatesCancelled
		if vlCancelDates is None:
			vlCancelDates = {}
			today = date.today()
	
			vlCancelDates[confdate] = today.strftime('%m-%d-%y')
			print vlCancelDates
			us.vlDatesCancelled = vlCancelDates

		today = date.today()
		vlCancelDates[confdate] = today.strftime('%m-%d-%y')
		print vlCancelDates
		us.vlDatesCancelled = vlCancelDates

		db_session.add(us)
		db_session.commit()
		flash('Cancellation Requested.')
		return redirect(url_for('.summary'))

	elif what_leave == 'offset':
		print 'offset'
		us.offsetDatesRecord[confdate] = 3

		## Record when the user applied for cancellation
		offsetCancelDates = us.offestDatesCancelled
		if offsetCancelDates is None:
			offsetCancelDates = {}
			today = date.today()
	
			offsetCancelDates[confdate] = today.strftime('%m-%d-%y')
			print offsetCancelDates
			us.offestDatesCancelled = offsetCancelDates

		today = date.today()
		offsetCancelDates[confdate] = today.strftime('%m-%d-%y')
		
		us.offestDatesCancelled = offsetCancelDates

		db_session.add(us)
		db_session.commit()
		flash('Cancellation Requested.')
		return redirect(url_for('.summary'))


@HR.route('/cancellation/<user>/<confdate>/<what_leave>/<decision>', methods=['GET', 'POST'])
def cancellation(user,confdate, what_leave,decision):
	u = User.query.filter_by(username=user).first()
	us = UserStatistics.query.filter_by(userId=u.id).first()

	if what_leave == 'sickleave':
		if decision == 'confirm_cancel':
			us.slDatesRecord[confdate] = 4
			num_of_days = confdate.split(';')
			add = len(num_of_days)
			us.sl = us.sl + add

			dates = us.slDates
			print dates
			del dates[confdate]
			
			us.slDates = dates
			print us.slDates

			slCancelDates = us.slDatesConfirmedCancelled
			if slCancelDates is None:
				slCancelDates = {}
				today = date.today()
		
				slCancelDates[confdate] = today.strftime('%m-%d-%y')
				print slCancelDates
				us.slDatesConfirmedCancelled = slCancelDates

			today = date.today()
			slCancelDates[confdate] = today.strftime('%m-%d-%y')
			print slCancelDates
			us.slDatesConfirmedCancelled = slCancelDates

			db_session.add(us)
			db_session.commit()
			flash('Cancelled Date Confirmed.')
			return redirect(url_for('.approval_of_leaves'))

		elif decision == 'cancel':
			us.slDatesRecord[confdate] = 1
			db_session.add(us)
			db_session.commit()
			flash('Application Cancelled.')
			return redirect(url_for('.approval_of_leaves'))

	elif what_leave == 'vacationleave':
		if decision == 'confirm_cancel':
			us.vlDatesRecord[confdate] = 4
			num_of_days = confdate.split(';')
			add = len(num_of_days)
			us.vl = us.vl + add

			dates = us.vlDates
			print dates
			del dates[confdate]
			
			us.vlDates = dates
			print us.vlDates

			vlCancelDates = us.vlDatesConfirmedCancelled
			if vlCancelDates is None:
				vlCancelDates = {}
				today = date.today()
		
				vlCancelDates[confdate] = today.strftime('%m-%d-%y')
				print vlCancelDates
				us.vlDatesConfirmedCancelled = vlCancelDates

			today = date.today()
			vlCancelDates[confdate] = today.strftime('%m-%d-%y')
			print vlCancelDates
			us.vlDatesConfirmedCancelled = vlCancelDates

			db_session.add(us)
			db_session.commit()
			flash('Cancelled Date Confirmed.')
			return redirect(url_for('.approval_of_leaves'))

		elif decision == 'cancel':
			us.vlDatesRecord[confdate] = 1
			db_session.add(us)
			db_session.commit()
			flash('Application Cancelled.')
			return redirect(url_for('.approval_of_leaves'))

	elif what_leave == 'offset':
		if decision == 'confirm_cancel':
			us.offsetDatesRecord[confdate] = 4
			num_of_days = confdate.split(';')
			add = len(num_of_days)
			us.offset = us.offset + add

			dates = us.offsetDates
			print dates
			del dates[confdate]
			
			us.offsetDates = dates
			print us.offsetDates

			offsetCancelDates = us.offestDatesConfirmedCancelled
			if offsetCancelDates is None:
				offsetCancelDates = {}
				today = date.today()
		
				offsetCancelDates[confdate] = today.strftime('%m-%d-%y')
				print offsetCancelDates
				us.offestDatesConfirmedCancelled = offsetCancelDates

			today = date.today()
			offsetCancelDates[confdate] = today.strftime('%m-%d-%y')
			print offsetCancelDates
			us.offestDatesConfirmedCancelled = offsetCancelDates

			db_session.add(us)
			db_session.commit()
			flash('Cancelled Date Confirmed.')
			return redirect(url_for('.approval_of_leaves'))

		elif decision == 'cancel':
			us.offsetDatesRecord[confdate] = 1
			db_session.add(us)
			db_session.commit()
			flash('Application Cancelled.')
			return redirect(url_for('.approval_of_leaves'))

