from flask import Flask, jsonify, g
from flask_cors import CORS
from flask_login import LoginManager, current_user
from flask_httpauth import HTTPTokenAuth
from resources.songs import song
from resources.user import user

import models

login_manager = LoginManager()

DEBUG = True
PORT = 8000

# Initialize an instance of the Flask class.
# This starts the website!
app = Flask(__name__)
# CORS(app)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'

auth = HTTPTokenAuth(scheme='Bearer')

###################### added these lines

app.secret_key = "LJAKLJLKJJLJKLSDJLKJASD" ## Need this to encode the session
login_manager.init_app(app) # set up the sessions on the app

@login_manager.user_loader # decorator function, that will load the user object whenever we access the session, we can get the user
# by importing current_user from the flask_login
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None
###################### added these lines

@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()

@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response

@auth.verify_token
def verify_token(token):
    print(token, "<--------token")
    return token

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' %current_user.username})

CORS(song, origins=['http://localhost:3000'], supports_credentials=True) # adding this line
app.register_blueprint(song, url_prefix='/api/v1/songs') # adding this line

################## added these lines
CORS(user, origins=['*','http://localhost:3000', '*'], supports_credentials=True)
app.register_blueprint(user, url_prefix='/user')
################## added these lines

# Run the app when the program starts!
if __name__ == '__main__':
    models.initialize()
    app.run(debug=DEBUG, port=PORT)