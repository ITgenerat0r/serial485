import serial
from time import sleep


class mc(object):
	def __init__(self, port='COM5'):
		self.ser = serial.Serial(port, 115200, timeout=1)
		if self.ser.isOpen():
			print('Connected successfully!')
		else:
			print("Failed conneciton!")
			exit(0)

	def send(self, tx):
		self.ser.write(tx)
		sleep(0.05)
		rx = self.ser.read_all()
		return rx
		