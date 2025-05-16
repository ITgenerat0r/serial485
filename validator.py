
from includes import *


class Validator():
	def __init__(self):
		self.__types = [
			{
				'name':['GTI DOL100', 'GTI DOPM-01', 'GTI DOPM', 'name'],
				'status':['Статус'], 
				'counter':['Счетчик'], 
				'frequency':['Частота']
			},
			{
				'name':['GTI PAS', 'name'],
				'status':['Статус'],
				'codes':['codes']
			}
		]

	def __validate_item(self, data):
		if 'data' in data:
			name = data['data']['name']
			data_type = {}
			for tp in self.__types:
				for nm in tp['name']:
					if nm == name:
						data_type = tp
						break
				if data_type:
					break
			for field in data_type:
				for f in data_type[field]:
					if f in data['data']:
						data[field] = data['data'][f]
		del data['data']

	def validate(self, data):
		if str(type(data)) == "<class 'dict'>":
			return self.__validate_item(data)
		elif str(type(data)) == "<class 'list'>":
			for item in data:
				item = self.__validate_item(item)
		return data
		





	def is_equal(self, v1, v2, d):
		if v1 < v2-d:
			return False
		elif v1 > v2+d:
			return False
		return True


	def check_dol_counter(self, spins, tp, counter):
		res = ""
		if tp == "GTI DOL100":
			f = spins * 20
			d = 1
		elif tp == "GTI DOPM-01":
			f = spins * 40
			d = 1
		elif tp == "GTI DOPM":
			f = spins * 100
			d = 1
		if not self.is_equal(counter, f, d):
			res = f"Counter error. Counted {counter}, should be {f}."
		return res

	def check_dol_frequency(self, tp, frequency):
		res = ""
		if tp == "GTI DOL100":
			f = 13.6
			d = 0.5
		elif tp == "GTI DOPM-01":
			f = 138
			d = 1
		elif tp == "GTI DOPM":
			f = 40
			d = 1
		if not self.is_equal(frequency, f, d):
			res = f"Frequency wrong {frequency}, instead {f}.\n"
		return res


	def check_dol(self, steps, tp, counter, frequency):
		return self.check_dol_counter(steps, tp, counter)+self.check_dol_frequency(tp, frequency)
		