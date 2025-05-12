import serial
from time import sleep
from includes import *
import serial.tools.list_ports
import os

class device():
	def __init__(self, port='COM8'):
		self.__addr = b'\x66' # 102
		self.__conf_fld = "config"

		self.__devices = {}
		self.__addresses = {}
		self.__addr_counter = 103

		self.__version = "2.1"
		self.__response_delay = 0.2

		self.__log = False
		self.__port_description = "USB Serial Port"

		# Открываем соединение
		self.__ser = None

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

	def open(self, port='COM8'):
		try:
			self.__ser = serial.Serial(port, 115200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)
		except Exception as e:
			print(f"Error: {e}")
		
		if self.__ser and self.__ser.isOpen():
			print(f"Connected to '{port}'!")
			return True
		else:
			print(f"Can't connect to '{port}'!")
			return False




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
		if self.__ser:
			tx = self.crc16(req)

			self.__log = True # debug
			self.__print("send: ")
			self.print_bytes(tx)
			self.__ser.write(tx)
			sleep(self.__response_delay)
			rx = self.__ser.read_all()
			self.__print("received: ")
			self.print_bytes(rx)
			self.__log = False # debug
			return rx
		return ""

	def get_bytes(self, reg, n_bytes, addr=b'', storage="input"):
		if not addr:
			addr = self.__addr
		if str(type(addr)) == "<class 'int'>":
			addr = addr.to_bytes(1)
		strg = b'\x04'
		if storage == "holding":
			strg = b'\x03'
		req = b''+ addr + strg
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

	def get_bytes_and_parse(self, reg, n, addr='', storage="input"):
		return self.parse(self.get_bytes(reg, n, addr, storage))
		
	def get_serial_number(self, addr=b''):
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
		lr = self.get_bytes_and_parse(1208, 1, addr)
		if lr:
			out = lr[0] << 8
			out += lr[1]
			return out
		return -1

	def get_time_all(self, addr=''):
		lr = self.get_bytes_and_parse(1206, 2, addr)
		if lr:
			out = lr[0] << 24
			out += lr[1] << 16
			out += lr[2] << 8
			out += lr[3]
			return out
		return -1

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
		overcount = 100
		while running:
			device = self.search_device()
			self.__print(f"Finded: {device}")
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
			if not overcount:
				break
			else:
				overcount -= 1






	def _parse_type(self, tp):
		if tp in ['int16', 'uint16']:
			return 1
		if tp in ['int32', 'uint32', 'float']:
			return 2
		if tp in ['double']:
			return 4
		print(red_text(f"Unknown type <{tp}>!"))
		return 1

	def parse_field(self, data, fld, shift=False):
		fnd = f'{fld}="'
		if shift:
			fnd = f'{fld} = "'
		ind_b = data.find(fnd)
		if ind_b >= 0:
			step = ind_b + len(fnd)
			ind_e = data[step:].find('"')
			if ind_e >= 0:
				return data[step:step+ind_e]
		return ""

	def parse_register(self, data):
		id = self.parse_field(data, 'id', True)
		res = {}
		res['title'] = self.parse_field(data, 'title', True)
		res['storage'] = self.parse_field(data, 'storage', True)
		res['addr'] = self.parse_field(data, 'addr', True)
		res['ln'] = self._parse_type(self.parse_field(data, 'type', True))
		return (id, res)

	def cut_register(self, data):
		reg = ""
		ind_b = data.find("<register")
		ind_e = data.find("/>")
		if ind_b >= 0 and ind_e >= 0:
			reg = data[ind_b:ind_e+2]
			data = data[ind_e+2:]
		return (reg, data)

	def _cutter(self, data, index):
		res = ""
		sens = {}
		if index >= 0:
			b_ind = data[:index].rfind("<sensor")
			e_ind = data[index:].find("</sensor>")
			if b_ind >= 0 and e_ind >= 0:
				res = data[b_ind:index+e_ind]
				sens['name'] = self.parse_field(res, 'name')
				sens['base'] = self.parse_field(res, 'base')
				sens['inputs'] = {}
				sens['holdings'] = {}
				while True:
					(reg, res) = self.cut_register(res)
					# print(blue_text(f"|{reg}|"))
					if len(reg) == 0:
						break
					(nm, params) = self.parse_register(reg)
					if params['storage'] == "input":
						sens['inputs'][nm] = params
					else:
						sens['holdings'][nm] = params
					# print(blue_text(res))
				# print(sens)
		# print(f"res: {res}")
		return sens


	def parse_config(self, fld, tp):
		fnd = f'type="{tp}"'
		# print(f"Finding: {fnd}")
		data = []
		for s in os.listdir(fld):
			fnm = f"{fld}/{s}"
			if os.path.isdir(os.path.abspath(fnm)):
				# print(yellow_text(s))
				data += self.parse_config(fnm, tp)
			else:
				if s.find(".config") >= 0:
					# print(green_text(s))
					f = open(fnm, "rb")
					dt = f.read().decode('utf-8')
					f.close()
					mp = self._cutter(dt, dt.find(fnd))
					if mp:
						data.append(mp)
				# else:
					# print(red_text(s))
		return data

	def get_data_str(self, addr=''):
		tp = self.get_type(addr)
		res = f"type: {addr}"
		sensors = self.parse_config(self.__conf_fld, tp)
		for sensor in sensors:
			# print(sensor)
			res += f"\n{sensor['name']}: [{sensor['base']}]\n"
			for ch in sensor['inputs']:
				dt = sensor['inputs'][ch]
				# print(dt)
				reg = int(dt['addr'])-1
				rx = self.get_bytes_and_parse(reg, dt['ln'], addr, dt['storage'])
				rx_i = 0
				for i in rx:
					rx_i <<= 8
					rx_i += i
				filler = "                                         "
				row = f" {dt['title']}: {rx_i}."
				row += filler[len(row):]
				res += f"{row} ({reg}, {dt['ln']}){rx}\n"
		return res