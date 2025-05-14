
from includes import *


class Validator():
	def __init__(self):
		self.__types = [
			{
				'name':['GTI DOL100', 'GTI DOPM-01', 'GTI DOPM'],
				'status':['Статус'], 
				'counter':['Счетчик'], 
				'frequency':['Частота']
			},
			{
				'name':['GTI PAS'],
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
		
		