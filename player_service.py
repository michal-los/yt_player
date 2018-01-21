import signal
import sys
from time import sleep

import zmq

from ytplayer import YouTubePlayer


class MyPlayer(YouTubePlayer):
    """
    Player class adjusted to work as service and receive commands via zeroMQ.
    """
    def shutdown(self):
        """
        Stops player subprocess before shutting down main service.
        """
        self.logger.debug("SIGTERM initialized. Shutting down service...")
        self.stop()
        self.logger.debug("Goodnight.")
        sys.exit(0)

    def wait_for_command(self):
        """
        Main player control method.
        Receives ZeroMQ messages with commands and controls the player subprocess.
        """
        zmq_context = zmq.Context()
        zmq_socket = zmq_context.socket(zmq.REP)
        zmq_socket.bind('tcp://*:7773')

        self.logger.debug("Waiting for control request.")
        control_data = zmq_socket.recv_pyobj()

        self.logger.debug("Received a data set. Executing control method.")
        try:
            if control_data['command'] == 'play':
                self.logger.debug("Received play command for video id %s ." % control_data['video_id'])
                self.play(control_data['video_id'])
                zmq_socket.send_pyobj(self.get_status())
            elif control_data['command'] == 'stop':
                self.stop()
                zmq_socket.send_pyobj(self.get_status())
            elif control_data['command'] == 'pause':
                self.pause()
                zmq_socket.send_pyobj(self.get_status())
            elif control_data['command'] == 'set_volume':
                self.set_volume(control_data['volume'])
                zmq_socket.send_pyobj(self.get_status())
            elif control_data['command'] == 'get_status':
                zmq_socket.send_pyobj(self.get_status())
            else:
                self.logger.error("Unknown command: '%s'" % control_data['command'])
                zmq_socket.send_pyobj(self.get_status())
        except Exception as err:
            self.logger.error("Error while executing player command due to following exception:\n" + repr(err))
            zmq_socket.send_pyobj(self.get_status())

    def run_service(self):
        """
        Main loop method that runs the player control method in a loop and handles interrupts.
        """
        self.logger.debug("Initialized. Starting main loop.")
        while True:
            try:
                self.wait_for_command()
            except KeyboardInterrupt as e:
                self.logger.error(repr(e))
                break

            except Exception as e:
                self.logger.error(e.__class__.__name__ + " in line " + str(e.__traceback__.tb_lineno) + ": " + str(e))
                sleep(0.1)


if __name__ == '__main__':
    player = MyPlayer()
    player.logger.debug("Configuring SIGTERM signal handler.")
    signal.signal(signal.SIGTERM, player.shutdown)
    player.run_service()
