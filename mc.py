import serial
from time import sleep
import serial.tools.list_ports



class mc(object):
	def __init__(self, port='COM5'):
		self.version = "1.0"
		self.__ser = None
		self.__port_description = "Arduino Micro"
		if not self.open(port):
			self.__find_port()

	def __find_port(self):
		ports = serial.tools.list_ports.comports()
		for port in ports:
			pt = f"{port}"
			x = pt.find(self.__port_description)
			if x >= 0:
				b = pt.rfind('(')
				e = pt.rfind(')')
				if b >= 0 and e >= 0:
					print(f"Try: {pt}")
					if self.open(pt[b+1:e]):
						break

	def open(self, port='COM5'):
		try:
			self.__ser = serial.Serial(port, 115200, timeout=1)
		except Exception as e:
			print(f"Error: {e}")
		
		if self.__ser and self.__ser.isOpen():
			print(f"Connected to '{port}'!")
			return True
		else:
			print(f"Can't connect to '{port}'!")
			return False

	def send(self, tx, dl=0.1):
		# tx - int()
		if self.__ser:
			self.__ser.write(bytes(str(tx), 'utf-8'))
			sleep(dl)
			rx = self.__ser.read_all()
			return rx
		return ""