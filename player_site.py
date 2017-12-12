from flask import Flask, render_template, jsonify, request

from ytplayer import get_yt_search_results

flask_app = Flask(__name__)


@flask_app.route("/")
def main_page():
    search_results = []
    if request.args.get('search', None):
        search_phrase = request.args['search']
        search_results = get_yt_search_results(search_phrase)
    return render_template('main.html', display_results=(len(search_results) > 0), search_results=search_results)


@flask_app.route('/play_video')
def play_video():
    video_id = request.args.get('video_id', "no video ID", type=str)
    with open("status.txt", 'r') as status_log:
        previous_video_id = status_log.read()

    if previous_video_id == video_id:
        _status = "stopped"
    else:
        _status = "playing"

    with open("status.txt", 'w') as status_log:
        status_log.write(video_id)

    return jsonify(status=_status)
