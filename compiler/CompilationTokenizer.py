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
		self.identifier_list.clear()
		self.block_comment = False
		self.accumulating_string_constant = False


	def tokenize(self):
		verified_tokens_xml = []
		for line in self.raw_code:
			line = line.split()
			if self._is_comment(line) != True:
				verified_tokens_and_types = self._process_tokens_in_line(line)
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
		if token in self.reserved_XML_symbol_replacements:
			return self.reserved_XML_symbol_replacements[token]
		else:
			return token


	def _process_tokens_in_line(self,line):
		processed_line = []
		for token in line:
			if not self.accumulating_string_constant:
				if token in self.keyword_list:
					processed_line.append([token,'keyword'])
				elif token in self.symbol_list:
					processed_line.append([self._replace_reserved_XML_symbols(token),'symbol'])
				elif token.isnumeric():
					processed_line.append([token,'integerConstant'])
				elif token in self.identifier_list:
					processed_line.append([token,'identifier'])
				elif token == '//':
					return processed_line
				else:
					possible_token_accumulator = ''
					num_char_removed_from_token = 0
					for character in token:
						if character in self.symbol_list:
							if len(possible_token_accumulator) > 0:
								processed_line.append([possible_token_accumulator, self._token_type(possible_token_accumulator)])
								num_char_removed_from_token	+= len(possible_token_accumulator)
								possible_token_accumulator = ''
							processed_line.append([self._replace_reserved_XML_symbols(character),'symbol'])
							num_char_removed_from_token += 1
						elif character == '"':
							self.accumulating_string_constant = True
							if len(possible_token_accumulator) > 0:
								processed_line.append([possible_token_accumulator, self._token_type(possible_token_accumulator)])
								possible_token_accumulator = ' '
						else:
							possible_token_accumulator = possible_token_accumulator + character
							if len(possible_token_accumulator) == (len(token) - num_char_removed_from_token):
								processed_line.append([possible_token_accumulator, self._token_type(possible_token_accumulator)])
								possible_token_accumulator = ' '
			else:
				if '"' not in token:
					possible_token_accumulator = possible_token_accumulator + ' ' + token
				else:
					self.accumulating_string_constant = False
					split_token = token.split('"')
					rest_of_string = split_token[0]
					if len(rest_of_string) > 0:
						possible_token_accumulator = possible_token_accumulator + rest_of_string
					processed_line.append([possible_token_accumulator, 'stringConstant'])
					if len(split_token) > 1:
						leftover_token = split_token[1]
						for character in leftover_token:
							if character in self.symbol_list:
								processed_line.append([self._replace_reserved_XML_symbols(character), 'symbol'])
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
							self.block_comment = True
							if '*/' in line:
								self.block_comment = False
								comment_found = True
				elif self.block_comment == True:
					if '*/' in line:
						self.block_comment = False
						comment_found = True
		return comment_found or self.block_comment or new_line


	def _token_type(self, possible_token):
		if possible_token in self.symbol_list:
			return 'symbol'
		elif possible_token in self.keyword_list:
			return 'keyword'
		elif possible_token.isnumeric():
			return 'integerConstant'
		elif possible_token in self.identifier_list:
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
			if possible_token not in self.identifier_list:
					self.identifier_list.append(possible_token)
			return 'identifier'
			