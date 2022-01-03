#This python program is an assembler for the Hack assembly language from The Elements of Computing Systems: Building a Modern Computer from First Principles aka Nand2Tetris
#https://www.nand2tetris.org/
#Programmer: Jayk Wilson
#Random inspirational quote....
# “Programming is the art of telling another human being what one wants the computer to do.”
# ― Donald Ervin Knuth

import argparse

class Assembler:

	def __init__(self):
		parser = argparse.ArgumentParser()
		parser.add_argument('--file', type=str, required=True)
		args = parser.parse_args()
		self.functionName = args.file.split(".")[:1]

		with open(args.file) as originalFile:
			f = originalFile.read()
		self.assemblyFile = f

		#Initialize symbolTable with pre-defined symbols
		self.symbolTable = {'SCREEN':16384, 'KBD':24576, 'SP':0, 'LCL':1, 'ARG':2, 'THIS':3, 'THAT':4}

		self.binFile = []

		self.destCommandList = {'':'000','M':'001','D':'010','DM':'011','A':'100','AM':'101','AD':'110','ADM':'111'}

		#comp bits are of the form acccccc whereby the a bit selects between passing the A or M register to the ALU and the cccccc bits represent the actual operation to perform. 
		self.compCommandList = {'':'','0':'0101010','1':'0111111','-1':'0111010','D':'0001100','A':'0110000','M':'1110000','!D':'0001101','!A':'0110001','!M':'1110001','-D':'0001111','-A':'0110011','-M':'1110011','D+1':'0011111',
								'A+1':'0110111','M+1':'1110111','D-1':'0001110','A-1':'0110010','M-1':'1110010','D+A':'0000010','D+M':'1000010','D-A':'0010011','D-M':'1010011','A-D':'0000111','M-D':'1000111','D&A':'0000000',
								'D&M':'1000000','D|A':'0010101','D|M':'0010101'}

		self.jumpCommandList = {'':'000','JGT':'001','JEQ':'010','JGE':'011','JLT':'100','JNE':'101','JLE':'110','JMP':'111'}

		for i in range(16):
			temp = "R" + str(i)
			self.symbolTable[temp] = i

		self.commands = []


	def tokenize(self):
		self.commands = self.assemblyFile.split('\n')
		tempList = []
		for i, command in enumerate(self.commands):
			self.commands[i] = command.replace(" ","")
			if command == '\n' or command  == '':
				pass
			elif command[:2] == "//":
				pass
			else:
				tempList.append(command)
		self.commands = tempList


	def parseVarsandLabels(self):
		varChecker = []
		for i, command in enumerate(self.commands):
			firstChar = command[0]

			if firstChar == '(':
				lastChar = command[-1]
				labelName = command[1:len(command)-1]
				
				if lastChar == ')':
					if labelName not in self.symbolTable:
						self.symbolTable[labelName] = i
						if labelName in varChecker:
							varChecker.remove(labelName)
					else:
						print("Error: only one declaration of label allowed")
				else:
					print("Error: improper formatting; missing ')'")

			elif firstChar == '@':

				labelName = command[1:len(command)]

				if labelName not in self.symbolTable and not labelName.isnumeric() :
					varChecker.append(labelName)

		for i, var in enumerate(varChecker):
			self.symbolTable[var] = 16 + i

	def convertToBinary(self):
		for i, command in enumerate(self.commands):
			destCommand = ''
			compCommand = ''
			jumpCommand = ''
			firstChar = command[0]

			if firstChar != '(':
				if firstChar =='@':
					#A INSTRUCTION
					labelName = command[1:len(command)]
					if labelName.isnumeric():
						aInstruction = '0' + str(format(int(labelName),'015b'))
						self.binFile.append(aInstruction)
					else:
						aInstruction = '0' + str(format(self.symbolTable[labelName],'015b'))
						self.binFile.append(aInstruction)
				else:
					#C INSTRUCTION
					if '=' in command:
						destCommand = command[:command.index('=')]

						if destCommand not in self.destCommandList:
							print("Error: destination command syntax not recognized")

						compCommand = command[command.index('=') + 1 :]
						if ';' in compCommand:
							compCommand = compCommand[: compCommand.index(';')]

						if compCommand not in self.compCommandList:
							print("Error: comp command syntax not recognized")

					if ';' in command:
						jumpCommand = command[command.index(';') + 1 :]
						#HANDLE SITUATION WHERE THERE IS NOT AN '=' BUT IS A COMPUTATION
						if '=' not in command:
							compCommand = command[:command.index(';')]

					cInstruction = '111' + self.compCommandList[compCommand] + self.destCommandList[destCommand] + self.jumpCommandList[jumpCommand]
					self.binFile.append(cInstruction)

	def writeBinaryFile(self):
		binFileName = self.functionName[0] + ".hack"
		with open(binFileName, 'w') as f:
			for line in self.binFile:
				f.write(line)
				f.write("\n")

#MAIN CODE
hackAssembler = Assembler()
hackAssembler.tokenize()
hackAssembler.parseVarsandLabels()
hackAssembler.convertToBinary()
hackAssembler.writeBinaryFile()


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
