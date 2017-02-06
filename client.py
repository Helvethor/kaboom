#!/usr/bin/python3 

import socket, time, subprocess, random, string, hashlib, signal, os

from cocos.director import director
from cocos.layer import MultiplexLayer
from cocos.scene import Scene

import log, audio, options, players
from menu import *
from game import *


description = None
game_client = None


class GameClient:

    def __init__(self):
        global game_client
        game_client = self

        self.scene = Scene(MenuMultiplexLayer())
        log.client("client.GameClient.__init__:: description: {}"
            .format(client.description.to_string()))

    def start(self):
        director.run(self.scene)

    def stop(self):
        stop_server()

    def send_recv(self, message, retry = 5):

        if retry == 0:
            director.scene.end("No response from server")
            return None

        socket, addr = self.server

        try:
            request = pickle.dumps(message)
            #log.client("game.Message.send_recv:: sendto: {}".format(request))
            socket.sendto(request, addr)

            socket.settimeout(2)
            response = pickle.loads(socket.recv(1024))
            #log.client("game.Message.send_recv:: recv: {}".format(response))

        except:
            response = self.send_recv(message, retry - 1)

        return response

    def request_players(self):

        pls = [Player(idc = idc, name = players.get_name(idc))
            for idc in range(description.get_nb_players())]

        message = self.send_recv(Message("players", pls))
        pls = message.get_data()

        if len(pls) != description.get_nb_players():
            log.client("client.GameScene.request_players:: end")
            director.scene.end("Not enough players returned")

        return pls

    def request_world_map(self):
        message = self.send_recv(Message("world_map", None))
        return message.get_data()


class GameScene(Scene):

    is_event_handler = True

    def __init__(self):
        super().__init__()

        self.schedule_interval(self.on_update, 1 / 2)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server = (self.socket,(
            description.get_server_ip(),
            server.description.get_port()
        ))
        game_client.server = self.server
        
    def on_enter(self):

        director.window.push_handlers(self)

        self.players = game_client.request_players()
        log.client("client.GameScene.on_enter:: players: {}"
            .format(self.players))

        self.wm = game_client.request_world_map()
        log.client("client.GameScene.on_enter:: world_map: {}"
            .format(self.wm))

    def on_exit(self):
        director.window.remove_handlers(self)

    def on_key_press(self, symbol, modifiers):

        log.client("client.GameScene.on_key_press:: sym, mod: {}, {}"
            .format(symbol, modifiers))

        t0 = time.time()
        response = game_client.send_recv(Message("key_press", (symbol, modifiers)))
        t1 = time.time()
        log.client("client.GameScene.on_key_press:: time: {}".format(t1 - t0))
        
        return True

    def on_update(self, dt):
        pass


class ClientDescription:

    def __init__(self):
        self.nb_players = 4
        self.identity = None
        self.server_ip = "127.0.0.1"

    def to_string(self):
        return repr({
            "nb_players":   self.nb_players,
            "identity":     self.identity,
            "server_ip":    self.server_ip
        })

    def from_string(string):
        data = eval(string)
        d = ServerDescription()

        d.nb_players    = data["nb_players"]
        d.identity      = data["identity"]
        d.server_ip     = data["server_ip"]

        return d
 
    def get_nb_players(self):
        return self.nb_players

    def set_nb_players(self, value):
        self.nb_players = int(value)

    def get_identity(self):

        if self.identity == None:
            m = hashlib.sha256()
            m.update("".join(random.sample(string.printable, 20)).encode())
            self.identity = m.hexdigest()[:10]

        return self.identity

    def set_identity(self, value):
        self.identity = value

    def get_server_ip(self):
        return self.server_ip

    def set_server_ip(self, value):
        self.server_ip = value


def init():
    global description
    description = ClientDescription()


def start_server():

    server.description.set_owner(description.get_identity())
    description.set_server_ip("127.0.0.1")

    server_process = subprocess.Popen(
        ["python3", "server_run.py", server.description.to_string()])
    log.client("client.start_server:: subprocess: {}"
        .format(server_process.pid))

    server.description.set_pid(server_process.pid)

def stop_server():
    pid = server.description.get_pid()
    if  pid != None:
        log.client("client.stop_server:: subprocess: {}"
                .format(pid))
        os.kill(pid, signal.SIGTERM)
