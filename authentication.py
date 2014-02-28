# Simple HTTP authentication module

from functools import wraps
from flask import Flask, request, Response

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
