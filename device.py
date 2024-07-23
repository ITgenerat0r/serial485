import serial
from time import sleep
from includes import *

class device():
	def __init__(self, port='COM8'):
		self.addr = b'\x66' # 102
		self.__version = "2.0"

		self.__log = False

		# Открываем соединение
		self.ser = serial.Serial(port, 115200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)
		if self.ser.isOpen():
			print(f"Connected to '{port}'!")
		else:
			print(f"Can't connect to '{port}'!")
			exit(0)

	def __print(self, text):
		if self.__log:
			print(blue_text(text))

	def version(self):
		return self.__version

	def enable_log(self, l=True):
		self.__log = l


	def print_bytes(self, data):
		if self.__log:
			res = "("
			for i in data:
				res += f"{hex(i)}, "
			if len(res) > 1:
				res = res[:-2]
			res+=")"
			print(blue_text(res))
		
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
		# print(yellow_text(f"crc16: {(crc&0xff).to_bytes(1)}, {chr(crc // 256).encode('latin-1')}"))
		result = data + (crc&0xff).to_bytes(1) + chr(crc // 256).encode('latin-1')
		return result

	def __send(self, req):
		tx = self.crc16(req)

		self.__print("send: ")
		self.print_bytes(tx)
		self.ser.write(tx)
		sleep(1)
		rx = self.ser.read_all()
		self.__print("received: ")
		self.print_bytes(rx)
		return rx

	def get_bytes(self, reg, n_bytes):
		req = b''+ self.addr + b'\x04'
		req += int(reg).to_bytes(2) + int(n_bytes).to_bytes(2)

		# self.print_bytes(req)

		return self.__send(req)


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

	def get_bytes_and_parse(self, reg, n):
		return self.parse(self.get_bytes(reg, n))
		
	def get_serial_number(self):
		lr = self.get_bytes_and_parse(1199, 2)
		if lr:
			out = lr[0] << 24
			out += lr[1] << 16
			out += lr[2] << 8
			out += lr[3]
			return out
		return -1

	def get_channel_count(self):
		lr = self.get_bytes_and_parse(1215, 1)
		if lr:
			out = lr[0] << 8
			out += lr[1]
			return out
		return -1

	def get_software_version(self):
		lr = self.get_bytes_and_parse(1204, 2)
		if lr:
			out = ""
			for i in lr:
				out += f"{i}."
			if len(out):
				out = out[:-1]
			return out
		return ""


	def get_hardware_version(self):
		lr = self.get_bytes_and_parse(1202, 4)
		if lr:
			out = lr[6] << 8
			out += lr[7]
			return out
		return -1

	def get_time_from_begining(self):
		lr = self.get_bytes_and_parse(1208, 3)
		return lr

	def get_time_all(self):
		lr = self.get_bytes_and_parse(1206, 4)
		return lr

	def get_type(self):
		lr = self.get_bytes_and_parse(1201, 1)
		if lr:
			out = lr[0] << 8
			out += lr[1]
			return out
		return -1

	def get_status(self):
		lr = self.get_bytes(1399, 8)
		if lr:
			out = lr[3] << 8
			out += lr[4]
			return out
		return -1

	def get_codes(self):
		lr = self.get_bytes(1399, 12)
		# self.print_bytes(lr)
		if lr:
			out = lr[13] << 8
			out += lr[14]
			return out
		return -1












	def set_addr(self, addr):
		self.addr = addr.to_bytes(1)
		self.__print(f"Set addr {self.addr}")


	def set_new_address(self, s_number, addr):
		if s_number > 0 and addr > 0:
			req = b'' + self.addr + b'\x65'
			req += addr.to_bytes(1)
			req += (s_number&0xffff).to_bytes(2)
			s_number >>= 16
			req += s_number.to_bytes(2)
			req += 0x0.to_bytes(4)
			rx = self.__send(req)
			if rx:
				return rx[0]
		return -1


	def reset_address(self):
		req = b'' + self.addr + b'\x66'
		rx = self.__send(req)
		if rx:
			return rx[0]
		return -1

	def search_device(self):
		rx = self.__send(b'\xf0\x64')
		data = self.parse(rx)
		if data:
			a = int(rx[0])
			self.__print(f"addr:  {rx[0]}")
			did = data[0]<<24
			did += data[1]<<16
			did += data[2]<<8
			did += data[3]
			self.__print(f"id: {did}")
			# a - address, did - serial_number
			return [a, did]
		return data

