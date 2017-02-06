import os, json, pickle
from threading import Condition
from queue import Queue
from itertools import product

import log, players, client, server


class Message:

    def __init__(self, verb, data):
        try:
            self.identity = client.description.get_identity()
        except:
            self.identity = server.description.get_owner()

        self.verb = verb
        self.data = data

    def __str__(self):
        return "Message({}, {}, {})".format(self.verb, self.identity, self.data)

    def __repr__(self):
        return str(self)

    def get_data(self):
        return self.data

    def get_identity(self):
        return self.identity

    def get_verb(self):
        return self.verb


class SharedList:

    def __init__(self):

        self.items = []
        self.cv = Condition()

    def push(self, item):
        self.items.append(item)

    def pop(self):
        try:
            return self.items.pop()
        except:
            return None

    def length(self):
        with self.cv:
            length = len(self.items)
        return length

    def acquire(self):
        self.cv.acquire()

    def release(self):
        self.cv.release()


class Player:

    def __init__(self, ids = None, idc = None, name = None, pos = None):

        self.ids = ids
        self.idc = idc
        self.name = name
        self.pos = pos
        self.keybindings = None 

    def __str__(self):
        return ("Player({}, {}, {}, {})"
            .format(self.ids, self.idc, self.name, self.pos))

    def __repr__(self):
        return str(self)

    def get_ids(self):
        return self.ids

    def set_ids(self, value):
        self.ids = value

    def get_idc(self):
        return self.idc

    def get_name(self):
        return self.name

    def set_pos(self, value):
        self.pos = value

    def get_pos(self):
        return self.pos

    def set_keybindings(self, keybindings):
        self.keybindings = keybindings

    def get_keybindings(self):
        return self.keybindings


class WorldMap:

    file_dir = "data/map/"
    file_extension = "map"

    def __init__(self, mapname, walls = None, bricks = None, starts = None):

        path = "{}/{}.{}".format(self.file_dir, mapname, self.file_extension)
        with open(path, "r") as f:
            wm = [list(map(str.strip, line.split(",")))
                for line in f.read().split('\n')[:-1]]

        #log.debug("game.WorldMap.__init__:: wm: {}".format(wm))

        self.name = mapname
        self.walls = set()
        self.bricks = set()
        self.starts = []

        for x, y in product(range(len(wm[0])), range(len(wm))):
            #log.debug("game.WorldMap.__init__:: x, y: {}, {}".format(x, y))
            if wm[y][x] == 'W':
                self.walls.add((x, y))
            elif wm[y][x] == 'B':
                self.bricks.add((x, y))
            elif wm[y][x] == 'S':
                self.starts.append((x, y))

    def __str__(self):
        return ("WorldMap({}, {}, {}, {})"
            .format(self.name, len(self.walls), len(self.bricks), len(self.starts)))

    def get_collidables(self):
        return self.walls.union(self.bricks)

    def get_bricks(self):
        return self.bricks

    def get_walls(self):
        return self.walls

    def get_starts(self):
        return self.starts

    def get_name(self):
        return self.name

    def list_files():
        return [f[:-4] for f in os.listdir(__class__.file_dir)
            if f.endswith(__class__.file_extension)]

