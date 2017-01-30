import socket

import pyglet
from pyglet.window import key
from cocos.director import director
from cocos.layer.base_layers import *
from cocos.scene import Scene
from cocos.menu import *
from cocos.actions import *

import log, audio, options, players, server, client


class KaboomMultiplexLayer(MultiplexLayer):

    def __init__(self):

        self.map = [
            'main',
            'play',
            'local',
            'network',
            'join',
            'options',
            'players',
            'keybindings@0',
            'keybindings@1',
            'keybindings@2',
            'keybindings@3'
        ]
        self.layer_stack = []

        super().__init__(
            MainMenu(),
            PlayMenu(),
            LocalMenu(),
            NetworkMenu(),
            JoinMenu(),
            OptionsMenu(),
            PlayersMenu(),
            *[KeybindingsMenu(idx) for idx in range(4)]
        )

    def step_in(self, next_layer):
        self.layer_stack.append(self.enabled_layer)
        super().switch_to(self.map.index(next_layer))

    def step_out(self):
        last_layer = self.layer_stack.pop()
        super().switch_to(last_layer)


class KaboomMenu(Menu):

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


class MainMenu(KaboomMenu):

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


class PlayMenu(KaboomMenu):

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


class LocalMenu(KaboomMenu):

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
        self.nb_players = idx + 2
        return True

    def on_start(self):
        return True


class NetworkMenu(KaboomMenu):

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
        pass


class JoinMenu(KaboomMenu):

    def __init__(self):
        super().__init__()

        self.ip_item = EntryMenuItem(
            "Host IP: ", 
            self.on_ip,
            server.get_ip()
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

        server.set_ip(self.ip_item.value) 
        director.push(Scene(client.GameLayer()))

class OptionsMenu(KaboomMenu):

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
            MenuItem("Players", self.on_players),
            *[MenuItem("Keybindings {}".format(players.names[idx]),
                self.on_keybindings, (idx))
                for idx in range(4)
            ]
        ]

        self.create_menu(items)

    def on_music_volume(self, idx):
        audio.music.set_volume(idx)

    def on_sound_volume(self, idx):
        audio.sound.set_volume(idx)

    def on_players(self):
        self.parent.step_in("players")

    def on_keybindings(self, idx):
        self.parent.step_in("keybindings@{}".format(idx))

    def on_exit(self):
        options.save()

class PlayersMenu(KaboomMenu):

    def __init__(self):
        super().__init__()

        items = [MenuItem(
            players.get_name(idx),
            self.on_player,
            idx
        ) for idx in players.get_idxs()]

        self.create_menu(items)

    def on_player(self, idx):
        pass

class KeybindingsMenu(KaboomMenu):

    def __init__(self, idx):
        super().__init__()

        self.keyb = None
        self.keyb_items = {
            k: MenuItem(
                "{}: {}".format(k, key.symbol_string(v)),
                self.on_keybinding,
                k
            )
            for k, v in players.keybindings[idx].items()
        }
        self.idx = idx

        self.create_menu(self.keyb_items.values())

    def update_layout(self):
        self._build_items(verticalMenuLayout)
        self._select_item(list(self.keyb_items).index(self.keyb))
        
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
