from functools import wraps
from flask import Flask, redirect, url_for, request, Response
from authentication import *

# Error Types
ERR_MISSING_USER = 1
ERR_WRONG_USER = 2

app = Flask(__name__)

list_of_users = []

class User:
    def __init__(self, username, firstname, lastname, location, password):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.location = location
        self.password = password
        list_of_users.append(self)

default_user = User("jgeller", "Jaden", "Geller", "uninitialized", "12345")
current_user = default_user


########## AUTHENTICATION ##########

def check_auth(auth_username, auth_password):
    """This function returns true if the username and password are in the list of authorized users."""
    for user in list_of_users:
        if user.username == auth_username and user.password == auth_password:
            global current_user
            current_user = user
            return True
    return False

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


########## MAIN ROUTING ##########

@app.route('/error/<int:error_type>')
def error(error_type):
    if error_type == ERR_MISSING_USER:
        return "User not found - if you are seeing this page, something has gone wrong."
    elif error_type == ERR_WRONG_USER:
        return "You are trying to edit a user that is not the user you logged in as."
    else:
        return "Unspecified error."

@app.route('/update_location/<username>/<location>')
@requires_auth
def update_location(username, location):
    # Checks that the user they are trying to update is the same user they
    # logged in as.
    if username == current_user.username:
        global current_user
        current_user.location = location
        return redirect(url_for('print_location', username=username))
    else:
        return redirect(url_for('error', error_type=ERR_MISSING_USER))

@app.route('/<username>')
def print_location(username):
    for user in list_of_users:
        if user.username == username:
            return user.firstname + " " + user.lastname + " is " + user.location
    return redirect(url_for('error', error_type=ERR_MISSING_USER))

@app.route('/')
def print_default_user():
    return print_location(default_user.username)

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
