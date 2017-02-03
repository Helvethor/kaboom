import socket, string

import pyglet
from pyglet.window import key
from cocos.director import director
from cocos.layer.base_layers import *
from cocos.scene import Scene
from cocos.menu import *
from cocos.actions import *

import log, audio, options, players, server, client, game


class MenuMultiplexLayer(Layer):

    def __init__(self):

        self.layers = {
            'main':     MainMenu(),
            'play':     PlayMenu(),
            'local':    LocalMenu(),
            'network':  NetworkMenu(),
            'join':     JoinMenu(),
            'host':     HostMenu(),
            'options':  OptionsMenu(),
            'players':  PlayersMenu(),
        }

        super().__init__()
        self.add(self.layers["main"], name = "main")
        self.stack = ["main"]


    def step_in(self, name):

        if name not in self.layers.keys():
            raise Exception("MenuMultiplexLayer: Layer name not found")

        self.remove(self.stack[-1])
        self.stack.append(name)
        self.add(self.layers[name], name = name)

    def step_out(self):
        self.remove(self.stack.pop())
        name = self.stack[-1]
        self.add(self.layers[name], name = name)

    def add_layer(self, layer, name):

        if name in self.layers.keys():
            raise Exception("MenuMultiplexLayer: Layer name already exists")

        self.layers[name] = layer

    def remove_layer(self, name):

        if name not in self.layers.keys():
            raise Exception("MenuMultiplexLayer: Layer name not found")

        del self.layers[name]


class GameMenu(Menu):

    def __init__(self):
        super().__init__("KabOOm!")

        font = "Upheaval TT (BRK)"

        self.font_title = {
            'font_name': font,
            'color': (204,164,164,255),
            'font_size': 72,
            'anchor_x': CENTER,
            'anchor_y': TOP
        }

        self.font_item  = {
            'font_name':  font,
            'color':  (32,16,32,255),
            'font_size':  28
        }

        self.font_item_selected = {
            'font_name':  font,
            'color':  (32,54,32,255),
            'font_size':  32
        }

        self.menu_halign = LEFT
        self.menu_valign = CENTER
        self.menu_vmargin = 30
        self.menu_hmargin = 50

    def on_quit(self):
        self.parent.step_out()

    def create_menu(self, items, **kwargs):
        
        if "selected_effect" not in kwargs:
            pass
            #kwargs["selected_effect"] = shake()
            #kwargs["selected_effect"] = Place((self.x + 20, self.y))

        if "unselected_effect" not in kwargs:
            pass
            #kwargs["unselected_effect"] = shake_back()
            #kwargs["unselected_effect"] = Place((self.x - 20, self.y))

        super().create_menu(items, **kwargs)


class MainMenu(GameMenu):

    def __init__(self):
        super().__init__()

        items = [
            MenuItem("Play", self.on_play),
            MenuItem("Options", self.on_options),
            MenuItem("Quit", self.on_quit)
        ]

        self.create_menu(items)


    def on_play(self):
        self.parent.step_in("play")

    def on_options(self):
        self.parent.step_in("options")

    def on_quit(self):
        pyglet.app.exit()


class PlayMenu(GameMenu):

    def __init__(self):
        super().__init__()

        items = [
            MenuItem("Local", self.on_local),
            MenuItem("Network", self.on_network)
        ]

        self.create_menu(items)

    def on_local(self):
        self.parent.step_in("local")

    def on_network(self):
        self.parent.step_in("network")


class LocalMenu(GameMenu):

    def __init__(self):
        super().__init__()

        items = [
            MultipleMenuItem(
                "Players: ",
                self.on_players,
                ["2", "3", "4"]
            ),
            MenuItem("Start", self.on_start)
        ]

        self.create_menu(items)

    def on_players(self, idx):
        players.set_nb_players(idx + 2)
        return True

    def on_start(self):
        return True


class NetworkMenu(GameMenu):

    def __init__(self):
        super().__init__()

        items = [
            MenuItem("Join", self.on_join),
            MenuItem("Host", self.on_host)
        ]

        self.create_menu(items)

    def on_join(self):
        self.parent.step_in("join")

    def on_host(self):
        self.parent.step_in("host")


