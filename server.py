#!/usr/bin/python3 


import socket, socketserver, threading, sys, traceback, pickle

import log
from game import *


description = None


class GameServer(socketserver.ThreadingUDPServer):

    def __init__(self):
        init(sys.argv[1])
        super().__init__(("", description.get_port()), GameRequestHandler)

        self.running = False

        self.wm = None
        self.messages = SharedList()
        self.players = SharedList()
        
        log.server("server.GameServer.__init__:: description: {}"
            .format(description.to_string()))

    def start(self):

        self.load_map()
        self.start_threads()
        self.run()

    def run(self):

        self.running = True

        try:
            while self.running:
                pass

        except Exception as e:
            log.server("server.start:: exception: {}".format(e))

        self.stop()

    def load_map(self):
        self.wm = WorldMap(description.get_mapname())
        log.server("server.GameServer.load_map:: map: {}"
            .format(self.wm.get_name()))

    def start_threads(self):

        self.threads = []
        
        for _ in range(description.get_max_players()):
            thread = threading.Thread(target = self.serve_forever)
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
 
    def stop(self):

        if self.running:
            self.shutdown()
            self.running = False

    def reply_message(self, message):

        verb = message.get_verb()

        try:
            handler = eval("self.reply_{}".format(verb))

        except Exception as e:
            log.server("server.GameServer.reply_message:: exception: {}"
                .format(e))
            return Message("error", "Unhandled message class")

        try:
            return handler(message)

        except Exception as e:
            log.server("server.GameServer.reply_message:: exception: {}"
                .format(traceback.format_exc()))
            return Message("error", "Message handling error")

    def reply_players(self, message):
        players = message.get_data()

        self.players.acquire()
        registered = self.players.length()

        if len(players) <= description.max_players - registered:

            idss = range(registered, registered + len(players))
            for idc, ids in enumerate(idss):
                players[idc].set_ids(ids) 
                players[idc].set_pos(self.wm.get_starts()[ids])

            log.server("server.GameServer.reply_players:: players: {}"
                .format(players))

            [self.players.push(p) for p in players]

        else:
            players = []

        self.players.release()

        return Message("players", players)

    def reply_world_map(self, message):
        log.server("server.GameServer.reply_world_map:: map: {}"
            .format(self.wm))
        return Message("world_map", self.wm)

    def get_player(self, ids):
        return self.players[ids]

    def get_players(self):
        return self.players

    def get_nb_players(self):
        return len(self.players)



class GameRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):

        try:
            message = pickle.loads(self.request[0])
            socket = self.request[1]
            #log.server("server.GameRequestHandler:: recv: {}'"
            #    .format(message))

            self.server.messages.push(message)
            response = pickle.dumps(self.server.reply_message(message))

            socket.sendto(response, self.client_address)
            #log.server("server.GameRequestHandler:: send: {}"
            #    .format(response))

        except Exception as e:
            log.server("server.GameRequestHandler.handler:: exception: {}"
                .format(traceback.format_exc()))


class ServerDescription:

    def __init__(self):
        self.max_players = 4
        self.owner = None
        self.mapname = "classic"
        self.port = 31415
        self.pid = None

    def to_string(self):
        return repr({
            "max_players":  self.max_players,
            "owner":        self.owner,
            "mapname":      self.mapname,
            "port":         self.port,
            "pid":          self.pid
        })

    def from_string(string):
        data = eval(string)
        d = ServerDescription()

        d.max_players   = data["max_players"]
        d.owner         = data["owner"]
        d.mapname       = data["mapname"]
        d.port          = data["port"]
        d.pid           = data["pid"]

        return d
    
    def get_max_players(self):
        return self.max_players

    def set_max_players(self, value):
        self.max_players = int(value)

    def get_owner(self):
        return self.owner

    def set_owner(self, value):
        self.owner = value

    def get_mapname(self):
        return self.mapname

    def set_mapname(self, value):
        self.mapname = value

    def get_port(self):
        return self.port

    def set_port(self, value):
        self.port = int(value)

    def get_pid(self):
        return pid

    def set_pid(self, value):
        self.pid = value


def init(string = None):
    global description

    if string == None:
        description = ServerDescription()
    else:
        description = ServerDescription.from_string(string)
