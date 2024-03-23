import requests
from flask import Flask, jsonify, request, redirect, url_for, session
from flask_cors import CORS

from api.utils.util import eprint
from api.utils.aws_util import *

app = Flask(__name__)
CORS(app)


@app.route("/api/register", methods=["POST"])
def handle_register():
    eprint("Register Endpoint Reached")
    # save to db
    # redirect to login page
    return redirect("/login", code=302)


@app.route("/api/login", methods=["POST"])
def handle_login():
    eprint("Login Endpoint Reached")
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for(''))
    # regenerate a new user session 
    # auth
    # redirect
    return redirect("/", code=302)


@app.route('/api/logout', methods=["GET"])
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route("/api/upload/<game_id>", methods=["POST"])
def handle_upload():
    eprint("Upload Endpoint Reached")
    # talk to s3
    return "<p>Test Upload Enpoint</p>"


@app.route("/api/game", methods=["POST"])
def hanlde_start():
    # check authorization

    # parse user config, default models/s3 models? red agents? stpes?

    # game state init
    '''
    {   
        game_id,
        step,
        state,
        red,
        maxx_step
    }
    '''
    
    # store it in redis {game_id, game_state}
    
    # schema
    # store {sess: id, curr_step, info: obj} in db
    
    # return game_id 

    # error handling
    pass


@app.route("/api/perform_step/<game_id>", methods=["GET"])
def handle_next_step(game_id):
    # the game_id should map to a redis records with a game state
    pass


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5328)
