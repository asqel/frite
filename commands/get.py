import shell

def run(info, args, cmd_name):
	if len(args) != 1:
		print(f"{cmd_name} <name>")
		return 
	name = args[0]
	if name not in info:
		print(f"{cmd_name}: {name} not found")
		return 
	shell.copy_to_clip(info[name][2])
	print("Password copied to clipboard")
