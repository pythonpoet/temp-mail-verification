from flask import Flask, redirect, url_for, session, render_template, jsonify, current_app,request
import hashlib

import uuid
import threading
import time
from verify import *
# Timeout for waiting on mail
mail_timout = 250
hash_key= 'test'
hash_file = 'users.txt'

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Global dictionaries to store session data and EMail instances
session_data_store = {}
email_instances = {}

# Create a handler to log errors to a file
file_handler = logging.FileHandler('error.log')
file_handler.setLevel(logging.ERROR)

# Create a formatter and attach it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(file_handler)

@app.errorhandler(500)
def internal_server_error(e):
    logger.error('Error: %s', e)
    return 'Error: ' + str(e), 500

# landing page
@app.route('/')
def index():
    session_id = str(uuid.uuid4())

    session_data_store[session_id] = {
        "email_address": None,
        "object": {"key": "value"},
        "message_body": None,
        "verified": False
    }
    session[session_id] = session_data_store[session_id]  # Store in session for request context
    print(f"Created session for {session_id} ")
    return redirect(url_for('verify_page', session_id=session_id))
# register page
@app.route('/verify_page/<session_id>')
def verify_page(session_id):
    # redicrect user if session does not exist
    if not session_id in session_data_store:
        return redirect(url_for('oops', session_id=session_id))
    
    session_data = session_data_store.get(session_id)
    return render_template('verify.html', session_id=session_id)

# register page
@app.route('/register/<session_id>/<token>')
def register_page(session_id,token):
    # redicrect user if session does not exist
    if not session_id in session_data_store:
        return redirect(url_for('oops', session_id=session_id))
    session_data = session_data_store.get(session_id)
    if validate_token(token):
        session_data_store['verified'] = True
    return render_template('register.html')


@app.route('/success/<session_id>')
def success(session_id):
    session_data = session_data_store.get(session_id)
    if session_data and session_data.get("verified"):
        return render_template('success.html', session_id=session_id)
    else:
        return redirect(url_for('oops', session_id=session_id))

@app.route('/oops/<session_id>')
def oops(session_id):
    return render_template('oops.html', session_id=session_id)



@app.route('/submit_email/<session_id>', methods=['POST'])
def submit_email(session_id):
    if not session_id in session_data_store:
        # Handle invalid session_id, e.g., return an error pageemail_address
        return redirect(url_for('oops', session_id=session_id))

    email_address = request.form.get('email')
    session_data_store[session_id]['email_address'] = email_address
    # validate email
    if check_email(email_address):
        #check if email aready exists and if not send email
        if auth_email(email_address):
            return jsonify({'message': 'Form submitted successfully'})

    return redirect(url_for('verify_page', session_id=session_id, message="Email wrong"))




if __name__ == '__main__':
    app.run(debug=True)
