from time import sleep
import os
from sys import argv
import sys


from includes import *
from device import *
from mc import *
from cfg_manager import *
from validator import *

version = '2.0'


com_rs485 = 6
com_arduino = 5


help_text = f" Version {version}\n"
help_text += f"  rs=*, where * is number for COM port for RS485 device (default = 6)\n"
help_text += f"  mc=*, where * is number for COM port for controller (default = 5)\n"


BORDER_LENGTH = 100

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

def search_devices():
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
	return last_x

print("Searching devices...")


if search_devices() == 0:
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
	print()
	print()


if mc_type == b"DOL":
	rx = m.send(0, until_response=True) # change direction
	if rx == b'1':
		print(m.send(0, until_response=True))


	# init_data = {}
	# collected_data = {}
	# for dt in data:
	# 	addr = dt['addr']
	# 	init_data[addr] = dt
	# 	collected_data[addr] = {}
	# 	collected_data[addr]['err'] = []

	#long
	print("="*BORDER_LENGTH)
	print("STAGE 1")
	print("-"*BORDER_LENGTH)
	direction = b'0'
	for i in range(2):
		spins = 750
		# spins = 50 # debug
		p.save_states()
		rx = m.send(4*spins)
		p.get_all_data()
		check_spins = 4 * spins
		if direction == b'1':
			check_spins *= -1
		p.check_data(check_spins)

		rx = m.get()
		print(rx)

		rx = m.send(0, until_response=True) # change direction
		print("Direction:", rx)
		direction = rx
		# init_data = data

	# input('Press enter to continue...')
	p.search_all()
	p.get_all_data()



	#short each
	print("="*BORDER_LENGTH)
	print("STAGE 2")
	print("-"*BORDER_LENGTH)
	for i in range(3):
		p.save_states()
		check_spins = 2
		rx = m.send(check_spins, until_response=True)
		rx = m.send(0, until_response=True)
		p.get_all_data()
		if rx == b'0':
			check_spins *= -1
		p.check_data(check_spins)

		p.save_states()
		check_spins = 1
		rx = m.send(check_spins, until_response=True)
		rx = m.send(0, until_response=True)
		p.get_all_data()
		if rx == b'0':
			check_spins *= -1
		p.check_data(check_spins)

	p.search_all()




	#short all
	print("="*BORDER_LENGTH)
	print("STAGE 3")
	print("-"*BORDER_LENGTH)
	p.get_all_data()
	p.save_states()
	for i in range(12):
		rx = m.send(1, until_response=True)
		rx = m.send(0, until_response=True)
		sleep(0.1)


		rx = m.send(2, until_response=True)
		rx = m.send(0, until_response=True)
		sleep(0.1)

	check_spins = -12
	search_devices()
	p.search_all()
	p.get_all_data()
	p.check_data(check_spins, check_spins*3)

elif mc_type == b"PAS" or mc_type == b"":
	delay = 2
	print()
	print("Stage 1. Ток:")
	m.send(0)
	sleep(1)
	for i in range(16):
		step = 0x1000
		print(hex(i*step))
		rx = m.send(i*step)
		sleep(delay)
		p.search_all()
		p.get_all_data()
		p.check_data(i*step)
	print()
	print("Stage 2. Напряжение:")
	for i in range(16):
		step = 0x100000
		print(hex(i*step))
		rx = m.send(i*step)
		sleep(delay)
		p.search_all()
		p.get_all_data()
		p.check_data(i*step)
	print()
	print("Stage 3. Импульс:")
	for i in range(16):
		step = 0x10000000
		print(hex(i*step))
		rx = m.send(i*step)
		sleep(delay)
		p.search_all()
		p.get_all_data()
		p.check_data(i*step)

# finish

counter = 0
devices = p.get_all_devices()
for dev_addr in devices:
	sens = devices[dev_addr]['sensor']
	errors = sens.get_errors()
	sens.clear_errors()
	if errors:
		counter += 1
		print()
		print(sens.get_title(), end='')
		print(red_text(f" {len(errors)} errors!"))
		for i in errors:
			print(red_text(i))
	else:
		print(sens.get_title(), end='')
		print(green_text(f" Good!"))

print(f"Good: {green_text(str(len(devices) - counter))}, Bad: {red_text(str(counter))}.")


print()
table = []
for addr, number in p.get_addresses().items():
	row = {}
	sens = p.get_sensor(number)
	if sens:
		row['name'] = sens.get_name()
	row['Address'] = addr
	row['Serial number'] = number
	row['Software version'] = p.get_software_version(addr.to_bytes())
	row['Hardware version'] = p.get_hardware_version(addr.to_bytes())
	table.append(row)
	print(f" {addr}: {number}")	
	print("   Software version: ", row['Software version'])
	print("   Hardware version: ", row['Hardware version'])


print(show_map_table(table))








