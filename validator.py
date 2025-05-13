
from includes import *


class Validator():
	def __init__(self):
		self.__types = [
			{
				'name':['GTI DOL100'],
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

	def validate(self, data):
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
		return data
		
		