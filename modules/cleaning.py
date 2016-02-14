import sys, os, glob, time

#function used to annotate the filtered variants
def cleaning(programDirectory,previousProcessFiles,processed,account):
        sys.path.append(os.path.join(programDirectory,"modules/cleaning"))
        import cleaningScript,common
        #read the process files
        processFiles=common.readProcessFiles(previousProcessFiles,processed,"cleaning")
        for tools in previousProcessFiles: 
             print("cleaning: "+tools);
             for sample in previousProcessFiles[tools]["analysed"]:
                if sample in processFiles[tools]["ongoing"]:
                    done=common.get_slurm_job_status(int(processFiles[tools]["ongoing"][sample]["pid"]))
                    processFiles=common.get_process_status(done,processFiles,tools,sample)
                elif sample in processFiles[tools]["failed"].keys():
                    print "sample {0} FAILED".format(sample)
                elif sample in processFiles[tools]["cancelled"].keys():
                    print "sample {0} CANCELLED".format(sample)
                elif sample in processFiles[tools]["timeout"].keys():
                    print "sample {0} TIMEOUT".format(sample)
                elif sample in processFiles[tools]["excluded"].keys():
                    print "sample {0} EXCLUDED".format(sample)
                elif sample in processFiles[tools]["analysed"].keys():
                    print "sample {0} COMPLETE".format(sample)
                else:
                    print("submitting: " + sample);
                    try:
                        outgoing=cleaningScript.submit2Cleaning(tools,sample,previousProcessFiles,programDirectory,account);
                        processFiles[tools]["ongoing"].update(outgoing)
                    except:
                        print("FAILED:was the sample excluded?");         

        common.UpdateProcessFiles(processFiles,processed,"cleaning")  
        finished=1;
        return(processFiles);
