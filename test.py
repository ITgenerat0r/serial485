
rx = 0

x = [0xff, 0xff]

for i in x:
	print(i, hex(i))
	rx <<= 8
	rx += i

	print(rx, hex(rx))