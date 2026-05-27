import shell

def run(info, args, cmd_name):
	if len(args) == 1 and args[0] == "-h":
		print(f"{cmd_name} <name> <arg>, arg={{-p, -ps, -u, -e, -x}}")
		print("\t-ps: set password from stdin")
		print("\t-p : set password from clipboard")
		print("\t-u : set username")
		print("\t-e : set email")
		print("\t-x : set extra from stdin")
		return 
	if len(args) != 2:
		print(f"{cmd_name} <name> <arg>, arg={{-p, -ps, -u, -e, -x}}")
		return 

	name = args[0]
	mode = args[1]
	if name not in info:
		print(f"{cmd_name}: {name} not found")
		return 

	if mode == "-ps":
		new_passwd = input("new password $> ")	
		info[name][2] = new_passwd
	elif mode == "-p":
		info[name][2] = shell.copy_from_clip()
	elif mode == "-u":
		info[name][0] = input("new username $> ")
	elif mode == "-e":
		info[name][1] = input("new emai $> ")
	elif mode == "-x":
		info[name][3] = input("new extra $> ")
