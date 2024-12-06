


class LData():
	"""docstring for LData"""
	def __init__(self, text_data = ''):
		self.__version = "1.2"
		if text_data:
			self.__list_data = str.split(text_data)
			self.__len_list_data = len(self.__list_data)
		else:
			self.__list_data = []
			self.__len_list_data = 0

	def get(self, position, default="", request=""):
		if self.__len_list_data > position:
			return self.__list_data[position]
		else:
			if request:
				return input(request)
			return default

	def get_int(self, position, default=0, request=""):
		if self.__len_list_data > position:
			try:
				return int(self.__list_data[position])
			except Exception as e:
				return default
		if request:
			x = input(request)
			try:
				return int(x)
			except Exception as e:
				return default
		return default

	def get_from(self, position):
		res = ''
		while position < self.__len_list_data:
			res += f"{self.__list_data[position]} "
			position += 1
		if res ==  '':
			return res
		else:
			return res[:-1]


	def get_size(self):
		return self.__len_list_data

	def get_all(self):
		return self.__list_data