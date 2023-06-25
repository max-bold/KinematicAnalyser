from collections.abc import Callable, Iterable, Mapping
from threading import Thread, Lock
from time import sleep, time
from typing import Any
from serial import Serial, SerialException
from queue import Queue, Empty

# from events import Events

startsring = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n"


class EventSlot:
    """Events library by Nicola Iarocci style event slot with light modifications by BM"""

    def __init__(self):
        self.targets = []

    def __call__(self, *a, **kw):
        for f in tuple(self.targets):
            f(*a, **kw)

    def __iadd__(self, f):
        self.targets.append(f)
        return self

    def __isub__(self, f):
        while f in self.targets:
            self.targets.remove(f)
        return self

    def __len__(self):
        return len(self.targets)

    def __iter__(self):
        def gen():
            for target in self.targets:
                yield target

        return gen()

    def __getitem__(self, key):
        return self.targets[key]


class Printer(object):
    class Sender(Thread):
        def __init__(self, port: Serial) -> None:
            self.stop = False
            self.port = port
            self.comnum = 0
            self.queue = Queue()
            self.resendflag = False
            self.confirmed = Lock()
            self.confirmed.acquire()
            self.onsend = EventSlot()
            self.onerror = EventSlot()
            return super().__init__()

        def formatrep(self, string: str, N: int = 0) -> bytes:
            """Formats input string to Reptier printer style, adds command number and checksum

            Args:
                string (str): input string (command)
                N (int, optional): comand number. Defaults to 0.

            Returns:
                bytes: byte seq to write into port
            """
            bs = f"N{N} {string}".encode("ascii")
            cs = 0
            for b in bs:
                cs ^= b
            return bs + b"*" + str(cs).encode("ascii") + b"\r\n"

        def run(self) -> None:
            com = ""
            lastcom = ""
            while not self.stop:
                if not self.resendflag:
                    try:
                        com = self.queue.get(timeout=1)
                        if com:
                            lastcom = com
                            self.comnum += 1
                    except Empty:
                        com = ""
                else:
                    com = lastcom
                if com:
                    try:
                        fcom = self.formatrep(com, self.comnum)
                        self.port.write(fcom)
                        self.onsend(self.comnum, fcom)
                        com = ""
                    except SerialException:
                        self.onerror("Connection lost")
                        # self.kill()
                    if not self.confirmed.acquire(timeout=10):
                        self.onerror("No confirmation received")
            self.stop = False

        def kill(self):
            self.stop = True
            self.queue.queue.clear()

        def resend(self, comnum: int):
            self.comnum = comnum
            self.resendflag = True
            self.confirmed.release()

        def confirm(self, comnum=None):
            # print(f"conf for {comnum} recieved, current {self.comnum}")
            if not comnum or comnum == self.comnum:
                if self.confirmed.locked():
                    self.confirmed.release()

        def clear(self):
            self.queue.queue.clear()

    class Reciever(Thread):
        def __init__(self, port: Serial):
            self.stop = False
            self.port = port
            self.onrecieve = EventSlot()
            self.onerror = EventSlot()
            self.onconfirm = EventSlot()
            self.onresend = EventSlot()
            self.ondata = EventSlot()
            self.comnum = None
            self.mdata = []
            self.mrec = False
            return super().__init__()

        def run(self):
            """Main reciever thread loop"""
            while not self.stop:
                try:
                    s = self.port.read_until(b"\r").decode("ascii")
                    if s == f"ok {self.comnum}\r":
                        self.onconfirm(int(s.split(" ")[1]))
                        self.onrecieve(s)
                    elif s == f"ok\r":
                        self.onconfirm()
                        self.onrecieve(s)
                    elif s.startswith("Resend"):
                        self.onresend(int(s.split(":")[1]))
                    elif s.startswith("X:"):
                        self.onconfirm()
                        self.onrecieve(s)
                    elif s == "Data start\r":
                        print("catched " + s)
                        self.mrec = True
                        self.mdata = []
                        self.onrecieve("Receiving data")
                    elif self.mrec:
                        self.mdata.append(s)
                    elif s == "Data end\r":
                        self.onrecieve(f"Received {len(self.mdata)} points")
                        self.mrec = False
                        self.ondata(self.mdata)
                    elif s:
                        self.onrecieve(s)
                except SerialException:
                    self.onerror("Connection lost")
                    # self.kill()
            self.stop = False

        def kill(self):
            """Kill sender thred"""
            self.stop = True

        def sended(self, comnum: int, *args):
            """Metod for informing Reciever about last sent command number to wait for confirmation

            Args:
                comnum (int): Sent command number
            """
            self.comnum = comnum

    def __init__(self) -> None:
        self.sender = None
        self.reciever = None

        self.port = None

        self.onrecieve = EventSlot()
        self.onconnect = EventSlot()
        self.ondisconnect = EventSlot()
        self.onerror = EventSlot()
        self.ondataready = EventSlot()
        self.onsend = EventSlot()

    def connect(self, portname: str) -> bool:
        """Connect to printer on given port

        Args:
            portname (str): Port name. ie 'COM8'

        Returns:
            bool: True if connected sacsessfully, else False
        """
        try:
            self.port = Serial(portname, timeout=10)
        except SerialException:
            self.onerror("Failed to open port")
            return False
        else:
            self.port.write(startsring)
            resp = self.port.read_until(b"\n")
            if not resp == startsring:
                self.onerror("No startstring recieved. Closing port")
                self.port.close()
                return False
            else:
                self.sender = self.Sender(self.port)
                self.reciever = self.Reciever(self.port)

                self.sender.onerror += self.onerror
                self.sender.onsend += self.onsend
                self.reciever.onerror += self.onerror
                self.sender.onsend += self.reciever.sended
                self.reciever.onconfirm += self.sender.confirm
                self.reciever.onresend += self.sender.resend
                self.reciever.onrecieve += self.onrecieve
                self.reciever.ondata += self.ondataready

                self.sender.start()
                self.reciever.start()
                self.onconnect("Connected")
                return True

    def disconnect(self) -> bool:
        """Disconnect from printer, purge send queue, and kill reciver and sender threads"""
        ctime = time()
        if self.sender and self.sender.is_alive():
            self.sender.kill()
            self.sender.join()
            ctime = time()
        if self.reciever and self.reciever.is_alive():
            self.reciever.kill()
            self.port.cancel_read()
            self.reciever.join()
        self.port.close()
        self.ondisconnect("Disconnected")

    def write(self, command: str) -> None:
        """Formats and sends a string to printer

        Args:
            command (str): String to send
        """
        if command and self.sender:
            self.sender.queue.put(command)
        elif not command:
            self.onerror("Command must be not empty")
        elif not self.sender:
            self.onerror("Sender is not runing")

    def clear(self) -> None:
        """Purges sender queue"""
        self.sender.clear()


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
                    # self.port.write(startsring)
                    pass
                elif com.startswith("M114"):
                    self.port.write("X:213 Y:145 Z:789 E:NAN\r".encode("ascii"))
                else:
                    self.port.write(f"ok {num}\r".encode("ascii"))
            else:
                # self.port.write(b"wait\r")
                pass
        self._stop = False

    def stop(self) -> None:
        self._stop = True
        self.port.cancel_read()


if __name__ == "__main__":
    p = Printer()
    r = Responder()
    p.onrecieve = lambda resp: print(f"<<< {[resp]}")
    p.onconnect = print
    p.ondisconnect = print
    p.onerror = print

    r.start("COM9")
    if p.connect("COM8"):
        p.sender.onsend += lambda comnum, com: print(f">>> {[com]}")
        p.write("M105")
        p.write("M114")
        sleep(5)
        p.disconnect()
    r.stop()
