from threading import Condition
from queue import Queue


class Gvent:

    def __init__(self, actor, verb, args):
        self.actor = actor
        self.verb = verb
        self.args = args

    def from_string(string):
        actor, va = string.split("@")
        verb, args = va.split(":")
        args = args.split(",")
        return Gvent(actor, verb, args)

    def to_string(self):
        return "{}@{}:{}".format(actor, verb, ",".join(args))

    def __str__(self):
        return "Gvent({}, {}, {})".format(self.actor, self.verb, self.args)


class GventStore:

    def __init__(self):

        self.gvents = Queue()
        self.cv = Condition()

    def push(self, gevent):
        with self.cv:
            self.gvents.put(gevent)

    def pop(self):

        with self.cv:

            if self.gvents.empty():
                value = False

            else:
                value = self.gvents.get()

        return value

