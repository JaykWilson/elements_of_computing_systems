class LinkedList:

	class Node:
		def __init__(self, data):
			self.data = data
			self.next = None


	class SymbolTable:

		#scope_num is used by the subroutine symbol tables to keep track of how many
		#levels of nested scope a particular variable/symbol has
		#the reason for keeping track of it within the symbol table is to check
		#if the scope number/levels of nested scope of existing symbols in the 
		#head table are equal to the scope of a newly encountered symbol. If the scope
		#of the head table is different, a new table must be created for a new scope
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


		def get_kind(self, name):
			idx = self.name.index(name)
			return self.kind[idx]


		def get_num(self, name):
			idx = self.name.index(name)
			return self.num[idx]

		# def reset_table(self):
		# 	self.name.clear()
		# 	self.symbol_type.clear()
		# 	self.kind.clear()
		# 	self.num.clear()
		# 	self.field_num = 0
		# 	self.static_num = 0
		# 	self.argument_num = 0
		# 	self.local_num = 0


		def print_table(self):
			for i in range(len(self.name)):
				print(self.name[i],self.symbol_type[i],self.kind[i],self.num[i])


	def __init__(self):
		self.head = None
		self.class_node = None


	def add_table(self):
		new_table = self.SymbolTable()
		self.add_node(new_table)


	def add_node(self, data):

		new_node = self.Node(data)
		new_node.next = self.head
		if self.head == None:
			self.class_node = new_node
		self.head = new_node


	def add_class_symbol(self, name, symbol_type, kind):
		self.class_node.data.add_symbol(name, symbol_type, kind)


	def add_subroutine_symbol(self, name, symbol_type, kind):
		self.head.data.add_symbol(name, symbol_type, kind)


	def has_symbol(self,symbol):
		if self.head is None:
			print("no symbol tables")
			return
		else:
			n = self.head
			while n is not None:
				if n.data.find_symbol() == True:
					return True
				n = n.next
			return False


	def get_kind(self, name):
		if self.head is None:
			print("no symbol tables")
			return
		else:
			n = self.head
			while n is not None:
				if n.data.find_symbol() == True:
					return n.get_kind(name)
		

	def get_num(self, name):
		if self.head is None:
			print("no symbol tables")
			return
		else:
			n = self.head
			while n is not None:
				if n.data.find_symbol() == True:
					return n.get_num(name)


	def reset_subroutine_tables(self):
		if self.head is None:
			print("no symbol tables")
		else:
			while self.head is not self.class_node:
				temp = self.head.next
				self.head.next = None
				self.head = temp


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
		print("class head", self.class_node)
		n = self.class_node
		n.data.print_table()
		nh = self.head

		print("head", self.head)
		nh.data.print_table()
		print('\n')