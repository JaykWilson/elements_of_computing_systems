import sys
import os

class Parser:

	arithmetic_commands_template = {'add':['@SP', 'AM=M-1', 'D=M', '@SP', 'AM=M-1', 'MD=D+M', '@SP', 'M=M+1'],

					'sub':[ '@SP', 'AM=M-1','D=M', '@SP', 'AM=M-1', 'MD=M-D', '@SP','M=M+1'],

					'neg':[ '@SP', 'AM=M-1', 'D=M', '@insert_neg_temp_var', 'M=D', '@0', 'D=A',
						'@SP', 'A=M', 'M=D', '@SP', 'M=M+1', '@insert_neg_temp_var', 'D=M',
						'@SP', 'A=M', 'M=D', '@SP',	'M=M+1', 'insert_sub_commands',],

					'rel':[ 'insert_sub_commands', '@SP', 'AM=M-1', 'D=M', '@replace_relation_true',
						'D;replace_relation_specific_jump_command', '@replace_relation_false',
						'0;JMP', '(replace_relation_true)', '@0', 'D=A-1', '@SP', 'A=M', 'M=D',
						'@SP', 'M=M+1', '@END', '0;JMP', '(replace_relation_false)', '@0', 'D=A',
						'@SP', 'A=M', 'M=D', '@SP', 'M=M+1', '(END)',],

					'and':[ '@SP', 'AM=M-1', 'M=D', '@SP', 'AM=M-1', 'M=D&M', '@SP', 'M=M+1',],

					'or':[ '@SP', 'AM=M-1', 'M=D', '@SP', 'AM=M-1', 'M=D|M', '@SP', 'M=M+1',],

					'not':[ '@SP', 'AM=M-1', 'M=!M', '@SP', 'M=M+1',],

					#gt, let, eq commands handled by 'rel' above
					'gt':'NULL',
					'lt':'NULL',
					'eq':'NULL',
					}


	push_data_from_address_template = ['@replace_segment_pointer', 'D=M', '@i', 'D=D+A', 'A=D', 'D=M']


	push_data_to_stack_commands = ['@SP', 'A=M', 'M=D', '@SP', 'M=M+1']


	pop_data_from_stack_commands = ['@SP', 'AM=M-1', 'D=M']


	pop_memory_command_template = ['@replace_segment_pointer', 'D=M', '@i', 'D=D+A', '@address', 'M=D', '@SP',
						'AM=M-1', 'D=M', '@address', 'A=M', 'M=D']


	function_return_commands = [# endFrame = LCL
				'@LCL', 'D=M', '@R13', 'M=D',
				# retAddr = *(endFrame - 5)
				'@5', 'D=A', '@R13', 'A=M-D', 'D=M', '@R14', 'M=D',
				# *ARG = pop()
				'@SP', 'AM=M-1', 'D=M', '@ARG', 'A=M', 'M=D',
				# SP = ARG + 1
				'@ARG', 'D=M+1', '@SP', 'M=D',
				# THAT = *(endFrame -1)
				'@R13', 'A=M-1', 'D=M', '@THAT', 'M=D',
				# THIS = *(endFrame -2)
				'@2', 'D=A', '@R13', 'A=M-D', 'D=M', '@THIS', 'M=D',
				# ARG = *(endFrame -3)
				'@3', 'D=A', '@R13', 'A=M-D', 'D=M', '@ARG', 'M=D',
				# LCL = *(endFrame - 4)
				'@4', 'D=A', '@R13', 'A=M-D', 'D=M', '@LCL', 'M=D',
				# goto retAddr
				'@R14', 'A=M', '0;JMP']


	def set_raw_commands(self,raw_commands):
		self.commands = raw_commands

	def get_parsed_commands(self):
		temp = [command for command in self.commands if command != '']
		self.commands = [command for command in temp if command[:2] != '//']
		return Parser.commands

	def is_arithmetic_command(self,command):
		return command in Parser.arithmetic_commands_template

	def is_memory_command(self,command):
		return command == 'push' or command == 'pop'

	def is_branch_command(self,command):
		return command == 'goto' or command == 'if-goto' or command == 'label'

	def is_function_command(self,command):
		return command == 'function' or command == 'call' or command == 'return'


