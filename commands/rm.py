def run(info, args, cmd_name):
	if len(args) != 1:
		print(f"{cmd_name} <name>")
		return 

	if args[0] not in info:
		print(f"{cmd_name}: {args[0]} not found")
		return 
		
	res = input("Do you really want to delete {args[0]} ? [y/N]")
	res = res.lower()
	if res in ["yes", "y"]:
		del info[args[0]]
		print("Success")
	else:
		print("Aborted")
