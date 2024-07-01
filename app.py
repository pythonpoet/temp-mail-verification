from flask import Flask, redirect, url_for, session, render_template, jsonify, current_app,request, flash, Blueprint
from logging.config import dictConfig
import hashlib

import uuid
import threading
import time
from verify import *
import keys

# Timeout for waiting on mail

app = Flask(__name__)
app.secret_key = keys.FLASK_SECRET_KEY

# Global dictionaries to store session data
session_data_store = {}

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s | %(module)s] %(message)s",
                "datefmt": "%B %d, %Y %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "ivt-trace.log",
                "formatter": "default",
            },
        },
        "root": {"level": "INFO", "handlers": ["console", "file"]},
    }
)
logger = logging.getLogger(__name__)
# define the blueprint
blueprint_xxxx = Blueprint(name="blueprint_xxx", import_name=__name__, url_prefix='/xxxx/yyyy')
logger.info(msg="some logging info")
# Create a handler to log errors to a file
file_handler = logging.FileHandler('error.log')
file_handler.setLevel(logging.ERROR)

# Create a formatter and attach it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(file_handler)


# landing page
@app.route('/')
def index():
    if not 'id' in session:
        session['id'] = str(uuid.uuid4())
    if not 'email' in session:
        session['email'] = None
    if not 'verified' in session:
        session['verified'] = False
    if not 'language' in session:
        # select language randomly to avoid language bias
        session['language'] = random.choice(config.SUPPORTED_LANG)
    logger.info(msg=f'Start session with id: {session.get('id')}')
    return render_template('index.html')

# register page
@app.route('/register/<session_id>/<token>')
def register_page(session_id, token):
    logger.info(msg=f'is session id initialised? {"id" in session}')
    logger.info(msg=f'link session_id: {session_id} cookie session id: {session.get("id")}')

    if not session_id == session.get('id'):
        return redirect(url_for('oops'))
    if validate_token(token):
        session['verified'] = True
        flash(vars.verify_token_success.get(vars.language),category='success')  
    return render_template('register.html' ,token=token)

@app.route('/success')
def success():
    if session["verified"]:
        return render_template('success.html',)
    else:
        return redirect(url_for('oops', ))

@app.route('/oops')
def oops():
    return render_template('oops.html')


@app.route('/submit_email', methods=['POST'])
def submit_email():
    email = request.form.get('email')
    session['email'] = email
    # validate email
    if check_email(email):
        #check if email aready exists and if not send email
        send_token(email,session['id'])
        flash(vars.auth_code_success.get(vars.language)% email, category='success')
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/create_account', methods=['POST'])
def create_account():
    # check that the session has been verified (token is already deleted)
    if not session['verified']: 
        return redirect(url_for('oops'))
    
    username = request.form['username']
    displayname = request.form['displayname']
    password = request.form['password']

    # Call the create_matrix_account function here
    #test_credentials(username, displayname, password)
    return render_template('success.html', )


if __name__ == '__main__':
    app.run(debug=True)
