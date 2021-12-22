#This python program is an assembler for the Hack assembly language from The Elements of Computing Systems: Building a Modern Computer from First Principles aka Nand2Tetris
#https://www.nand2tetris.org/
#Programmer: Jayk Wilson
#Random inspirational quote....
# “Programming is the art of telling another human being what one wants the computer to do.”
# ― Donald Ervin Knuth


class Assembler:


	def __init__(self,data):
		self.assemblyFile = data
		#Initialize symbolTable with pre-defined symbols
		symbolTable = {'SCREEN':16384, 'KBD':24576, 'SP':0, 'LCL':1, 'ARG':2, 'THIS':3, 'THAT':4}

		for i in range(16):
			temp = "R" + str(i)
			symbolTable[temp] = i

		print(symbolTable)

	def tokenize(self):
		commands = self.assemblyFile.split('\n')
		for i, command in enumerate(commands):
			command = command.replace(" ","")
			print(i,command)

	def parseVarsandLabels(self):
		




data = '''@7
M = D + 1
(LOOP)
@5
D = A
M = D + 5
@sum
D;JNE
@LOOP'''

x = Assembler(data)
x.tokenize()
x.parseVarsandLabels()


#implementation notes:
#STEP 0: Constructor initialize
#Create symbol table(dictionary type), populate with keywords

#STEP 1: Tokenize
#break file into a list of strings based on line (EOL delimiter)
#remove all white spaces 

#STEP 2: Complete symbol table
# Iterate through command list 
#if first letter of string == '(', check if following string already exists in symbol map(dictionary) before creating new item, then create add string to hash map where value is set to 0, if string exists multiply value by -1 to indicate a label was found
#if first letter of string == @ and following characters represent a string, check if the string exists in the hash map,  if value is greater than 0  increment value and move on, if value is 0, increment and replace with location of ( from symbol
#	if value is -1 decrement to keep track of how many varibles without label name exist
#if first letter of string ==@ and name doesn't exist already initialized to zero, add with value -1
#after iterating through the file, iterate through the hash map for any keys that have negative values, create variables in hashmap for those strings and then replace string with address
#add all lines with commands added to symbol table to linesConverted list, which will be used to remove from a ranged list for all lines to skip those lines when going through on a second pass

#STEP 3: parse through the list for a second time to convert commands to A or C instructions
#if command[0](first letter) == '@' process A instruction via convertAInstruction()
#if command[0] == 'M, D, A, 0, 1, -, !, process C instruction via convertCInstruction()

#STEP 4 print list of binary commands to txt file located in same directory as the executable
