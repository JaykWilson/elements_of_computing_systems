import os
import sys
import argparse
import SymbolTableList


class Tokenizer:
	keyword_list = ['class', 
					'constructor', 
					'function', 
					'method', 
					'field', 
					'static',
					'var',
					'int',
					'char',
					'boolean',
					'void',
					'true',
					'false',
					'null',
					'this',
					'let',
					'do',
					'if',
					'else',
					'while',
					'return',
					]

	symbol_list = ['{',
				   '}',
				   '(',
				   ')',
				   '[',
				   ']',
				   '.',
				   ',',
				   ';',
				   '+',
				   '-',
				   '*',
				   '/',
				   '&',
				   '|',
				   '<',
				   '>',
				   '=',
				   '~',
				  ]


	identifier_list	= []
	block_comment = False
	accumulating_string_constant = False
	reserved_XML_symbol_replacements = {'>' : '&gt;', '<' : '&lt;', '&' : '&amp;', '"' : '&quot;'}

	def set_raw_code(self, raw_code):
		self.raw_code = raw_code
		Tokenizer.identifier_list.clear()
		Tokenizer.block_comment = False
		Tokenizer.accumulating_string_constant = False

	def tokenize(self):
		verified_tokens_xml = []
		for line in self.raw_code:
			line = line.split()
			if Tokenizer._is_comment(line) != True:
				verified_tokens_and_types = Tokenizer._process_tokens_in_line(line)
				for verified_token_and_type in verified_tokens_and_types:
					verified_token = verified_token_and_type[0]
					token_type = verified_token_and_type[1]
					#xml_formatted_token = '\t' + '<' + token_type + '> ' + verified_token + ' </' + token_type + '>'
					xml_formatted_token = '<' + token_type + '> ' + verified_token + ' </' + token_type + '>'
					verified_tokens_xml.append(xml_formatted_token)
			else:
				pass
		return verified_tokens_xml


	def _replace_reserved_XML_symbols(self, token):
		if token in Tokenizer.reserved_XML_symbol_replacements:
			return Tokenizer.reserved_XML_symbol_replacements[token]
		else:
			return token

	def _process_tokens_in_line(self,line):
		processed_line = []
		for token in line:
			if not Tokenizer.accumulating_string_constant:
				if token in Tokenizer.keyword_list:
					processed_line.append([token,'keyword'])
				elif token in Tokenizer.symbol_list:
					processed_line.append([Tokenizer._replace_reserved_XML_symbols(token),'symbol'])
				elif token.isnumeric():
					processed_line.append([token,'integerConstant'])
				elif token in Tokenizer.identifier_list:
					processed_line.append([token,'identifier'])
				elif token == '//':
					return processed_line
				else:
					possible_token_accumulator = ''
					num_char_removed_from_token = 0
					for character in token:
						if character in Tokenizer.symbol_list:
							if len(possible_token_accumulator) > 0:
								processed_line.append([possible_token_accumulator,Tokenizer._token_type(possible_token_accumulator)])
								num_char_removed_from_token	+= len(possible_token_accumulator)
								possible_token_accumulator = ''
							processed_line.append([Tokenizer._replace_reserved_XML_symbols(character),'symbol'])
							num_char_removed_from_token += 1
						elif character == '"':
							Tokenizer.accumulating_string_constant = True
							if len(possible_token_accumulator) > 0:
								processed_line.append([possible_token_accumulator,Tokenizer._token_type(possible_token_accumulator)])
								possible_token_accumulator = ' '
						else:
							possible_token_accumulator = possible_token_accumulator + character
							if len(possible_token_accumulator) == (len(token) - num_char_removed_from_token):
								processed_line.append([possible_token_accumulator,Tokenizer._token_type(possible_token_accumulator)])
								possible_token_accumulator = ' '
			else:
				if '"' not in token:
					possible_token_accumulator = possible_token_accumulator + ' ' + token
				else:
					Tokenizer.accumulating_string_constant = False
					split_token = token.split('"')
					rest_of_string = split_token[0]
					if len(rest_of_string) > 0:
						possible_token_accumulator = possible_token_accumulator + rest_of_string
					processed_line.append([possible_token_accumulator, 'stringConstant'])
					if len(split_token) > 1:
						leftover_token = split_token[1]
						for character in leftover_token:
							if character in Tokenizer.symbol_list:
								processed_line.append([Tokenizer._replace_reserved_XML_symbols(character), 'symbol'])
							else:
								raise Exception("Syntax error")
		return processed_line


	def _is_comment(self,line):
		comment_found = False
		new_line = False
		if len(line) == 0:
			new_line = True
		else:
			first_token = line[0]
			if len(first_token) > 0:
				if first_token[0] == '/':
					if len(first_token) >= 2:
						if first_token[1] == '/':
							comment_found =True
						elif first_token[1] == '*':
							Tokenizer.block_comment = True
							if '*/' in line:
								Tokenizer.block_comment = False
								comment_found = True
				elif Tokenizer.block_comment == True:
					if '*/' in line:
						Tokenizer.block_comment = False
						comment_found = True
		return comment_found or Tokenizer.block_comment or new_line


	def _token_type(self, possible_token):
		if possible_token in Tokenizer.symbol_list:
			return 'symbol'
		elif possible_token in Tokenizer.keyword_list:
			return 'keyword'
		elif possible_token.isnumeric():
			return 'integerConstant'
		elif possible_token in Tokenizer.identifier_list:
			return 'identifier'
		elif possible_token[0] == '"' and possible_token [-1] == '"':
			if '"' not in possible_token[1:-1:1] and '\n' not in possible_token[1:-1:1]:
				return 'stringConstant'
		else:
			if possible_token[0].isnumeric():
				raise Exception("invalid token: beginning token with numeric is not allowed")
			for c in possible_token:
				if not c.isalnum() and c != '_':
					raise Exception("invalid token: tokens may only contain alphanumeric characters and underscores")
			if possible_token not in Tokenizer.identifier_list:
					Tokenizer.identifier_list.append(possible_token)
			return 'identifier'