class Translator:
	pop_address_counter = 0
	function_count = 0
	unique_label_counter = {'gt':0,'lt':0,'eq':0,'neg':0}
	relational_jump_command = {'gt':'JGT','lt':'JLT','eq':'JEQ'}
	
	def __init__(self,add_bootstrap,file):
		# bootstrap code is not used when translating a single vm file
		# as it's assumed not needed
		if add_bootstrap:
			bootstrap_stack_pointer = ['@256','D=A','@SP','M=D']
			comment = '//Set RAM[0]=256'
			self._write_comment_and_commands_to_file(file,bootstrap_stack_pointer,comment)
			self.write_function_to_file('call Sys.init 0',file)

	def _get_relational_command(self,comparison):
		# this function formats relational commands (equal, greater than, less than) including
		# ensuring each instance of temporary variable used is unique across instances of the
		# same command
		Translator.unique_label_counter[comparison] += 1
		relational_commands = Parser.arithmetic_commands_template['rel'][:]
		relational_commands.remove('insert_sub_commands')
		relational_commands = Parser.arithmetic_commands_template['sub'] + relational_commands
		for i in range(len(relational_commands)):
			if 'replace_relation_specific_jump_command' in relational_commands[i]: 
				relational_commands[i] = relational_commands[i].replace('replace_relation_specific_jump_command'
											,Translator.relational_jump_command[comparison])

			if 'replace_relation_true' in relational_commands[i]:
				relational_commands[i] = relational_commands[i].replace('replace_relation_true', comparison + '_true_' 
											+ str(Translator.unique_label_counter[comparison]))

			if 'replace_relation_false' in relational_commands[i]:
				relational_commands[i] = relational_commands[i].replace('replace_relation_false', comparison + '_false_' 
											+ str(Translator.unique_label_counter[comparison]))

			if 'END' in relational_commands[i]:
				relational_commands[i] = relational_commands[i].replace('END', comparison + '_end_' 
											+ str(Translator.unique_label_counter[comparison]))
		return relational_commands

	def _get_add_command():
		return Parser.arithmetic_commands_template['add']

	def _get_sub_command():
		return Parser.arithmetic_commands_template['sub']

	def _get_gt_command():
		return Translator._get_relational_command('gt')

	def _get_neg_command():
		Translator.unique_label_counter['neg'] += 1
		negCommands = Parser.arithmetic_commands_template['neg'][:]
		negCommands.remove('insert_sub_commands')
		negCommands = negCommands + Parser.arithmetic_commands_template['sub']
		for i in range(len(negCommands)):
			if negCommands[i] == '@insert_neg_temp_var':
				negCommands[i] = negCommands[i].replace('insert_neg_temp_var','insert_neg_temp_var_' + str(Translator.unique_label_counter['neg']))
		return negCommands

	def _get_lt_command():
		return Translator._get_relational_command('lt')

	def _get_eq_command():
		return Translator._get_relational_command('eq')

	def _get_and_command():
		return Parser.arithmetic_commands_template['and']

	def _get_or_command():
		return Parser.arithmetic_commands_template['or']

	def _get_not_command():
		return Parser.arithmetic_commands_template['not']

	def set_vm_file_name(self,vm_file_name):
		self.vm_file_name = vm_file_name.split('.')[0]

	_get_arithmetic_commands = {"add": _get_add_command,'sub': _get_sub_command,'gt': _get_gt_command,'lt': _get_lt_command
				    ,'eq': _get_eq_command,'neg': _get_neg_command,'and': _get_and_command,'or': _get_or_command
				    , 'not': _get_not_command}

	def _write_comment_and_commands_to_file(self,file,assembly_command_list,comment):
		file.write(comment)
		file.write("\n")
		for i, line in enumerate(assembly_command_list):
			file.write(line)
			file.write("\n")

	def _write_arithmetic_to_file(self,command,file):
		assembly_command_list = Translator._get_arithmetic_commands[command]()
		assembly_command_comment = '//' + command
		Translator._write_comment_and_commands_to_file(file,assembly_command_list,assembly_command_comment)

	def _list_replace(self,my_list,element_to_replace,new_element,num_occurences=-1):
		if num_occurences == -1:
			num_replacements = len(my_list)
		else:
			num_replacements = num_occurences
		replacement_count = 0

		for i in range(len(my_list)):
			if my_list[i] == element_to_replace:
				my_list[i] = new_element
				replacement_count += 1
			if replacement_count >= num_replacements:
				break

	def _push_data_from_address_commands(self,virtual_segment,index):
		# this function formats specific push commands from a generalized
		# push_data_from_address template.
		# the general push command template is calculate address = segment pointer address + i,
		# push data stored at that address to the stack, increment the stack pointer
		if virtual_segment == 'local':
			address_data_command = Parser.push_data_from_address_template[:]
			Translator._list_replace(address_data_command,'@replace_segment_pointer','@LCL',1)
			Translator._list_replace(address_data_command,'@i','@' + str(index),1)
		elif virtual_segment == 'argument':
			address_data_command = Parser.push_data_from_address_template[:]
			Translator._list_replace(address_data_command,'@replace_segment_pointer','@ARG',1)
			Translator._list_replace(address_data_command,'@i','@' + str(index),1)
		elif virtual_segment == 'this':
			address_data_command = Parser.push_data_from_address_template[:]
			Translator._list_replace(address_data_command,'@replace_segment_pointer','@THIS',1)
			Translator._list_replace(address_data_command,'@i','@' + str(index),1)
		elif virtual_segment == 'that':
			address_data_command = Parser.push_data_from_address_template[:]
			Translator._list_replace(address_data_command,'@replace_segment_pointer','@THAT',1)
			Translator._list_replace(address_data_command,'@i','@' + str(index),1)
		elif virtual_segment == 'static':
			address_data_command = ['@' + self.vm_file_name + '.' + str(index),'D=M']
		elif virtual_segment == 'constant':
			address_data_command = ['@' + str(index),'D=A']
		elif virtual_segment == 'temp':
			address_data_command = ['@5','D=A','@' + str(index),'A=D+A','D=M']
		elif virtual_segment == 'pointer':
			address_data_command = ['@THIS' if index == '0' else '@THAT','D=M']
		else:
			address_data_command = ['ERROR: virtual segment not recognized']
			print("ERROR: virtual segment not recognized")
		return address_data_command

	def _popDatatoAddressCommands(self,virtual_segment,index):
		# this function formats specific pop commands from a generalized pop_memory_command_template
		# the general pop command format is calculate address = segment pointer address + i, 
		# decrement the stack pointer, store the data located at the top of the stack and 
		# store it in the address calculated for the specific segment pointer location
		Translator.pop_address_counter += 1
		if virtual_segment == 'local':
			write_command_list = Parser.pop_memory_command_template[:]
			Translator._list_replace(write_command_list,'@replace_segment_pointer','@LCL',1)
			Translator._list_replace(write_command_list,'@i','@' + str(index),1)
			uniqueAddress = '@address' + str(Translator.pop_address_counter)
			Translator._list_replace(write_command_list,'@address',uniqueAddress,2)
		elif virtual_segment == 'argument':
			write_command_list = Parser.pop_memory_command_template[:]
			Translator._list_replace(write_command_list,'@replace_segment_pointer','@ARG',1)
			Translator._list_replace(write_command_list,'@i','@' + str(index),1)
			uniqueAddress = '@address' + str(Translator.pop_address_counter)
			Translator._list_replace(write_command_list,'@address',uniqueAddress,2)
		elif virtual_segment == 'this':
			write_command_list = Parser.pop_memory_command_template[:]
			Translator._list_replace(write_command_list,'@replace_segment_pointer','@THIS',1)
			Translator._list_replace(write_command_list,'@i','@' + str(index),1)
			uniqueAddress = '@address' + str(Translator.pop_address_counter)
			Translator._list_replace(write_command_list,'@address',uniqueAddress,2)
		elif virtual_segment == 'that':
			write_command_list = Parser.pop_memory_command_template[:]
			Translator._list_replace(write_command_list,'@replace_segment_pointer','@THAT',1)
			Translator._list_replace(write_command_list,'@i','@' + str(index),1)
			uniqueAddress = '@address' + str(Translator.pop_address_counter)
			Translator._list_replace(write_command_list,'@address',uniqueAddress,2)
		elif virtual_segment == 'static':
			write_command_list = ['@' + self.vm_file_name + '.' + str(index),'M=D']
		elif virtual_segment == 'temp':
			write_command_list = ['@5','D=A','@' + str(index),'D=D+A','@popaddress' + str(Translator.pop_address_counter)
					      ,'M=D','@SP','AM=M-1','D=M','@popaddress' + str(Translator.pop_address_counter),'A=M','M=D']
		elif virtual_segment == 'pointer':
			write_command_list = ['@THIS' if index == '0' else '@THAT','M=D']
		else:
			write_command_list = ['ERROR: virtual segment not recognized']
			print("ERROR: virtual segment not recognized")
		return write_command_list

	def write_push_pop_to_file(self,command,virtual_segment,index,file):
		if command == 'push':
			assembly_command_list = Translator._push_data_from_address_commands(virtual_segment,index) + Parser.push_data_to_stack_commands
			assembly_command_comment = '//' + command + ' ' + virtual_segment + ' ' + index
			Translator._write_comment_and_commands_to_file(file,assembly_command_list,assembly_command_comment)
		elif command == 'pop':
			if virtual_segment == 'static' or virtual_segment == 'pointer':
				assembly_command_list = Parser.pop_data_from_stack_commands + Translator._popDatatoAddressCommands(virtual_segment,index)
			else:
				assembly_command_list = Translator._popDatatoAddressCommands(virtual_segment,index)
			assembly_command_comment = '//' + command + ' ' + virtual_segment + ' ' + index
			Translator._write_comment_and_commands_to_file(file,assembly_command_list,assembly_command_comment)

	def write_branch_to_file(self,command,label,file):
		if command == 'goto':
			assembly_command_list = ['@' + label, '0;JMP']
		elif command == 'label':
			assembly_command_list = ['(' + label + ')']
		elif command == 'if-goto':
			assembly_command_list = Parser.pop_data_from_stack_commands[:]
			assembly_command_list = assembly_command_list + ['@' + label,'D;JNE']
		assembly_command_comment = '//' + command + ' ' + label
		Translator._write_comment_and_commands_to_file(file,assembly_command_list,assembly_command_comment)

	def write_function_to_file(self,full_command,file):
		parsed_command_list = full_command.split(' ')
		command = parsed_command_list[0]
		if command == 'return':
			assembly_command_list = Parser.function_return_commands[:]
		elif command == 'function':
			function_name = parsed_command_list[1]
			n_vars = int(parsed_command_list[2])
			assembly_command_list = ['(' + function_name + ')']
			push_nvars_zeros = Translator._push_data_from_address_commands('constant',0) + Parser.push_data_to_stack_commands
			for i in range(n_vars):
				assembly_command_list = assembly_command_list + push_nvars_zeros
		elif command == 'call':
			Translator.function_count += 1
			function_name = parsed_command_list[1]
			n_args = int(parsed_command_list[2])
			# push return address and add function name label to command stream
			assembly_command_list = ['@' + function_name + '$ret.' + str(Translator.function_count),'D=A'] + Parser.push_data_to_stack_commands
			# push LCL
			assembly_command_list = assembly_command_list + ['@LCL','D=M'] + Parser.push_data_to_stack_commands
			# push ARG
			assembly_command_list = assembly_command_list + ['@ARG','D=M'] + Parser.push_data_to_stack_commands
			# push THIS
			assembly_command_list = assembly_command_list + ['@THIS','D=M'] + Parser.push_data_to_stack_commands
			# push THAT
			assembly_command_list = assembly_command_list + ['@THAT','D=M'] + Parser.push_data_to_stack_commands
			# save SP of caller in ARG, ARG = SP-5-n_args
			assembly_command_list = assembly_command_list + ['@' + str(5+n_args),'D=A','@SP','D=M-D','@ARG','M=D']
			# set locals to stack pointer for callee, LCL = SP
			assembly_command_list = assembly_command_list + ['@SP','D=M','@LCL','M=D']
			# goto callee now
			assembly_command_list = assembly_command_list + ['@' + function_name,'0;JMP']
			# add return label to command stream
			assembly_command_list = assembly_command_list + ['(' + function_name + '$ret.' + str(Translator.function_count) + ')']
		assembly_command_comment = '//' + full_command
		self._write_comment_and_commands_to_file(file,assembly_command_list,assembly_command_comment)

