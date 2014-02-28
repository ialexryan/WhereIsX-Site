from functools import wraps
from flask import Flask, redirect, url_for, request, Response
from authentication import *

app = Flask(__name__)

default_user = "Jaden"

global_user_location_dict = {default_user:"uninitialized"}

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
