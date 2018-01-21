# YouTube Music Player #

YouTube search tool and music player application.



### What is this repository for? ###

* Search tool is built on top of urllib and html.parser libraries.

* Player (yt_player.py) uses pafy library to extract audio stream url and video meta data, and spawns subprocess of specific music player - foobar on Windows platform and mplayer on Linux.
* Application is built to play music on Bluetooth speaker connected to Raspberry PI so the default Linux methods run mplayer with 'bluealsa' audio output.
* Player service (player_service.py) is designed to work as interface between the actual music player and the web user interface.
Its purpose is to work as systemd service and spawn player subprocess during the playback.
* Web service (player_site.py) works as user interface for the actual music player.

### Install and configure ###

* git clone https://github.com/Mirdalan/yt_player.git
* pip install -r requirements.txt 
* run yt_player.py to use command line player
* run player_service.py to start player service required for web interface
* player_site.py is a Flask based web interface
* player_site.service and player_daemon.service can be usedto create systemd services
* test_site.bat runs Flask site on Windows
