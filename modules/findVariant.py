import sys, os, glob
sys.path.append("modules/calling")
sys.path.append("modules")
sys.path.append("calling")
import scripts,slurm_job

#function used to find variants
def variantCalling(programDirectory,analysis,projectToProcess,working_dir,path_to_bam,available_tools,account,exclude,analysed,ongoing,processed):
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
							done=slurm_job.get_slurm_job_status(int(ongoing[tools][sample_name]["pid"])) 
							if done == 0:
                                                                analysed[tools][sample_name] = ongoing[tools][sample_name]
								del ongoing[tools][sample_name]
                                                                
								print "sample {0} DONE".format(sample_name)
  							else:
								print "sample {0} ONGOING".format(sample_name)
						else:
							# sample state is NEW
							# submit this sample, if submission works fine store it in under analysis with the PID 
							call="scripts." + tools+"(\""+programDirectory+"\",\""+local_project_dir+"/"+tools+"\",\""+sample_name+"\",\""+os.path.join(path_to_sample, file)+"\",\""+account+"\")"
							print(call);
							pid = eval(call)
							ongoing[tools][sample_name] = {"pid":pid,"project":project_name,"outpath": local_project_dir}
							#ongoing[tools][sample_name] = random.randint(1,2000);
							print "sample {0} LAUNCHED".format(sample_name)
							#time.sleep(300)
						#write ongoing to file (rewrite it)
    						with open(os.path.join(processed,tools, "analysed"), 'w') as analysed_fd:
							for sample, dictionary in analysed[tools].items():
                                                                pid=dictionary["pid"]
                                                                projectName=dictionary["project"]
                                                                outPath=dictionary["outpath"]

								analysed_fd.write("{0} {1} {2} {3}\n".format(sample,pid ,projectName,outPath))

						#write analyse to file (rewrite it)
						with open(os.path.join(processed,tools, "ongoing"), 'w') as ongoing_fd:
							for sample, dictionary in ongoing[tools].items():
                                                                pid=dictionary["pid"]
                                                                projectName=dictionary["project"]
                                                                outPath=dictionary["outpath"]

								ongoing_fd.write("{0} {1} {2} {3}\n".format(sample,pid ,projectName,outPath))
        return(analysed,ongoing);
