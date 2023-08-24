import random
import string

from asciimatics.effects import Print, Sprite
from asciimatics.paths import Path
from asciimatics.renderers import SpeechBubble, StaticRenderer
from asciimatics.screen import Screen

cow = [
    """
^__^
(oo)\_______
(__)\       )\/
    ||----w |
    ||     ||
""",
    """
^__^
(--)\_______
(__)\       )\/
    ||----w |
    ||     ||
""",
    """
^__^
(oo)\_______
(..)\       )\/
    ||----w |
    ||     ||
"""
]
cow_matrix = [
    """
^__^
(==)\_______
(__)\       )\/
    ||----w |
    ||     ||
""",
    """
^__^
(==)\_______
(__)\       )\/
    ||----w |
    ||     ||
""",
    """
^__^
(==)\_______
(..)\       )\/
    ||----w |
    ||     ||
"""
]


def _blink():
    if random.random() > 0.9:
        return 1
    else:
        return 0


def _speak():
    if random.random() > 0.5:
        return 0
    else:
        return 2


def group_words_by_count(input_string, max_width):
    words = input_string.split(" ")
    lines = []
    current_line = ""

    for word in words:
        if word in string.punctuation and len(word) == 1:
            current_line = current_line + " " + (word)
            continue
        if len(current_line) >= max_width:
            lines.append(current_line)
            current_line = ""
        current_line = current_line + " " + (word)

    lines.append(current_line)
    return lines


class Cowsay(Sprite):
    """
    Sample Cowsay sprite
    """

    def __init__(self, screen, x, y, animation=_blink, colour=Screen.COLOUR_CYAN,
                 start_frame=0, stop_frame=0, speed: int = 0, matrix: bool = False):
        """
        See :py:obj:`.Sprite` for details.
        """
        path = Path()
        path.jump_to(x, y)

        super(Cowsay, self).__init__(
            screen,
            renderer_dict={
                "default": StaticRenderer(images=cow,
                                          animation=animation),
            },
            path=path,
            colour=colour,
            start_frame=start_frame,
            stop_frame=stop_frame,
            speed=speed)


class SpeakingCowsay(Cowsay):
    """
    Sample Cowsay talking sprite - mouth move will a bubble is display
    """

    def __init__(self, screen, x, y, text: str = "", colour=Screen.COLOUR_CYAN,
                 start_frame=0, duration_frame=0, speed: int = 0, matrix: bool = False):
        """
        See :py:obj:`.Sprite` for details.
        """
        text_as_lines = group_words_by_count(text, 25)

        self.bubble = Print(
            screen,
            SpeechBubble("\n".join(text_as_lines), "R",
                         uni=screen.unicode_aware),
            x=x-len(max(text_as_lines, key=len))-12, y=y-3-len(text_as_lines),
            colour=Screen.COLOUR_RED,
            clear=True,
            speed=0,
            transparent=False,
            start_frame=start_frame,
            stop_frame=start_frame+duration_frame)

        super(SpeakingCowsay, self).__init__(
            screen,
            x, y,
            animation=_speak,
            colour=colour,
            start_frame=start_frame,
            stop_frame=start_frame+duration_frame,
            matrix=matrix,
            speed=speed)

    def get_as_effects(self):
        return [self, self.bubble]
