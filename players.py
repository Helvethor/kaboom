from pyglet.window import key

max_players = 4
nb_players = 1
names = ["P1", "P2", "P3", "P4"]
keybindings = [
    {
        'UP':       key.W,
        'DOWN':     key.S,
        'LEFT':     key.A,
        'RIGHT':    key.D,
        'BOMB':     key.Q,
        'SPECIAL':  key.E
    },
    {
        'UP':       key.UP,
        'DOWN':     key.DOWN,
        'LEFT':     key.LEFT,
        'RIGHT':    key.RIGHT,
        'BOMB':     key.RCTRL,
        'SPECIAL':  key.NUM_0
    },
    {
        'UP':       key.I,
        'DOWN':     key.K,
        'LEFT':     key.J,
        'RIGHT':    key.L,
        'BOMB':     key.U,
        'SPECIAL':  key.O
    },
    {
        'UP':       key.NUM_8,
        'DOWN':     key.NUM_5,
        'LEFT':     key.NUM_4,
        'RIGHT':    key.NUM_6,
        'BOMB':     key.NUM_7,
        'SPECIAL':  key.NUM_9
    }
]


def get_keys():
    return keybindings[0].keys()

def get_keybinding(idx, key):
    return keybindings[int(idx)][key]

def set_keybinding(value, idx, key):
    keybindings[int(idx)][key] = int(value)

def get_idxs():
    return range(max_players)

def get_name(idx):
    return names[idx]


class Player:

    def __init__(self, ):
        self.idx = self.count
        self.count += 1
        self.Keybindings = keybindings[self.idx]

    def get_idx(self):
        return idx

    def get_keybindings(self):
        return self.Keybindings

