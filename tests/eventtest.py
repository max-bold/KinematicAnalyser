from collections.abc import Callable, Iterable, Mapping
from threading import Thread
from typing import Any
from events import Events
from time import sleep


class dispatcher(Thread):
    def __init__(self) -> None:
        self.e = Events()
        super().__init__()

    def run(self):
        while True:
            self.e.ontimer("hello")
            sleep(1)


def printer(text):
    print(text)


if __name__ == "__main__":
    d = dispatcher()
    d.e.ontimer += printer
    d.start()
    # d.join()
