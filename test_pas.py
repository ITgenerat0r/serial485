from device import *
from mc import *
from includes import *


version = "1.0"

print("Tester PAS")
print(f"Version {version}")

filename = "pas_calibr.cfg"
d = device('COM7')
m = mc()

s_number = d.get_serial_number()
print(f"Serial number: {s_number}")
tp = d.get_type()
print(f"Type: {tp}")

print("Software version: ", d.get_software_version())
print("Hardware version: ", d.get_hardware_version())

status = d.get_status()
if not status:
	print(f"Status: [{green_text(status)}]")
else:
	print(f"Status: [{red_text(status)}]")



calibr = {}
pas_types = [161]

# calibr
make_calibr = False
if make_calibr:
	if tp in pas_types:
		print("For I:")
		precision = 5
		for i in range(0x10):
			m.send(i<<12, 1)
			sleep(0.1)
			rx = d.get_codes()
			print(f"{i}: {rx}")
			prcsn = int(rx*precision/100)
			minrx = rx - prcsn
			if minrx < 0:
				minrx = 0
			calibr[i<<12] = (minrx, rx+prcsn)
		print("For U:")
		precision = 10
		for u in range(0x11):
			m.send(u<<20, 1)
			sleep(0.1)
			rx = d.get_codes()
			print(f"{u}: {rx}")
			prcsn = int(rx*precision/100)
			minrx = rx - prcsn
			if minrx < 0:
				minrx = 0
			calibr[u<<20] = (minrx, rx+prcsn)
		f = open(filename, 'w+')
		f.write(str(calibr))
		f.close()
	else:
		print("Wrong device type!")




#parsing



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


# print(calibr)



errors = 0

if tp in pas_types:
	for i in calibr:
		m.send(i, 0.5)
		sleep(0.1)
		rx = d.get_codes()
		if rx >= calibr[i][0] and rx <= calibr[i][1]:
			print(f"{hex(i)}[{green_text(rx)}]({calibr[i][0]}, {calibr[i][1]})")
		else:
			print(f"{hex(i)}[{red_text(rx)}]({calibr[i][0]}, {calibr[i][1]})")
			errors += 1
	status = d.get_status()
	if status != 0:
		print(red_text(f"Wrong status ({status})!"))
	if errors:
		print(red_text(f"Check device ({errors}/{len(calibr)} errors)."))
	if status == 0 and errors == 0:
		print(green_text(f"Everything okay!"))