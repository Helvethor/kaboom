import os, json
from threading import Condition
from queue import Queue
from itertools import product

import log, players, client, server


class Message:

    encoder = json.JSONEncoder()
    decoder = json.JSONDecoder()

    def __init__(self, data):
        if "identity" not in data:
            try:
                data["identity"] = client.description.get_identity()
            except:
                data["identity"] = server.description.get_owner()

        data["cls"] = ".".join(str(type(self)).split("'")[1].split('.')[1:])[:-7]
        self.data = data

    def __str__(self):
        return self.to_string()

    def get_data(self):
        return self.data

    def get_identity(self):
        return self.get("identity")

    def get_cls(self):
        return self.get("cls")

    def get(self, key):
        return self.data.get(key)

    def from_data(data):
        return Message(data)

    def from_string(string):
        data = __class__.decoder.decode(string)
        cls = data.get("cls")
        return eval("{}Message.from_data".format(cls))(data)

    def to_string(self):
        return self.encoder.encode(self.data)


class PlayersMessage(Message):

    def __init__(self, players):
        data = {
            "players": [p.get_data() for p in players]
        }
        super().__init__(data)


    def from_data(data):
        return PlayersMessage([Player.from_data(p)
            for p in data.get("players")])

    def get_players(self):
        return [Player.from_data(p) for p in self.get("players")]


class WorldMapMessage(Message):

    def __init__(self, wm = None):

        if wm is None:
            wm_data = None
        else:
            wm_data = wm.get_data()

        data = {
            "wm": wm_data
        }
        super().__init__(data)

    def from_data(data):
        return WorldMapMessage(WorldMap.from_data(data.get("wm")))


class KeyPressMessage(Message):

    def __init__(self, symbol, modifiers):
        data = {
            "symbol": symbol,
            "modifiers": modifiers
        }
        super().__init__(data)


class ErrorMessage(Message):

    def __init__(self, content):
        data = {
            "content": content
        }
        super().__init__(data)

    def get_content(self):
        return self.get("content")

    def from_data(data):
        return ErrorMessage(data.get("content"))


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
        return repr(self.get_data())

    def __repr__(self):
        return self.__str__()

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

    def get_data(self):
        return {
            "ids": self.get_ids(),
            "idc": self.get_idc(),
            "name": self.get_name(),
            "pos": self.get_pos()
        }

    def from_data(data):
        return Player(
            ids = data["ids"],
            idc = data["idc"],
            name = data["name"],
            pos = data["pos"]
        )


class WorldMap:

    file_dir = "data/map/"
    file_extension = "map"

    def __init__(self, mapname, walls = None, bricks = None, starts = None):

        if walls is None or bricks is None or starts is None:
            self.file_init(mapname)

        else:
            self.name = mapname
            self.walls = walls
            self.bricks = bricks
            self.starts = starts

    def file_init(self, mapname):

        with open("{}/{}.{}".format(self.file_dir, mapname, self.file_extension), "r") as f:
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

    def from_data(data):
        log.server("data: {}".format(data))
        return WorldMap(
            data.get("name"),
            data.get("walls"),
            data.get("bricks"),
            data.get("starts")
        )

    def get_data(self):
        return {
            "name": self.get_name(),
            "walls": self.get_walls(),
            "bricks": self.get_bricks(),
            "starts": self.get_starts()
        } 

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

