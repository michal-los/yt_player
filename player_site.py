from flask import Flask, render_template, jsonify, request
flask_app = Flask(__name__)


@flask_app.route("/")
def main_page():
    return render_template('main.html')


@flask_app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)
