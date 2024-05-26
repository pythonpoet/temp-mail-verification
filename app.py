from flask import Flask, redirect, url_for, session, render_template, jsonify, current_app
import hashlib

import uuid
import threading
import time
from tempmail import EMail
from admin import *
# Timeout for waiting on mail
mail_timout = 250
hash_key= 'test'
hash_file = 'users.txt'

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Global dictionaries to store session data and EMail instances
session_data_store = {}
email_instances = {}


def verify_mail(message):
    email_addr = message.from_addr
    if contains_uva_email(email_addr):
        if not is_email_in_file(email_addr, hash_key, hash_file):
            hash_code = generate_combined_hash(email_addr, hash_key)
            append_hash_to_file(hash_code=hash_code, file_path=hash_file)
            return True
        else:
            print(f'email is already registered')
            #TODO add error case
    else:
        print(f'email address: {email_addr} is not from the accepted institutions')
    #TODO add error case
    return False

# Function to simulate a long-running task
def my_function(app, session_id):
    email_instance = email_instances.get(session_id)
    message_body = "Timeout reached"
    if email_instance:
        try:
            msg = email_instance.wait_for_message(timeout=mail_timout) 
            verification_successful = verify_mail(msg)  
        except TimeoutError:
            verification_successful = False
            message_body = "Timeout reached"

        with app.app_context():
            if session_id in session_data_store:
                session_data_store[session_id]['message_body'] = message_body
                session_data_store[session_id]['verified'] = verification_successful
                print(f"Updated session_data_store[{session_id}]['message_body'] to: {message_body}")
                print(f"Verification result for session_id {session_id}: {verification_successful}")
            email_instances.pop(session_id, None)
            print(f"Removed session id {session_id} from email_instances")

@app.route('/')
def index():
    session_id = str(uuid.uuid4())
    email_instance = EMail()
    email_instances[session_id] = email_instance
    session_data_store[session_id] = {
        "email_address": email_instance.address,
        "object": {"key": "value"},
        "message_body": None,
        "verified": False
    }
    session[session_id] = session_data_store[session_id]  # Store in session for request context
    print(f"Created session for {session_id} with email: {email_instance.address}")
    return redirect(url_for('session_page', session_id=session_id))

@app.route('/session/<session_id>')
def session_page(session_id):
    session_data = session_data_store.get(session_id)
    email_instance = email_instances.get(session_id)
    if session_data and email_instance:
        thread = threading.Thread(target=my_function, args=(app, session_id))
        thread.start()
        email_address = session_data["email_address"] if session_data["email_address"] else "no-email@address.com"
        print(f"Starting thread for session_id: {session_id}")
        return render_template('index.html', email=email_address, session_id=session_id, obj=session_data["object"], message_body=session_data["message_body"])
    else:
        return redirect(url_for('index'))

@app.route('/status/<session_id>')
def status(session_id):
    session_data = session_data_store.get(session_id)
    if session_data:
        message_body = session_data.get("message_body")
        verified = session_data.get('verified')
        print(f"Status check for session_id: {session_id}, message_body: {message_body}, verified:{verified}")
        if message_body is not None:
            return jsonify({"status": "finished", "message_body": message_body, "verified":verified})
        else:
            return jsonify({"status": "running"})
    else:
        return jsonify({"status": "finished"})

@app.route('/refresh/<session_id>')
def refresh(session_id):
    session_data = session_data_store.get(session_id)
    email_instance = email_instances.get(session_id)
    if session_data and email_instance:
        email_address = session_data["email_address"] if session_data["email_address"] else "no-email@address.com"
        return render_template('index.html', email=email_address, session_id=session_id, obj=session_data["object"], message_body=session_data["message_body"])
    else:
        return redirect(url_for('index'))

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

if __name__ == '__main__':
    app.run(debug=True)
