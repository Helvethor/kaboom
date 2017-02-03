import time


def to_file(filename, smt):
    with open(filename, "a") as f:
        f.write("{}\n".format(smt))

def debug(smt):
    to_file("debug.log", smt)

def server(smt):
    to_file("server.log", smt)

def client(smt):
    to_file("client.log", smt)

def init():
    separation = " {} ".format(time.ctime()).center(80, "=")
    debug(separation)
    server(separation)
    client(separation)
