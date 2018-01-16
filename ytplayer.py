from urllib import parse, request
from html.parser import HTMLParser
import subprocess
import platform
import time
import logging

import pafy

from logger_configuration import configure_logger


class YouTubePlayer:
    def __init__(self):
        self.logger = configure_logger("youtube_player_service.log", logging.DEBUG)
        self.logger.debug("Initializing service...")
        self.player_process = None
        self.now_playing = {
                'video_id': None,
                'title': None,
                'duration': None,
                'started_ts': None,
                'thumbnail': None,
                'status': 'stopped',
                'volume': 50,
            }

    def __del__(self):
        self.stop()

    def play(self, video_id):
        self.logger.debug("Creating pafy video object for id %s ." % video_id)
        video = pafy.new(video_id)
        self.logger.debug("Video object created. Extracting best audio url.")
        video_url = video.getbestaudio().url

        if platform.system() == "Windows":
            player = "C:\\Program Files (x86)\\foobar2000\\foobar2000.exe"
            player_command = [player, video_url]
        elif platform.system() == "Linux":
            player = "mplayer"
            player_command = [player, "-ao", "alsa:device=bluealsa", video_url]
        else:
            self.logger.error("Unsupported OS: %s" % platform.system())
            raise OSError

        self.logger.debug("Stopping previous instance.")
        self.stop()
        try:
            self.logger.debug("Spawning player subprocess.")
            self.player_process = subprocess.Popen(player_command)
            new_status = {
                'video_id': video.videoid,
                'title': video.title,
                'duration': video.duration,
                'started_ts': time.time(),
                'thumbnail': video.thumb,
                'status': 'playing',
            }
            self.now_playing.update(new_status)
            self.logger.debug("Now playing %s" % video.title)
        except Exception as e:
            self.logger.error("Error while starting player subprocess due to following exception:\n" + repr(e))

    def stop(self):
        try:
            self.player_process.kill()
            self.now_playing['status'] = 'stopped'
            self.logger.debug("Player process stopped.")
        except AttributeError:
            self.logger.debug("Could not kill - subprocess was not created.")

    def set_volume(self, volume):
        if platform.system() == "Windows":
            volume_options = {
                88: 'Set to -0 dB',
                76: 'Set to -3 dB',
                64: 'Set to -6 dB',
                52: 'Set to -9 dB',
                40: 'Set to -12 dB',
                28: 'Set to -15 dB',
                16: 'Set to -18 dB',
                4: 'Set to -21 dB',
            }
            volume_string = "Mute"
            for possible_volume, possible_volume_string in volume_options.items():
                if possible_volume < volume <= possible_volume + 12:
                    volume_string = possible_volume_string
                    break
            volume_command = [
                'C:\\Program Files (x86)\\foobar2000\\foobar2000.exe',
                '/command:' + volume_string
            ]
        elif platform.system() == "Linux":
            volume_command = [
                "amixer",
                "-D",
                "bluealsa",
                "sset",
                "'DANCER ROCK - A2DP'",
                str(volume) + "%"
            ]
        else:
            self.logger.error("Unsupported OS: %s" % platform.system())
            raise OSError

        try:
            subprocess.run(volume_command)
            self.now_playing['volume'] = volume
            self.logger.debug("Volume set to %d" % volume)
        except Exception as e:
            self.logger.error("Could not set volume due to following exception:\n" + repr(e))


class ResultsParser(HTMLParser):

    def reset(self):
        self.data = []
        self.ids = []
        HTMLParser.reset(self)

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        if 'title' not in [attr[0] for attr in attrs]:
            return
        video_id, title = None, None

        for attribute in attrs:
            if attribute[0] == 'href':
                if '/watch?v=' not in attribute[1]:
                    return
                id_pos = attribute[1].find('/watch?v=')+9
                video_id = attribute[1][id_pos:id_pos+11]
                if video_id in self.ids:
                    return

            if attribute[0] == 'title':
                title = attribute[1]

        self.ids.append(video_id)
        self.data.append({
            'title': title,
            'video_id': video_id
        })


def get_yt_search_results(search_string):
    query_string = parse.urlencode({"search_query": search_string})
    html_content = request.urlopen("http://www.youtube.com/results?" + query_string)
    encoding = html_content.getheader('Content-Type').split('charset=')[-1]
    results_html = html_content.read().decode(encoding)

    parser = ResultsParser()
    parser.feed(results_html)
    results = parser.data
    parser.reset()
    return results


if __name__ == '__main__':
    _search_string = input("what do you look for? ")
    search_results = get_yt_search_results(_search_string)

    index = 0
    for result in search_results:
        print(index, ". ", result['title'])
        index += 1

    chosen_index = int(input("Which track do you wish to hear? "))
    myplayer = YouTubePlayer()
    myplayer.play(search_results[chosen_index]['video_id'])
    input("Press [Enter] to stop playback.")
    myplayer.stop()
