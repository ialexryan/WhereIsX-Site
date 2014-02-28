from functools import wraps
from flask import Flask, redirect, url_for, request, Response
from authentication import *

app = Flask(__name__)

# Error Types
ERR_MISSING_USER = 1

default_user = "Jaden"

global_user_location_dict = {default_user:"uninitialized"}

@app.route('/error/<int:error_type>')
def error(error_type):
    if error_type == ERR_MISSING_USER:
        return url_for(print_default_user)
    else:
        return "Unspecified error." + url_for(print_default_user)

@app.route('/update_location/<username>/<location>')
#@requires_auth
def update_location(username, location):
    if username in global_user_location_dict:
        global global_user_location_dict
        global_user_location_dict[username] = location
        return redirect(url_for('print_location', username=username))
    else:
        return redirect(url_for('error', error_type=ERR_MISSING_USER))

@app.route('/<username>')
def print_location(username):
    if username in global_user_location_dict:
        return username + " is " + global_user_location_dict[username] + "."
    else:
        return redirect(url_for('error', error_type=ERR_MISSING_USER))

@app.route('/')
def print_default_user():
    return print_location(default_user)

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
