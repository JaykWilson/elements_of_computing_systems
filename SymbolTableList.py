class LinkedList:

	class Node:
		def __init__(self, data):
			self.data = data
			self.next = None


	class SymbolTable:
		field_num = 0
		static_num = 0
		argument_num = 0
		local_num = 0


		def __init__(self):
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


		def reset_table(self):
			self.name.clear()
			self.symbol_type.clear()
			self.kind.clear()
			self.num.clear()
			self.field_num = 0
			self.static_num = 0
			self.argument_num = 0
			self.local_num = 0


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
		self.head = new_node
		#class level symbol table will be first node, keep pointer to it for resetting subrouting level nodes
		if self.head.next == None:
			self.class_node = self.head


	def add_class_symbol(self, name, symbol_type, kind):
		self.class_node.data.add_symbol(name, symbol_type, kind)


	def add_subroutine_symbol(self, name, symbol_type, kind):
		self.head.data.add_symbol(name, symbol_type, kind)


	def find_symbol(self,symbol):
		if self.head is None:
			print("no symbol tables")
			return
		else:
			n = self.head
			while n is not None:
				if n.data.name == symbol:
					print("symbol found")
					return
				n = n.next


	def reset_subroutine_nodes(self):
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
			while n is not None:
				n.data.print_table()
				print("\n")
				n = n.next