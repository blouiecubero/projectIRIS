## The function of this file is to provide email functionality for the program.

from threading import Thread
from flask import current_app, render_template
from flask.ext.mail import Message
from .. import mail
from . import email

## This function makes the program asynchronous in sending emails.
## It means that the program can now send emails while doing something else
## in the program.
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

## This function is the one that sends the email to the specified user.
def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
