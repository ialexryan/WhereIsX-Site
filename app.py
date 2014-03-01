from functools import wraps
from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form
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

@app.route('/error/<int:error_type>')
def error(error_type):
    if error_type == ERR_MISSING_USER:
        return "User not found - if you are seeing this page, something has gone wrong."
    elif error_type == ERR_WRONG_USER:
        return "You are trying to edit a user that is not the user you logged in as."
    else:
        return "Unspecified error."

UserForm = model_form(User, base_class=Form)

@app.route('/register')
def register():
    form = UserForm(name=u'bad')
    return render_template('register.html', form=form)

@app.route('/edit/<int:id>')
def edit_user(id):
    MyForm = model_form(User, base_class=Form)
    user = User.query.get(id)
    form = MyForm(request.form, user)

    if request.method == 'POST' and form.validate():
        form.populate_obj(model)
        db.session.commit()
        flash("User updated")
        return redirect(url_for('print_location', username=user.username))
    #return render_template("edit.html", form=form)
    return form


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
        return redirect(url_for('error', error_type=ERR_WRONG_USER))

@app.route('/<username>')
def print_location(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        return redirect(url_for('error', error_type=ERR_MISSING_USER))
    else:
        #return user.firstname + " " + user.lastname + " is " + user.location
        return render_template('location.html', user=user)

@app.route('/')
def print_default_user():
    return print_location(default_user.username)

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
