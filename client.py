#!/usr/bin/python3 


from cocos.director import director
from cocos.layer import MultiplexLayer
from cocos.scene import Scene
from pyglet import font, resource

import log, audio, options, game
from menu import *


class GameClient:

    def __init__(self):

        resource.path.append('data')
        resource.reindex()
        font.add_directory('data/font')

        audio.init()
        options.init()
        director.init()

        self.scene = Scene(KaboomMultiplexLayer())

    def start(self):
        director.run(self.scene)


class GameLayer(Layer):

    is_event_handler = True

    def __init__(self):
        super().__init__()

        self.gvents = game.GventStore()
        self.schedule_interval(self.on_update, 1 / 2)

    def on_key_press(self, symbol, modifiers):

        log.debug("client.GameLayer.on_key_press:: sym, mod: {}, {}"
            .format(symbol, modifiers))
        
        
        
        return True

    def on_update(self, dt):
        pass

if __name__ == "__main__":
    client = GameClient()
    client.start()
