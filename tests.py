import unittest
from unittest.mock import patch, MagicMock

from player_service import MyPlayer


class MockZmq(MagicMock):

    def socket(self, *args):
        return self


def recv_play():
    return {
        'command': 'play',
        'video_id': ''
    }


class PlayerServiceTestCase(unittest.TestCase):

    @patch('zmq.Context')
    @patch('zmq.sugar.socket.Socket.recv_pyobj')
    @patch('player_service.MyPlayer.play')
    def test_sends_play_command(self, MockZmq, recv_play, MagicMock):
        player = MyPlayer()
        player.wait_for_command()
        self.assertEqual(player.status_meta_data['status'], "playing")


if __name__ == '__main__':
    unittest.main()
