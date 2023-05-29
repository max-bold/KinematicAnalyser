from serial import Serial
from threading import Thread
from analyser import plotdata3
from traceback import print_exc
from time import sleep



dataready = False

def formatrep(string: str, N: int = 0) -> bytes:
    bs = f'N{N} {string}'.encode('ascii')
    cs = 0
    for b in bs:
        cs ^= b
    return bs+b'*'+str(cs).encode('ascii')+b'\r\n'

comnum = 1


def sender():
    global comnum
    while True:
        s = input()
        for ss in s.split(';'):
            if ss:
                bs = formatrep(ss, comnum)
                port.write(bs)
                # print(bs)
                comnum += 1


def reciever():
    global comnum
    global dataready
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
                    # plotdata3(log)                    
                    log.close()
                    dataready = True
                    rec = False
                elif rec:
                    log.write(s)
                    # print(s)
                elif s.startswith('Resend'):
                    comnum=int(s.split(':')[1])
                # elif s.startswith('Error:expected line'):g9
                elif s.startswith('GUI'):
                    pass
                else:
                    print(s)
                s = ''
        except Exception as ex:
            # try:
            #     print
            #     port.open()
            # except:
            #     pass
            # else:
            print_exc()

if __name__ == '__main__':
    try:
        port = Serial('COM5')
    except:
        print('Failed to open port')
    else:
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
            port.write(formatrep(com, comnum))
            comnum += 1
        txthread = Thread(target=sender)
        txthread.start()
        rxthred = Thread(target=reciever)
        rxthred.start()
        while True:
            if dataready:
                print('dataready')
                with open('tests/data.log','r') as data:
                    plotdata3(data)
                dataready = False
            sleep(1)
