# Import Form and RecaptchaField (optional)
from flask.ext.wtf import Form # , RecaptchaField

from wtforms import TextField, PasswordField, FileField, SelectField, SubmitField
from app.users.models import Role, User
# Import Form validators
from wtforms.validators import Required, Email, EqualTo


# Define the login form (WTForms)
class LoginForm(Form):
    username    = TextField('Username')
    password 	= PasswordField('Password',)

class ChangePasswordForm(Form):
	old_password = PasswordField('Old password')
	new_password = PasswordField('New password')
	confirm_password = PasswordField('Confirm password')

class UploadProfilePictureForm(Form):
	image = FileField('Image')


