import os

#this function is used to read the config file
def readConfigFile(programDirectory):
	#open the config file to read through the settings
	with open(os.path.join(programDirectory,"config.txt")) as ongoing_fd:
		for line in ongoing_fd:
			option = line.rstrip().split()[0];
			option= option.split("=")
			if(option[0] == "working_directory"):
				#get the working directory
				working_dir = option[1]
				if(working_dir == "default"):
					working_dir=os.path.join(programDirectory,"output")
			if(option[0] == "bamfile_location"):
				#get the path to a bam file when standing in a project directory
				if(len(option) > 1):
					path_to_bam = option[1]
				else:
					path_to_bam="";
			if(option[0] == "available_tools"):
				#get a list of the available tools
				available_tools = option[1]
				available_tools=available_tools.split(";");
			if(option[0] == "excluded_tools"):
				#get a list of the excluded tools
				if(len(option) > 1):
					excluded_tools = option[1]
					excluded_tools=excluded_tools.split(";");
				else:
					excluded_tools=[];
			if(option[0]=="account"):
				#get the account
				account= option[1]
			if(option[0]=="excluded_projects"):
				#get a list of the excluded projects
				if(len(option) > 1):
					excluded_projects = option[1]
					excluded_projects=excluded_projects.split(";");
				else:
					excluded_projects=[];
			if(option[0]=="processed"):
				#get the processed file directory
				processed = option[1]
				#if the processed folder is set to default, it will be placed in the program filder
				if(processed == "default"):
					processed=os.path.join(programDirectory,"analysed");

			if(option[0]=="uppmax"):
				# use module system etc on a machine 
				# similar to UPPMAX standard layout
				uppmax = option[1].strip();
				if(uppmax == "yes"):
					modules=True;
				else:
					modules=False;

	#remove the excluded tools from the available tools list
	available_tools=list(set(available_tools) - set(excluded_tools))

    
	#add the excluded projects to a dictionary
	exclude={};
	for projects in excluded_projects:
		exclude[projects]="";

	return(working_dir,path_to_bam,available_tools,account,exclude,processed,modules)
