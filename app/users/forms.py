# Import Form and RecaptchaField (optional)
from flask.ext.wtf import Form # , RecaptchaField

from wtforms import TextField, widgets, SelectMultipleField, IntegerField, PasswordField, FileField, StringField, SelectField, SubmitField, BooleanField
from app.users.models import Role, User
# Import Form validators
from wtforms.validators import Required, Email, EqualTo, Length, Regexp
from wtforms import ValidationError

# Define the login form (WTForms)
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.TableWidget()
    option_widget = widgets.CheckboxInput()
    
class LoginForm(Form):
    username    = TextField('Username')
    password 	= PasswordField('Password',)

class ChangePasswordForm(Form):
	old_password = PasswordField('Old password')
	new_password = PasswordField('New password')
	confirm_password = PasswordField('Confirm password')

class UploadProfilePictureForm(Form):
	image = FileField('Image')

class AddRolesForm(Form):
    rolename = StringField('Role Name:', validators = [
        Required(), Length(1,64), Regexp('[A-za-z][A-Za-z0-9_.]*$', 0,
                                         'Rolenames must have only letters,'
                                         'numbers, dots or underscores')])
    string_of_files = ['one\r\ntwo\r\nthree\r\n']
    list_of_files = string_of_files[0].split()
    files = [(x, x) for x in list_of_files]
    example = MultiCheckboxField('Label', choices=files)
    submit = SubmitField('Create Role')
    
class AddUserForms(Form):
    fname = StringField('First Name:', validators =[Required()])
    midname = StringField('Middle Name:', validators =[Required()])
    lname = StringField('Last Name:', validators =[Required()])
    email = StringField('Email', validators =[Required(), Length(1,64),
                                              Email()])
    username = StringField('Username',validators = [
        Required(), Length(1,64), Regexp('[A-za-z][A-Za-z0-9_.]*$', 0,
                                         'Usernames must have only letters,'
                                         'numbers, dots or underscores')])
    select_role = SelectMultipleField('Choose Role (To choose more than 1, press and hold Ctrl button, then click to your second choice)',coerce=int)
<<<<<<< HEAD
    number_of_sick_leaves = IntegerField('Number of sick leaves: ', validators=[Required()])
    number_of_vacation_leaves = IntegerField('Number of vacation leaves: ', validators=[Required()])
    select_supervisor = SelectField('Choose a supervisor', coerce=str)
    check_if_supervisor = BooleanField('Is this user a supervisor?')

=======
>>>>>>> 35877167617b9bff5c3a29ff1a2035b05f75dc31
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')


    
