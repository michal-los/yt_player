import os
from urllib import parse, request
from html.parser import HTMLParser
from multiprocessing import Process

import pafy


def play(video):
    player = "C:\\Program Files (x86)\\foobar2000\\foobar2000.exe"

    audio_url = ' "' + video.getbestaudio().url + '"'

    os.execv(player, [audio_url])


class ResultsParser(HTMLParser):
    data = []
    ids = []

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
                video_id = attribute[1][-11:]
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
    return parser.data


if __name__ == '__main__':
    _search_string = input("what do you look for? ")
    search_results = get_yt_search_results(_search_string)

    index = 0
    for result in search_results:
        print(index, ". ", result['title'])
        index += 1

    chosen_index = int(input("Which track do you wish to hear? "))
    chosen_video = pafy.new(search_results[chosen_index]['video_id'])
    play(chosen_video)
