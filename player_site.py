from flask import Flask, render_template, jsonify, request
import zmq

from ytplayer import get_yt_search_results

flask_app = Flask(__name__)


def command_player(control_data):
    """
    Sends control command with related data to player service.
    :param control_data: Control command and related data dictionary.
    :return: Player status received as feedback from player.
    """
    zmq_socket = zmq.Context().socket(zmq.REQ)
    try:
        zmq_socket.connect("tcp://localhost:7773")
    except zmq.error.ZMQError as e:
        print("tcp://localhost:7773" + str(e))
        return
    zmq_socket.send_pyobj(control_data)
    return zmq_socket.recv_pyobj()


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

    player_status = command_player({'command': 'get_status'})
    if player_status['status'] == 'playing' and player_status['video_id'] == video_id:
        player_command = {'command': 'stop'}
    else:
        player_command = {
            'command': 'play',
            'video_id': video_id
        }

    player_status = command_player(player_command)

    return jsonify(player_status)


@flask_app.route('/set_volume')
def set_volume():
    volume = request.args.get('volume', "no video ID", type=int)
    player_command = {
        'command': 'set_volume',
        'volume': volume
    }

    return jsonify(command_player(player_command))


@flask_app.route('/get_status')
def get_status():
    return jsonify(command_player({'command': 'get_status'}))


@flask_app.route('/stop_video')
def stop_video():
    return jsonify(command_player({'command': 'stop'}))
