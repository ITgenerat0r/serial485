from device import *
from mc import *
from time import sleep
import os
from includes import *


version = "2.0"
filename = "pas_calibr.cfg"

PATH_DATA = 'Data/'

if not os.path.exists(PATH_DATA):
	print(f"Path {PATH_DATA} not exist!")
	exit(0)




print("Tester PAS")
print(f"Version {version}")


files = os.listdir(PATH_DATA)
for f in files:
	os.remove(f"{PATH_DATA}{f}")

p = device('COM7')
m = mc()


# devices[30058498] = 102
# devices[30061234] = 103

p.set_addr(102)

p.enable_log(False)
p.set_response_delay(0.1)

# sleep(7) # for reset already setted addresses

calibr = {}
pas_types = [161]

def parse_config(data):
	res = {}
	data = data[1:-1]
	element = ""
	overp = 0
	for i in data:
		if i == ' ':
			continue
		elif i == ',':
			if overp:
				# parse element
				key = ''
				value = ''
				ind = element.find(':')
				# print(f"<{element}> ({ind})")
				if ind >= 0:
					key = element[:ind]
					value = element[ind+2:-1]
					# parse value
					indv = value.find(',')
					if indv >= 0:
						minv = int(value[:indv])
						maxv = int(value[indv+1:])
						res[int(key)] = (minv, maxv)
						# print(f"#[{key}]({minv}, {maxv})")
					# end parse value
				# end parse element
				element = ""
				overp = 0
			else:
				overp += 1
				element += i
		else:
			element += i
	return res


f = open(filename, 'r')
strdata = f.read()
f.close()

calibr = parse_config(strdata)







os.system('cls')
p.search_all()
p.print_devices()

devices = p.get_devices()

print(f"Finded {len(devices)} devices.")

for d in devices:
	print(f"\nFor {d} ({p.get_device_address(d)}):")
	s_number = p.get_serial_number(p.get_device_address(d))
	print(f"  Serial number: {s_number}")
	if s_number == -1:
		print(f"Renew {p.get_device_address(d)} address.")
		rx = p.set_new_address(d, p.get_device_address(d), 240)
		if rx == -1:
			print(f"    Remove address {p.get_device_address(d)}({s_number})")
			if os.path.exists(f"{PATH_DATA}{d}"):
				os.remove(f"{PATH_DATA}{d}")
			p.delete_device(s_number)
			# del devices[d]
		else:
			s_number = rx
	elif s_number != d:
		print(f"    Change address {p.get_device_address(d)}({s_number})")
		# devices[s_number] = devices[d]
		# del devices[d]

	else:
		tp = p.get_type(p.get_device_address(d))
		stat = p.get_status(p.get_device_address(d))
		soft = p.get_software_version(p.get_device_address(d))
		hard = p.get_hardware_version(p.get_device_address(d))
		codes = p.get_codes(p.get_device_address(d))

		print(f"Serial number: {s_number}")
		print(f"Type: {tp}")
		print(f"Software version: {soft}")
		print(f"Hardware version: {hard}")
		
		if not stat:
			print(f"Status: [{green_text(stat)}]")
		else:
			print(f"Status: [{red_text(stat)}]")



for d in devices:
	p.set_device_field(d, 'errors', 0)

p.print_devices()

for i in calibr:
	m.send(i, 0.5)
	sleep(0.1)
	for d in devices:
		addr = p.get_device_address(d)
		rx = p.get_codes(addr)
		if rx >= calibr[i][0] and rx <= calibr[i][1]:
			print(f"{d}: {hex(i)}[{green_text(rx)}]({calibr[i][0]}, {calibr[i][1]})")
		else:
			print(f"{d}: {hex(i)}[{red_text(rx)}]({calibr[i][0]}, {calibr[i][1]})")
			p.set_device_field(d, 'errors', p.get_device_field(d, 'errors')+1)
m.send(0, 0.5)

for d in devices:
	addr = p.get_device_address(d)
	status = p.get_status(addr)
	errors = p.get_device_field(d, 'errors')
	if status != 0:
		print(red_text(f"({d}) Wrong status ({status})!"))
	if errors:
		print(red_text(f"({d}) Check device ({errors}/{len(calibr)} errors)."))
	if status == 0 and errors == 0:
		print(green_text(f"({d}) Everything okay!"))