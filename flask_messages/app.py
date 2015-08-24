from flask import Flask, request, jsonify
from db import search_messages, post_message, list_messages, list_user_messages
app = Flask(__name__)


@app.route('/')
def index():
    return 'I am a message server.'


@app.route('/messages/')
def message_list():
    messages = list_messages()
    return jsonify({'count': len(messages), 'messages': messages})


@app.route('/messages/search')
def message_search():
    search = request.args.get('search')
    if not search:
        messages = []
    else:
        messages = search_messages(search)

    return jsonify({'count': len(messages), 'messages': messages})


@app.route('/messages/post', methods=['POST'])
def message_post():
    m = post_message(request.form['user_id'], request.form['message'])
    return jsonify(**m)


@app.route('/messages/<int:user_id>', methods=['GET'])
def user_messages(user_id):
    messages = list_user_messages(user_id)

    return jsonify({'count': len(messages), 'messages': messages})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
