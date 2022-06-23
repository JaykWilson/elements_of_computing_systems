import os
import sys
import argparse
import CompilationTokenizer
import CompilationEngine


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
CompilationEngine = CompilationEngine.CompilationEngine()
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
