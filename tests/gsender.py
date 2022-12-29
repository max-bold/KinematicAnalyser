from serial import Serial
from time import sleep
from threading import Thread
import matplotlib.pyplot as plt
from analyser import plotdata
from traceback import print_exc

try:
    port = Serial('COM7')
except:
    print('Failed to open port')


def formatrep(string: str, N: int = 0) -> bytes:
    bs = f'N{N} {string}'.encode('ascii')
    cs = 0
    for b in bs:
        cs ^= b
    return bs+b'*'+str(cs).encode('ascii')+b'\r\n'


def sender(comnum):
    while True:
        s = input()
        for ss in s.split(';'):
            bs = formatrep(ss, comnum)
            port.write(bs)
            # print(bs)
            comnum += 1


def reciever():
    s = ''
    log=open('tests/data.log','w')
    rec= False
    data = []
    while True:
        try:
            s += port.read().decode('ascii')
            if s.endswith('\r'):
                if s == 'wait\r':
                    pass
                elif s in ['\r', 'ok\r']:
                    pass
                elif s == 'Data start\r':
                    print('catched '+s)
                    rec = True
                    log=open('tests/data.log','w+')
                elif s == 'Data end\r':
                    print('catched '+s)
                    plotdata(log)
                    log.close()
                    rec = False
                elif rec:
                    log.write(s)
                else:
                    print(s)
                s = ''
        except Exception as ex:
            print_exc()

if __name__ == '__main__':
    port.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n')
    i = 1
    for com in [
        'M110',
        'M115',
        'M105',
        'M114',
        'M111 S6',
        'T0',
        'M80',
        'M155 S0'
    ]:
        port.write(formatrep(com, i))
        i += 1
    txthread = Thread(target=sender, args=[i])
    txthread.start()
    rxthred = Thread(target=reciever)
    rxthred.start()
