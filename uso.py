import requests
import socket
from includes import *

HOST = "192.168.80.2"
PORT = 80

# BEGIN = b'\x41\x54\x41\x44'
# END = b'\x2e\x44\x4e\x45'

BEGIN = b'\x44\x41\x54\x41'
END = b'\x45\x4e\x44\x2e'
DATA = b'sensorinforq'

SIZE = len(DATA).to_bytes(1)

def print_bytes(d):
	for i in d:
		print(hex(i))

# print_bytes(DATA)

try:
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((HOST, PORT))
		req = BEGIN+SIZE+DATA+END
		print("=> ", req)
		s.sendall(req)
		rx = s.recv(1024)
		print("<= ", rx)
except Exception as e:
	print("Exception raised: ", e)




