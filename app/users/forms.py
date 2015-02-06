<<<<<<< HEAD
# Import Form and RecaptchaField (optional)
from flask.ext.wtf import Form # , RecaptchaField

from wtforms import TextField, widgets, SelectMultipleField, PasswordField, FileField, StringField, SelectField, SubmitField
from app.users.models import Role, User
# Import Form validators
from wtforms.validators import Required, Email, EqualTo, Length, Regexp


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
    submit = SubmitField('Register')

class DeleteUserForms(Form):
    chosen_user = SelectField('Select user',coerce=int)
    submit = SubmitField('Delete user')
    
=======
## This is where all the forms that will be used in the main blueprint
## will be stored.

from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from flask.ext.wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.ext.sqlalchemy.orm import model_form
from ..models import User



class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

class EditUserNameForm(Form):
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    submit = SubmitField('Submit')


>>>>>>> cee9d0b2da1d3dbeac36bfe675438c30487e7305
