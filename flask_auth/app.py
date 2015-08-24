from flask import Flask, request, jsonify
from db import create_user, authenticate_user, get_user_by_id
app = Flask(__name__)


@app.route('/')
def index():
    return 'I am an auth server.'


@app.route('/users/<int:user_id>/')
def user(user_id):
    u = get_user_by_id(user_id)
    if not u:
        return jsonify(id=None)

    return jsonify(id=u.id, username=u.username)


@app.route('/signup/', methods=['POST'])
def signup():
    create_user(request.form['username'], request.form['password'])
    return jsonify(success=True)


@app.route('/login/', methods=['POST'])
def login():
    u = authenticate_user(request.form['username'], request.form['password'])

    if u:
        return jsonify(username=u.username, id=u.id)

    return jsonify(id=None)

if __name__ == "__main__":
    app.run(debug=True)
