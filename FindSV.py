import sys, os, glob, argparse
sys.path.append("modules")
import readConfigFile, findVariant, applyFilter, annotation


def main(args):
	analysis = args.analysis
	projectToProcess = args.project   

	#read the config file
	programDirectory=os.path.dirname(os.path.abspath(__file__));
	working_dir,path_to_bam,available_tools,account,exclude,analysed,ongoing,processed=readConfigFile.readConfigFile(programDirectory)

        #create a directory to keep track of the analysed files
	if not (os.path.exists(processed)):
		os.makedirs(processed)

        #function used to find variants
	analysed,ongoing=findVariant.variantCalling(programDirectory,analysis,projectToProcess,working_dir,path_to_bam,available_tools,account,exclude,analysed,ongoing,processed);

        #function that filters the variant files and constructs databases
        filtered=applyFilter.applyFilter(programDirectory,analysed,processed,account);

        #function used to annotate the samples
        finished=annotation.annotation(programDirectory,filtered,processed);
	return

if __name__ == '__main__':
	parser = argparse.ArgumentParser("""This scripts checks the analysis folder given in the config file(bamfile_location), every found file is analysed with the selected tools and the results are stored in the the working_dir folder given in the config file\nTo exclude a tool, copy it to the excluded_tools line of the config file. multiple tools should be separated using ;
   """)
	parser.add_argument('--analysis', type=str, required=False, help="The path to a folder containing project folders\n")
	parser.add_argument('--project', type=str, required=False, default=None, help="restrict analysis to the specified project\n")
	parser.add_argument('--list', required=False, action='store_true', help="print the available tools, unless tools are excluded, they will all be used\n")
	args = parser.parse_args()
	if(args.analysis):
		main(args)
	elif(args.list):
		i=0;
		#list the available tools
		print("available tools");
		programDirectory=os.path.dirname(os.path.abspath(__file__));
		with open(os.path.join(programDirectory, "config.txt")) as ongoing_fd:
			for line in ongoing_fd:
				i=i+1
				if(i == 3):
					available_tools=line.rstrip().split()[0];
					available_tools = available_tools.split("=")[1]
					available_tools=available_tools.split(";");
		for tools in available_tools:
			print(tools);

	else:
		print("Set the --analysis option to run the pipeline, or use the --list argument to print the availble tools");
