import requests
import colorama
from colorama import Fore, Back, Style
colorama.init()
from sys import platform
import datetime




operating_system = 'unknown'

if platform == "linux" or platform == "linux2":
  operating_system = 'linux'
elif platform == "darwin":
  operating_system = 'x'
elif platform == "win32":
  operating_system = 'windows'



def get_time():
  return datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")[:-3]


def print_time(ps="", oc=True):
	now = datetime.datetime.now()
	if oc:
		print(now.strftime("%H:%M:%S"), ps)
	else:
		return now.strftime("%H:%M:%S")+" "+ps


def get_out_ip():
	try:
		response = requests.get("https://2ip.ru")
		if response.status_code != 200:
			return "unknown"
		t = response.text

		page = str(t)
		key = "return '"
		index = page.find(key)
		if index < 0:
			return "unknown"
		res = page[index+len(key):index+len(key)+16]
		index = res.find("'")
		if index:
			res = res[:index]
		return res
	except Exception as e:
		return "unknown"
		

dbgs = True
def dbg(text=""):
	if dbgs:
		print(text)


def red_text(text):
  return Fore.RED + text + Style.RESET_ALL

def blue_text(text):
  return Fore.BLUE + text + Style.RESET_ALL

def green_text(text):
  return Fore.GREEN + text + Style.RESET_ALL

def yellow_text(text):
  return Fore.YELLOW + text + Style.RESET_ALL