# MAIN
input_arg = sys.argv[1]
if os.path.isdir(input_arg):
	output_file_name = os.path.basename(input_arg) + '.asm'
	directory_contents = os.listdir(input_arg)
	vm_file_list = [x for x in directory_contents if '.vm' in x]
	os.chdir(input_arg)
	add_bootstrap = True
elif os.path.isfile(input_arg):
	output_file_name = os.path.basename(input_arg).replace('vm','asm')
	vm_file_list = [os.path.basename(input_arg)]
	os.chdir(os.path.dirname(input_arg))
	add_bootstrap = False
else:
	print('Directory or File not recognized')
	sys.exit()

Parser = Parser()
with open(output_file_name,"w") as file:
	Translator = Translator(add_bootstrap,file)
	for i, vm_file in enumerate(vm_file_list):
		Translator.set_vm_file_name(vm_file)
		with open(vm_file) as f:
			data = f.read()
		raw_commands = data.split('\n')
		Parser.set_raw_commands(raw_commands)
		command_list = Parser.get_parsed_commands()
		for i, command in enumerate(command_list):
			command_components = command.split(' ')
			if Parser.is_arithmetic_command(command_components[0]):
				Translator._write_arithmetic_to_file(command_components[0],file)
			elif Parser.is_memory_command(command_components[0]):
				Translator.write_push_pop_to_file(command_components[0],command_components[1],command_components[2],file)
			elif Parser.is_branch_command(command_components[0]):
				Translator.write_branch_to_file(command_components[0],command_components[1],file)
			elif Parser.is_function_command(command_components[0]):
				Translator.write_function_to_file(command,file)
