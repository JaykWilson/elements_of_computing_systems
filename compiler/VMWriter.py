class VmWriter:

	def __init__(self):
		self.vm_commands = []
		self.command_count = 0

	def write_arithmetic(self, OP):
		self.command_count += 1
		if OP == "+":
			self.vm_commands.append("add")
		elif OP == "-":
			self.vm_commands.append("sub")
		elif OP == "/":
			self.vm_commands.append("call Math.divide 2")
		elif OP == "*":
			self.vm_commands.append("call Math.multiply 2")
		elif OP == "&amp;":
			self.vm_commands.append("and")
		elif OP == "|":
			self.vm_commands.append("or")
		elif OP == "&gt;":
			self.vm_commands.append("gt")
		elif OP == "&lt;":
			self.vm_commands.append("lt")
		elif OP == "=":
			self.vm_commands.append("eq")
		elif OP == "not":
			self.vm_commands.append("not")
	
	def write_unary(self, OP):
		self.command_count += 1
		if OP == "~":
			self.vm_commands.append("not")
		elif OP == "-":
			self.vm_commands.append("neg")


	def write_call(self, subroutine):
		self.command_count += 1
		command = "call " + subroutine
		self.vm_commands.append(command)


	def write_push(self, symbol):
		
		if symbol == "-1":
			self.command_count += 2
			self.vm_commands.append("push constant 0")
			self.vm_commands.append("not")
		else:
			self.command_count += 1
			command = "push " + str(symbol)
			self.vm_commands.append(command)


	def write_pop(self, symbol):
		self.command_count += 1
		command = "pop " + symbol
		self.vm_commands.append(command)


	def write_return(self):
		self.command_count += 1
		self.vm_commands.append("return")


	def write_label(self, label_type, label_name, num):
		self.command_count += 1
		label = label_type + " " + label_name + str(num)
		self.vm_commands.append(label)


	def reset_command_counter(self):
		self.command_count = 0


	def write_function(self, func_name, nargs):
		func_idx = len(self.vm_commands) - self.command_count
		print("func", func_name)
		print("command_count", self.command_count)
		print("vm_commands", len(self.vm_commands))
		print("idx", func_idx)
		command = "function " + func_name + " " + str(nargs)
		self.vm_commands.insert(func_idx, command)
		self.reset_command_counter()


	def get_commands(self):
		return self.vm_commands


	def print_vm_commands(self):
		print(self.vm_commands)

	def reset(self):
		self.reset_command_counter()
		self.vm_commands.clear()
