from serial import Serial

port = Serial('COM8',timeout=5)
port.read_until(b'\n')
print('done')
