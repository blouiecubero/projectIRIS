from flask import current_app

class FileChecker():
    
    ## Defining functions for filechecking when upload functions are used.
    
    def allowed_pic(self,filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_PICTURES']

    def allowed_files(self,filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_DOCUMENTS']   
