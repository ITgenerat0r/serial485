
from device import *
from mc import *
import os




m = mc()
p = device('COM7')


def hex_from_str(row):
	res = 0
	for i in row:
		cd = ord(i)
		if cd in {48, 49, 50, 51, 52, 53, 54, 55, 56, 57}:
			if res:
				res = res << 4
			res += cd - 48
		elif cd in {97, 98, 99, 100, 101, 102}:
			if res:
				res = res << 4
			res += cd - 87
	return res

# s_number = p.get_serial_number()
# print("Serial number: ", s_number)
# print("Type: ", p.get_type())
# print("Channels: ", p.get_channel_count())
# print("Software version: ", p.get_software_version())
# print("Hardware version: ", p.get_hardware_version())
# status = p.get_status()
# print("Status: ", status)

# p.enable_log()

# print("Codes: ", p.get_codes())


for i in range(5):
	os.system('cls')
	p.search_all()
	p.print_devices()
	sleep(1)
# rx = p.get_bytes_and_parse(1399, 12)
# print("data (1399, 12): ", rx)
# for i in rx:
# 	print(hex(i))


# print("TEST:")
# print("reset")
# p.reset_address()
# print("search...")
# print(p.search_device())
# print("new address")
# s_number = 0x1caa802
# p.set_addr(0xf0)
# rs = p.set_new_address(s_number, 103)
# p.set_addr(103)
# print("rs: ", rs)

cm = ""
while True:
	cm = input("->")
	if cm == "search":
		print("search")
		rx = p.search_device()
		print(f"Address: {rx[0]} ({hex(rx[0])})")
		print(f"Serial number: {rx[1]}")
	elif cm == "newaddr":
		s_number = int(input("Serial number: "))
		addr = int(input("Address (for device): "))
		print("new address")
		# s_number = 0x1caa802
		p.set_addr(0xf0)
		rs = p.set_new_address(s_number, addr)
		if rs == addr:
			p.set_addr(addr)
			print(f"Local address changed to {addr}.")
		print("rs: ", rs)
	elif cm == "setaddr":
		addr = int(input("Address (for terminal): "))
		p.set_addr(addr)
	elif cm == "reset":
		print("reset")
		p.reset_address()
	elif cm == "get":
		reg = input("reg: ")
		n_bytes = input("n: ")
		result = p.get_bytes_and_parse(reg, n_bytes)
		print("response: ", result)
		for i in result:
			print(hex(i))
	elif cm == "id":
		s_number = p.get_serial_number()
		print("Serial number: ", s_number)
	elif cm == "type":
		print("Type: ", p.get_type())
	elif cm == "channel":
		print("Channels: ", p.get_channel_count())
	elif cm == "version":
		print(f"Version: {p.version()}")
		print("Software version: ", p.get_software_version())
		print("Hardware version: ", p.get_hardware_version())
	elif cm == "status":
		print("Status: ", p.get_status())
	elif cm == "codes":
		print("Codes: ", p.get_codes())

	elif cm == "mc":
		data = input("codes:")
		idata = hex_from_str(data)
		m.send(idata, 1)
	elif cm == "exit":
		break
