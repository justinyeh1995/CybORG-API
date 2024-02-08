import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/register")
def handle_register():
    pass

@app.route("/login")
def handle_login():
    pass

@app.route("/start")
def hanlde_start():
    # session creation
    # store it in redis {sess, info}
    # perform first step
    # store {sess: id, curr_step, info: obj} in db
    # return info 
    pass


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5555)
