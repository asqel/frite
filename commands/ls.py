
def run(info, args, cmd_name = "ls") -> None:
	is_l = False
	is_a = False
	for i in args:
		if not i.startswith("-"):
			continue
		is_l = is_l or ('l' in i)
		is_a = is_a or ('a' in i)
	for i, k in info.items():
		print(i, end = "")

		if is_l:
			print("", k[0], k[1], end = "")
		if is_a:
			print("", k[3], end = "")

		print()
