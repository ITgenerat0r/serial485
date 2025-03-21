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

		

dbgs = True
def dbg(text=""):
	if dbgs:
		print(text)


def red_text(text):
  return Fore.RED + str(text) + Style.RESET_ALL

def blue_text(text):
  return Fore.BLUE + str(text) + Style.RESET_ALL

def green_text(text):
  return Fore.GREEN + str(text) + Style.RESET_ALL

def yellow_text(text):
  return Fore.YELLOW + str(text) + Style.RESET_ALL