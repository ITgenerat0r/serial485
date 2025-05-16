from time import sleep
import os
from sys import argv
import sys


from includes import *
from device import *
from mc import *
from cfg_manager import *
from validator import *

version = '1.0'


com_rs485 = 6
com_arduino = 5


help_text = f" Version {version}\n"
help_text += f"  rs=*, where * is number for COM port for RS485 device (default = 6)\n"
help_text += f"  mc=*, where * is number for COM port for controller (default = 5)\n"


for a in argv:
	if a == "-help":
		print(help_text)
		sys.exit()
	ind = a.find('=')
	if ind >= 0:
		key = a[:ind]
		value = a[ind+1:]
		print(f"{key}: {value}")
		if key == "mc":
			com_arduino = value
		elif key == "rs":
			com_rs485 = value

print("GFM Universe Tester")
print(f"Version {version}")

p = device(f"COM{com_rs485}")
p.set_addr(102)

p.enable_log(False)
p.set_response_delay(0.1)


m = mc(f"COM{com_arduino}")

validator = Validator()


# get mc type(programm)
mc_type = m.send(-1)
print("type:", mc_type)


# read config by mc type
last_x = 0
for i in range(10):
	x = p.search_all()
	if x == last_x:
		break
	last_x = x
	sleep(0.5)
p.print_devices()

if last_x == 0:
	sys.exit(0)

init_data = validator.validate(p.get_all_data())
print(show_map_table(init_data))
for dt in init_data:
	print(f"Addr: {dt['addr']},   Number:", yellow_text(dt['number']))
	# print(dt['data'])
	status = dt['status']
	if status == 0:
		print("Status:", green_text(status))
	else:
		print("Status:", red_text(status))





rx = m.send(0, until_response=True) # change direction
if rx == b'1':
	print(m.send(0, until_response=True))



#long
collected_data = {}
for i in range(2):
	rx = m.send(4*1000)
	is_done = 1
	while is_done != 0:
		is_first = True
		data = validator.validate(p.get_all_data())
		print(show_map_table(data))
		for dt in data:
			# print(f"Addr: {dt['addr']},   Number: {dt['number']}")
			# print(dt['data'])
			# check frequency
			if is_first:
				is_done = dt['frequency']
				is_first = False
			else:
				if dt['frequency'] > is_done:
					is_done = dt['frequency']
	rx = m.get()
	print(rx)
	# check counter
	data = validator.validate(p.get_all_data())
	print(show_map_table(data))
	rx = m.send(0, until_response=True) # change direction
	print("Direction:", rx)


#short
for i in range(10):
	rx = m.send(2, until_response=True)
	rx = m.send(0, until_response=True)
	rx = m.send(1, until_response=True)
	rx = m.send(0, until_response=True)
#check counter
data = validator.validate(p.get_all_data())
print(show_map_table(data))




