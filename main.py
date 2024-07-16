
from device import *





p = device()

print("Serial number: ", p.get_serial_number())
print("Type: ", p.get_type())
print("Channels: ", p.get_channel_count())
print("Software version: ", p.get_software_version())
print("Hardware version: ", p.get_hardware_version())
status = p.get_status()
print("Status: ", status)
print("Codes: ", p.get_codes())


print()
rx = p.send_and_parse(1399, 12)
print("data (1399, 12): ", rx)
for i in rx:
	print(hex(i))

exit(0)

while True:
	reg = input("reg: ")
	n_bytes = input("n: ")
	result = p.send_and_parse(reg, n_bytes)
	print("response: ", result)
	for i in result:
		print(hex(i))
