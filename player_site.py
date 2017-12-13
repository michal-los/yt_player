from flask import Flask, render_template, jsonify, request
import zmq

from ytplayer import get_yt_search_results

flask_app = Flask(__name__)


def request_playback(control_data):
    zmq_client = zmq.Context().socket(zmq.REQ)
    try:
        zmq_client.connect("tcp://localhost:7773")
    except zmq.error.ZMQError as e:
        print("tcp://localhost:7773" + str(e))
        return
    zmq_client.send_pyobj(control_data)


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

    with open("status.txt", 'w') as status_log:
        if previous_video_id == video_id:
            _status = "stopped"
        else:
            _status = "playing"
            status_log.write(video_id)

    request_playback({'video_id': video_id})

    return jsonify(status=_status)
