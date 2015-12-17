import os,sys
sys.path.append("modules/database")
sys.path.append("modules")
sys.path.append("")
import submitToDatabase,common,time,process


def buildDatabase(programDirectory,previousProcessFiles,processed,account):
    print("constructing databases");
    processFiles=common.readProcessFiles(previousProcessFiles,processed,"database")

        
    #create a dictionary containing the samples that are yet to be run through build db
    newsamples={}
    for tool in previousProcessFiles:
        newsamples[tool]={}
        for sample in previousProcessFiles[tool]["analysed"]:
            if sample not in processFiles[tool]["ongoing"] and sample not in processFiles[tool]["analysed"] and sample not in processFiles[tool]["cancelled"] and sample not in processFiles[tool]["failed"] and sample not in processFiles[tool]["excluded"] and sample not in processFiles[tool]["timeout"]:
                newsamples[tool].update({sample:previousProcessFiles[tool]["analysed"][sample]})

    #check if any of the ongoing samples are finished, and add finished samples to the finished dictionary
    for tools in processFiles:
        samples=[]
        for sample in processFiles[tools]["ongoing"]:
            samples.append(sample);

        while len(samples) > 0:
            try:
                done=common.get_slurm_job_status(int(processFiles[tools]["ongoing"][samples[0]]["pid"]))
                processFiles=common.get_process_status(done,processFiles,tools,samples[0])
                del samples[0];
            except:
                print("Warning, unnable to get slurm job status for job {}, please try again".format(processFiles[tools]["ongoing"][samples[0]]["pid"]));
                del samples[0];

    #submit the new samples and add them to ongoing
    print("submitting");
    for tools in newsamples:
        print(tools);
        for sample in newsamples[tools]:
            print("sample:" + sample);
            databaseOutput=submitToDatabase.submit2DB(newsamples,tools,sample,programDirectory,processed,account)
            processFiles[tools]["ongoing"].update({sample:newsamples[tools][sample]})
            processFiles[tools]["ongoing"][sample]["pid"]=databaseOutput[0];
            processFiles[tools]["ongoing"][sample]["outputFile"]=databaseOutput[1];
            project=processFiles[tools]["ongoing"][sample]["project"]
        if newamples[tool]:
            step["filter"]=True
            process.restart(programDirectory,step,project,"all")

    common.UpdateProcessFiles(processFiles,processed,"database")


    return(processFiles)
        
