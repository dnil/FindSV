import sys, os, glob, time
sys.path.append("filter")
sys.path.append("modules")
sys.path.append("modules/filter")
import common
import filterScripts

#function used to apply filters on the varian call files.
def applyFilter(programDirectory,analysed,processed,account):
    print("applying filter");
    filtered,ongoing=common.readProcessFiles(analysed,processed,"filter")
        
    #itterate through every tool that is available
    for tool in analysed:
        print("filtering the output of {0}".format(tool));
        filteredProjects = {};
        ongoingProjects = {};
        for sample in filtered[tool]:
            filteredProjects[filtered[tool][sample]["project"]]=[];
        for sample in ongoing[tool]:
            ongoingProjects[ongoing[tool][sample]["project"]]=[];

        analysedProjects= {};
        #create a set of all projects and all their samples that have been analysed
        for sample in analysed[tool]:
                

            if(analysed[tool][sample]["project"] in analysedProjects):
                analysedProjects[analysed[tool][sample]["project"]].append(sample);
            else:
                analysedProjects[analysed[tool][sample]["project"]]=[sample];
                    
            #test if the sample is already filtered
            if(analysed[tool][sample]["project"] in filteredProjects):
                filteredProjects[analysed[tool][sample]["project"]].append(sample);
                #test if the sample is ongoing

                        
        #see if the filtered and analysed samples are different, if so run analysis
        for project in analysedProjects:
            #if files of the project is analysed, but the project is not filtered and not undergoing filtraton
            if(project not in filteredProjects and project not in ongoingProjects):
                if(analysedProjects[project] is not None):
                    if(sample not in ongoing[tool]):
                        print("submitting project {0} for filtering".format(analysedProjects[project]))
                        add2Ongoing=filterScripts.runScripts(tool,analysedProjects[project],analysed,programDirectory,account);
                        ongoing[tool].update(add2Ongoing);
                                        
            else:                        
            #if the project exists we must check to see if there are any files that were recently finnished
                for sample in analysedProjects[project]:
                    if project in filteredProjects:
                        if( (sample not in filteredProjects[project] or sample not in filtered[tool] ) and project not in ongoingProjects):
                            if(sample not in ongoing[tool]):
                                add2Ongoing=filterScripts.runScripts(tool,analysedProjects[project],analysed,programDirectory,account);
                                ongoing[tools].update(add2Ongoing);
                                                        

        for sample in ongoing[tool]:
            try:
                print(ongoing[tool][sample]["pid"]);
                                        
                done=common.get_slurm_job_status(int(ongoing[tool][sample]["pid"])) 
                if done == 0:
                    filtered[tool][sample] = ongoing[tool][sample];
                                                                
                    print "sample {0} DONE".format(sample)
                else:
                    print "sample {0} ONGOING".format(sample)
            except:
                print("Warning, unnable to get slurm job status for job {}, please try again".format(ongoing[tool][sample]["pid"]));
        #print the filtered samples
        for sample in filtered[tool]:
            print "sample {0} ANALYSED".format(sample);
            if (sample in ongoing[tool]):
                del ongoing[tool][sample];
    
    common.UpdateProcessFiles(filtered,ongoing,processed,"filter")
                             
    return(filtered);
