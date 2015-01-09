from flask import render_template, send_from_directory, current_app
from . import main
from flask.ext.login import login_required, current_user

@main.route('/', methods=['GET', 'POST'])
@login_required
def homepage():
    ## This is the same as the index page. Kept it here if ever there will be a homepage.
    return render_template('home.html')

@main.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    ## Same as the homepage, but there's a strong possibility that the homepage will be differentiated
    ## from the index page. Hence, it's kept this way for further changes. 
    return render_template('index.html')


@main.route('/uploads/photos/<filename>')
def send_photo(filename):
    ## Displays photos in the browser
    return send_from_directory(current_app.config['PICTURE_FOLDER'], filename)

@main.route('/uploads/files/<filename>')
def send_file(filename):
    ## Displays files in the browser
    return send_from_directory(current_app.config['FILES_FOLDER'], filename)



