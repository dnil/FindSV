import sys, os, glob, time
sys.path.append("modules/annotation")
import common
import annotationScript

#function used to annotate the filtered variants
def annotation(programDirectory,filtered,processed,account):
       
        #read the process files
        analysed,ongoing=common.readProcessFiles(filtered,processed,"annotation")
        for tools in filtered: 
             print("annotation: "+tools);
            for sample in filtered[tools]:
                if sample in ongoing[tools]:
                    #check the status of the ongoing sample;
                    done=common.get_slurm_job_status(int(ongoing[tools][sample]["pid"])) 
                    if done == 0:
                        analysed[tools][sample] = ongoing[tools][sample];
                        del ongoing[tools][sample]                                        
                        print "sample {0} DONE".format(sample)
                    else:
                        print "sample {0} ONGOING".format(sample)

                    print("ongoing: " + sample);
                elif sample in analysed[tools]:
                    print("analysed: " + sample);
                else:
                    print("submitting: " + sample);
                    outgoing=annotationScript.submit2Annotation(tools,sample,filtered,programDirectory,account);
                    ongoing[tools].update(outgoing)
                                    

        common.UpdateProcessFiles(analysed,ongoing,processed,"annotation")  
        finished=1;
        return(analysed);
