import signal
import sys
import logging
from time import sleep

import zmq

from ytplayer import YouTubePlayer
from logger_configuration import configure_logger


# ---------------- INITIATING LOGGER ---------------
logger = configure_logger("youtube_player_service.log", logging.DEBUG)
logger.debug("Initializing service...")


class MyPlayer(YouTubePlayer):
    def __init__(self):
        self.logger = logger
        YouTubePlayer.__init__(self)

    def shutdown(self):
        logger.debug("SIGTERM initialized. Shutting down service...")
        self.stop()
        logger.debug("Goodnight.")
        sys.exit(0)

    def wait_for_command(self):
        zmq_socket = zmq.Context().socket(zmq.REP)
        zmq_socket.bind('tcp://*:7773')

        logger.debug("Waiting for control request.")
        control_data = zmq_socket.recv_pyobj()

        logger.debug("Received a data set. Executing control method.")
        try:
            if control_data['command'] == 'play':
                self.play(control_data['video_id'])
                zmq_socket.send_pyobj(self.now_playing)
            elif control_data['command'] == 'stop':
                self.stop()
                zmq_socket.send_pyobj(self.now_playing)
            elif control_data['command'] == 'get_status':
                zmq_socket.send_pyobj(self.now_playing)
            else:
                logger.error("Unknown command: '%s'" % control_data['command'])
        except Exception as err:
            logger.error(repr(err))


if __name__ == '__main__':
    logger.debug("Initiating player instance.")
    player = MyPlayer()
    logger.debug("Configuring SIGTERM signal handler.")
    signal.signal(signal.SIGTERM, player.shutdown)

    logger.debug("Initialized. Starting main loop.")
    while True:
        try:
            player.wait_for_command()
        except KeyboardInterrupt as e:
            logger.error(repr(e))
            break

        except Exception as e:
            logger.error(e.__class__.__name__ + " in line " + str(e.__traceback__.tb_lineno) + ": " + str(e))
            sleep(0.1)
