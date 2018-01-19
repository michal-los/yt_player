import unittest
from unittest.mock import patch, MagicMock

from player_service import MyPlayer


class MockZmq(MagicMock):

    def socket(self, *args):
        return self


class PlayerServiceTestCase(unittest.TestCase):

    @patch('zmq.Context')
    def test_sends_play_command(self, MockZmq):
        player = MyPlayer()
        player.wait_for_command()
        self.assertEqual(player.status_meta_data['status'], "playing")


if __name__ == '__main__':
    unittest.main()
