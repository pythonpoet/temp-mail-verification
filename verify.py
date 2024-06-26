#!/usr/bin/python3

import re
import hashlib,os
import logging
import vars
import database
from email_handler import send_auth_code
import random
import concurrent.futures
import time

synapse_url='matrix.yuva.fyi'
salt = 'jwqsTQ6FWhOkCn7u'
allowed_domains = ['uva.nl','student.uva.nl']
address = 'herpDerp+test@uVa.nl'
TOKEN_DELETE_TIME = 330

#connect to db
db = database.Database('yuva.txt')


# Set up the logger
logger = logging.getLogger('auth')
#logger.setLevel(logging.INFO)  # set the logging level

handler = logging.StreamHandler()  # create a handler to print logs to the console
handler.setLevel(logging.DEBUG)  # set the level of the handler

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")  # create a formatter
handler.setFormatter(formatter)  # set the formatter to the handler

logger.addHandler(handler)  # add the handler to the logger

def is_username_available(username):
    """
    Checks whether a username is available on a Matrix server.
    Returns True if available, False if not available, raises an exception for other errors.
    """
    # Define the API endpoint URL
    api_url = f"{synapse_url}/_matrix/client/r0/register/available?username={username}"

    # Send the GET request to the API endpoint
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response data as a JSON dictionary
        response_data = json.loads(response.text)

        # Check if the desired username is available
        if response_data.get("available") is True:
            return True
        else:
            return False
    else:
        False

def check_if_valid_character(address):
    return re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',address)

def get_domain(address):
    domain = address[address.index('@') + 1 : ]
    return domain.lower()

def check_if_domain_allowed(address):
    domain = get_domain(address)
    print(domain)
    return domain in allowed_domains

def get_localpart(address):
    localpart = address[ : address.index('@') ]
    if '+' in localpart:
        localpart = localpart[ : localpart.index('+') ]
    return localpart.lower()

def get_hash(address):
    uniquepart = salt + get_localpart(address) + get_domain(address)
    hashedaddress = hashlib.sha256(uniquepart.encode('utf-8'))
    print(hashedaddress.hexdigest())
def contains_double_registration(email):
    hash_code = get_hash(email)
    return db.user_id_already_exists(hash_code)

def check_email(email):
    if not check_if_domain_allowed(email):
        logger.error(vars.auth_message_no_uva_mail.get(vars.language))
        return False
    if contains_double_registration(email):
        logger.error(vars.auth_message_mail_dubble_registered.get(vars.language))
        return False
    if check_if_valid_character(email):
        logger.error(vars.aut_message_mail_format.get(vars.language))
        return False
    return True
def create_matrix_accout(username, displayname, password, is_admin=False):
    """
    Signs up a user using the Synapse Matrix Homeserver API.
    """
    # Define the request data
    data = {
        "nonce": "thisisanonce",
        "username": username,
        "displayname": displayname,
        "password": password,
        "admin": is_admin
    }

    # Define the API endpoint URL
    api_url = f"{synapse_url}/_synapse/admin/v1/register"

    # Generate a mac digest for the request data
    secret = base64.b64decode(synapse_secret.encode())
    mac = hmac.new(secret, digestmod=hashlib.sha1)
    mac.update(json.dumps(data, sort_keys=True).encode())
    mac_digest = base64.b64encode(mac.digest()).decode()

    # Add the mac digest to the request data
    data["mac"] = mac_digest

    # Send the POST request to the API endpoint
    response = requests.post(api_url, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        # Return the response data
        return True#response.json()
    else:
        # Raise an exception with the error message
        error_message = response.json()["error"]
        raise Exception(error_message)

def delete_token_async(token):
    #delete interval
    time.sleep(TOKEN_DELETE_TIME)
    db.delete_token(token)

def send_token(email):
    # gen a unique token
    while True:
        token = str(random.randint(100000, 999999))
        if not db.check_token_exists(token):
            break
    
    # write to db
    db.insert_token(token)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(delete_token_async, token)
    # send emal via smtp
    send_auth_token(email, token)

def auth_email(email):
    hash_code = get_hash(email)
    if not db.user_id_exists(hash_code):
        send_token(email)
    else:
        logger.error(vars.auth_message_mail_dubble_registered.get(vars.language))
def validate_token(token):
    # check if token exists and delete it
    if db.check_token_exists(token):
        db.delete_token(token)
        return True
    else:
        logger.error(vars.verify_token_error.get(vars.language))
        return False

def create_yuva_accout(code,email, username,displayname, password):
    if not validate_code(code):
        logger.error(vars.auth_code_error.get(vars.language))
        if is_username_available(username):
            if check_mail(email):
                hash_code = get_hash(email)
                if not db.user_id_exists(hash_code):
                    if create_matrix_accout(username=username,displayname=displayname,password=password):
                        logger.info(vars.aut_message_account_created.get(vars.language))
                        db.insert_userID(hash_code)
                    else:
                        logger.error(vars.auth_message_account_error.get(vars.language))
                else:
                    logger.error(vars.auth_message_mail_dubble_registered.get(vars.language))
        else: 
            logger.error(vars.aut_message_name_already_taken.get(vars.language))

