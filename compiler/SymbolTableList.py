class LinkedList:

	class Node:
		def __init__(self, data):
			self.data = data
			self.next = None


	class SymbolTable:
		# scope_num tracks nested scope
		scope_num = 0


		def __init__(self):
			self.field_num = 0
			self.static_num = 0
			self.argument_num = 0
			self.local_num = 0
			self.name = []
			self.symbol_type = []
			self.kind = []
			self.num = []
		

		def increment_num(self,kind):
			if kind == "field":
				self.field_num += 1
			elif kind == "static":
				self.static_num += 1
			elif kind == "argument":
				self.argument_num += 1
			elif kind == "local":
				self.local_num += 1


		def add_symbol(self, name, symbol_type, kind):
			self.name.append(name)
			self.symbol_type.append(symbol_type)
			self.kind.append(kind)
			if kind == "field":
				self.num.append(self.field_num)
			elif kind == "static":
				self.num.append(self.static_num)
			elif kind == "argument":
				self.num.append(self.argument_num)
			elif kind == "local":
				self.num.append(self.local_num)
			self.increment_num(kind)


		def find_symbol(self, name):
			return name in self.name


		def get_kind(self, name):
			idx = self.name.index(name)
			return self.kind[idx]


		def get_num(self, name):
			idx = self.name.index(name)
			return self.num[idx]


		def get_type(self, name):
			idx = self.name.index(name)
			return self.symbol_type[idx]


		def get_nargs(self):
			return self.argument_num


		def get_nlocals(self):
			return self.local_num


		def get_num_class_field_var(self):
			return self.field_num


		def print_table(self):
			for i in range(len(self.name)):
				print(self.name[i],self.symbol_type[i],self.kind[i],self.num[i])


	def __init__(self):
		self.head = None
		self.class_head = None


	def add_table(self):
		new_table = self.SymbolTable()
		self.add_node(new_table)


	def add_node(self, data):
		new_node = self.Node(data)
		new_node.next = self.head
		if self.head == None:
			self.class_head = new_node
		self.head = new_node


	def add_class_symbol(self, name, symbol_type, kind):
		self.class_head.data.add_symbol(name, symbol_type, kind)


	def add_subroutine_symbol(self, name, symbol_type, kind):
		self.head.data.add_symbol(name, symbol_type, kind)


	def has_symbol(self,symbol):
		if self.head is None:
			print("no symbol tables")
			return
		else:
			n = self.head
			while n is not None:
				if n.data.find_symbol(symbol) == True:
					return True
				n = n.next
			return False


	def get_segment(self, symbol):
		if self.head is None:
			print("no symbol tables")
			return
		else:
			n = self.head
			while n is not None:
				if n.data.find_symbol(symbol) == True:
					kind = n.data.get_kind(symbol)
					if kind == "field":
						kind = "this"
					num = str(n.data.get_num(symbol))
					return kind + " " + num
				n = n.next
			if n == None:
				raise Exception("symbol not found in symbol tables")


	def get_kind(self, name):
		if self.head is None:
			print("no symbol tables")
			return
		else:
			n = self.head
			while n is not None:
				if n.data.find_symbol(name) == True:
					return n.data.get_kind(name)
				n = n.next

			if n == None:
				raise Exception("symbol not found in symbol tables")
		

	def get_num(self, name):
		if self.head is None:
			print("no symbol tables")
			return
		else:
			n = self.head
			while n is not None:
				if n.data.find_symbol(name) == True:
					return n.data.get_num(name)
				n = n.next
			if n == None:
				raise Exception("symbol not found in symbol tables")


	def get_class(self, name):
		if self.head is None:
			print("no symbol tables")
			return
		else:
			n = self.head
			while n is not None:
				if n.data.find_symbol(name) == True:
					return n.data.get_type(name)
				n = n.next
			if n == None:
				raise Exception("symbol not found in symbol tables")


	def get_nargs(self):
		return self.head.data.get_nargs()


	def get_nlocals(self):
		return self.head.data.get_nlocals()


	def get_num_class_field_var(self):
		return self.class_head.data.get_num_class_field_var()


	def reset_subroutine_tables(self):
		if self.head is None:
			print("no symbol tables")
		else:
			while self.head is not self.class_head:
				temp = self.head.next
				self.head.next = None
				self.head = temp
	

	def has_symbol(self, name):
		if self.head is None:
			print("no symbol tables")
			return False
		else:
			n = self.head
			while n is not None:
				if n.data.find_symbol(name) == True:
					return True
				n = n.next
			if n == None:
				return False
		

	def print_list(self):
		if self.head is None:
			print("no symbol tables")
		else:
			n = self.head
			i = 1
			while n is not None:
				print("head: ",n, i)
				n.data.print_table()
				n = n.next
				print('\n')
				i += 1


	def print_class(self):
		print("class head", self.class_head)
		n = self.class_head
		n.data.print_table()
		nh = self.head
