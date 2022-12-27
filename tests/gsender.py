from serial import Serial
from time import sleep
from threading import Thread

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
        bs = formatrep(s, comnum)
        port.write(bs)
        print(bs)
        comnum += 1


def reciever():
    s = ''
    while True:
        s += port.read().decode('ascii')
        if s.endswith('\r'):
            if s == 'wait\r':
                pass
            elif s in ['\r', 'ok\r']:
                pass
            else:
                print(s)
            s = ''


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
    # port.write(b'N1 M110*34\r\n')
    # port.write(b'N2 M115*36\r\n')
    # port.write(b'N3 M105*36\r\n')
    # port.write(b'N4 M114*35\r\n')
    # port.write(b'N5 M111 S6*98\r\n')
    # port.write(b'N6 T0*60\r\n')
    # port.write(b'N7 M20*22\r\n')
    # port.write(b'N8 M80*19\r\n')
    # port.write(b'N9 M105*46\r\n')
    # port.write(b'N10 M111 S6*86\r\n')
    # port.write(b'N11 T0*10\r\n')
    # port.write(formatrep('M155 S0',12))
    txthread = Thread(target=sender, args=[i])
    txthread.start()
    rxthred = Thread(target=reciever)
    rxthred.start()
