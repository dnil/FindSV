import sys, os, glob, time
sys.path.append("calling")
sys.path.append("filter")
sys.path.append("modules")
sys.path.append("modules/calling")
sys.path.append("modules/filter")
import slurm_job
import filterScripts

#function used to apply filters on the varian call files.
def applyFilter(programDirectory,analysed,processed,account):
        print("applying filter");
	
        #open the config file to read through the settings
	with open(os.path.join(programDirectory,"filterconfig.txt")) as ongoing_fd:
		for line in ongoing_fd:
			option = line.rstrip().split();
                        if(len(option) > 0):
                                option=option[0]
			        option= option.split("=")
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

    	#remove the excluded tools from the available tools list
        available_tools=list(set(available_tools) - set(excluded_tools))

        

        filtered={}
        ongoing={};
        #look for the files used to keep track of the processing, if the files exists, read them. If not, create empty files
        for variantTool in analysed:
                filtered[variantTool]={}
                ongoing[variantTool]={};
	        for tools in available_tools:
		        filtered[variantTool][tools]={};
		        ongoing[variantTool][tools]={};
                        pathToVariantFiles=os.path.join(processed,variantTool,"filter",tools);
		        if not (os.path.exists(pathToVariantFiles)):
		        	os.makedirs(os.path.join(pathToVariantFiles))
		        	open(os.path.join(pathToVariantFiles,"ongoing"), 'a').close()
		        	open(os.path.join(pathToVariantFiles,"filtered"), 'a').close()
		        else:
		        	with open(os.path.join(pathToVariantFiles, "filtered")) as analysed_fd:
		        		for sample in analysed_fd:
		        				sample , pid ,project, outpath = sample.rstrip().split()
		        				filtered[variantTool][tools][sample] = {"pid":pid,"project":project,"outpath":outpath}
		        	with open(os.path.join(pathToVariantFiles, "ongoing")) as ongoing_fd:
		        		for sample in ongoing_fd:
		        			if(sample[0] != "\n"):
		        				sample , pid ,project, outpath = sample.rstrip().split()
		        				ongoing[variantTool][tools][sample] = {"pid":pid,"project":project,"outpath":outpath}

        
        #itterate through every tool that is available
        for variantTool in analysed:
                for tools in available_tools:
                        print("filtering the output of {0} using {1}".format(variantTool,tools));
                        filteredProjects = {};
                        ongoingProjects = {};
                        for sample in filtered[variantTool][tools]:
                                filteredProjects[filtered[variantTool][tools][sample]["project"]]=[];
                        for sample in ongoing[variantTool][tools]:
                                ongoingProjects[ongoing[variantTool][tools][sample]["project"]]=[];

                        analysedProjects= {};
                        #create a set of all projects and all their samples that have been analysed
                        for sample in analysed[variantTool]:
                

                                if(analysed[variantTool][sample]["project"] in analysedProjects):
                                        analysedProjects[analysed[variantTool][sample]["project"]].append(sample);
                                else:
                                        analysedProjects[analysed[variantTool][sample]["project"]]=[sample];
                    
                        #test if the sample is already filtered
                                if(analysed[variantTool][sample]["project"] in filteredProjects):
                                        filteredProjects[analysed[variantTool][sample]["project"]].append(sample);
                        #test if the sample is ongoing

                        
                        #see if the filtered and analysed samples are different, if so run analysis
                        for project in analysedProjects:
                                        #if files of the project is analysed, but the project is not filtered and not undergoing filtraton
                                        if(project not in filteredProjects and project not in ongoingProjects):
                                                if(analysedProjects[project] is not None):
                                                        print("submitting project {0} for filtering".format(analysedProjects[project]))
                                                        add2Ongoing=filterScripts.runScripts(variantTool,tools,analysedProjects[project],analysed,programDirectory,account);
                                                        ongoing[variantTool][tools].update(add2Ongoing);
                                        
                                        else:                        
                                        #if the project exists we must check to see if there are any files that were recently finnished
                                                for sample in analysedProjects[project]:
                                                        if project in filteredProjects:
                                                                if( (sample not in filteredProjects[project] or sample not in filtered[variantTool][tools] ) and project not in ongoingProjects):
                                                                        add2Ongoing=filterScripts.runScripts(variantTool,tools,analysedProjects[project],analysed,programDirectory,account);
                                                                        ongoing[variantTool].update(add2Ongoing);
                                                        


                        #print the samples undergoing filtration, and update the finished samples
                        time.sleep(10)
                        for sample in ongoing[variantTool][tools]:
                                try:
                                        print(ongoing[variantTool][tools][sample]["pid"]);
                                        
                                        done=slurm_job.get_slurm_job_status(int(ongoing[variantTool][tools][sample]["pid"])) 
                                        if done == 0:
                                                filtered[variantTool][tools][sample] = ongoing[variantTool][tools][sample];
                                                                
                                                print "sample {0} DONE".format(sample)
                                        else:
                                                print "sample {0} ONGOING".format(sample)
                                except:
                                        print("Warning, unnable to get slurm job status for job {}, please try again".format(ongoing[variantTool][tools][sample]["pid"]));
                        #print the filtered samples
                        for sample in filtered[variantTool][tools]:
                                print "sample {0} ANALYSED".format(sample);
                                if (sample in ongoing[variantTool][tools]):
                                        del ongoing[variantTool][tools][sample];

                        #print to file
                        with open(os.path.join(processed,variantTool,"filter",tools, "filtered"), 'w') as analysed_fd:
                                for sample, dictionary in filtered[variantTool][tools].items():
                                        pid=dictionary["pid"]
                                        projectName=dictionary["project"]
                                        outPath=dictionary["outpath"]

                                        analysed_fd.write("{0} {1} {2} {3}\n".format(sample,pid ,projectName,outPath))


		        with open(os.path.join(processed,variantTool,"filter",tools, "ongoing"), 'w') as ongoing_fd:
		        	for sample, dictionary in ongoing[variantTool][tools].items():
                                        pid=dictionary["pid"]
                                        projectName=dictionary["project"]
                                        outPath=dictionary["outpath"]

                                        ongoing_fd.write("{0} {1} {2} {3}\n".format(sample,pid ,projectName,outPath))
                             
        return(filtered);
