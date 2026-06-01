import curses
import math
import shlex
import shell

import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

screen_h = 0
screen_w = 0

info = {}

page_idx = 0
page_sub_idx = 0
command = ""

def get_page_len():
	return screen_h - 3

def get_entry_line(entry: str):
	nb_col = 4
	col_size = (screen_w - nb_col + 1) // nb_col

	col = [entry, info[entry][0], info[entry][1], info[entry][3]]
	for i in range(len(col)):
		if len(col[i]) < col_size:
			to_add = col_size - len(col[i])
			left = to_add // 2
			right = to_add - left
			col[i] = " " * left + col[i] + " " * right 
		elif len(col[i]) > col_size:
			col[i] = col[i][:(col_size - 3)] + "..."
	res = f"{col[0]}|{col[1]}|{col[2]}|{col[3]}"
	while len(res) < screen_w:
		res += " "
	return res

def fix_page_idx():
	global page_idx
	global page_sub_idx
	
	page_len = get_page_len()
	nb_pages = math.ceil(len(info.keys()) / page_len)
	if nb_pages == 0:
		page_idx = 0
		page_sub_idx = 0
		return 

	if page_idx >= nb_pages:
		page_idx = nb_pages - 1
		page_sub_idx = page_len - 1

	elif page_sub_idx >= page_len:
		page_sub_idx = page_len - 1

def page_up():
	global page_idx
	global page_sub_idx
	
	if page_idx == 0 and page_sub_idx == 0:
		return 
	
	page_sub_idx -= 1
	if page_sub_idx < 0:
		page_idx -= 1
		page_sub_idx = get_page_len() - 1
	
def page_down():
	global page_idx
	global page_sub_idx

	page_len = get_page_len()
	nb_pages = math.ceil(len(info.keys()) / page_len)
	
	if page_idx == nb_pages -1 and page_sub_idx == page_len - 1:
		return
	
	page_sub_idx += 1
	if page_sub_idx == page_len:
		page_idx += 1
		page_sub_idx = 0

def draw_box(text : str, stdscr):
	lines = [
		"╔" + "═" * len(text) + "╗",
		"║" + text + "║",
		"╚" + "═" * len(text) + "╝",
	]

	y = screen_h / 2 - 1
	x = screen_w / 2 - (len(text) + 2) / 2
	y = int(y)
	x = int(x)
	stdscr.addstr(y, x, lines[0])
	stdscr.addstr(y + 1, x, lines[1])
	stdscr.addstr(y + 2, x, lines[2])
	stdscr.refresh()
	stdscr.getch()

def refresh(stdscr, help_info, col_names, page, focused):
	stdscr.clear()
	if screen_h < 3 or screen_w < 20:
		stdscr.addstr(0, 0, "at least 20x3 term")
		return 
	spaces = max(1, (screen_w - sum(len(i) for i in help_info) - 2) / (len(help_info) - 1))
	spaces = int(spaces)
	top = ""
	x = 1
	for idx, text in enumerate(help_info):
		stdscr.addstr(0, x, text)
		x += len(text) + spaces
	
	col_size = screen_w // len(col_names)
	header = ""
	for i in col_names:
		spaces = col_size - len(i)
		left = spaces // 2
		right = spaces - left
		header += " " * left + i + " " * right
	header += " " * (screen_w - len(header))
	stdscr.addstr(1, 0, header, curses.A_REVERSE)

	for idx, entry in enumerate(page):
		y = 2 + idx
		if y >= screen_h:
			break
		line = ""
		if entry is None:
			line = '-' * screen_w
		else:
			line = get_entry_line(entry)

		if idx == focused:
			stdscr.addstr(y, 0, line, curses.A_REVERSE)
		else:
			stdscr.addstr(y, 0, line)
	command_line = command
	if len(command_line) > screen_w:
		command_line = command_line[(len(command_line) - screen_w):]
	stdscr.addstr(2 + get_page_len(), 0, command_line)


	stdscr.refresh()
		
def build_pages():
	pages = [[None] * get_page_len()]

	idx = 0
	for key in info.keys():
		if idx == len(pages[-1]):
			pages.append([None] * screen_h)
			idx = 0
		pages[-1][idx] = key

		idx += 1
	
	return pages

MOD_NORMAL = 0
MOD_CMD = 1
MOD_SEARCH = 2

current_mod = MOD_NORMAL

def on_key_normal(key: int, pages, stdscr):
	global page_sub_idx, page_idx
	global current_mod
	global command

	if key == ord('j'):
		page_down()
	elif key == ord('k'):
		page_up()
	elif key == ord(':'):
		current_mod = MOD_CMD
		if len(command) == 0:
			command += ":"
	elif key == ord('y'):
		if stdscr.getch() == ord('y'):
			shell.copy_to_clip(info[pages[page_idx][page_sub_idx]][2])
			draw_box("Copied to Clipboard", stdscr)

	
	while (pages[page_idx][page_sub_idx] is None and page_sub_idx > 0):
		page_sub_idx -= 1

def exec_command():
	global info

	try:
		argv = shlex.split(command)
	except:
		return 
	if not argv:
		return 

	if argv[0] in (':n', ':na'):
		# :n name [uname] [email] [extra]
		if len(argv) < 2:
		 	return 
		key = argv[1]
		if key in info.keys():
			return 
		elements = ["", "", "", ""]
		for i in range(2, min(5, len(argv))):
			elements[i - 2] = argv[i]
		elements[3] = elements[2]
		if argv[0] == ':na':
			elements[2] = shell.gen_passwd()
		else:
			elements[2] = shell.gen_passwd_utf8()
		info[key] = elements
	if argv[0] == ':q':
		raise KeyboardInterrupt
		
			


def on_key_cmd(key: int):
	global current_mod
	global command

	if key == 0x1b:
		current_mod = MOD_NORMAL
		command = ""
		return 
	if key in (curses.KEY_BACKSPACE, 127, 8):
		if len(command) > 1:
			command = command[:-1]
		return 
	if key in (curses.KEY_ENTER, 10, 13):
		exec_command()
		command = ""
		current_mod = MOD_NORMAL
		return
	try:
		c = chr(key)
		if c.isprintable():
			command += c
			return
	except:
		...
	

def main(stdscr):
	global screen_h, screen_w
	global info
	global current_mod

	curses.curs_set(0)

	help_info = [
		"r: remove",
		"n: new",
		"f or /: search",
		"e: edit",
		"yy: copy password",
		"^C: to quit"

	]
	collumns = ["name", "username", "email", "info"]

	screen_h, screen_w = stdscr.getmaxyx()
	screen_h -= 1
	screen_w -= 1
	fix_page_idx()
	pages: list[list[str]] = build_pages()
	refresh(stdscr, help_info, collumns, pages[page_idx], page_sub_idx)
	while (1):
		screen_h, screen_w = stdscr.getmaxyx()
		screen_h -= 1
		screen_w -= 1
		fix_page_idx()
		pages: list[list[str]] = build_pages()
		refresh(stdscr, help_info, collumns, pages[page_idx], page_sub_idx)

		key = stdscr.getch()
		if current_mod == MOD_NORMAL:
			on_key_normal(key, pages, stdscr)
		elif current_mod == MOD_CMD:
			on_key_cmd(key)


def start_visual(info_dict = {}):
	global info
	info = info_dict
	try:
		curses.wrapper(main)
	except KeyboardInterrupt:
		print("exited")
	info = {}
		

if __name__ == "__main__":
	start_visual()
	
