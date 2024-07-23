from device import *
from time import sleep
import os


PATH_DATA = 'Data/'

if not os.path.exists(PATH_DATA):
	print(f"Path {PATH_DATA} not exist!")

p = device('COM7')


devices = {}

devices[30058498] = 102
devices[30061234] = 103


print("=======DEVICES===============================")
print(devices)
print("=============================================")

while True:
	for d in devices:
		print(d)
		print(devices[d])
		s_number = p.get_serial_number(devices[d])
		if s_number == -1:
			print(f"Remove address {devices[d]}({s_number})")
			if os.path.exists(f"{PATH_DATA}{d}"):
				os.remove(f"{PATH_DATA}{d}")
			# del devices[d]
		elif s_number != d:
			print(f"Change address {devices[d]}({s_number})")
			devices[s_number] = devices[d]
			# del devices[d]

		else:
			stat = p.get_status(devices[d])
			codes = p.get_codes(devices[d])
			data = f"status:{stat}|codes:{codes}"
			f = open(f"{PATH_DATA}{d}", 'w+')
			f.write(str(data))
			f.close()
	sleep(1)
	break # dev

print(devices)

