import time
from enum import Enum
from queue import Queue

from asciimatics.effects import Matrix, Snow, Stars
from asciimatics.exceptions import StopApplication
from asciimatics.scene import Scene
from asciimatics.screen import Screen

from .cowsay import Cowsay, SpeakingCowsay


class Background(str, Enum):
    MATRIX = "matrix"
    STARS = "stars"
    SNOW = "snow"


class EndMessage(StopApplication):
    def __init__(self, message):
        super().__init__(message)


class Avatar():
    def __init__(self, screen: Screen = None, stars: int = 10) -> None:
        self.screen = screen
        self.location = (0, 0)
        self.effects = []
        self.duration = -1
        self.stars = stars
        self.background = Background.MATRIX
        self.message_queue = Queue(1)

    def play(self):
        if self.screen is None:
            raise StopApplication("Screen is empty")
        while True:
            self.screen.set_scenes([Scene(self.effects, -1)])
            try:
                while True:
                    a = time.time()
                    self.screen.draw_next_frame(False)
                    b = time.time()
                    if b - a < 0.05:
                        # Just in case time has jumped (e.g. time change),
                        # ensure we only delay for 0.05s
                        pause = min(0.05, a + 0.05 - b)
                        time.sleep(pause)
                    if self.message_queue.qsize() == 1:
                        if self.screen._frame > self.duration:
                            raise EndMessage("")
            except EndMessage:
                message = self.message_queue.get(block=False)
                self.update(message.content, message.duration*20)
            except StopApplication as e:
                if str(e) == 'User terminated app':
                    return
                self.update()
                self.duration = -1

    def init_screen(self, screen):
        self.screen = screen
        self.location = (screen.width * 3 // 4, screen.height * 3 // 4)
        self.update_background()
        self.effects.append(Cowsay(
            screen, self.location[0], self.location[1]))

    def update(self, text=None, duration_frame=-1):
        self.effects = []
        self.update_background()
        if text is not None:
            speaking_cow = SpeakingCowsay(
                self.screen, self.location[0],  self.location[1],
                text=text, duration_frame=duration_frame).get_as_effects()
            self.effects.append(speaking_cow[0])
            self.effects.append(speaking_cow[1])
        self.effects.append(Cowsay(self.screen, self.location[0],  self.location[1],
                                   start_frame=duration_frame))

    def update_background(self):
        if self.background == Background.STARS:
            self.effects.append(
                Stars(self.screen, self.stars))
        elif self.background == Background.MATRIX:
            self.effects.append(Matrix(self.screen))
        elif self.background == Background.SNOW:
            self.effects.append(Snow(self.screen))

    def add_stars(self, x):
        self.stars += x

    def set_background(self, x):
        self.background = Background(x)

    def speak(self, message):
        self.message_queue.put(message, block=False)
