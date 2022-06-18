import os
import sys
import argparse
import SymbolTableList
import CompilationTokenizer
import VMWriter
import pdb


class CompilationEngine:

	def __init__(self):
		self.compiled_xml = []
		self.tokenized_xml = []
		self.token_iterator = 0
		self.indents = 0
		self.if_label_num = 0
		self.while_label_num = 0
		self.class_name = ""
		self.void_functions = []
		self.current_func_nargs = 0
		self.symbol_tables = SymbolTableList.LinkedList()
		self.vm_writer = VMWriter.VmWriter()

		self.op_list = ['+','-','*','/','&amp;','|','&lt;','&gt;','=']

		self.unary_list = ['-', '~']

		self.keyword_constants = ['true','false','null','this']

		self.func_tag = {'class': 'class', 'static': 'classVarDec', 'field': 'classVarDec', 'var': 'varDec',
					'let': 'letStatement', 'while': 'whileStatement', 'do': 'doStatement', 'return': 'returnStatement', 'method': 'subroutineDec',
					'function': 'subroutineDec', 'constructor': 'subroutineDec', 'expression': 'expression', 'statements': 'statements',
					'term': 'term', 'subroutineBody': 'subroutineBody', 'subroutineDec': 'subroutineDec', 'parameterList': 'parameterList',
					'expressionList': 'expressionList', 'if': 'ifStatement'}


	def format_scoped_structure(self, token):
		func = CompilationEngine.functions[token]
		xml_tag = CompilationEngine.func_tag[token]
		def wrap():
			opening_xml_tag = "<" + xml_tag + ">"
			CompilationEngine.write_compiled_xml(opening_xml_tag)
			CompilationEngine.indents += 1
			func()
			closing_xml_tag = "</" + xml_tag + ">"
			CompilationEngine.indents -= 1
			CompilationEngine.write_compiled_xml(closing_xml_tag)
		return wrap


	def pop_token(self):
		current_token_xml = CompilationEngine.tokenized_xml[CompilationEngine.token_iterator]
		# print(current_token_xml)
		CompilationEngine.token_iterator += 1
		return current_token_xml


	def peek_current_token(self):
		token_xml_split = CompilationEngine.tokenized_xml[CompilationEngine.token_iterator].split()
		print("NO SPLIT", CompilationEngine.tokenized_xml[CompilationEngine.token_iterator])
		print("XML SPLIT", token_xml_split)
		token_type = token_xml_split[0][1:-1]
		if token_type == "stringConstant":
			token = ' '.join(token_xml_split[1:-1])
		else:
			token = token_xml_split[1]
		print("TOKEN:", token)
		return token


	def peek_current_type(self):
		token_xml_split = CompilationEngine.tokenized_xml[CompilationEngine.token_iterator].split()
		token_type = token_xml_split[0][1:-1]
		token = token_xml_split[1]
		return token_type


	def peek_next_token(self):
		if CompilationEngine.token_iterator < len(CompilationEngine.tokenized_xml) - 1:
			token_xml_split = CompilationEngine.tokenized_xml[CompilationEngine.token_iterator + 1].split()
			token_type = token_xml_split[0][1:-1]
			token = token_xml_split[1]
			return token
		else:
			raise Exception("Syntax error: out of bounds check")


	def write_compiled_xml(self,current_token_xml):
		indent = ""
		for i in range(CompilationEngine.indents):
			indent += "  "
		current_token_xml = indent + current_token_xml
		CompilationEngine.compiled_xml.append(current_token_xml)


	def set_verified_xml_tokens(self,verified_tokens_xml):
		CompilationEngine.compiled_xml.clear()
		CompilationEngine.tokenized_xml.clear()
		CompilationEngine.tokenized_xml = verified_tokens_xml


	def expect_token(self, expected_token):
		current_token = CompilationEngine.peek_current_token()
		if current_token == expected_token:
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token())
		else:
			raise Exception("syntax error: missing expected token")


	def expect_token_type(self, expected_type):
		current_token_type = CompilationEngine.peek_current_type()
		if current_token_type == expected_type:
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token())
		else:
			raise Exception("syntax error: invalid type")


	def optional_token(self, optional_token):
		current_token = CompilationEngine.peek_current_token()
		if current_token == optional_token:
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token())
			return True
		else: 
			return False


	def compile_class_var_dec():
		symbol_kind = CompilationEngine.peek_current_token()                
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token())                         # pop kind (static | field)
		symbol_type = CompilationEngine.peek_current_token()
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token())                         # pop type
		symbol_name = CompilationEngine.peek_current_token()
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token())                         # pop varName
		CompilationEngine.symbol_tables.add_class_symbol(symbol_name, symbol_type, symbol_kind)     # add symbol to symbol table
		while CompilationEngine.optional_token(",") == True:
			symbol_name = CompilationEngine.peek_current_token()
			CompilationEngine.symbol_tables.add_class_symbol(symbol_name, symbol_type, symbol_kind) # add symbol to symbol table
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop varName
		CompilationEngine.expect_token(";")
		return


	def compile_subroutine_dec():
		CompilationEngine.vm_writer.reset_command_counter()
		CompilationEngine.symbol_tables.add_table()                         # init new symbol table for method's locals

		func_type = CompilationEngine.peek_current_token()
		if func_type == "constructor":
			CompilationEngine.vm_writer.write_push("constant " + str(CompilationEngine.symbol_tables.get_num_class_field_var()))       # push num field vars onto stack for alloc
			CompilationEngine.vm_writer.write_call("Memory.alloc 1")
			CompilationEngine.vm_writer.write_pop("pointer 0")
		elif func_type == "method":
			CompilationEngine.symbol_tables.add_subroutine_symbol("this", CompilationEngine.class_name, "argument") # add "this" pointer for all methods to refer to object
			CompilationEngine.vm_writer.write_push("argument 0")
			CompilationEngine.vm_writer.write_pop("pointer 0")  

		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop (constructor | function | method)

		# return_type = CompilationEngine.peek_current_token()
		
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop return type

		func_name = CompilationEngine.class_name + "." +  CompilationEngine.peek_current_token()   # method name


		#POSSIBLY DELETE PRY DONT NEED TO TRACK VOID FUNCTIONS
		# if return_type == 'void':
		# 	CompilationEngine.void_functions.append(func_name)

		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop method name
		CompilationEngine.expect_token("(")
		CompilationEngine.format_scoped_structure("parameterList")()
		CompilationEngine.expect_token(")")
		CompilationEngine.format_scoped_structure("subroutineBody")()
		# CompilationEngine.symbol_tables.print_list()
		# CompilationEngine.symbol_tables.print_class()
		
		nlocals = CompilationEngine.symbol_tables.get_nlocals()
		if func_type == "constructor":
			CompilationEngine.vm_writer.write_function(func_name, nlocals)
		elif func_type == "method":
			# CompilationEngine.symbol_tables.add_subroutine_symbol("this", CompilationEngine.class_name, "argument") # add "this" pointer for all methods to refer to object
			# CompilationEngine.vm_writer.write_push("argument 0")
			# CompilationEngine.vm_writer.write_pop("pointer 0")     
			CompilationEngine.vm_writer.write_function(func_name, nlocals)                                                 	
		elif func_type == "function":
			CompilationEngine.vm_writer.write_function(func_name, nlocals)

		CompilationEngine.symbol_tables.reset_subroutine_tables()

		return


	def compile_parameter_list():
		if CompilationEngine.peek_current_token() == ")":
			return #this case handles an empty parameter list
		else:
			symbol_type = CompilationEngine.peek_current_token()
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token())                            # pop type
			symbol_name = CompilationEngine.peek_current_token()
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token())                            # pop varName
			CompilationEngine.symbol_tables.add_subroutine_symbol(symbol_name, symbol_type, "argument")         # add symbol to symbol table
			while CompilationEngine.optional_token(",") == True:
				symbol_type = CompilationEngine.peek_current_token()
				CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop type
				symbol_name = CompilationEngine.peek_current_token()
				CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop varName
				CompilationEngine.symbol_tables.add_subroutine_symbol(symbol_name, symbol_type, "argument")     # add symbol to symbol table
			return


	def compile_subroutine_body():
		CompilationEngine.expect_token("{")
		current_token = CompilationEngine.peek_current_token()
		while current_token != "}":
			print(current_token)
			if current_token == "var":
				CompilationEngine.format_scoped_structure("var")()
			else:
				CompilationEngine.format_scoped_structure("statements")()
			current_token = CompilationEngine.peek_current_token()
		CompilationEngine.expect_token("}")
		return


	def compile_var_dec():
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop "var"
		symbol_type = CompilationEngine.peek_current_token()
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop type
		symbol_name = CompilationEngine.peek_current_token()
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop varName
		CompilationEngine.symbol_tables.add_subroutine_symbol(symbol_name, symbol_type, "local") # add symbol to symbol table
		while CompilationEngine.optional_token(",") == True:
			symbol_name = CompilationEngine.peek_current_token()
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop varName
			CompilationEngine.symbol_tables.add_subroutine_symbol(symbol_name, symbol_type, "local") # add symbol to symbol table
		CompilationEngine.expect_token(";")
		return


	def compile_let():
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop "let"
		var_name = CompilationEngine.peek_current_token()
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop "varName
		
		array_access = False
		if CompilationEngine.optional_token("[") == True:
			array_access = True
			seg_pointer = CompilationEngine.symbol_tables.get_segment(var_name)
			CompilationEngine.vm_writer.write_push(seg_pointer)
			CompilationEngine.format_scoped_structure("expression")()
			CompilationEngine.vm_writer.write_arithmetic("+")
			CompilationEngine.expect_token("]")

		CompilationEngine.expect_token("=") 		

		if CompilationEngine.optional_token("(") == True:
			CompilationEngine.format_scoped_structure("expression")()
			CompilationEngine.expect_token(")")
		else:
			#This else case may need to be removed/debugged
			CompilationEngine.format_scoped_structure("expression")()
		CompilationEngine.expect_token(";")

		if array_access == True:
			CompilationEngine.vm_writer.write_pop("temp 0")
			CompilationEngine.vm_writer.write_pop("pointer 1")
			CompilationEngine.vm_writer.write_push("temp 0")
			CompilationEngine.vm_writer.write_pop("that 0")
			return
		elif CompilationEngine.symbol_tables.has_symbol(var_name):
			seg_pointer = CompilationEngine.symbol_tables.get_segment(var_name)
			CompilationEngine.vm_writer.write_pop(seg_pointer)                  # store evaluated expression into variable
			return
		else:
			raise Exception("variable segment not found in symbol table")

	#FLOW CONTROL LOGIC MAY BE OFF
	def compile_if():
		CompilationEngine.if_label_num += 2
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop "if"

		CompilationEngine.expect_token("(")
		CompilationEngine.format_scoped_structure("expression")()
		CompilationEngine.expect_token(")")
		CompilationEngine.vm_writer.write_arithmetic("not")

		L1 = CompilationEngine.if_label_num
		L2 = CompilationEngine.if_label_num + 1
		CompilationEngine.vm_writer.write_label("if-goto", "IF_FALSE", L1)               # if not(expression), goto label 1 in the else statement

		CompilationEngine.expect_token("{")
		CompilationEngine.format_scoped_structure("statements")()
		CompilationEngine.expect_token("}")
		CompilationEngine.vm_writer.write_label("goto", "IF_END", L2)                  

		if CompilationEngine.optional_token("else") == False:
			CompilationEngine.vm_writer.write_label("label", "IF_END", L2)
			CompilationEngine.vm_writer.write_label("label", "IF_FALSE", L1)				
			return
		else:
			CompilationEngine.expect_token("{")
			CompilationEngine.vm_writer.write_label("label", "IF_FALSE", L1)
			CompilationEngine.format_scoped_structure("statements")()
			CompilationEngine.expect_token("}")

			CompilationEngine.vm_writer.write_label("label", "IF_END", L2)
			return

	#FIX LABEL NAMING AND ADD NAME ARG TO WRITE_LABEL FUNC
	def compile_while():
		CompilationEngine.while_label_num += 2
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop "while"

		L1 = CompilationEngine.while_label_num
		L2 = CompilationEngine.while_label_num + 1
		CompilationEngine.vm_writer.write_label("label", "WHILE_EXP", L1)

		CompilationEngine.expect_token("(")
		CompilationEngine.format_scoped_structure("expression")()
		CompilationEngine.expect_token(")")

		CompilationEngine.vm_writer.write_arithmetic("not")
		CompilationEngine.vm_writer.write_label("if-goto", "WHILE_END", L2)

		CompilationEngine.expect_token("{")
		CompilationEngine.format_scoped_structure("statements")()
		CompilationEngine.expect_token("}")

		CompilationEngine.vm_writer.write_label("goto", "WHILE_EXP", L1)
		CompilationEngine.vm_writer.write_label("label", "WHILE_END", L2)
		return

	OS_classes = ['Math', 'Memory', 'Screen', 'Output', 'Keyboard', 'String', 'Array', 'Sys']
	def subroutine_call(self):
		#this may need to become a local variable to handle recursive calls to subroutine_call
		CompilationEngine.current_func_nargs = 0
		next_token = CompilationEngine.peek_next_token()
		# object method | OS call | 
		if next_token == ".":
			obj = CompilationEngine.peek_current_token()                        # object name | OS Class
			obj_class = obj														# init object class to object (only true for OS calls)

			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop object name | OS class
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop "."

			subroutine_name = CompilationEngine.peek_current_token()			# get subroutine call name

			#NEED TO GET SUBROUTINE TYPE (METHOD/FUNCTION/CONSTRUCTOR)?????

			# object method call
			call_name = ""
			if obj not in CompilationEngine.OS_classes and CompilationEngine.symbol_tables.has_symbol(obj):
				CompilationEngine.current_func_nargs += 1
				obj_segment = CompilationEngine.symbol_tables.get_segment(obj)
				obj_class = CompilationEngine.symbol_tables.get_class(obj)
				CompilationEngine.vm_writer.write_push(obj_segment)				# push object memory segment
				call_name = obj_class + "." + subroutine_name
			# elif obj in CompilationEngine.OS_classes:
			# 	call_name = obj + "." + subroutine_name
			else:
				call_name = obj + "." + subroutine_name
				
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop subroutineName
			CompilationEngine.expect_token("(")
			CompilationEngine.format_scoped_structure("expressionList")()       # pushing arguments should be handled by expressionList > expression
			CompilationEngine.expect_token(")")

			#REEANBLE FOR TEMP 0 VOID???

			subroutine_call_command = call_name + " " + str(CompilationEngine.current_func_nargs)
			CompilationEngine.vm_writer.write_call(subroutine_call_command)			# call subroutine
			return
		#function call
		elif next_token == "(":
			subroutine_name = CompilationEngine.peek_current_token()
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop subroutineName
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop "("
			CompilationEngine.vm_writer.write_push("pointer 0")                 # may need to be conditionally pushed only when calling method
			CompilationEngine.format_scoped_structure("expressionList")()
			CompilationEngine.expect_token(")")
			CompilationEngine.current_func_nargs += 1
			subroutine_call_command = CompilationEngine.class_name + "." + subroutine_name + " " + str(CompilationEngine.current_func_nargs)
			CompilationEngine.vm_writer.write_call(subroutine_call_command)
			return
		else:
			raise Exception("syntax error: subroutine call incorrectly formatted")

		
	def compile_do():
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop "do"
		CompilationEngine.subroutine_call()
		CompilationEngine.vm_writer.write_pop("temp 0")                     # do statements don't need return value
		CompilationEngine.expect_token(";")
		return


	def compile_return():
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop "return"

		if CompilationEngine.optional_token(";") == True:
			CompilationEngine.vm_writer.write_push("constant 0")
			CompilationEngine.vm_writer.write_return()

			return
		else:
			CompilationEngine.format_scoped_structure("expression")()
			CompilationEngine.expect_token(";")
			CompilationEngine.vm_writer.write_return()
			return

	
	def compile_expression():
		CompilationEngine.format_scoped_structure("term")()
		operator_found = False
		operator = ""
		current_token = CompilationEngine.peek_current_token()
		if current_token in CompilationEngine.op_list:
			operator_found = True
			operator = current_token
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop op token
			CompilationEngine.format_scoped_structure("term")()

		if operator_found == True:
			CompilationEngine.vm_writer.write_arithmetic(operator)


	def compile_term():
		if CompilationEngine.optional_token("(") == True:
			CompilationEngine.format_scoped_structure("expression")()
			CompilationEngine.expect_token(")")
			return
		else:
			next_token = CompilationEngine.peek_next_token()
			#array indexing
			if next_token == "[":
				var_name = CompilationEngine.peek_current_token()
				seg_pointer = CompilationEngine.symbol_tables.get_segment(var_name)
				CompilationEngine.vm_writer.write_push(seg_pointer)
				CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop varName
				CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop "["
				CompilationEngine.format_scoped_structure("expression")()
				current_token = CompilationEngine.peek_current_token()
				if current_token == "]":
					CompilationEngine.write_compiled_xml(CompilationEngine.pop_token())
					CompilationEngine.vm_writer.write_arithmetic("+")
					CompilationEngine.vm_writer.write_pop("pointer 1")
					CompilationEngine.vm_writer.write_push("that 0")
					return
			#subroutine call (method or function)
			elif (next_token == "." or next_token == "(") and CompilationEngine.peek_current_token() not in CompilationEngine.unary_list: #UNARY FIX NEEDED
				print("current token,", CompilationEngine.peek_current_token())
				print("next token: ", next_token)
				CompilationEngine.subroutine_call()
				return

			current_token_type = CompilationEngine.peek_current_type()
			current_token = CompilationEngine.peek_current_token()
			if (current_token_type == 'integerConstant'
				or current_token_type == 'stringConstant' 
				or current_token_type == 'identifier'
				or current_token in CompilationEngine.keyword_constants):
				if current_token_type == 'integerConstant':
					vm_constant = "constant " + str(current_token)
					CompilationEngine.vm_writer.write_push(vm_constant)
				elif current_token_type == 'stringConstant':
					print("________________CURRENT:", current_token)
					CompilationEngine.vm_writer.write_string(current_token)

				elif current_token_type == "identifier":
					if CompilationEngine.symbol_tables.has_symbol(current_token) == True:
						kind = CompilationEngine.symbol_tables.get_kind(current_token)
						num = str(CompilationEngine.symbol_tables.get_num(current_token))
						command = ""
						if kind == "field":
							command = "this " + num
						else:
							command = kind + " " + num
						CompilationEngine.vm_writer.write_push(command)

				elif current_token in CompilationEngine.keyword_constants:
					if current_token == "false" or current_token == "null":
						CompilationEngine.vm_writer.write_push("constant 0")
					if current_token == "true":
						CompilationEngine.vm_writer.write_push("-1")
					if current_token == 'this':
						CompilationEngine.vm_writer.write_push("pointer 0")

				CompilationEngine.write_compiled_xml(CompilationEngine.pop_token())
				return

			if current_token in CompilationEngine.unary_list:
				unary_op = CompilationEngine.peek_current_token()
				CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop unary operator
				CompilationEngine.format_scoped_structure("term")()
				CompilationEngine.vm_writer.write_unary(unary_op)
				# CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop constant
				return

			if CompilationEngine.optional_token("(") == True:
				CompilationEngine.format_scoped_structure("expression")()
				CompilationEngine.expect_token(")")
			return


	statements = ["let", "if", "while", "do", "return"]
	def compile_statements():
		current_token = CompilationEngine.peek_current_token()
		while current_token in CompilationEngine.statements:
			CompilationEngine.format_scoped_structure(current_token)()
			current_token = CompilationEngine.peek_current_token()
		return


	def compile_expression_list():
		#if next token is ")" empty expression list and return
		current_token = CompilationEngine.peek_current_token()
		if current_token == ")":
			return #empty expression list, let caller handle ")"
			
		CompilationEngine.format_scoped_structure("expression")()
		CompilationEngine.current_func_nargs += 1
		while CompilationEngine.optional_token(",") == True:
			CompilationEngine.format_scoped_structure("expression")()
			CompilationEngine.current_func_nargs += 1
		return


	def compile_class():
		#add first table which will store class scoped symbols
		CompilationEngine.symbol_tables.add_table()		
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop "class"
		CompilationEngine.class_name = CompilationEngine.peek_current_token()
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop className
		CompilationEngine.expect_token("{")
		current_token = CompilationEngine.peek_current_token()
		while current_token != "}":
			CompilationEngine.format_scoped_structure(current_token)()
			current_token = CompilationEngine.peek_current_token()
		CompilationEngine.expect_token("}")
		return


	functions = {'statements': compile_statements,'class': compile_class, 'static': compile_class_var_dec, 'field': compile_class_var_dec, 'var': compile_var_dec,
				'let': compile_let, 'while': compile_while, 'do': compile_do, 'return': compile_return, 'method': compile_subroutine_dec,
				'subroutineDec': compile_subroutine_dec, 'function': compile_subroutine_dec, 'constructor': compile_subroutine_dec,
				'parameterList': compile_parameter_list, 'subroutineBody': compile_subroutine_body, 'expression': compile_expression,
				'expressionList': compile_expression_list,'term': compile_term, 'if': compile_if}
								

	def compile(self):
		#each line is a unique symbol
		#check if symbol is in compilation_engine_functions dictionary
		# if it is, set tag name to the func tag name, print, call compile statement, it's return
		# CompilationEngine.init_functions_dict()
		# pdb.set_trace()
		while(CompilationEngine.token_iterator < len(CompilationEngine.tokenized_xml)):
			current_token = CompilationEngine.peek_current_token()
			if current_token in CompilationEngine.functions:
				#set up decorated function call with tag
				CompilationEngine.format_scoped_structure(current_token)()
			else:
				#this may need to be updated with more logic to handle scenarios where scope is defined arbitrarily, may be only circumstance though
				raise Exception("invalid syntax")
		return CompilationEngine.compiled_xml


