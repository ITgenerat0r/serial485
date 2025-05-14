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



# where first row is titles, others data
def show_list_table(data):
	if len(data):
		print()
		titles = []
		titles_len = {}
		# titles_rows = {}
		header = ""
		for title in data[0]:
			titles.append(title)
			titles_len[title] = len(title)
			# titles_rows[title] = []
		for row in data:
			for title in titles:
				if len(str(row[title])) > titles_len[title]:
					titles_len[title] = len(str(row[title]))
		filler = " "*100
		border_filler = "-"*100
		text, border, head = "", "", ""
		for title in titles:
			border += "+-"
			head += "| "
			head += (title + filler)[:titles_len[title]]
			border += border_filler[:titles_len[title]]
		border += "-+\n"
		head += " |\n"
		text = border + head + border
		for row in data:
			txt_row = ""
			for title in titles:
				txt_row += "| "
				txt_row += (str(row[title]) + filler)[:titles_len[title]]
			txt_row += " |\n"
			text += txt_row
			text += border
		return text
	return ''


# list of maps
def show_map_table(data):
	if len(data):
		titles = []
		titles_len = {}
		header = ""
		for row in data:
			for title in row:
				if not title in titles:
					titles.append(title)
					titles_len[title] = len(title)+1
				if len(str(row[title]))+1 > titles_len[title]:
					titles_len[title] = len(str(row[title]))+1
		filler = " "*100
		border_filler = "-"*100
		text, border, head = "", "", ""
		for title in titles:
			border += "+-"
			head += "| "
			head += (str(title) + filler)[:titles_len[title]]
			border += border_filler[:titles_len[title]]
		border += "-+\n"
		head += " |\n"
		bold_border = border.replace('-', '=')
		text = bold_border + head + bold_border
		for row in data:
			txt_row = ""
			for title in titles:
				txt_row += "| "
				if title in row:
					txt_row += (str(row[title]) + filler)[:titles_len[title]]
				else:
					txt_row += filler[:titles_len[title]]
			txt_row += " |\n"
			text += txt_row
			text += border
		return text
	return ''