from functools import wraps
from flask import Flask, redirect, url_for, request, Response, flash, render_template
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

# Error Types
ERR_MISSING_USER = 1
ERR_WRONG_USER = 2


########## DATABASE SETUP ##########

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://whereisxdbuser:mysqlpass@localhost/whereisxdb"
db = SQLAlchemy(app)


########## USER SETUP ##########

list_of_users = []
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(127), unique=True)
    email = db.Column(db.String(127), unique=True)
    firstname = db.Column(db.String(127))
    lastname = db.Column(db.String(127))
    location = db.Column(db.String(500))
    password = db.Column(db.String(127))
    def __init__(self, username, email, firstname, lastname, location, password):
        self.username = username
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.location = location
        self.password = password
        list_of_users.append(self)

default_user = User.query.filter_by(username="jgeller").first()
current_user = None


########## ERROR HANDLING ##########

def error(err):
    if err == ERR_MISSING_USER:
        return "User not found."
    elif err == ERR_WRONG_USER:
        return "You are trying to edit a user that is not the user you are logged in as."
    else:
        return "Unspecified error " + err


########## AUTHENTICATION ##########

def check_auth(auth_username, auth_password):
    """This function returns true if the username and password are in the list of authorized users."""
    user = User.query.filter_by(username=auth_username).first()
    if user.password == auth_password:
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

@app.route('/register', methods=['GET', 'POST'])
@requires_auth
def register_response():
    if request.method == 'POST':
        newusername = request.form['username']
        newemail = request.form['email']
        newfirstname = request.form['firstname']
        newlastname = request.form['lastname']
        newpassword = request.form['password']
        newuser = User(newusername, newemail, newfirstname, newlastname, "somewhere", newpassword)
        db.session.add(newuser)
        db.session.commit()
        flash("User " + username + " has been created.")
        return redirect(url_for('print_default_user'))
    else:
        return render_template('register.html')

@app.route('/update_location/<username>/<location>')
@requires_auth
def update_location(username, location):
    # Checks that the user they are trying to update is the same user they
    # logged in as.
    global current_user
    if username == current_user.username:
        current_user.location = location
        db.session.commit()
        return redirect(url_for('print_location', username=username))
    else:
        flash(error(ERR_WRONG_USER))
        return redirect(url_for('print_default_user'))

@app.route('/<username>')
def print_location(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash(error(ERR_MISSING_USER))
        return redirect(url_for('print_default_user'))
    else:
        #return user.firstname + " " + user.lastname + " is " + user.location
        return render_template('location.html', user=user)

@app.route('/')
def print_default_user():
    return print_location(default_user.username)

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
