import sys, os, glob, time

#function used to apply filters on the varian call files.
def applyFilter(programDirectory,previousProcessFiles,processed,account,frequency_db):
    sys.path.append(os.path.join(programDirectory,"modules/filter"))
    import common,filterScripts
    print("applying filter");
    processFiles=common.readProcessFiles(previousProcessFiles,processed,"filter")
        
    #itterate through every available tool
    for tool in previousProcessFiles:

        print("filtering the output of {0}".format(tool));
        #this is a list of all the files that have already passed the filter
        filtered=processFiles[tool]["analysed"].keys()+processFiles[tool]["cancelled"].keys()+processFiles[tool]["timeout"].keys()+processFiles[tool]["failed"].keys()+processFiles[tool]["excluded"].keys()
        database=previousProcessFiles[tool]["analysed"].keys();
        #only run the query when the previous query was finished and when there are newly generated databases
        #WARNING, if the user removes samples from the database log file, the condition will always be true,TODO: change to set comparison
        if(processFiles[tool]["ongoing"] == {} and sorted(filtered) != sorted(database) ):
            add2Ongoing=filterScripts.runScripts(tool,previousProcessFiles[tool]["analysed"].keys(),previousProcessFiles,programDirectory,account,frequency_db);
            processFiles[tool]["ongoing"].update(add2Ongoing);
                                                        
        samples=[]
        for sample in processFiles[tool]["ongoing"]:
            samples.append(sample);

        while len(samples) > 0:
            try:                
                done=common.get_slurm_job_status(int(processFiles[tool]["ongoing"][samples[0]]["pid"]))
                processFiles=common.get_process_status(done,processFiles,tool,samples[0])
                del samples[0];
            except:
                print("Warning, unnable to get slurm job status for job {}, please try again".format(processFiles[tool]["ongoing"][sample]["pid"]));
                del samples[0];

    common.UpdateProcessFiles(processFiles,processed,"filter")      
    return(processFiles);
