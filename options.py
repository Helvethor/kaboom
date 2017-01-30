import os.path

import log, audio, players, server


filename = "options.txt"
references = [
    "server:ip",
    "audio.music:volume",
    "audio.sound:volume"
] + [
    "players:keybinding@{},{}".format(idx, key)
    for idx in range(4) for key in players.get_keys()
]


def init():
    if os.path.isfile(filename):
        load()

def save():
    with open(filename, "w") as f:
        for ref in references:
            line = "{}={}".format(ref, get_ref(ref))
            log.debug("options.save:: line: {}".format(line))
            f.write(line + "\n")

def load():

    with open(filename, "r") as f:
        for line in f.read().split("\n"):

            if line == '':
                continue

            log.debug("options.load:: line: {}".format(line))
            ref, value = line.split("=")
            set_ref(ref, value)

def get_ref(ref):

    obj, attr = ref.split(":")
    args = []

    if "@" in attr:
        attr, args = attr.split("@")
        args = args.split(",")

    return eval("{}.get_{}(*{})".format(obj, attr, args))

def set_ref(ref, value):

    obj, attr = ref.split(":")
    args = []

    if "@" in attr:
        attr, args = attr.split("@")
        args = args.split(",")

    args = [value] + args
    
    command = "{}.set_{}(*{})".format(obj, attr, args)
    log.debug("options.set_ref:: command: {}".format(command))

    return eval(command)
