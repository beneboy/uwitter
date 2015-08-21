from flask import Flask, request, jsonify
from db import create_user, authenticate_user
app = Flask(__name__)


@app.route('/')
def index():
    return 'I am an auth server.'


@app.route('/signup/', methods=['POST'])
def signup():
    create_user(request.form['username'], request.form['password'])
    return jsonify(success=True)


@app.route('/login/', methods=['POST'])
def login():
    return jsonify(success=authenticate_user(request.form['username'], request.form['password']))

if __name__ == "__main__":
    app.run()
