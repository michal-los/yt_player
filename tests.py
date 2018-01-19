import unittest
from unittest.mock import patch, Mock

from player_service import MyPlayer


class PlayerServiceTestCase(unittest.TestCase):

    @patch('zmq.sugar.socket.Socket')
    def test_sends_play_command(self, zmq_socket):
        player = MyPlayer()
        player.wait_for_command()


if __name__ == '__main__':
    unittest.main()
