import signal
import sys
from time import sleep

import zmq

from ytplayer import play
from logger_configuration import configure_logger


# ---------------- INITIATING LOGGER ---------------
logger = configure_logger("youtube_player_service.log")
logger.debug("Initializing service...")


# ---------------- WAIT FOR REQUEST FUNCTION ---------------
def get_control_data():
    zmq_socket = zmq.Context().socket(zmq.REP)
    zmq_socket.bind('tcp://*:7773')
    return zmq_socket.recv_pyobj()


if __name__ == '__main__':
    logger.debug("Initiating player instance.")
    previous_video_id = ''
    playing_process = None
    # logger.debug("Configuring SIGTERM signal handler.")
    # signal.signal(signal.SIGTERM, dimmers_control.systemd_shutdown)

    logger.debug("Initialized. Starting main loop.")
    while True:
        try:
            logger.debug("Waiting for control request.")
            control_data = get_control_data()
            logger.debug("Received a data set. Executing control method.")
            try:
                playing_process.kill()
            except AttributeError:
                logger.info("Could not kill - subprocess was not created.")
            if control_data['video_id'] == previous_video_id:
                previous_video_id = ''
            else:
                playing_process = play(control_data['video_id'])
                previous_video_id = control_data['video_id']

        except KeyboardInterrupt as e:
            logger.error(repr(e))
            break

        except Exception as e:
            logger.error(e.__class__.__name__ + " in line " + str(e.__traceback__.tb_lineno) + ": " + str(e))
            sleep(0.1)
