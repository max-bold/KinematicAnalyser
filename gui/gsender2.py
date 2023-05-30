from serial import Serial, SerialException
from threading import Thread, Lock

# from queue import Queue

# from analyser import plotdata3
from traceback import print_exc
from time import sleep
import queue as q

sendqueue = q.Queue()
recivequeue = q.Queue()
confirmed = Lock()
confirmed.acquire()
resend = False
port: Serial = None
comnum = 0
stopthreads = False


def formatrep(string: str, N: int = 0) -> bytes:
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


def sender():
    """Sender thread. Takes a command form sendqueue, formats it and sends to printer, waiting for confirmation.
    If no confirmation returned within 10 seconds, write a warning to recivequeue.
    Every time it sendы a command (if no resend==True) it rises comnum by one, for printer duplicate filtering
    """

    global comnum
    global resend
    global stopthreads
    lastcom = ""

    while True:
        if not resend:
            try:
                com = sendqueue.get(timeout=1)
                lastcom = com
                comnum += 1
            except q.Empty:
                # print("send queue empty")
                pass
        else:
            com = lastcom
        if com:
            try:
                port.write(formatrep(com, comnum))
                recivequeue.put(f">{com}")
                com = ""
            except SerialException:
                recivequeue.put("Connection lost")
            except:
                print_exc()
            if not confirmed.acquire(timeout=10):
                recivequeue.put("No confirmation received")
        # recivequeue.put('confirmed')
        if stopthreads:
            break


def reciever():
    """Reciever thread. Reads from port and puts recieved data into recievequeue.
    If data is a confirmation, it rises confirmed by one, for printer duplicate filtering
    """

    global resend
    global comnum
    global stopthreads
    s = ""
    while True:
        try:
            s += port.read().decode("ascii")
            if s:
                if s.endswith("\r") or s.endswith("\n"):
                    # print([s])
                    if s == f"ok {comnum}\r" or s == f"ok\r":
                        confirmed.release()
                    elif s.startswith("Resend"):
                        comnum = int(s.split(":")[1])
                        resend = True
                        confirmed.release()
                    elif s.startswith("X:"):
                        if confirmed.locked():
                            confirmed.release()
                        recivequeue.put(s)
                    else:
                        recivequeue.put(s)
                    s = ""
        except SerialException:
            recivequeue.put("Connection lost")
        except:
            print_exc()
        if stopthreads:
            break


txthread: Thread = None
rxthread: Thread = None
port = Serial(timeout=1)


def run(comport: str):
    """Connects to port and starts threads

    Args:
        comport (str): Port name to connect. Ex. 'COM5' in windows.
    """
    global port
    global txthread
    global rxthread
    port.port = comport
    try:
        # port = Serial(comport)
        port.open()
    except SerialException:
        recivequeue.put("Error: Failed to open port")
    else:
        sendqueue.queue.clear()
        txthread = Thread(target=sender)
        txthread.start()
        rxthread = Thread(target=reciever)
        rxthread.start()
        port.write(
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n"
        )
        recivequeue.put("Connected")
        for com in ["M110", "M115", "M105", "M114", "M111 S6", "T2", "M80", "M155 S0"]:
            sendqueue.put(com)


def stop():
    """Stops threads, clears sendqueue and closes port"""

    print("disconnecting")
    global stopthreads
    global port
    stopthreads = True
    sendqueue.queue.clear()
    sendqueue.put("M0")
    txthread.join()
    rxthread.join()
    stopthreads = False
    port.close()
    recivequeue.put("Disconnected")
