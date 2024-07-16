


class mc(object):
	def __init__(self, port='COM5'):
		self.ser = serial.Serial(port, 115200, timeout=1)
		if self.ser.isOpen():
			print('Connected successfully!')
		else:
			print("Failed conneciton!")
			exit(0)

	def send(tx):
		ser.write(tx)
		time.sleep(0.05)
		rx = ser.read_all()
		return rx
		