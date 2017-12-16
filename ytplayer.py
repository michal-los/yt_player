from urllib import parse, request
from html.parser import HTMLParser
import subprocess
import platform

import pafy


def play(video_id):
    video = pafy.new(video_id)
    video_url = video.getbestaudio().url

    if platform.system() == "Windows":
        player = "C:\\Program Files (x86)\\foobar2000\\foobar2000.exe"
        player_command = [player, video_url]
    elif platform.system() == "Linux":
        player = "mplayer"
        player_command = [player, "-ao", "alsa:device=bluealsa", video_url]
    else:
        print("Unsupported OS: %s" % platform.system())
        return

    return subprocess.Popen(player_command)


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
    print(search_string)
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
    play_process = play(search_results[chosen_index]['video_id'])
    input("Press [Enter] to stop playback.")
    play_process.kill()
