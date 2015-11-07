import sys, os, glob, time
sys.path.append("modules/combine")
import common
import combineScript



#function used to annotate the filtered variants
def combine(programDirectory,previousProcessFiles,processed,account,bamFilePaths):
       
        #read the process files
        processFiles=common.readProcessFiles(["FindSV"],processed,"combine")
        samplesToMerge={};
        #combinedProcessFile={}
        firstTool= True
        #find all samples that has been analysed by the callers
        for tools in previousProcessFiles: 
            for sample in previousProcessFiles[tools]["analysed"]:
                if firstTool:

                    #combinedProcessFile[sample].update(samplepreviousProcessFiles[tools][sample])
                    samplesToMerge.update({sample:1})
                elif( sample in samplesToMerge):
                    samplesToMerge[sample]+=1
            firstTool=False
        
        #merge the caller results of each sample that has been analysed by all available callers
        for sample in samplesToMerge:
            if samplesToMerge[sample] == len(previousProcessFiles):
                #check the status of each sample
                if sample in processFiles["FindSV"]["ongoing"]:
                    done=common.get_slurm_job_status(int(processFiles["FindSV"]["ongoing"][sample]["pid"]))
                    processFiles=common.get_process_status(done,processFiles,"FindSV",sample)
                elif sample in processFiles["FindSV"]["failed"].keys():
                    print "sample {0} FAILED".format(sample)
                elif sample in processFiles["FindSV"]["cancelled"].keys():
                    print "sample {0} CANCELLED".format(sample)
                elif sample in processFiles["FindSV"]["timeout"].keys():
                    print "sample {0} TIMEOUT".format(sample)
                elif sample in processFiles["FindSV"]["excluded"].keys():
                    print "sample {0} EXCLUDED".format(sample)
                elif sample in processFiles["FindSV"]["analysed"].keys():
                    print "sample {0} COMPLETE".format(sample)
                else:
                    print("submitting: " + sample);
                    combinedProcessFile={}
                    tool="";
                    for tools in previousProcessFiles:
                        tool = tools
                        combinedProcessFile.update({tools:previousProcessFiles[tools]["analysed"][sample]})
                    outgoing=combineScript.submit4combination(tool,sample,combinedProcessFile,programDirectory,account,bamFilePaths[sample]);
                    processFiles["FindSV"]["ongoing"].update(outgoing)
       
        common.UpdateProcessFiles(processFiles,processed,"combine")  
        finished=1;
        return(processFiles);
