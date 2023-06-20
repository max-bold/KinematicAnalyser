from serial import Serial

port = Serial("COM6",baudrate=9600)
port.write(b"?\x03\xff\xfa\x00\x01\x90\xf1")
s = b""
while True:
    s = port.write(b'ff')
    # try:
    #     s = s.decode('ascii')
    # except:
    #     pass
    # print(s,end='\n')
