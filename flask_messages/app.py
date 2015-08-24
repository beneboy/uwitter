from flask import Flask, request, jsonify
from db import search_messages, post_message, list_messages
app = Flask(__name__)


@app.route('/')
def index():
    return 'I am a message server.'


@app.route('/messages/')
def message_list():
    messages = [m.to_dict() for m in list_messages()]
    return jsonify({'count': len(messages), 'messages': messages})


@app.route('/messages/search')
def message_search():
    search = request.args.get('search')
    if not search:
        messages = []
    else:
        messages = [m.to_dict() for m in search_messages(search)]

    return jsonify({'count': len(messages), 'messages': messages})


@app.route('/messages/post', methods=['POST'])
def message_post():
    m = post_message(request.form['user_id'], request.form['message'])
    return jsonify(**m.to_dict())


if __name__ == "__main__":
    app.run(debug=True, port=5001)
