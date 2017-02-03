#!/usr/bin/python3 

from cocos.director import director
from pyglet import font, resource

import audio, client, server, options, log


def main():

    resource.path.append('data')
    resource.reindex()
    font.add_directory('data/font')

    log.init()
    audio.init()
    client.init()
    server.init()
    options.init()
    director.init()

    clt = client.GameClient()
    clt.start()
    clt.stop()


if __name__ == "__main__":
    main()
