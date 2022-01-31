# Nand2Tetris
Code for The Elements of Computing Systems: Building a Modern Computer from First Principles, aka Nand2Tetris

Nand2Tetris is an ambitious course that builds a complete computer virtually starting with only nand gates; creates gates such as and, or, not, mux; uses those gates to create adders, an ALU, program counter, RAM, register, CPU; creates an assembler to convert assembly language to binary; creates a virtual machine to convert stack based virtual machine  commands in assembly; creates a compiler for a high level language based on Java into stack based virtual machine code; and creates an OS.

The course content can be downloaded from https://www.nand2tetris.org on the "software" page. 

Testing Instructions:
-Assembler.py: download the course contents, run any of the ".asm" files in ..projects\06 to generator the binary code (.hack extension), run CPUEmulator.bat in the tools folder and load the generated binary code

-VMTranslator.py: run from cli with absolute path of any of the ".vm" files or directory if directory contains multiple ".vm" files to generate the ".asm" assembly code, run CPUEmulator.bat in the tools folder, load the corresponding test script with (.tst extension) in the CPUEmulator.bat. Test scripts are loaded by pressing the "script" button to the left of the red flag button. Also note that test scripts with "VME" at the end of the name are meant to be run in the VMEmulator.bat and don't auto load the user generated assembly code within that folder. 

