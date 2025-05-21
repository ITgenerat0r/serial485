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


print("Searching devices...")
last_x = 0
for i in range(10):
	print('.', end='')
	x = p.search_all()
	# if x == last_x:
	# 	break
	last_x = x
	sleep(0.2)
print()
p.print_devices()

if last_x == 0:
	sys.exit(0)

# p.get_all_data()
data = p.get_all_data()
for dt in data:
	print(dt)
	# for ch in dt.get_channels():
	# 	print(ch)
	if dt.check_status():
		print("Status:", green_text(dt.get_status()))
	else:
		print("Status:", red_text(dt.get_status()))



rx = m.send(0, until_response=True) # change direction
if rx == b'1':
	print(m.send(0, until_response=True))


init_data = {}
collected_data = {}
for dt in data:
	addr = dt['addr']
	init_data[addr] = dt
	collected_data[addr] = {}
	collected_data[addr]['err'] = []

#long
for i in range(2):
	spins = 1000
	# is_done = 1
	p.save_states()
	rx = m.send(4*spins)
	p.get_all_data()
	p.check_data(spins)
	# while is_done != 0:
		# is_first = True
		# data = validator.validate(p.get_all_data())
		# print(show_map_table(data))
		# for dt in data:
		# 	addr = dt['addr']
		# 	# check frequency
		# 	if 'frequency' in collected_data[addr]:
		# 		if dt['frequency'] > collected_data[addr]['frequency']:
		# 			collected_data[addr]['frequency'] = dt['frequency']
		# 	else:
		# 		collected_data[addr]['frequency'] = dt['frequency']
		# 	# check status
		# 	if dt['status'] != 0:
		# 		print(red_text(f"Status {dt['status']}"))
		# 		collected_data[addr]['err'].append(dt)
		# 	if is_first:
		# 		is_done = dt['frequency']
		# 		is_first = False
		# 	else:
		# 		if dt['frequency'] > is_done:
		# 			is_done = dt['frequency']
	rx = m.get()
	print(rx)
	# check counter
	# data = validator.validate(p.get_all_data())
	# print(show_map_table(data))
	# for dt in data:
	# 	if dt['addr'] in init_data and dt['addr'] in collected_data:
	# 		err = validator.check_dol(spins, dt['name'], dt['counter']-init_data[dt['addr']]['counter'], collected_data[dt['addr']]['frequency'])
	# 		if err:
	# 			collected_data[dt['addr']]['err'].append(err)
	rx = m.send(0, until_response=True) # change direction
	print("Direction:", rx)
	init_data = data


#short
for i in range(12):
	rx = m.send(2, until_response=True)
	rx = m.send(0, until_response=True)
	sleep(0.1)
	rx = m.send(1, until_response=True)
	rx = m.send(0, until_response=True)
	sleep(0.1)
#check counter & status
data = validator.validate(p.get_all_data())
print(show_map_table(data))

for dt in data:
	if dt['status'] != 0:
		collected_data[addr]['err'].append(dt)
	err = validator.check_dol_counter(400, dt['name'], dt['counter'])
	if err:
		collected_data[dt['addr']]['err'].append(err)

print()
print(collected_data)
print()
for i in collected_data:
	if collected_data[i]['err']:
		for e in collected_data[i]['err']:
			print(f"Error: {e}")