from device import *
from mc import *
from includes import *


d = device('COM7')
m = mc()

s_number = d.get_serial_number()
print(f"Serial number: {s_number}")
tp = d.get_type()
print(f"Type: {tp}")
status = d.get_status()
if not status:
	print(f"Status: [{green_text(status)}]")
else:
	print(f"Status: [{red_text(status)}]")


print(f"ID: {s_number}, type: {tp}")

if tp in [161]:
	print("For U:")
	for u in range(0xff):
		m.send(u<<16)
		sleep(0.1)
		rx = d.get_codes()
		print(u, rx)
	print("For I:")
	for i in range(0xff):
		m.send(i<<8)
		sleep(0.1)
		rx = d.get_codes()
		print(i, rx)
else:
	print("Wrong device type!")