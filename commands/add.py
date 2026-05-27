import shell
"""
add <name> [username] [email]

"""
def run(info, args, cmd_name="add"):
	if len(args) == 0 or len(args) > 3:
		print(f"{cmd_name} <name> [username] [email]")
		return 
	name = args[0]
	username = ""
	email = ""
	if name in info:
		print(f"{cmd_name}: {name} already exists")
		return
		
	if len(args) >= 2:
		username = args[1]
	if len(args) >= 3:
		email = args[2]
	info[name] = [username, email, shell.gen_passwd(), ""]
