from flask.ext.wtf import Form
from wtforms import FileField

class UploadFileForm(Form):
    files = FileField('File')