class CompilationEngine:
	compiled_xml = []
	tokenized_xml = []
	token_iterator = 0
	indents = 0

	op_list = ['+',
			   '-',
			   '*',
			   '/',
			   '&amp;', #"&"
			   '|',
			   '&lt;', #"<"
			   '&gt;', #">"
			   '=',
			   ]

	unary_list = ['-',
				  '~',
				  ]

	keyword_constants = ['true',
						 'false',
						 'null',
						 'this',
						 ]

	class_symbol_table = SymbolTableList.SymbolTable()

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
		CompilationEngine.token_iterator += 1
		return current_token_xml

	def peek_current_token(self):
		token_xml_split = CompilationEngine.tokenized_xml[CompilationEngine.token_iterator].split()
		token_type = token_xml_split[0][1:-1]
		token = token_xml_split[1]
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

		#WRITE TO CLASS SYMBOL TABLE

		symbol_kind = CompilationEngine.peek_current_token()
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop kind (static | field)

		symbol_type = CompilationEngine.peek_current_token()
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop type

		symbol_name = CompilationEngine.peek_current_token()
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop varName

		class_symbol_table.add_symbol(symbol_name, symbol_type, symbol_kind)
		while CompilationEngine.optional_token(",") == True:
			symbol_name = CompilationEngine.peek_current_token()
			class_symbol_table.add_symbol(symbol_name, symbol_type, symbol_kind)
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop varName

		CompilationEngine.expect_token(";")
		return


	def compile_subroutine_dec():
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop (constructor | function | method)
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop return type
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop method name
		CompilationEngine.expect_token("(")
		CompilationEngine.format_scoped_structure("parameterList")()
		CompilationEngine.expect_token(")")
		CompilationEngine.format_scoped_structure("subroutineBody")()
		return


	def compile_parameter_list():
		if CompilationEngine.peek_current_token() == ")":
			return #this case handles an empty parameter list
		else:
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop type
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop varName
			while CompilationEngine.optional_token(",") == True:
				CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop type
				CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop varName
			return


	def compile_subroutine_body():
		CompilationEngine.expect_token("{")
		current_token = CompilationEngine.peek_current_token()
		while current_token != "}":
			if current_token == "var":
				CompilationEngine.format_scoped_structure("var")()
			else:
				CompilationEngine.format_scoped_structure("statements")()
			current_token = CompilationEngine.peek_current_token()
		CompilationEngine.expect_token("}")
		return


	def compile_var_dec():
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop "var"
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop type
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop varName
		while CompilationEngine.optional_token(",") == True:
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop varName
		CompilationEngine.expect_token(";")
		return

	
	def compile_let():
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop "let"
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop "varName
	
		if CompilationEngine.optional_token("[") == True:
			CompilationEngine.format_scoped_structure("expression")()
			CompilationEngine.expect_token("]")

		CompilationEngine.expect_token("=") 		

		if CompilationEngine.optional_token("(") == True:
			CompilationEngine.format_scoped_structure("expression")()
			CompilationEngine.expect_token(")")

		CompilationEngine.format_scoped_structure("expression")()
		CompilationEngine.expect_token(";")
		return


	def compile_if():
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop "if"

		CompilationEngine.expect_token("(")
		CompilationEngine.format_scoped_structure("expression")()
		CompilationEngine.expect_token(")")

		CompilationEngine.expect_token("{")
		CompilationEngine.format_scoped_structure("statements")()
		CompilationEngine.expect_token("}")

		if CompilationEngine.optional_token("else") == False:
			return
		CompilationEngine.expect_token("{")
		CompilationEngine.format_scoped_structure("statements")()
		CompilationEngine.expect_token("}")
		return


	def compile_while():
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) # pop "while"

		CompilationEngine.expect_token("(")
		CompilationEngine.format_scoped_structure("expression")()
		CompilationEngine.expect_token(")")

		CompilationEngine.expect_token("{")
		CompilationEngine.format_scoped_structure("statements")()
		CompilationEngine.expect_token("}")
		return


	def subroutine_call(self):

		#RESET SUBROUTINE SYMBOL TABLE

		next_token = CompilationEngine.peek_next_token()
		#subroutine call, via class member access operator
		if next_token == ".":
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop className | varName
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop "."
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop subroutineName
			CompilationEngine.expect_token("(")
			CompilationEngine.format_scoped_structure("expressionList")()
			CompilationEngine.expect_token(")")
			return
		#subroutine call
		elif next_token == "(":
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop subroutineName
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop "("
			CompilationEngine.format_scoped_structure("expressionList")()
			CompilationEngine.expect_token(")")
			return
		else:
			raise Exception("syntax error: subroutine call incorrectly formatted")

		
	def compile_do():
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop "do"
		CompilationEngine.subroutine_call()
		CompilationEngine.expect_token(";")
		return


	def compile_return():
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop "return"

		if CompilationEngine.optional_token(";") == True:
			return
		else:
			CompilationEngine.format_scoped_structure("expression")()
			CompilationEngine.expect_token(";")
			return

	
	def compile_expression():
		CompilationEngine.format_scoped_structure("term")()
		if CompilationEngine.peek_current_token() in CompilationEngine.op_list:
			CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop op token
			CompilationEngine.format_scoped_structure("term")()


	def compile_term():
		if CompilationEngine.optional_token("(") == True:
			CompilationEngine.format_scoped_structure("expression")()
			CompilationEngine.expect_token(")")
			return
		else:
			next_token = CompilationEngine.peek_next_token()
			#rray indexing
			if next_token == "[":
				CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop varName
				CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop "["
				CompilationEngine.format_scoped_structure("expression")()
				current_token = CompilationEngine.peek_current_token()
				if current_token == "]":
					CompilationEngine.write_compiled_xml(CompilationEngine.pop_token())
					return
			#subroutine call
			elif next_token == "." or next_token == "(":
				CompilationEngine.subroutine_call()
				return

			current_token_type = CompilationEngine.peek_current_type()
			current_token = CompilationEngine.peek_current_token()
			if (current_token_type == 'integerConstant'
				or current_token_type == 'stringConstant' 
				or current_token_type == 'identifier'
				or current_token in CompilationEngine.keyword_constants):

				CompilationEngine.write_compiled_xml(CompilationEngine.pop_token())
				return

			if current_token in CompilationEngine.unary_list:
				CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop unary operator
				CompilationEngine.format_scoped_structure("term")()
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

		while CompilationEngine.optional_token(",") == True:
			CompilationEngine.format_scoped_structure("expression")()

		return

	def compile_class():		
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop "class"
		CompilationEngine.write_compiled_xml(CompilationEngine.pop_token()) #pop className
		CompilationEngine.expect_token("{")
		current_token = CompilationEngine.peek_current_token()
		while current_token != "}":
			CompilationEngine.format_scoped_structure(current_token)()
			current_token = CompilationEngine.peek_current_token()
		CompilationEngine.expect_token("}")
		return


	func_tag = {'class': 'class', 'static': 'classVarDec', 'field': 'classVarDec', 'var': 'varDec',
				'let': 'letStatement', 'while': 'whileStatement', 'do': 'doStatement', 'return': 'returnStatement', 'method': 'subroutineDec',
				'function': 'subroutineDec', 'constructor': 'subroutineDec', 'expression': 'expression', 'statements': 'statements',
				'term': 'term', 'subroutineBody': 'subroutineBody', 'subroutineDec': 'subroutineDec', 'parameterList': 'parameterList',
				'expressionList': 'expressionList', 'if': 'ifStatement'}

	functions = {'statements': compile_statements,'class': compile_class, 'static': compile_class_var_dec, 'field': compile_class_var_dec, 'var': compile_var_dec,
				'let': compile_let, 'while': compile_while, 'do': compile_do, 'return': compile_return, 'method': compile_subroutine_dec,
				'subroutineDec': compile_subroutine_dec, 'function': compile_subroutine_dec, 'constructor': compile_subroutine_dec,
				'parameterList': compile_parameter_list, 'subroutineBody': compile_subroutine_body, 'expression': compile_expression,
				'expressionList': compile_expression_list,'term': compile_term, 'if': compile_if}
								

	def compile(self):
		#each line is a unique symbol
		#check if symbol is in compilation_engine_functions dictionary
		#	if it is, set tag name to the func tag name, print, call compile statement, it's return
		# CompilationEngine.init_functions_dict()
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
# pars.add_argument("--logIF", help="log tokenized xml output to file")
args = pars.parse_args()

