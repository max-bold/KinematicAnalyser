from serial import Serial
from time import sleep

hostport = Serial('COM3', timeout=0)
printerport = Serial('COM7', timeout=0)

logfile = open('conection.log', 'w', encoding='UTF-8')

while (True):
    hline = hostport.readline()
    if hline:
        print([hline])
        logfile.write('Host: '+str(hline)+'\n')
        logfile.flush()
        printerport.write(hline)

    pline = printerport.readline()
    if pline:
        print([pline])
        logfile.write('Printer: '+str(pline)+'\n')
        logfile.flush()
        hostport.write(pline)
    sleep(0.01)
