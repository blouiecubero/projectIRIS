from app.users.models import User, Role, Permission, Payslip, UserStatistics
from app.database import db_session
from werkzeug import generate_password_hash

def a():
	from app.users.models import User, Role, Permission, Payslip
	from app.database import db_session
	from werkzeug import generate_password_hash

def u(fname, mname, lname, email, username, pword):
	u = User(fname,mname,lname ,email,username,generate_password_hash(pword))
	db_session.add(u)
	db_session.commit()

def seer():
	u('Seer','super','SuperAdmin','superseer@seer-technologies.com','seer','seer')
	user = User.query.filter_by(username='seer').first()
	r = Role.query.filter_by(name='Administrator').first()
	user.roles.append(r)
	user.is_supervisor = True
	db_session.add(user)
	db_session.commit()

def p():
	a = Permission('Administrator')
	b = Permission('View Payslip')
	c = Permission('HR Functionalities')
	d = Permission('See Projects')
	e = Permission('Upload Payslip')

	perms = [a,b,c,d,e]

	for i in perms:
		db_session.add(i)

	db_session.commit()

def r():
	a = Role('Administrator')
	b = Role('HR')
	c = Role('Finance')

	roles = [a,b,c]

	for i in roles:
		db_session.add(i)

	db_session.commit()

def init_admin_perms():
	r = Role.query.filter_by(name='Administrator').first()
	perms = Permission.query.all()
	
	for i in perms:
		r.permissions.append(i)

	db_session.add(r)
	db_session.commit()

def resetdates():
	u = User.query.all()

	for i in u:
	    us = UserStatistics.query.filter_by(userId=i.id).first()
	    us.vl = 15
	    us.sl = 15
	    us.slDates = {}
	    us.vlDates = {}
	    us.offsetDates = {}
	    us.slDatesRecord = {}
	    us.vlDatesRecord = {}
	    us.offsetDatesRecord = {}
	    us.slDatesAppliedDates = {}
	    us.vlDatesAppliedDates = {}
	    us.offsetDatesAppliedDates = {}
	    us.slDatesDecidedDates = {}
	    us.vlDatesDecidedDates = {}
	    us.offsetDatesDecidedDates = {}

	db_session.add(us)
	db_session.commit()
