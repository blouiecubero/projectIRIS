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


