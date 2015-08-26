import os,sys
sys.path.append("modules/database")
sys.path.append("modules")
sys.path.append("")
import submitToDatabase,common,time


def buildDatabase(programDirectory,analysed,processed,account):
    print("constructing databases");
    databaseFinished,ongoing=common.readProcessFiles(analysed,processed,"database")

        
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
                print(sample)
                time.sleep(10)
                done=common.get_slurm_job_status(int(ongoing[tools][sample]["pid"])) 
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

    common.UpdateProcessFiles(databaseFinished,ongoing,processed,"database")


    return(databaseFinished)
        
