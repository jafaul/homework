import random
import string
from datetime import datetime

from flask import Flask, request, Response, jsonify

app = Flask(__name__)


@app.route('/whoami/', methods=['GET'])
def whoami():
    return {
        "user_agent": request.headers.get('User-Agent'),
        "IP": request.remote_addr,
        "timestamp": datetime.now().isoformat()
    }


@app.route('/source_code/')
def source_code():
    with open("app.py", "r") as file:
        content = file.read()
        return Response(content, mimetype='text/python')


# /random?length=42&specials=1&digits=0
@app.route('/random')
def get_random_string():
    length = request.args.get('length', default=8, type=int)
    specials = request.args.get('specials', default=0, type=int)
    digits = request.args.get('digits', default=0, type=int)

    if length > 100 or length < 1:
        return jsonify("Length must be between 1 and 100"), 400
    if specials not in {0, 1}:
        return jsonify("Specials must be 0 or 1"), 400
    if digits not in {0, 1}:
        return jsonify("Digits must be 0 or 1"), 400

    all_characters = string.ascii_letters
    if specials: all_characters += string.punctuation
    if digits: all_characters += string.digits

    return ''.join(random.choices(all_characters, k=length))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")