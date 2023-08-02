import time
from enum import Enum
from queue import Queue

from asciimatics.effects import Matrix, Snow, Stars, RandomNoise
from asciimatics.exceptions import StopApplication
from asciimatics.scene import Scene
from asciimatics.screen import Screen

from .cowsay import Cowsay, SpeakingCowsay


class Background(str, Enum):
    MATRIX = "matrix"
    STARS = "stars"
    SNOW = "snow"
    NOISE = "noise"


class EndMessage(StopApplication):
    def __init__(self, message):
        super().__init__(message)


class Avatar():
    def __init__(self, screen: Screen = None, stars: int = 10) -> None:
        self.screen = screen
        self.location = (0, 0)
        self.scene = Scene([], -1)
        self.duration = -1
        self.stars = stars
        self.background = Background.NOISE
        self.background_updated = False
        self.message_queue = Queue(1)

    def play(self):
        if self.screen is None:
            raise StopApplication("Screen is empty")
        while True:
            try:
                a = time.time()
                self.screen.draw_next_frame(False)
                b = time.time()
                if b - a < 0.05:
                    # Just in case time has jumped (e.g. time change),
                    # ensure we only delay for 0.05s
                    pause = min(0.05, a + 0.05 - b)
                    time.sleep(pause)
                if self.message_queue.qsize() == 1\
                        and self.screen._frame > self.duration:
                    message = self.message_queue.get(block=False)
                    self.update(message.content, message.duration * 20)
            except StopApplication as e:
                if str(e) == 'User terminated app':
                    return

    def init_screen(self, screen: Screen):
        self.screen = screen
        self.location = (screen.width * 3 // 4, screen.height * 3 // 4)
        self.update_background()
        self.scene.add_effect(Cowsay(
            screen, self.location[0], self.location[1]))
        self.screen.set_scenes([self.scene])

    def update(self, text=None, duration_frame=-1):
        frame_no = self.screen._frame
        should_reset_scenes = not self.background_updated

        if should_reset_scenes:
            frame_no = 0
            self.update_background()

        if text is not None:
            speaking_cow = SpeakingCowsay(
                self.screen,
                self.location[0],  self.location[1],
                text=text,
                start_frame=frame_no,
                duration_frame=duration_frame).get_as_effects()
            self.scene.add_effect(speaking_cow[0])
            self.scene.add_effect(speaking_cow[1])

        if should_reset_scenes:
            self.scene.add_effect(
                Cowsay(self.screen, self.location[0], self.location[1],
                       start_frame=frame_no+duration_frame))
            self.screen.set_scenes([self.scene])

    def update_background(self):
        self.scene.effects.clear()
        background_effect = None

        if self.background == Background.STARS:
            background_effect = Stars(self.screen, self.stars)
        elif self.background == Background.MATRIX:
            background_effect = Matrix(self.screen)
        elif self.background == Background.NOISE:
            background_effect = RandomNoise(self.screen)
        elif self.background == Background.SNOW:
            background_effect = Snow(self.screen)

        self.scene.add_effect(background_effect)
        self.background_updated = True

    def set_background(self, x):
        if Background(x) != self.background:
            self.background = Background(x)
            self.background_updated = False

    def speak(self, message):
        self.set_background(message.background)
        self.stars = message.stars
        self.message_queue.put(message, block=False)
