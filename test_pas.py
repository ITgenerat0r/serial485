from device import *
from mc import *


d = device('COM8')
m = mc()

s_number = d.get_serial_number()
tp = d.get_type()

print(f"ID: {s_number}, type: {tp}")

if tp in [161]:
	print("For U:")
	for u in range(0xff):
		m.send(b'\x00'+u.to_bytes(1)+b'\x00\x00')
		sleep(0.1)
		rx = p.get_codes()
		print(u, rx)
	print("For I:")
	for i in range(0xff):
		m.send(b'\x00\x00'+i.to_bytes(1)+b'\x00')
		sleep(0.1)
		rx = p.get_codes()
		print(i, rx)
else:
	print("Wrong device type!")