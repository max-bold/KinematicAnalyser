from serial import Serial
from time import sleep
from threading import Thread

try:
    port = Serial('COM7', timeout=0.01)
except:
    print('Failed to open port')


def formatrep(string: str, N: int = 0) -> bytes:
    bs = f'N{N} {string}'.encode('ascii')
    cs = 0
    for b in bs:
        cs ^= b
    return bs+b'*'+str(cs).encode('ascii')+b'\r\n'


def sender():
    comnum = 1
    while True:
        s = input()
        bs=formatrep(s, comnum)
        port.write(bs)
        print(bs)
        comnum += 1


def reciever():
    while True:
        line = (port.readline())
        if line:
            print(line.decode('ascii'))


txthread = Thread(target=sender)
txthread.start()
rxthred = Thread(target=reciever)
rxthred.start()
