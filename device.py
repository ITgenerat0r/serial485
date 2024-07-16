import serial
from time import sleep

class device():
	def __init__(self, port='COM8'):
		self.addr = b'\x66' # 102
		self.cmd = b'\x04' # read inputs

		# Открываем соединение
		self.ser = serial.Serial(port, 115200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)
		if self.ser.isOpen():
			print('Connected successfully!')
		else:
			print("Failed conneciton!")
			exit(0)


	def print_bytes(self, data):
		res = "("
		for i in data:
			res += f"{hex(i)}, "
		if len(res) > 1:
			res = res[:-2]
		res+=")"
		print(res)
		
	def crc16(self, data):
		crc = 0xFFFF 
		l = len(data)
		i = 0
		while i < l:
			j = 0
			crc = crc ^ data[i]
			while j < 8:
				if (crc & 0x1):
					mask = 0xA001
				else:
					mask = 0x00
				crc = ((crc >> 1) & 0x7FFF) ^ mask
				j += 1
			i += 1
		if crc < 0:
			crc -= 256
		result = data + chr(crc % 256).encode() + chr(crc // 256).encode('latin-1')
		return result

	def send(self, reg, n_bytes):
		req = b''+ self.addr + self.cmd
		req += int(reg).to_bytes(2) + int(n_bytes).to_bytes(2)

		# self.print_bytes(req)

		tx = self.crc16(req)

		# print("send: ")
		# self.print_bytes(tx)
		self.ser.write(tx)
		sleep(1)
		rx = self.ser.read_all()
		# print("received: ")
		# self.print_bytes(rx)
		return rx


	def parse(self, data):
		if len(data) > 4:
			n = data[2]+2
			value = []
			while n > 3:
				value.append(data[n-1])
				value.append(data[n])
				n -= 2
			if n == 3:
				value.append(data[n])
			return value
		return data

	def send_and_parse(self, reg, n):
		return self.parse(self.send(reg, n))
		
	def get_serial_number(self):
		lr = self.send_and_parse(1199, 2)
		out = lr[0] << 24
		out += lr[1] << 16
		out += lr[2] << 8
		out += lr[3]
		return out

	def get_channel_count(self):
		lr = self.send_and_parse(1215, 1)
		out = lr[0] << 8
		out += lr[1]
		return out

	def get_software_version(self):
		lr = self.send_and_parse(1204, 2)
		out = ""
		for i in lr:
			out += f"{i}."
		if len(out):
			out = out[:-1]
		return out
		# if len(r) == 9:
		# 	return f"{r[5]}.{r[6]}.{r[3]}.{r[4]}"
		# return "?"

	def get_hardware_version(self):
		lr = self.send_and_parse(1202, 4)
		out = lr[6] << 8
		out += lr[7]
		return out

	def get_time_from_begining(self):
		lr = self.send_and_parse(1208, 3)
		return lr

	def get_time_all(self):
		lr = self.send_and_parse(1206, 4)
		return lr

	def get_type(self):
		lr = self.send_and_parse(1201, 1)
		out = lr[0] << 8
		out += lr[1]
		return out



