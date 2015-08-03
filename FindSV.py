import sys, os, glob, argparse
sys.path.append("modules")
import scripts,slurm_job,readConfigFile


def main(args):
	analysis = args.analysis
	projectToProcess = args.project   



	#read the config file
	programDirectory=os.path.dirname(os.path.abspath(__file__));
	working_dir,path_to_bam,available_tools,account,exclude,analysed,ongoing,processed=readConfigFile.readConfigFile(programDirectory)

	if not (os.path.exists(processed)):
		os.makedirs(processed)

	for project_name  in os.listdir(analysis):
		if not project_name.startswith('.') and project_name not in exclude.keys() and not os.path.islink(os.path.join(analysis, project_name)):
			if(projectToProcess):
				if projectToProcess != project_name:
					continue
			local_project_dir = os.path.join(working_dir, project_name)
			if not os.path.isdir(local_project_dir):
				os.makedirs(local_project_dir)
			for tools in available_tools:
				path_to_project  = os.path.join(analysis, project_name)
				path_to_sample = os.path.join(path_to_project, path_to_bam)
				print(tools);
				if os.path.exists(path_to_sample):
					for file in os.listdir(path_to_sample):
						if file.endswith(".bam"):
							sample_name = file.split(".")[0]
						else:
							continue         
						if sample_name in analysed[tools].keys():
							# sample state is ANALYSED
							print "sample {0} ANALYSED".format(sample_name)
						elif sample_name in ongoing[tools].keys():
							# sample state is UNDER_ANALYSIS
							 # check if it is still running in that case delete it from ongoing and add to analysed
							done=slurm_job.get_slurm_job_status(int(ongoing[tools][sample_name])) 
							if done == 0:
								del ongoing[tools][sample_name]
								analysed[tools][sample_name] = ""
								print "sample {0} DONE".format(sample_name)
  							else:
								print "sample {0} RUNNING".format(sample_name)
						else:
							# sample state is NEW
							# submit this sample, if submission works fine store it in under analysis with the PID 
							call="scripts." + tools+"(\""+programDirectory+"\",\""+local_project_dir+"/"+tools+"\",\""+sample_name+"\",\""+os.path.join(path_to_sample, file)+"\",\""+account+"\")"
							print(call);
							pid = eval(call)
							ongoing[tools][sample_name] = pid
							#ongoing[tools][sample_name] = random.randint(1,2000);
							print "sample {0} LAUNCHED".format(sample_name)
							#time.sleep(300)
						#write ongoing to file (rewrite it)
    						with open(os.path.join(processed,tools,"FindVariants", "analysed"), 'w') as analysed_fd:
							for sample, empty in analysed[tools].items():
								analysed_fd.write("{0} {1} {2}\n".format(sample,project_name,local_project_dir))

						#write analyse to file (rewrite it)
						with open(os.path.join(processed,tools,"FindVariants", "ongoing"), 'w') as ongoing_fd:
							for sample, pid in ongoing[tools].items():
								ongoing_fd.write("{0} {1} {2} {3}\n".format(sample, pid,project_name,local_project_dir))
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