# tokenizer_output_enabled = False
# if args.logIF:
# 	tokenizer_output_enabled = True

input_arg = args.path


if os.path.isdir(input_arg):
	#output_file_name = os.path.basename(input_arg) + '.xml'
	directory_contents = os.listdir(input_arg)
	jack_files_list = [x for x in directory_contents if '.jack' in x]
	output_file_names = [x.replace('jack','xml') for x in jack_files_list]
	os.chdir(input_arg)
elif os.path.isfile(input_arg):
	output_file_names = [os.path.basename(input_arg).replace('jack','xml')]
	jack_files_list = [os.path.basename(input_arg)]
	os.chdir(os.path.dirname(input_arg))
else:
	print('Directory or File not recognized')
	sys.exit()

Tokenizer = Tokenizer()
CompilationEngine =CompilationEngine()
for jack_file, output_file_name in zip(jack_files_list, output_file_names):
	with open(jack_file) as f:
		data = f.read()
	raw_code_lines = data.split('\n')
	Tokenizer.set_raw_code(raw_code_lines)
	verified_tokens_xml = Tokenizer.tokenize()
	#optional logging of intermediate tokenized xml
	# if tokenizer_output_enabled:
	# 	with open(output_file_name, "w") as file:
	# 		for xml_line in verified_tokens_xml:
	# 			file.write(xml_line)
	# 			file.write('\n')

	CompilationEngine.set_verified_xml_tokens(verified_tokens_xml)
	compiled_tokens_xml = CompilationEngine.compile()
	with open(output_file_name, "w") as file:
			for line in compiled_tokens_xml:
				file.write(line)
				file.write('\n')
