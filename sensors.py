
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
		case 61:
			return Sensor_61()
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
		self._tp = 0
		self._name = "Base sensor"
		self._base = ""
		self._channels = {}
		self._addr = 0
		self._serial_number = 0
		self._errors = []



	def parse_channels(self, sensors):
		dt = []
		for sensor in sensors:
			if len(sensors)>1 and sensor['base'] == "GTI_LOWCOST":
				continue
			ss = {}
			self._name = sensor['name']
			self._base = sensor['base']
			for row in sensor['inputs']:
				ch = Channel(sensor['inputs'][row])
				if ch.field_name:
					self._channels[ch.field_name] = ch
			break
		return self._channels

	def get_channels(self):
		return self._channels

	def get_errors(self):
		return self._errors

	def clear_errors(self):
		self._errors = []

	def set_serial_number(self, num):
		self._serial_number = num

	def set_address(self, addr):
		self._addr = addr

	def get_serial_number(self):
		return self._serial_number

	def get_address(self):
		return self._addr


	def save_values(self):
		for _, ch in self._channels.items():
			ch.last_value = ch.value

	def is_equal(self, value_1, value_2, precision):
		if value_1 < value_2 - precision:
			return False
		elif value_1 > value_2 + precision:
			return False
		return True

	def check_status(self):
		if not 'status' in self._channels:
			self._errors.append(f"Error (status): Failed get status.")
			return False
		if self._channels['status'].value != 0:
			self._errors.append(f"Error (status): Status should be 0, but got {self._channels['status'].value}")
			return False
		return True

	def get_status(self):
		if 'status' in self._channels:
			return self._channels['status'].value
		return -1

	def during_check_data(self, data):
		return self.check_status()

	def finally_check_data(self, data):
		return self.check_status()

	def get_title(self):
		return f"({self._addr}) {self._serial_number}: {self._name} ({self._base})"

	def __str__(self):
		res = f"{self._addr}.{self._serial_number} ({self._tp}): {self._name} ({self._base})\n"
		if self._channels:
			for ch in self._channels:
				res += f"{self._channels[ch]}\n"
		return res






class Sensor_speed(Sensor):
	"""docstring for Sensor_speed"""
	def __init__(self):
		super(Sensor_speed, self).__init__()
		self._name = "Speed sensor"

		self._distance = 25
		self._distance_precision = 1
		self._is_reverible = True
		self._is_first_check_distance = True
		self._toward = 1

		self._frequency = 11.8
		self._frequency_precision = 0.5
		self._max_frequency = 0

	def during_check_data(self, data):
		self.check_status()
		return self.is_speed_done()

	def finally_check_data(self, data):
		res = True
		if not self.check_status():
			res = False
		if not self.check_speed(data):
			return False
		if not self.check_distance(data):
			res = False
		return res

	def reset_max_frequency(self):
		self._max_frequency = 0

	def is_speed_done(self):
		current_frequency = self._channels['frequency'].value
		counted = self._channels['counter'].value - self._channels['counter'].last_value
		counter = self._channels['counter'].value
		print(f"({self._addr:>3}){self._serial_number:>8}: {self._name:<12}/   Counter: {counter:>8}/   Counted: {counted:<8}/   Frequency: {current_frequency}")
		if current_frequency > self._max_frequency:
			self._max_frequency = current_frequency
		if current_frequency:
			return False
		return True

	def check_speed(self, speed):
		# ch = self._channels['frequency']
		# frequency = ch.value
		frequency = self._max_frequency
		if speed > 999:
			if not self.is_equal(frequency, self._frequency, self._frequency_precision):
				self._errors.append(f"Error (frequency): For speed {speed}, frequency should be in {self._frequency-self._frequency_precision}-{self._frequency+self._frequency_precision} but got {frequency}!")
				return False
		else:
			if not frequency:
				self._errors.append(f"Error (frequency): For speed {speed}, frequency should be not 0! Got {frequency}.")
				return False
		return True

	def check_distance(self, spins):
		ch = self._channels['counter']
		counted = ch.value - ch.last_value
		dist = spins * self._distance * self._toward
		if self._is_first_check_distance:
			self._is_first_check_distance = False
			if spins < 0 and counted > 0 or (spins > 0 and counted < 0):
				self._toward *= -1
		if not self._is_reverible:
			dist = abs(dist)
		if not self.is_equal(counted, dist, self._distance_precision):
			self._errors.append(f"Error (counter): For spins {spins}, counter should be {dist-self._distance_precision}-{dist+self._distance_precision} but got {counted}")
			return False
		return True


		


class Sensor_61(Sensor_speed):
	"""docstring for Sensor_DOL100"""
	def __init__(self):
		super(Sensor_61, self).__init__()
		self._tp = 61
		self._distance = 25
		self._distance_precision = 4
		self._frequency = 11.8
		self._frequency_precision = 1
		

class Sensor_58(Sensor_speed):
	"""docstring for Sensor_DOPM-01"""
	def __init__(self):
		super(Sensor_58, self).__init__()
		self._tp = 58
		self._distance = 10
		self._distance_precision = 1
		self._frequency = 138
		self._frequency_precision = 2
		


class Sensor_42(Sensor_speed):
	"""docstring for Sensor_DOPM"""
	def __init__(self):
		super(Sensor_42, self).__init__()
		self._tp = 42
		self._distance = 5
		self._distance_precision = 2
		self._is_reverible = False
		self._frequency = 233
		self._frequency_precision = 5


		


		




class Sensor_PAS(Sensor):
	"""docstring for Sensor_PAS"""
	def __init__(self):
		self._tp = 0
		self._name = "PAS Sensor"
		