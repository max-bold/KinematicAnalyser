from serial import Serial, SerialException
from threading import Thread, Lock

# from analyser import plotdata3
from traceback import print_exc
from time import sleep
import queue as q

sendqueue = q.Queue()
recivequeue = q.Queue()
confirmed = Lock()
confirmed.acquire()
resend = False
port:Serial = None
comnum = 0


def formatrep(string: str, N: int = 0) -> bytes:
    bs = f"N{N} {string}".encode("ascii")
    cs = 0
    for b in bs:
        cs ^= b
    return bs + b"*" + str(cs).encode("ascii") + b"\r\n"


def sender():
    global comnum
    global resend
    com = ""
    while True:
        if not resend:
            com = sendqueue.get()
            comnum += 1
        else:
            resend = False
        port.write(formatrep(com, comnum))
        confirmed.acquire()


def reciever():
    global resend
    global comnum
    s = ""
    while True:
        try:
            s += port.read().decode("ascii")
            if s.endswith("\r")or s.endswith("\n"):
                print([s])
                if s == "ok\r":
                    confirmed.release()
                elif s.startswith("Resend"):
                    comnum = int(s.split(":")[1])
                    resend = True
                    confirmed.release()
                else:
                    recivequeue.put(s)
                s = ""
        except:
            print_exc()


def run(comport: str):
    global port
    # port.port = comport
    try:
        port = Serial(comport)
    except SerialException:
        recivequeue.put("Error: Failed to open port")
    else:
        sendqueue.queue.clear()
        txthread = Thread(target=sender)
        txthread.start()
        rxthred = Thread(target=reciever)
        rxthred.start()
        port.write(
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n"
        )
        recivequeue.put('Connected')
        for com in ["M110", "M115", "M105", "M114", "M111 S6", "T0", "M80", "M155 S0"]:
            sendqueue.put(com)
