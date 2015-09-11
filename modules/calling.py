import sys, os, glob
sys.path.append("modules/calling")
sys.path.append("modules")
sys.path.append("calling")
import scripts,common

#function used to find variants
def variantCalling(programDirectory,analysis,projectToProcess,working_dir,path_to_bam,available_tools,account,exclude,processFiles,processed):
        project_name=projectToProcess
        if not project_name.startswith('.') and project_name not in exclude.keys() and not os.path.islink(os.path.join(analysis, project_name)):
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
                            call="scripts." + tools+"(\""+programDirectory+"\",\""+local_project_dir+"/"+tools+"\",\""+sample_name+"\",\""+os.path.join(path_to_sample, file)+"\",\""+account+"\")"
                            print(call);
                            pid = eval(call)
                            processFiles[tools]["ongoing"][sample_name] = {"pid":pid,"project":project_name,"outpath": local_project_dir}
                            print "sample {0} LAUNCHED".format(sample_name)

        common.UpdateProcessFiles(processFiles,processed,"calling")
        return(processFiles);
