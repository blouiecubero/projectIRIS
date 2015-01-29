from flask import current_app
from flask.ext.login import current_user
class Store_Users():
    
    ## The purpose of this class is to stand as a threshold and a storage for the selection process
    ## in the admin functionality. This class also eliminates the initialization error that occurs
    ## everytime the program starts due to some certain variables that are left null in the beginning.

    ## In short, this class serves as temporary holder.
    
    stored_user = ""

    ## This function stores the selected user by the admin to view the chosen user's files.
    def store(self, name):
        self.stored_user = name
        return self.stored_user

    ## This function initializes the user_file variable (in the admin_user function) when the program is just starting.
    def check_if_none(self):    
        if self.stored_user == "":            # If the program had just started (At this point, it will be none.)
            self.stored_user = current_user.username # Then the initialized user would be the admin itself. 
            return self.stored_user
        return self.stored_user               # Else, it would load the current stored_user. (This will be changed if the admin has already chose a user.

class FileChecker():
    
    ## Defining functions for filechecking when upload functions are used.
    
    def allowed_pic(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_PICTURES']

    def allowed_files(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_DOCUMENTS']   
