import requests
from flask import Flask, jsonify, request, redirect
from flask_cors import CORS

from api.utils.util import eprint
from api.utils.aws_util import *

app = Flask(__name__)
CORS(app)

@app.route("/api/register", methods=["GET", "POST"])
def handle_register():
    eprint("Register Endpoint Reached")

@app.route("/api/login", methods=["GET", "POST"])
def handle_login():
    eprint("Login Endpoint Reached")
    # generate a new user session 
    # auth
    # redirect
    return redirect("/", code=302)

@app.route("/api/upload", methods=["GET", "POST"])
def handle_upload():
    eprint("Upload Endpoint Reached")

@app.route("/api/start", methods=["GET", "POST"])
def hanlde_start():
    # session creation
    # store it in redis {sess, info}
    # perform first step
    # store {sess: id, curr_step, info: obj} in db
    # return info 
    pass


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5328)
