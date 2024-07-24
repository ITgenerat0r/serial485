from device import *
from time import sleep
import os


PATH_DATA = 'Data/'

if not os.path.exists(PATH_DATA):
	print(f"Path {PATH_DATA} not exist!")
	exit(0)

files = os.listdir(PATH_DATA)
for f in files:
	os.remove(f"{PATH_DATA}{f}")

p = device('COM7')



# devices[30058498] = 102
# devices[30061234] = 103

p.set_addr(102)

p.enable_log(False)
p.set_response_delay(0.2)

# sleep(7) # for reset already setted addresses

	



while True:
	sleep(1)
	os.system('cls')
	p.search_all()
	p.print_devices()

	devices = p.get_devices()

	for d in devices:
		print(f"\nFor {d} ({devices[d]}):")
		s_number = p.get_serial_number(devices[d])
		print(f"s_number: {s_number}")
		if s_number == -1:
			print(f"Renew {devices[d]} address.")
			rx = p.set_new_address(d, devices[d], 240)
			if rx == -1:
				print(f"Remove address {devices[d]}({s_number})")
				if os.path.exists(f"{PATH_DATA}{d}"):
					os.remove(f"{PATH_DATA}{d}")
				# del devices[d]
		elif s_number != d:
			print(f"Change address {devices[d]}({s_number})")
			# devices[s_number] = devices[d]
			# del devices[d]

		else:
			stat = p.get_status(devices[d])
			codes = p.get_codes(devices[d])
			data = f"status:{stat}|codes:{codes}"
			print(data)
			f = open(f"{PATH_DATA}{d}", 'w+')
			f.write(str(data))
			f.close()


print(devices)

