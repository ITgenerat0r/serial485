import serial
from time import sleep
from includes import *

class device():
	def __init__(self, port='COM8'):
		self.__addr = b'\x66' # 102

		self.__devices = {}
		self.__addresses = {}
		self.__addr_counter = 103

		self.__version = "2.0"
		self.__response_delay = 0.2

		self.__log = False

		# Открываем соединение
		self.__ser = serial.Serial(port, 115200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)
		if self.__ser.isOpen():
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

	def set_response_delay(self, new_delay=0.5):
		self.__response_delay = new_delay


	def print_bytes(self, data, force=False):
		if self.__log or force:
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
		self.__ser.write(tx)
		sleep(self.__response_delay)
		rx = self.__ser.read_all()
		self.__print("received: ")
		self.print_bytes(rx)
		return rx

	def get_bytes(self, reg, n_bytes, addr=b''):
		if not addr:
			addr = self.__addr
		if str(type(addr)) == "<class 'int'>":
			addr = addr.to_bytes(1)
		req = b''+ addr + b'\x04'
		req += int(reg).to_bytes(2) + int(n_bytes).to_bytes(2)

		# self.print_bytes(req)

		return self.__send(req)


	def parse(self, data):
		if len(data) > 4:
			n = data[2]+2
			if n > len(data):
				print(f"N very big")
				self.print_bytes(data, True)
				n = len(data)-3
			value = []
			while n > 3:
				value.append(data[n-1])
				value.append(data[n])
				n -= 2
			if n == 3:
				value.append(data[n])
			return value
		return data

	def get_bytes_and_parse(self, reg, n, addr=''):
		return self.parse(self.get_bytes(reg, n, addr))
		
	def get_serial_number(self, addr=''):
		lr = self.get_bytes_and_parse(1199, 2, addr)
		if lr:
			out = lr[0] << 24
			out += lr[1] << 16
			out += lr[2] << 8
			out += lr[3]
			return out
		return -1

	def get_channel_count(self, addr=''):
		lr = self.get_bytes_and_parse(1215, 1, addr)
		if lr:
			out = lr[0] << 8
			out += lr[1]
			return out
		return -1

	def get_software_version(self, addr=''):
		lr = self.get_bytes_and_parse(1204, 2, addr)
		if lr:
			out = ""
			for i in lr:
				out += f"{i}."
			if len(out):
				out = out[:-1]
			if addr in self.__addresses:
				self.set_device_field(self.__addresses[addr], 'software', out)
			return out
		return ""


	def get_hardware_version(self, addr=''):
		lr = self.get_bytes_and_parse(1202, 4, addr)
		if lr:
			out = lr[6] << 8
			out += lr[7]
			if addr in self.__addresses:
				self.set_device_field(self.__addresses[addr], 'hardware', out)
			return out
		return -1

	def get_time_from_begining(self, addr=''):
		lr = self.get_bytes_and_parse(1208, 3, addr)
		return lr

	def get_time_all(self, addr=''):
		lr = self.get_bytes_and_parse(1206, 4, addr)
		return lr

	def get_type(self, addr=''):
		lr = self.get_bytes_and_parse(1201, 1, addr)
		if lr:
			out = lr[0] << 8
			out += lr[1]
			if addr in self.__addresses:
				self.set_device_field(self.__addresses[addr], 'type', out)
			return out
		return -1

	def get_status(self, addr=''):
		lr = self.get_bytes(1399, 8, addr)
		if lr:
			out = lr[3] << 8
			out += lr[4]
			return out
		return -1

	def get_codes(self, addr=''):
		lr = self.get_bytes(1399, 12, addr)
		# self.print_bytes(lr)
		if lr:
			out = lr[13] << 8
			out += lr[14]
			return out
		return -1












	def set_addr(self, addr):
		self.__addr = addr
		self.__print(f"Set addr {self.__addr}")

	def get_addr(self):
		return self.__addr


	def set_new_address(self, s_number, addr, old_addr=b''):
		if not old_addr:
			old_addr = self.__addr
		if s_number > 0 and addr > 0:
			req = b'' + old_addr.to_bytes(1) + b'\x65'
			# req = b'\xf0\x65'
			req += addr.to_bytes(1)
			req += (s_number&0xffff).to_bytes(2)
			s_number >>= 16
			req += s_number.to_bytes(2)
			req += 0x0.to_bytes(4)
			rx = self.__send(req)
			if rx:
				return rx[0]
		return -1


	def reset_address(self, addr=b''):
		if not addr:
			addr = self.__addr
		if str(type(addr)) == "<class 'int'>":
			addr = addr.to_bytes(1)
		req = b'' + addr + b'\x66'
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






	def print_devices(self):
		print("=======DEVICES=======================================")
		for d in self.__devices:
			print(f"   {d} : {self.__devices[d]}")
		print()
		print(self.__addresses)
		print("=====================================================")


	def get_devices(self):
		res  = []
		for d in self.__devices:
			res.append(d)
		return res

	def set_device_field(self, number, field='address', value = 0):
		if not number in self.__devices:
			self.__devices[number] = {}
		self.__devices[number][field] = value


	def get_device_field(self, number, field='address'):
		if number in self.__devices:
			if field in self.__devices[number]:
				return self.__devices[number][field]
		return -1

	def delete_device(self, number):
		if number in self.__devices:
			del self.__devices[number]

	def get_device_type(self, number):
		return self.get_device_field(number, 'type')

	def get_device_address(self, number):
		return self.get_device_field(number)


	def search_all(self):
		self.__addr = b'\x66'
		running = True
		while running:
			device = self.search_device()
			print(f"Finded: {device}")
			if device:
				if device[0] == 102 or device[0] == 240:
					if device[1] in self.__devices: # already in devices
						rx = self.set_new_address(device[1], self.get_device_field(device[1]), device[0])
						if rx != self.get_device_field(device[1]):
							print(f"Error, during regain address {device[1]} - {self.get_device_field(device[1])}")
					else: # add to devices
						rx = self.set_new_address(device[1], self.__addr_counter, device[0])
						if rx == self.__addr_counter:
							# self.__devices[device[1]]['address'] = rx
							self.set_device_field(device[1], 'address', rx)
							self.__addresses[self.__addr_counter] = device[1]
						else:
							print("Error, during change address.")
				else:
					if device[1] < 100000000: 
						if device[1] in self.__devices:
							if self.__devices[device[1]]['address'] != device[0]:
								print("How can this be possible?")
						else:
							if device[0] in self.__addresses:
								rx = self.set_new_address(device[1], self.__addr_counter, device[0])
								if rx == self.__addr_counter:
									# self.__devices[device[1]]['address'] = rx
									self.set_device_field(device[1], 'address', rx)
									self.__addresses[self.__addr_counter] = device[1]
								else:
									print("Error, during change address.")
							else:
								# self.__devices[device[1]]['address'] = device[0]
								self.set_device_field(device[1], 'address', device[0])
								self.__addresses[device[0]] = device[1]
					if self.__addr == b'\x66':
						self.__addr = b'\xf0'
					else:
						self.__addr = b'\x66'
						running = False

				if self.__addr_counter == 240:
					if len(self.__addresses) > 137:
						print("There is many devices (addresses is over)")
					else:
						self.__addr_counter = 103
				while self.__addr_counter in self.__addresses:
					if self.__addr_counter < 240:
						self.__addr_counter += 1


