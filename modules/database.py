import os,sys
sys.path.append("modules/database")
sys.path.append("modules")
sys.path.append("")
import submitToDatabase,slurm_job


def buildDatabase(programDirectory,analysed,processed,account):
    print("constructing databases");
    databaseFinished={}
    ongoing={};
    #look for the files used to keep track of the processing, if the files exists, read them. If not, create empty files
    for tool in analysed:
        databaseFinished[tool]={}
        ongoing[tool]={}
        pathToVariantFiles=os.path.join(processed,tool,"database");

        if not (os.path.exists(pathToVariantFiles)):
            os.makedirs(os.path.join(pathToVariantFiles))
            open(os.path.join(pathToVariantFiles,"ongoing"), 'a').close()
            open(os.path.join(pathToVariantFiles,"databaseFinished"), 'a').close()

        else:
            with open(os.path.join(pathToVariantFiles, "databaseFinished")) as analysed_fd:
                for sample in analysed_fd:
                    sample , pid ,project, outpath = sample.rstrip().split()
                    databaseFinished[tool][sample] = {"pid":pid,"project":project,"outpath":outpath}
            with open(os.path.join(pathToVariantFiles, "ongoing")) as ongoing_fd:
                for sample in ongoing_fd:
                    if(sample[0] != "\n"):
	                    sample , pid ,project, outpath = sample.rstrip().split()
	                    ongoing[tool][sample] = {"pid":pid,"project":project,"outpath":outpath}

        
    #create a dictionay containing the samples that are yet to be run through build db
    newsamples={}
    for tool in analysed:
        newsamples[tool]={}
        for sample in analysed[tool]:
            if sample not in ongoing[tool] and sample not in databaseFinished[tool]:
                newsamples[tool].update({sample:analysed[tool][sample]})



    #check if any of the ongoing samples are finished, and add finished samples to the finished dictionary
    for tools in ongoing:
        for sample in ongoing[tools]:
            try:
                done=slurm_job.get_slurm_job_status(int(ongoing[tools][sample]["pid"])) 
                if done == 0:
                    databaseFinished[tools].update({sample:ongoing[tools][sample]})  
                    print "sample {0} DONE".format(sample)
                else:
                    print "sample {0} ONGOING".format(sample)
            except:
                print("Warning, unnable to get slurm job status for job {}, please try again".format(ongoing[tools][sample]["pid"]));


    #now remove every finished samples from the ongoing dictionary
    for tools in databaseFinished:
        for sample in databaseFinished[tools]:
            if sample in ongoing[tools]:
                del ongoing[tools][sample];  

    #submit the new samples and add them to ongoing
    print("submitting");
    for tools in newsamples:
        print(tools);
        for sample in newsamples[tools]:
            print("sample:" + sample);
            pid=submitToDatabase.submit2DB(newsamples,tools,sample,programDirectory,processed,account)
            ongoing[tools].update({sample:newsamples[tools][sample]})
            ongoing[tools][sample]["pid"]=pid

    #update the process files and return the finished dictionary
    for tools in databaseFinished:
        pathToVariantFiles=os.path.join(processed,tools,"database");
        with open(os.path.join(pathToVariantFiles, "databaseFinished"), 'w') as analysed_fd:
            for sample, dictionary in databaseFinished[tools].items():
                    pid=dictionary["pid"]
                    projectName=dictionary["project"]
                    outPath=dictionary["outpath"]
                    analysed_fd.write("{0} {1} {2} {3}\n".format(sample,pid ,projectName,outPath))


    for tools in ongoing:
        pathToVariantFiles=os.path.join(processed,tools,"database");
        with open(os.path.join(pathToVariantFiles, "ongoing"), 'w') as ongoing_fd:
            for sample, dictionary in ongoing[tools].items():
                pid=dictionary["pid"]
                projectName=dictionary["project"]
                outPath=dictionary["outpath"]
                ongoing_fd.write("{0} {1} {2} {3}\n".format(sample,pid ,projectName,outPath))


    return(databaseFinished)
        
