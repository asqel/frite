import os
import readline
import subprocess
from getpass import getpass
import secrets
import shlex
import commands.ls as c_ls
import commands.add as c_add
import commands.rm as c_rm
import commands.set as c_set
import commands.get as c_get
import commands.clear as c_clear

commands = {
	"ls": c_ls.run,
	"list": c_ls.run,
	"add": c_add.run,
	"rm": c_rm.run,	
	"set": c_set.run,
	"get": c_get.run,
	"clear": c_clear.run
}

def is_wayland():
	return os.environ.get("WAYLAND_DISPLAY") is not None

def is_x11():
	return os.environ.get("DISPLAY") is not None and not is_wayland()

def copy_to_clip(text):
	if is_wayland():
		subprocess.run("wl-copy", input=text, text=True);
	elif is_x11():
		subprocess.run(["xclip", "-selection", "clipboard"], input=text , text=True)

def copy_from_clip() -> str:
	if is_wayland():
		res = subprocess.run("wl-paste", capture_output=True, text=True).stdout
	elif is_x11():
		res = subprocess.run(
			["xclip", "-selection", "clipboard", "-o"],
		capture_output=True, text=True).stdout
	return res

alphabet = "";
for i in range(ord(' ') + 1, ord('~') + 1):
	alphabet += chr(i);

alphabet_utf8 = alphabet + "ΓΔΘΠΛΣΨ" + "Ω" + "δζλξπд£¥¤¦§±øùúûü" + "àáâãäåèéêëñ"

def gen_passwd():
	passwd = "";
	for i in range(35):
		passwd += secrets.choice(alphabet);
	return passwd;

def gen_passwd_utf8():
	passwd = "";
	for i in range(35):
		passwd += secrets.choice(alphabet_utf8);
	return passwd;


"""
name: [username, email, password, extra]
"""

def main(info):
	while 1:
		try:
			cmd = input("\033[35m$ \033[0m");
		except EOFError:
			print();
			break;
		except KeyboardInterrupt:
			print()
			continue
		except Exception as e:
			break;

		try:
			cmd = shlex.split(cmd)
		except Exception as e:
			print(e)
			continue
		if not cmd:
			continue
		try:
			commands[cmd[0]](info, cmd[1:], cmd[0])
		except KeyboardInterrupt:
			...
		except KeyError as e:
			print(f"Unknown command {cmd[0]}")
		except Exception as e:
			print(e)
			
