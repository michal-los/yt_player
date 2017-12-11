from flask import Flask, render_template
flask_app = Flask(__name__)


@flask_app.route("/")
def main_page():
    return render_template('main.html')
