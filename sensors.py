
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
	# 	self.reg = 1400
	# 	self.len = 1
	# 	self.tp = "int16"
	# 	self.parse_channel(ch)

	# def parse_channel(self, ch):
		self.reg = int(ch['addr'])-1
		self.len = int(ch['ln'])
		self.tp = ch['type']
		self.storage = ch['storage']

		self.value = None

	def __str__(self):
		return f"{self.value:>10}: {self.tp:<6}, ({self.reg:>4}, {self.len:>1})"



class Sensor():
	def __init__(self):
		self.__tp = 0
		self.__name = "Base sensor"
		self.__base = ""
		self.__channels = []
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
				self.__channels.append(ch)
			break
		return self.__channels

	def get_channels(self):
		return self.__channels

	def set_serial_number(self, num):
		self.__serial_number = num

	def set_address(self, addr):
		self.__addr = addr

	def __str__(self):
		res = f"{self.__tp}: {self.__name} ({self.__base})\n"
		for ch in self.__channels:
			res += f"{ch}\n"
		return res






class Sensor_speed(Sensor):
	"""docstring for Sensor_speed"""
	def __init__(self):
		super().__init__()
		self.__name = "Speed sensor"

		


class Sensor_104(Sensor_speed):
	"""docstring for Sensor_DOL100"""
	def __init__(self):
		super().__init__()
		self.__tp = 104
		

class Sensor_58(Sensor_speed):
	"""docstring for Sensor_DOPM-01"""
	def __init__(self):
		super().__init__()
		self.__tp = 58
		


class Sensor_42(Sensor_speed):
	"""docstring for Sensor_DOPM"""
	def __init__(self):
		super().__init__()
		self.__tp = 42
		







class Sensor_PAS(Sensor):
	"""docstring for Sensor_PAS"""
	def __init__(self):
		self.tp = 0
		