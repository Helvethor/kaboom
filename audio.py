import log


class AudioInterface:

    volumes = [str(i) if i != 0 else "Mute" for i in range(0, 101, 10)]

    def __init__(self):
        self.volume = 6

    def get_volume(self):
        return self.volume

    def set_volume(self, value):
        self.volume = int(value)

    def get_volumes(self):
        return self.volumes


class Music(AudioInterface):

    def __init__(self):
        super().__init__()


class Sound(AudioInterface):

    def __init__(self):
        super().__init__()


music = None
sound = None


def init():
    global music, sound

    music = Music()
    sound = Sound()
