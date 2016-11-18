#!/usr/bin/env python

import sys
from subprocess import check_call
from subprocess import call
from subprocess import check_output

import argparse

def open_file(argFile):
	if (call(["file", argFile]) == 0):
		file_out = check_output(["file", argFile])
		if (file_out.find("executable") != -1):
			objdump_out = check_output(["objdump", "-d", "-M", "intel", argFile])
			#print objdump_out
			return objdump_out
		else:
			print("File needs to be of an executable type!")
			sys.exit(1)
	else:
		print("Error with %s as a file" % argFile)
		sys.exit(1) 
	

def extract_opcode(objdump_out):
	global function
	global verbosity
	global asm
	
	inFunc = False
	func_name = ''
	if (function != None):
		func_name = function
		
        out = ''
	lines = objdump_out.split("\n")
        for line in lines:
		#print ("working on %s" % line)
		
		left_index = line.find("<")
		right_index = line.find(">:")
                function_search = "<" + func_name + ">:"
		bolo_function = line.find(function_search)
		if ((left_index != -1) and (right_index != -1)):
			if ((bolo_function != -1) or (func_name == '')):
				inFunc = True
				if (verbosity):
					print (line[left_index:(right_index + 1)])
				#Below I add 2 to right index in order to capture the '>:' char
				out += line[left_index:(right_index + 2)] + '\n'
			else:
				inFunc = False
		
		elif(inFunc):
			line_split = line.split("\t")
			if (len(line_split) > 2):
				if (verbosity):
					print (line_split[1])
                                op_split = line_split[1].split()
				for op in op_split:
					out += '\\x' + op
				if (asm):
					out += '\t' + "\\\\" + line_split[2]
				out += '\n'
					
	return out
		

def main ():
	global bin_file
	global function
	global asm
	global quotes
	global condense

	str_opcode = ''
	objdump_file = None
	objdump_file = open_file(bin_file)
	if (objdump_file != None):
		str_opcode = extract_opcode(objdump_file)
	else:
		print("Error opening %s" % sys.argv[1])
		sys.exit(1)
	
	if (not(condense) and not(asm)):
		if (not(quotes)):
			print (str_opcode)
		else:
			str_quoted = ''
			opcode_lines = str_opcode.strip().split('\n')
			for line in opcode_lines:
				if (line.__contains__('>:')):
					str_quoted += line + "\n"
				else:
					str_quoted += "\"" + line + "\"\n"
						
			print (str_quoted)	

	#str_opcode should now have all of our opcode
	#If asm and condense are both true, then print asm first
	if (asm):	
		if (not(quotes)):
			print (str_opcode)
		else:
			asm_quoted = ''
			opcode_lines = str_opcode.strip().split('\n')
			for line in opcode_lines:
				#print line
				if (line.__contains__('>:')):
					asm_quoted += line + "\n"
				else:
					if(len(line.split()) > 1): 
						comment_index = line.find("\\\\")
						asm_quoted += "\"" + line.split()[0] + "\""
						if (comment_index > -1):
							asm_quoted += "\t" + line[comment_index:] + "\n"
					
			print (asm_quoted)

	
	if (condense):
		condense_code = ''
		opcode_lines = str_opcode.strip().split('\n')
		if (not(asm)):
			for line in opcode_lines:
				if(line.__contains__('>:')):
					if (quotes):
						if (len(condense_code) > 0):
							condense_code += "\""
						condense_code += "\n" + line + "\n\""
					else:
						condense_code += "\n" + line + "\n"
				else:
					condense_code += line
			#Need to append one more quote mark
			if (quotes):
				condense_code += "\""
			#condense_opcode = "".join(str_opcode.split('\n'))
		else:
			#strip away the assembly
			for line in opcode_lines:
				if (line.__contains__('>:')):
					if (quotes):
						if (len(condense_code) > 0):
							condense_code += "\""
						condense_code += "\n" + line + "\n\""
					else:
						condense_code += "\n" + line + "\n"
				else:
					if(len(line.split()) > 1): 
						#comment_index = line.find("\\\\")
						condense_code += line.split()[0]
			
			#append the last quotation mark
			if(quotes):
				condense_code += "\""
						
		print (condense_code)
				

if (__name__=="__main__"):
	global function
	global quotes
	global asm
	global condense
	global bin_file

	#Build our handler for commandline args
	arg_parser = argparse.ArgumentParser()
	
	arg_parser.add_argument('-f','--function', help="Search bin_file for a specified function")
	arg_parser.add_argument('-q','--quotations', dest='quotes', action='store_true', help="Place quotations (\")around opcode ")
	arg_parser.add_argument('-a', '--asm', dest='asm', action='store_true', help="Print the mnemonic asm code (preceded by C-style comment marker \\\)")
	arg_parser.add_argument('-c', '--condense', dest='condense', action='store_true', help="Condense the code to a single line of text")

	arg_parser.add_argument('-v', '--verbose', dest='verbosity', action='store_true', help="Condense the code to a single line of text")
	arg_parser.add_argument('bin_file')
	
	args = arg_parser.parse_args()
	
	bin_file = args.bin_file
	function = args.function
	quotes = args.quotes
	asm = args.asm
	condense = args.condense
	verbosity = args.verbosity
	
	#Now head to our main function
	main()


