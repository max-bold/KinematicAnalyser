from threading import Thread
from serial import Serial

startsring = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n"


class Responder(Thread):
    def __init__(self) -> None:
        self.port = None
        self._stop = False
        super().__init__()

    def start(self, portname: str) -> None:
        self.port = Serial(portname, timeout=5)
        return super().start()

    def run(self) -> None:
        """Responder main loop"""
        while not self._stop:
            raw = self.port.readline()
            if raw:
                line = raw.decode("ASCII")
                print(f">>> {line}")
                num = line[1 : line.find(" ")]
                com = line[line.find(" ") + 1 : line.find("*")]
                chsum = line[line.find("*") + 1 :]
                if raw == startsring:
                    self.port.write(startsring)
                    pass
                elif com.startswith("M114"):
                    self.port.write("X:213 Y:145 Z:789 E:NAN\r".encode("ascii"))
                else:
                    self.port.write(f"ok {num}\r".encode("ascii"))
            else:
                self.port.write(b"wait\r")
                pass
        self._stop = False

    def stop(self) -> None:
        self._stop = True
        self.port.cancel_read()


r = Responder()
r.start("COM9")
