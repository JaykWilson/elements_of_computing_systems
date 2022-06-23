import SymbolTableList
import VMWriter


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
		func = self.functions[token]
		xml_tag = self.func_tag[token]
		def wrap():
			opening_xml_tag = "<" + xml_tag + ">"
			self.write_compiled_xml(opening_xml_tag)
			self.indents += 1
			func(self)
			closing_xml_tag = "</" + xml_tag + ">"
			self.indents -= 1
			self.write_compiled_xml(closing_xml_tag)
		return wrap


	def pop_token(self):
		current_token_xml = self.tokenized_xml[self.token_iterator]
		self.token_iterator += 1
		return current_token_xml


	def peek_current_token(self):
		token_xml_split = self.tokenized_xml[self.token_iterator].split()
		token_type = token_xml_split[0][1:-1]
		if token_type == "stringConstant":
			token = ' '.join(token_xml_split[1:-1])
		else:
			token = token_xml_split[1]
		return token


	def peek_current_type(self):
		token_xml_split = self.tokenized_xml[self.token_iterator].split()
		token_type = token_xml_split[0][1:-1]
		return token_type


	def peek_next_token(self):
		if self.token_iterator < len(self.tokenized_xml) - 1:
			token_xml_split = self.tokenized_xml[self.token_iterator + 1].split()
			token = token_xml_split[1]
			return token
		else:
			raise Exception("Syntax error: out of bounds check")


	def write_compiled_xml(self,current_token_xml):
		indent = ""
		for i in range(self.indents):
			indent += "  "
		current_token_xml = indent + current_token_xml
		self.compiled_xml.append(current_token_xml)


	def set_verified_xml_tokens(self,verified_tokens_xml):
		self.compiled_xml.clear()
		self.tokenized_xml.clear()
		self.tokenized_xml = verified_tokens_xml


	def expect_token(self, expected_token):
		current_token = self.peek_current_token()
		if current_token == expected_token:
			self.write_compiled_xml(self.pop_token())
		else:
			raise Exception("syntax error: missing expected token")


	def expect_token_type(self, expected_type):
		current_token_type = self.peek_current_type()
		if current_token_type == expected_type:
			self.write_compiled_xml(self.pop_token())
		else:
			raise Exception("syntax error: invalid type")


	def optional_token(self, optional_token):
		current_token = self.peek_current_token()
		if current_token == optional_token:
			self.write_compiled_xml(self.pop_token())
			return True
		else: 
			return False


	def compile_class_var_dec(self):
		symbol_kind = self.peek_current_token()                
		self.write_compiled_xml(self.pop_token())                                      # pop kind (static | field)
		symbol_type = self.peek_current_token()
		self.write_compiled_xml(self.pop_token())                                      # pop type
		symbol_name = self.peek_current_token()
		self.write_compiled_xml(self.pop_token())                                      # pop varName
		self.symbol_tables.add_class_symbol(symbol_name, symbol_type, symbol_kind)     # add symbol to symbol table
		while self.optional_token(",") == True:
			symbol_name = self.peek_current_token()
			self.symbol_tables.add_class_symbol(symbol_name, symbol_type, symbol_kind) # add symbol to symbol table
			self.write_compiled_xml(self.pop_token())                                  # pop varName
		self.expect_token(";")
		return


	def compile_subroutine_dec(self):
		self.vm_writer.reset_command_counter()
		self.symbol_tables.add_table()                         											  # init new symbol table for method's locals

		func_type = self.peek_current_token()
		if func_type == "constructor":
			self.vm_writer.write_push("constant " + str(self.symbol_tables.get_num_class_field_var()))    # push num field vars onto stack for alloc
			self.vm_writer.write_call("Memory.alloc 1")
			self.vm_writer.write_pop("pointer 0")
		elif func_type == "method":
			self.symbol_tables.add_subroutine_symbol("this", self.class_name, "argument") 				  # add "this" pointer for all methods
			self.vm_writer.write_push("argument 0")
			self.vm_writer.write_pop("pointer 0")  

		self.write_compiled_xml(self.pop_token()) 														  # pop (constructor | function | method)
		self.write_compiled_xml(self.pop_token()) 														  # pop return type

		func_name = self.class_name + "." +  self.peek_current_token()   								  # method name

		self.write_compiled_xml(self.pop_token())                                                         # pop method name
		self.expect_token("(")
		self.format_scoped_structure("parameterList")()
		self.expect_token(")")
		self.format_scoped_structure("subroutineBody")()
		
		nlocals = self.symbol_tables.get_nlocals()
		if func_type == "constructor":
			self.vm_writer.write_function(func_name, nlocals)
		elif func_type == "method":    
			self.vm_writer.write_function(func_name, nlocals)                                                 	
		elif func_type == "function":
			self.vm_writer.write_function(func_name, nlocals)

		self.symbol_tables.reset_subroutine_tables()
		return


	def compile_parameter_list(self):
		if self.peek_current_token() == ")":
			return 																				# empty parameter list
		else:
			symbol_type = self.peek_current_token()
			self.write_compiled_xml(self.pop_token())                            		        # pop type
			symbol_name = self.peek_current_token()
			self.write_compiled_xml(self.pop_token())                           		        # pop varName
			self.symbol_tables.add_subroutine_symbol(symbol_name, symbol_type, "argument")    	# add symbol to symbol table
			while self.optional_token(",") == True:
				symbol_type = self.peek_current_token()
				self.write_compiled_xml(self.pop_token()) 							            # pop type
				symbol_name = self.peek_current_token()
				self.write_compiled_xml(self.pop_token()) 							            # pop varName
				self.symbol_tables.add_subroutine_symbol(symbol_name, symbol_type, "argument")  # add symbol to symbol table
			return


	def compile_subroutine_body(self):
		self.expect_token("{")
		current_token = self.peek_current_token()
		while current_token != "}":
			if current_token == "var":
				self.format_scoped_structure("var")()
			else:
				self.format_scoped_structure("statements")()
			current_token = self.peek_current_token()
		self.expect_token("}")
		return


	def compile_var_dec(self):
		self.write_compiled_xml(self.pop_token()) 							                # pop "var"
		symbol_type = self.peek_current_token()
		self.write_compiled_xml(self.pop_token()) 							                # pop type
		symbol_name = self.peek_current_token()
		self.write_compiled_xml(self.pop_token()) 							                # pop varName
		self.symbol_tables.add_subroutine_symbol(symbol_name, symbol_type, "local") 		# add symbol to symbol table
		while self.optional_token(",") == True:
			symbol_name = self.peek_current_token()
			self.write_compiled_xml(self.pop_token()) 						                # pop varName
			self.symbol_tables.add_subroutine_symbol(symbol_name, symbol_type, "local") 	# add symbol to symbol table
		self.expect_token(";")
		return


	def compile_let(self):
		self.write_compiled_xml(self.pop_token()) 		                                    #pop "let"
		var_name = self.peek_current_token()
		self.write_compiled_xml(self.pop_token()) 		                                    #pop "varName
		array_access = False
		if self.optional_token("[") == True:
			array_access = True
			seg_pointer = self.symbol_tables.get_segment(var_name)
			self.vm_writer.write_push(seg_pointer)
			self.format_scoped_structure("expression")()
			self.vm_writer.write_arithmetic("+")
			self.expect_token("]")

		self.expect_token("=") 		

		if self.optional_token("(") == True:
			self.format_scoped_structure("expression")()
			self.expect_token(")")
		else:
			self.format_scoped_structure("expression")()
		if self.peek_current_token() in self.op_list:
			self.format_scoped_structure("expression")()
		self.expect_token(";")

		if array_access == True:
			self.vm_writer.write_pop("temp 0")
			self.vm_writer.write_pop("pointer 1")
			self.vm_writer.write_push("temp 0")
			self.vm_writer.write_pop("that 0")
			return
		elif self.symbol_tables.has_symbol(var_name):
			seg_pointer = self.symbol_tables.get_segment(var_name)
			self.vm_writer.write_pop(seg_pointer)                 	                        # store evaluated expression into variable
			return
		else:
			raise Exception("variable segment not found in symbol table")


	def compile_if(self):
		self.if_label_num += 2
		self.write_compiled_xml(self.pop_token()) 	                                        # pop "if"

		self.expect_token("(")
		self.format_scoped_structure("expression")()
		self.expect_token(")")
		self.vm_writer.write_arithmetic("not")

		L1 = self.if_label_num
		L2 = self.if_label_num + 1
		self.vm_writer.write_label("if-goto", "IF_FALSE", L1)                               # if not(expression), goto label 1 in the else statement

		self.expect_token("{")
		self.format_scoped_structure("statements")()
		self.expect_token("}")
		self.vm_writer.write_label("goto", "IF_END", L2)                  

		if self.optional_token("else") == False:
			self.vm_writer.write_label("label", "IF_END", L2)
			self.vm_writer.write_label("label", "IF_FALSE", L1)				
			return
		else:
			self.expect_token("{")
			self.vm_writer.write_label("label", "IF_FALSE", L1)
			self.format_scoped_structure("statements")()
			self.expect_token("}")

			self.vm_writer.write_label("label", "IF_END", L2)
			return


	def compile_while(self):
		self.while_label_num += 2
		self.write_compiled_xml(self.pop_token()) 	                                        # pop "while"

		L1 = self.while_label_num
		L2 = self.while_label_num + 1
		self.vm_writer.write_label("label", "WHILE_EXP", L1)

		self.expect_token("(")
		self.format_scoped_structure("expression")()
		self.expect_token(")")

		self.vm_writer.write_arithmetic("not")
		self.vm_writer.write_label("if-goto", "WHILE_END", L2)

		self.expect_token("{")
		self.format_scoped_structure("statements")()
		self.expect_token("}")

		self.vm_writer.write_label("goto", "WHILE_EXP", L1)
		self.vm_writer.write_label("label", "WHILE_END", L2)
		return

	OS_classes = ['Math', 'Memory', 'Screen', 'Output', 'Keyboard', 'String', 'Array', 'Sys']
	def subroutine_call(self):
		self.current_func_nargs = 0
		next_token = self.peek_next_token()
		if next_token == ".":
			obj = self.peek_current_token()                                                 # object name | OS Class
			obj_class = obj														            # init object class to object (only true for OS calls)

			self.write_compiled_xml(self.pop_token())                                       # pop object name | OS class
			self.write_compiled_xml(self.pop_token())                                       # pop "."

			subroutine_name = self.peek_current_token()			                            # get subroutine call name
			# object method call
			call_name = ""
			if obj not in self.OS_classes and self.symbol_tables.has_symbol(obj):
				self.current_func_nargs += 1
				obj_segment = self.symbol_tables.get_segment(obj)
				obj_class = self.symbol_tables.get_class(obj)
				self.vm_writer.write_push(obj_segment)				                        # push object memory segment
				call_name = obj_class + "." + subroutine_name
			else:
				call_name = obj + "." + subroutine_name
				
			self.write_compiled_xml(self.pop_token())                                       # pop subroutineName
			self.expect_token("(")
			self.format_scoped_structure("expressionList")()
			self.expect_token(")")

			subroutine_call_command = call_name + " " + str(self.current_func_nargs)
			self.vm_writer.write_call(subroutine_call_command)		                        # call subroutine
			return
		# function call
		elif next_token == "(":
			subroutine_name = self.peek_current_token()
			self.write_compiled_xml(self.pop_token())                                       # pop subroutineName
			self.write_compiled_xml(self.pop_token())                                       # pop "("
			self.vm_writer.write_push("pointer 0")
			self.format_scoped_structure("expressionList")()
			self.expect_token(")")
			self.current_func_nargs += 1
			subroutine_call_command = self.class_name + "." + subroutine_name + " " + str(self.current_func_nargs)
			self.vm_writer.write_call(subroutine_call_command)
			return
		else:
			raise Exception("syntax error: subroutine call incorrectly formatted")

		
	def compile_do(self):
		self.write_compiled_xml(self.pop_token())                                           # pop "do"
		self.subroutine_call()
		self.vm_writer.write_pop("temp 0")
		self.expect_token(";")
		return


	def compile_return(self):
		self.write_compiled_xml(self.pop_token())                                           # pop "return"
		if self.optional_token(";") == True:
			self.vm_writer.write_push("constant 0")
			self.vm_writer.write_return()
			return
		else:
			self.format_scoped_structure("expression")()
			self.expect_token(";")
			self.vm_writer.write_return()
			return

	
	def compile_expression(self):
		self.format_scoped_structure("term")()
		operator_found = False
		operator = ""
		current_token = self.peek_current_token()
		if current_token in self.op_list:
			operator_found = True
			operator = current_token
			self.write_compiled_xml(self.pop_token())                                       # pop op token
			self.format_scoped_structure("term")()
		if operator_found == True:
			self.vm_writer.write_arithmetic(operator)


	def compile_term(self):
		if self.optional_token("(") == True:
			self.format_scoped_structure("expression")()
			self.expect_token(")")
			return
		else:
			next_token = self.peek_next_token()
			# array indexing
			if next_token == "[":
				var_name = self.peek_current_token()
				seg_pointer = self.symbol_tables.get_segment(var_name)
				self.vm_writer.write_push(seg_pointer)
				self.write_compiled_xml(self.pop_token())                                   # pop varName
				self.write_compiled_xml(self.pop_token())                                   # pop "["
				self.format_scoped_structure("expression")()
				current_token = self.peek_current_token()
				if current_token == "]":
					self.write_compiled_xml(self.pop_token())
					self.vm_writer.write_arithmetic("+")
					self.vm_writer.write_pop("pointer 1")
					self.vm_writer.write_push("that 0")
					return
			# subroutine call (method or function)
			elif (next_token == "." or next_token == "(") and self.peek_current_token() not in self.unary_list \
					and self.peek_current_token() not in self.op_list: 
				self.subroutine_call()
				return

			current_token_type = self.peek_current_type()
			current_token = self.peek_current_token()
			if (current_token_type == 'integerConstant'
				or current_token_type == 'stringConstant' 
				or current_token_type == 'identifier'
				or current_token in self.keyword_constants):
				if current_token_type == 'integerConstant':
					vm_constant = "constant " + str(current_token)
					self.vm_writer.write_push(vm_constant)
				elif current_token_type == 'stringConstant':
					self.vm_writer.write_string(current_token)

				elif current_token_type == "identifier":
					if self.symbol_tables.has_symbol(current_token) == True:
						kind = self.symbol_tables.get_kind(current_token)
						num = str(self.symbol_tables.get_num(current_token))
						command = ""
						if kind == "field":
							command = "this " + num
						else:
							command = kind + " " + num
						self.vm_writer.write_push(command)

				elif current_token in self.keyword_constants:
					if current_token == "false" or current_token == "null":
						self.vm_writer.write_push("constant 0")
					if current_token == "true":
						self.vm_writer.write_push("-1")
					if current_token == 'this':
						self.vm_writer.write_push("pointer 0")

				self.write_compiled_xml(self.pop_token())
				return

			if current_token in self.unary_list:
				unary_op = self.peek_current_token()
				self.write_compiled_xml(self.pop_token())                                   # pop unary operator
				self.format_scoped_structure("term")()
				self.vm_writer.write_unary(unary_op)
				return

			if self.optional_token("(") == True:
				self.format_scoped_structure("expression")()
				self.expect_token(")")
			return


	statements = ["let", "if", "while", "do", "return"]
	def compile_statements(self):
		current_token = self.peek_current_token()
		while current_token in self.statements:
			self.format_scoped_structure(current_token)()
			current_token = self.peek_current_token()
		return


	def compile_expression_list(self):
		# if next token is ")" empty expression list and return
		current_token = self.peek_current_token()
		if current_token == ")":
			return
			
		self.format_scoped_structure("expression")()
		self.current_func_nargs += 1
		while self.optional_token(",") == True:
			self.format_scoped_structure("expression")()
			self.current_func_nargs += 1
		return


	def compile_class(self):
		# add first table which will store class scoped symbols
		self.symbol_tables.add_table()		
		self.write_compiled_xml(self.pop_token())                                           # pop "class"
		self.class_name = self.peek_current_token()
		self.write_compiled_xml(self.pop_token())                                           # pop className
		self.expect_token("{")
		current_token = self.peek_current_token()
		while current_token != "}":
			self.format_scoped_structure(current_token)()
			current_token = self.peek_current_token()
		self.expect_token("}")
		return


	functions = {'statements': compile_statements,'class': compile_class, 'static': compile_class_var_dec, 'field': compile_class_var_dec, 'var': compile_var_dec,
				'let': compile_let, 'while': compile_while, 'do': compile_do, 'return': compile_return, 'method': compile_subroutine_dec,
				'subroutineDec': compile_subroutine_dec, 'function': compile_subroutine_dec, 'constructor': compile_subroutine_dec,
				'parameterList': compile_parameter_list, 'subroutineBody': compile_subroutine_body, 'expression': compile_expression,
				'expressionList': compile_expression_list,'term': compile_term, 'if': compile_if}
								

	def compile(self):
		while(self.token_iterator < len(self.tokenized_xml)):
			current_token = self.peek_current_token()
			if current_token in self.functions:
				self.format_scoped_structure(current_token)()
			else:
				raise Exception("invalid syntax")
		return self.compiled_xml
        