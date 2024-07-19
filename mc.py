import serial
from time import sleep


class mc(object):
	def __init__(self, port='COM5'):
		self.version = "1.0"
		self.ser = serial.Serial(port, 115200, timeout=1)
		if self.ser.isOpen():
			print(f"Connected to '{port}'!")
		else:
			print(f"Can't connect to '{port}'!")
			exit(0)

	def send(self, tx, dl=0.1):
		# tx - int()
		self.ser.write(bytes(str(tx), 'utf-8'))
		sleep(dl)
		rx = self.ser.read_all()
		return rx
		