class JoinMenu(GameMenu):

    def __init__(self):
        super().__init__()

        self.ip_item = EntryMenuItem(
            "Host IP: ", 
            self.on_ip,
            client.description.get_server_ip()
        )

        items = [
            self.ip_item,
            MenuItem("Start", self.on_start)
        ]

        self.create_menu(items)

    def on_ip(self, ip):

        filtered = filter(lambda ch: ch in "0123456789.", ip)
        blocks = ''.join(filtered).split(".")

        if len(blocks) > 4:
            blocks = blocks[:4]
        blocks = [b if len(b) <= 3 else b[:3] for b in blocks]
        
        self.ip_item.value = '.'.join(blocks)

        log.debug("menu.JoinMenu.on_connect:: ip, blocks: {}, {}"
            .format(ip, blocks))

    def on_start(self):

        try:
            socket.inet_aton(self.ip_item.value)
        except:
            return

        client.description.set_nb_players(1)
        client.description.set_server_ip(self.ip_item.value) 
        options.save()
        log.client("menu.JoinMenu.on_start:: scene_stack: {}".format(director.scene_stack))
        director.push(client.GameScene())


class HostMenu(GameMenu):

    def __init__(self):
        super().__init__()

        self.maps = game.WorldMap.list_files()

        items = [
            MultipleMenuItem("Players: ", self.on_players, ["2", "3", "4"]),
            MultipleMenuItem("Map: ", self.on_map, self.maps),
            MenuItem("Start", self.on_start)
        ]

        self.create_menu(items)

    def on_players(self, idx):
        server.description.set_max_players(idx + 2)

    def on_map(self, idx):
        server.description.set_mapname(self.maps[idx])

    def on_start(self):
        client.start_server()
        client.description.set_nb_players(1)
        director.push(client.GameScene())

class OptionsMenu(GameMenu):

    def __init__(self):
        super().__init__()

        items = [
            MultipleMenuItem(
                "Music volume: ",
                self.on_music_volume,
                audio.music.get_volumes(),
                audio.music.get_volume()
            ),
            MultipleMenuItem(
                "Sound: ",
                self.on_sound_volume,
                audio.sound.get_volumes(),
                audio.sound.get_volume()
            ),
            MenuItem("Players", self.on_players)
        ]

        self.create_menu(items)

    def on_music_volume(self, idx):
        audio.music.set_volume(idx)

    def on_sound_volume(self, idx):
        audio.sound.set_volume(idx)

    def on_players(self):
        self.parent.step_in("players")

    def on_exit(self):
        options.save()

class PlayersMenu(GameMenu):

    def __init__(self):
        super().__init__()

        items = [MenuItem(
            players.get_name(idx),
            self.on_player,
            idx
        ) for idx in players.get_idxs()]

        self.create_menu(items)

    def on_player(self, idx):
        self.parent.add_layer(PlayerMenu(idx), "player")
        self.parent.step_in("player")
        self.parent.remove_layer("player")


class PlayerMenu(GameMenu):

    def __init__(self, idx):
        super().__init__()

        self.idx = idx

        self.keyb = None
        self.keyb_items = {
            k: MenuItem(
                "{}: {}".format(k, key.symbol_string(v)),
                self.on_keybinding,
                k
            )
            for k, v in players.get_keybindings(idx).items()
        }

        self.name_item = EntryMenuItem(
            "Name: ",
            self.on_name,
            players.get_name(self.idx)
        )
        
        items = [self.name_item] + list(self.keyb_items.values())

        self.create_menu(items)

    def update_layout(self):
        self._build_items(verticalMenuLayout)
        self._select_item(list(self.keyb_items).index(self.keyb))

    def on_name(self, value):
        self.name_item.value = ''.join(filter(
            lambda c: c in string.ascii_letters + string.digits, value))
        players.set_name(self.name_item.value, self.idx)
        
    def on_keybinding(self, keyb):
        log.debug("menu.Keybinding.on_keybinding:: idx, keyb: {}, {}"
            .format(self.idx, keyb))

        self.keyb_items[keyb].label = "{}: PRESS KEY".format(keyb)
        self.keyb = keyb
        self.update_layout()

    def on_key_press(self, symbol, modifiers):
        if self.keyb == None:
            return super().on_key_press(symbol, modifiers)

        log.debug("menu.Keybinding.on_key_press:: symbol: {}".format(symbol)) 
        players.set_keybinding(symbol, self.idx, self.keyb)
        self.keyb_items[self.keyb].label = ("{}: {}"
            .format(self.keyb, key.symbol_string(symbol)))
        self.update_layout()
        self.keyb = None

        return True