pars = argparse.ArgumentParser()
pars.add_argument("--path", help="path to either a single file or directory to compile")
args = pars.parse_args()
input_arg = args.path


if os.path.isdir(input_arg):
	directory_contents = os.listdir(input_arg)
	jack_files_list = [x for x in directory_contents if '.jack' in x]
	xml_out_file_names = [x.replace('jack','xml') for x in jack_files_list]
	vm_out_file_names = [x.replace('jack','vm') for x in jack_files_list]
	os.chdir(input_arg)
elif os.path.isfile(input_arg):
	xml_out_file_names = [os.path.basename(input_arg).replace('jack','xml')]
	vm_out_file_names = [os.path.basename(input_arg).replace('jack','vm')]

	jack_files_list = [os.path.basename(input_arg)]
	os.chdir(os.path.dirname(input_arg))
else:
	print('Directory or File not recognized')
	sys.exit()

Tokenizer = CompilationTokenizer.Tokenizer()
CompilationEngine =CompilationEngine()
for jack_file, xml_out_name, vm_out_name in zip(jack_files_list, xml_out_file_names, vm_out_file_names):
	with open(jack_file) as f:
		data = f.read()
	raw_code_lines = data.split('\n')
	Tokenizer.set_raw_code(raw_code_lines)
	verified_tokens_xml = Tokenizer.tokenize()
	CompilationEngine.set_verified_xml_tokens(verified_tokens_xml)

	compiled_tokens_xml = CompilationEngine.compile()
	with open(xml_out_name, "w") as file:
			for line in compiled_tokens_xml:
				file.write(line)
				file.write('\n')

	compiled_vm_commands = CompilationEngine.vm_writer.get_commands()
	with open(vm_out_name, "w") as file:
			for command in compiled_vm_commands:
				file.write(command)
				file.write('\n')
	CompilationEngine.vm_writer.reset()
	CompilationEngine.token_iterator = 0
