#!/usr/bin/python3 


import socket, socketserver, threading

import log
from game import *


ip = "127.0.0.1"
port = 31415


def get_ip():
    return ip

def set_ip(value):
    ip = value


class GameServer:

    def __init__(self):

        self.running = False
        self.gvents = GventStore()

        self.server = socketserver.ThreadingTCPServer(
            ("localhost", port), KaboomRequestHandler)
        self.server.gvents = self.gvents

    def start(self):

        self.start_threads()
        self.running = True

        try:
            while self.running:

                gevent = self.gvents.pop()
                if gevent:
                    print(gevent)

        except Exception as e:
            print(e)

        self.stop()

    def start_threads(self):

        self.threads = []
        
        for _ in range(4):
            thread = threading.Thread(target = self.server.serve_forever)
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
 
    def stop(self):

        if self.running:
            self.server.shutdown()
            self.server.server_close()
            self.running = False


class KaboomRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        
        data = self.request.recv(1024).decode()
        log.server("server.KaboomRequestHandler:: recv: {}".format(data))

        gevent = Gvent.from_string(data)
        self.server.gvents.push(gevent)

        cur_thread = threading.current_thread()
        response = "{}: {}".format(cur_thread, data).encode()
        self.request.sendall(response)
        log.server("server.KaboomRequestHandler:: send: {}".format(response.decode()))

def client(addr, message):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)

    try:
        sock.sendall(message.encode())
        log.server("server.client:: send: {}".format(message))
        response = sock.recv(1024).decode()
        log.server("server.client:: recieve: {}".format(response))

    finally:
        sock.close()


def main():
    game_server = GameServer()
    game_server.start()

if __name__ == "__main__":
    main()
