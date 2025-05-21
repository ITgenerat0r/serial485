
FIELDS = {
				'status':['Статус'], 
				'counter':['Счетчик'], 
				'frequency':['Частота'],
				'codes':['codes', 'Коды']
			}


def choose_sensor(tp):
	match tp:
		case 42:
			return Sensor_42()
		case 58:
			return Sensor_58()
		case 104:
			return Sensor_104()
		case _:
			return Sensor()

class Channel():
	def __init__(self, ch):
		self.field_name = self.parse_field_name(ch['title'])
		self.reg = int(ch['addr'])-1
		self.len = int(ch['ln'])
		self.tp = ch['type']
		self.storage = ch['storage']

		self.value = None
		self.last_value = None

	def parse_field_name(self, channel_name):
		for i in FIELDS:
			if channel_name in FIELDS[i]:
				return i

	def __str__(self):
		return f" -{str(self.field_name):<10}:{str(self.value):>8}, {self.tp:<6}, ({self.reg:>4}, {self.len:>1})"



class Sensor():
	def __init__(self):
		self.__tp = 0
		self.__name = "Base sensor"
		self.__base = ""
		self.__channels = {}
		self.__addr = 0
		self.__serial_number = 0



	def parse_channels(self, sensors):
		dt = []
		for sensor in sensors:
			if len(sensors)>1 and sensor['base'] == "GTI_LOWCOST":
				continue
			ss = {}
			self.__name = sensor['name']
			self.__base = sensor['base']
			for row in sensor['inputs']:
				ch = Channel(sensor['inputs'][row])
				if ch.field_name:
					self.__channels[ch.field_name] = ch
			break
		return self.__channels

	def get_channels(self):
		return self.__channels

	def set_serial_number(self, num):
		self.__serial_number = num

	def set_address(self, addr):
		self.__addr = addr

	def get_serial_number(self):
		return self.__serial_number

	def get_address(self):
		return self.__addr


	def save_values(self):
		for ch in self.__channels:
			ch.last_value = ch.value

	def is_equal(self, value_1, value_2, precision):
		if value_1 < value_2 - precision:
			return False
		elif value_1 > value_2 + precision:
			return False
		return True

	def check_status(self):
		if not 'status' in self.__channels:
			return False
		if self.__channels['status'].value != 0:
			return False
		return True

	def get_status(self):
		if 'status' in self.__channels:
			return self.__channels['status'].value
		return -1

	def check_data(self, data):
		return self.check_status()

	def __str__(self):
		res = f"{self.__serial_number} ({self.__tp}): {self.__name} ({self.__base})\n"
		if self.__channels:
			for ch in self.__channels:
				res += f"{self.__channels[ch]}\n"
		return res






class Sensor_speed(Sensor):
	"""docstring for Sensor_speed"""
	def __init__(self):
		super().__init__()
		self.__name = "Speed sensor"
		self.__distance = 25
		self.__distance_precision = 1

	def check_data(self, data):
		res = True
		if not self.check_status():
			res = False
		if not self.check_speed():
			res = False
		if not self.check_distance(data):
			res = False
		return res

	def check_speed(self, speed):
		pass

	def check_distance(self, spins):
		ch = self.__channels['counter']
		counted = ch.value - ch.last_value
		dist = spins * self.__distance
		if not self.is_equal(counted, dist, self.__distance_precision):
			return False
		return True


		


class Sensor_104(Sensor_speed):
	"""docstring for Sensor_DOL100"""
	def __init__(self):
		super().__init__()
		self.__tp = 104
		self.__distance = 5
		self.__distance_precision = 1
		

class Sensor_58(Sensor_speed):
	"""docstring for Sensor_DOPM-01"""
	def __init__(self):
		super().__init__()
		self.__tp = 58
		self.__distance = 10
		self.__distance_precision = 1
		


class Sensor_42(Sensor_speed):
	"""docstring for Sensor_DOPM"""
	def __init__(self):
		super().__init__()
		self.__tp = 42
		self.__distance = 25
		self.__distance_precision = 1
		







class Sensor_PAS(Sensor):
	"""docstring for Sensor_PAS"""
	def __init__(self):
		self.tp = 0
		