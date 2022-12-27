from serial import Serial

hostport = Serial('COM3', timeout = 0)
printerport = Serial('COM6', timeout =0)

logfile = open('conection.log', 'w', encoding='UTF-8')
# logfile.write('hello')
# logfile.close()
while (True):
    hline = hostport.readline()
    # print(hline)
    if hline:
        print([hline])
        logfile.write('Host: '+str(hline)+'\n')
        logfile.flush()
        # logfile.write('Hello\n')
        printerport.write(hline)

    pline = printerport.readline()
    if pline:
        print([pline])
        logfile.write('Printer: '+str(pline)+'\n')
        logfile.flush()
        hostport.write(pline)
