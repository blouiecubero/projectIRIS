## Manage.py serves as the gateway to multiple commands that can be accessed
## by the user. Running the app, db configuration by accessing the shell,
## migrating, downgrading, and upgrading the database.


import os
from app import create_app, db
from app.models import User, Role, FileBase
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from flask import Flask

## The *app* serves as the main application of the program. It is initialized
## with the configuration listed in the config.py file.
## The create_app was imported from __init__.py file from app folder.
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

## The *Manager* class is the class that serves as a gateway.
manager = Manager(app)

## The *Migrate* class is the class that runs the migrating function of db.
## It's integrated in the manager.
migrate = Migrate(app,db)

## These are the only tables that can be passed on to shell. 
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, FileBase=FileBase)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
