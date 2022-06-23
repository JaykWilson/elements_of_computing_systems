import argparse

class Assembler:

	def __init__(self):
		self.bin_file = []
		self.commands = []
		parser = argparse.ArgumentParser()
		parser.add_argument('--file', type = str, required = True)
		args = parser.parse_args()
		self.function_name = args.file.split(".")[:1]

		with open(args.file) as original_file:
			f = original_file.read()
		self.assembly_file = f

		self.symbol_table = {'SCREEN':16384, 'KBD':24576, 'SP':0, 'LCL':1, 'ARG':2, 'THIS':3, 'THAT':4}

		self.dest_command_list = {'':'000', 'M':'001', 'D':'010', 'DM':'011', 'A':'100', 'AM':'101', 
					'AD':'110', 'ADM':'111'}

		self.comp_command_list = {'':'',
					'0':'0101010',
					'1':'0111111',
					'-1':'0111010',
					'D':'0001100',
					'A':'0110000',
					'M':'1110000',
					'!D':'0001101',
					'!A':'0110001',
					'!M':'1110001',
					'-D':'0001111',
					'-A':'0110011',
					'-M':'1110011',
					'D+1':'0011111',
					'A+1':'0110111',
					'M+1':'1110111',
					'D-1':'0001110',
					'A-1':'0110010',
					'M-1':'1110010',
					'D+A':'0000010',
					'D+M':'1000010',
					'D-A':'0010011',
					'D-M':'1010011',
					'A-D':'0000111',
					'M-D':'1000111',
					'D&A':'0000000',
					'D&M':'1000000',
					'D|A':'0010101',
					'D|M':'1010101'}

		self.jump_command_list = {'':'000',
					'JGT':'001',
					'JEQ':'010',
					'JGE':'011',
					'JLT':'100',
					'JNE':'101',
					'JLE':'110',
					'JMP':'111'}


		for i in range(16):
			temp = "R" + str(i)
			self.symbol_table[temp] = i

	def tokenize(self):
		# this function parses out the command list into individual commands,
		# removes tabs, removes whitespace, removes blank lines, 
		# removes comments and creates a new list of cleaned commands
		self.commands = self.assembly_file.split('\n')
		temp_list = []
		for i, command in enumerate(self.commands):
			self.commands[i] = command.replace("   ","")
			command = command.replace(" ","")
			if command == '\n' or command  == '':
				pass
			elif command[:2] == "//":
				pass
			elif "//" in command:
				command = command.split("//")[0]
				temp_list.append(command)
			else:
				temp_list.append(command)
		self.commands = temp_list

	def parse_possible_variables_and_labels(self):
		# this function uses the two pass method for differentiating between
		# variables and labels. variables are of the form "@variable_name"
		# while labels (or goto statements) are of the form "@label_name"
		# but also have a corresponding goto location of the form "(label_name)"
		# since either the label name in parentheses or command to jump there may
		# be seen first, we aren't sure until we've parsed the entire file whether 
		# a command starting with a "@" denotes a jump-to-label or variable command
		possible_variables = []
		num_label_lorrection = 0
		for i, command in enumerate(self.commands):
			first_char = command[0]
			if first_char == '(':
				last_char = command[-1]
				label_name = command[1:len(command)-1]
				if last_char == ')':
					if label_name not in self.symbol_table:
						self.symbol_table[label_name] = i - num_label_lorrection
						num_label_lorrection += 1
						if label_name in possible_variables:
							possible_variables.remove(label_name)
					else:
						print("Error: only one declaration of label allowed")
				else:
					print("Error: improper formatting; missing ')'")
			elif first_char == '@':
				label_name = command[1:len(command)]
				#change name of possible_variables to possibly a variable
				if label_name not in self.symbol_table and not label_name.isnumeric() and label_name not in possible_variables:
					possible_variables.append(label_name)
		# variables are stored starting at RAM[16]
		for i, var in enumerate(possible_variables):
			self.symbol_table[var] = 16 + i

	def convert_to_binary(self):
		for i, command in enumerate(self.commands):
			dest_command = ''
			comp_command = ''
			jump_command = ''
			first_char = command[0]
			# commands that are enclosed in parantheses are just labels so they are ignored when converting to binary
			if first_char == '(':
				continue
			else:
				if first_char =='@':
					# A INSTRUCTION
					label_name = command[1:len(command)]
					#a_instructions with numeric values are translated into binary directly 
					if label_name.isnumeric():
						a_instruction = '0' + str(format(int(label_name),'015b'))
						self.bin_file.append(a_instruction)
					else:
						# a_instructions that are not numeric values represent variables
						a_instruction = '0' + str(format(self.symbol_table[label_name],'015b'))
						self.bin_file.append(a_instruction)
				else:
					#C INSTRUCTION
					if '=' in command:
						dest_command = command[:command.index('=')]
						dest_command = ''.join(sorted(dest_command))
						if dest_command not in self.dest_command_list:
							print("Error: destination command syntax not recognized")
						comp_command = command[command.index('=') + 1 :]
						if ';' in comp_command:
							comp_command = comp_command[: comp_command.index(';')]
						if comp_command not in self.comp_command_list:
							print("Error: comp command syntax not recognized")
					if ';' in command:
						jump_command = command[command.index(';') + 1 :]
						if '=' not in command:
							comp_command = command[:command.index(';')]
					c_instruction = '111' + self.comp_command_list[comp_command] + self.dest_command_list[dest_command] 
							+ self.jump_command_list[jump_command]
					self.bin_file.append(c_instruction)

	def write_binary_file(self):
		bin_file_name = self.function_name[0] + ".hack"
		with open(bin_file_name, 'w') as f:
			for line in self.bin_file:
				f.write(line)
				f.write("\n")


hackAssembler = Assembler()
hackAssembler.tokenize()
hackAssembler.parse_possible_variables_and_labels()
hackAssembler.convert_to_binary()
hackAssembler.write_binary_file()
