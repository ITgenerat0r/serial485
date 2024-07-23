from device import *
from time import sleep


PATH_DATA = 'Data/'


p = device('COM7')


devices = {}

devices[30051234] = 102
devices[30061234] = 103

while True:
	for d in devices:
		print(d)
		print(devices[d])
		f = open(f"{PATH_DATA}{d}", 'w+')
		f.write(str(devices[d]))
		f.close()
	sleep(1)
	break # dev

