import signal
import sys
import logging
from time import sleep

import zmq

from ytplayer import YouTubePlayer


class MyPlayer(YouTubePlayer):

    def shutdown(self):
        self.logger.debug("SIGTERM initialized. Shutting down service...")
        self.stop()
        self.logger.debug("Goodnight.")
        sys.exit(0)

    def wait_for_command(self):
        zmq_socket = zmq.Context().socket(zmq.REP)
        zmq_socket.bind('tcp://*:7773')

        self.logger.debug("Waiting for control request.")
        control_data = zmq_socket.recv_pyobj()

        self.logger.debug("Received a data set. Executing control method.")
        try:
            if control_data['command'] == 'play':
                self.logger.debug("Received play command for video id %s ." % control_data['video_id'])
                self.play(control_data['video_id'])
                zmq_socket.send_pyobj(self.now_playing)
            elif control_data['command'] == 'stop':
                self.stop()
                zmq_socket.send_pyobj(self.now_playing)
            elif control_data['command'] == 'set_volume':
                self.set_volume(control_data['volume'])
                zmq_socket.send_pyobj(self.now_playing)
            elif control_data['command'] == 'get_status':
                zmq_socket.send_pyobj(self.now_playing)
            else:
                self.logger.error("Unknown command: '%s'" % control_data['command'])
                zmq_socket.send_pyobj(self.now_playing)
        except Exception as err:
            self.logger.error("Error while executing player command due to following exception:\n" + repr(err))
            zmq_socket.send_pyobj(self.now_playing)


if __name__ == '__main__':
    player = MyPlayer()
    player.logger.debug("Configuring SIGTERM signal handler.")
    signal.signal(signal.SIGTERM, player.shutdown)

    player.logger.debug("Initialized. Starting main loop.")
    while True:
        try:
            player.wait_for_command()
        except KeyboardInterrupt as e:
            player.logger.error(repr(e))
            break

        except Exception as e:
            player.logger.error(e.__class__.__name__ + " in line " + str(e.__traceback__.tb_lineno) + ": " + str(e))
            sleep(0.1)
