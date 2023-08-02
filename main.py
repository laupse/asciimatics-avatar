import sys
import threading
from queue import Full

import uvicorn
from asciimatics.exceptions import ResizeScreenError
from asciimatics.screen import Screen
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from avatar.avatar import Avatar, Background

HOST_NAME = "localhost"
PORT_NUMBER = 8000

app = FastAPI()
avatar = Avatar(stars=200)


class Message(BaseModel):
    content: str
    duration: int
    background: Background
    stars: int = 200


@app.post("/speak")
def message(message: Message):
    try:
        avatar.speak(message)
    except Full:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Unavailable',
        )
    return "Ok"


def animation(screen: Screen):
    avatar.init_screen(screen)
    avatar.play()


def start_http_server():
    uvicorn.run(app, host="127.0.0.1", port=PORT_NUMBER,
                log_config="./log.ini")


if __name__ == "__main__":

    threading.Thread(target=start_http_server, daemon=True).start()

    try:
        Screen.wrapper(animation)
        sys.exit(0)
    except ResizeScreenError:
        pass
