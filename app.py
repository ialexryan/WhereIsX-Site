from functools import wraps
from flask import Flask, redirect, url_for, request, Response
app = Flask(__name__)

default_user = "Jaden"

global_user_location_dict = {default_user:"uninitialized"}
global_authorized_users = {"myfirstuser":"password123"}

#
def check_auth(auth_username, auth_password):
    """This function returns true if the username and password are in the list of authorized users."""
    return (auth_username in global_authorized_users and global_authorized_users[auth_username] == auth_password)

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

@app.route('/update_location/<username>/<location>')
@requires_auth
def update_location(username, location):
        global global_user_location_dict
        global_user_location_dict[username] = location
        return redirect(url_for('print_location', username=username))

@app.route('/<username>')
def print_location(username):
        if username in global_user_location_dict:
                return username + " is " + global_user_location_dict[username] + "."
        else:
                return "User not found - if you are seeing this page, something has gone wrong.  Please create the user."

@app.route('/')
def print_default_user():
        return print_location(default_user)

if __name__ == '__main__':
        app.run('0.0.0.0', debug=True)
