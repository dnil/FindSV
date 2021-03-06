import sys, os, glob


#function used to find variants
def variantCalling(programDirectory,analysis,projectToProcess,working_dir,path_to_bam,available_tools,account,modules,bam_files,exclude,processFiles,processed):
    sys.path.append(os.path.join(programDirectory,"modules/calling"))
    import scripts,common
    project_name=projectToProcess
    if not project_name.startswith('.') and project_name not in exclude.keys():
        local_project_dir = os.path.join(working_dir, project_name)
        if not os.path.isdir(local_project_dir):
            os.makedirs(local_project_dir)
        for tools in available_tools:
            print(tools);
            for sample_name in bam_files:
                if sample_name in processFiles[tools]["analysed"].keys():
                    # sample state is ANALYSED
                    print "sample {0} ANALYSED".format(sample_name)
                elif sample_name in processFiles[tools]["ongoing"].keys():
                    # sample state is UNDER_ANALYSIS
                    # check if it is still running in that case delete it from ongoing and add to analysed
                    done=common.get_slurm_job_status(int(processFiles[tools]["ongoing"][sample_name]["pid"]))
                    processFiles=common.get_process_status(done,processFiles,tools,sample_name);
                elif sample_name in processFiles[tools]["failed"].keys():
                    print "sample {0} FAILED".format(sample_name)
                elif sample_name in processFiles[tools]["cancelled"].keys():
                    print "sample {0} CANCELLED".format(sample_name)
                elif sample_name in processFiles[tools]["excluded"].keys():
                    print "sample {0} EXCLUDED".format(sample_name)
                elif sample_name in processFiles[tools]["timeout"].keys():
                    print "sample {0} TIMEOUT".format(sample_name)
                else:
                    # sample state is NEW
                    # submit this sample, if submission works fine store it in under analysis with the PID 
                    call="scripts." + tools+"(\""+programDirectory+"\",\""+local_project_dir+"/"+tools+"\",\""+sample_name+"\",\""+bam_files[sample_name]["path"]+"\",\""+account+"\",\""+str(modules)+"\")"
                    callerOutput = eval(call)
                    processFiles[tools]["ongoing"][sample_name] = {"pid":callerOutput[0],"project":project_name,"outpath": local_project_dir,"outputFile":callerOutput[1]}
                    print "sample {0} LAUNCHED".format(sample_name)

        common.UpdateProcessFiles(processFiles,processed,"calling")
        return(processFiles);
