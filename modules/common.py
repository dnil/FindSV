import sys, os, glob,re
import subprocess
import shlex


#this function is used to create a folder to keep the output of each tool
def createFolder(local_dir):
    sbatch_dir = os.path.join(local_dir, "sbatch")
    out_dir    = os.path.join(local_dir, "sbatch_out")
    err_dir    = os.path.join(local_dir, "sbatch_err")

    if not os.path.isdir(sbatch_dir):
        os.makedirs(sbatch_dir)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    if not os.path.isdir(err_dir):
        os.makedirs(err_dir)
    return(sbatch_dir,out_dir,err_dir);
#this function submits the slurmjob generated by one of the tool scripts
def generateSlurmJob(sbatch_dir,sample_name):
    process = "sbatch {0}".format(os.path.join(sbatch_dir, "{0}.slurm").format(sample_name))
    p_handle = subprocess.Popen(process, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)    
    p_out, p_err = p_handle.communicate()
    #try:
    return( re.match(r'Submitted batch job (\d+)', p_out).groups()[0] );
    #except AttributeError:
     #   raise RuntimeError('Could not submit sbatch')

#read the ongoing or analysis files or create empty files
def readProcessFiles(analysed,processed,step):
    finished={}
    ongoing={};
    #look for the files used to keep track of the processing, if the files exists, read them. If not, create empty files
    processFiles={}
    Files=["ongoing","analysed","failed","timeout","cancelled","excluded"]
    for tool in analysed:
        processFiles.update({ tool:{} })
        for file in Files:
            processFiles[tool].update({file:{}})
        pathToVariantFiles=os.path.join(processed,tool,step);
        
        if not (os.path.exists(pathToVariantFiles)):
            os.makedirs(os.path.join(pathToVariantFiles))
            for file in Files:
                open(os.path.join(pathToVariantFiles,file), 'a').close()
        else:
            for file in Files:
                pathToProcessFile=os.path.join(pathToVariantFiles,file);
                if not (os.path.exists(pathToProcessFile)):
                    open(pathToProcessFile, 'a').close()

        for file in processFiles[tool]:
            with open(os.path.join(pathToVariantFiles, file)) as analysed_fd:
                for sample in analysed_fd:

                    row = sample.rstrip().split()
                    sample=row[0];
                    pid=row[1]
                    project=row[2]
                    outpath=row[3]
                    if len(row) == 4:
                        processFiles[tool][file][sample] = {"pid":pid,"project":project,"outpath":outpath}
                    else:
                        outputFile=row[4]
                        processFiles[tool][file][sample] = {"pid":pid,"project":project,"outpath":outpath,"outputFile":outputFile}

    return(processFiles)

#update the ongoing and analysesd files
def UpdateProcessFiles(processFiles,processed,step):

    #update the process files and return the finished dictionary
    for tools in processFiles:
        for file in processFiles[tools]:
            pathToVariantFiles=os.path.join(processed,tools,step);
            with open(os.path.join(pathToVariantFiles, file), 'w') as analysed_fd:
                for sample, dictionary in processFiles[tools][file].items():
                        pid=dictionary["pid"]
                        projectName=dictionary["project"]
                        outPath=dictionary["outpath"]
                        if not "outputFile" in dictionary: 
                            analysed_fd.write("{0} {1} {2} {3}\n".format(sample,pid ,projectName,outPath))
                        else:
                            outputFile=dictionary["outputFile"]
                            analysed_fd.write("{0} {1} {2} {3} {4}\n".format(sample,pid ,projectName,outPath,outputFile))

#get the status of the slurm jobs
def get_slurm_job_status(slurm_job_id):
    """Gets the State of a SLURM job and returns it as an integer (or None).
    :param int slurm_job_id: An integer of your choosing
    :returns: The status of the job (None == Queued/Running, 0 == Success, 1 == Failure)
    :rtype: None or int
    :raises TypeError: If the input is not/cannot be converted to an int
    :raises ValueError: If the slurm job ID is not found
    :raises RuntimeError: If the slurm job status is not understood
    """

    SLURM_EXIT_CODES = {"PENDING": 1,
                        "RUNNING": 1,
                        "RESIZING": 1,
                        "SUSPENDED": 1,
                        "COMPLETED": 2,
                        "CANCELLED": 3,
                        "FAILED": 0,
                        "TIMEOUT": 4,
                        "PREEMPTED": 0,
                        "BOOT_FAIL": 0,
                        "NODE_FAIL": 0,
                        }

    try:
        check_cl = "sacct -n -j {0} -o STATE".format(slurm_job_id)
        # If the sbatch job has finished, this returns two lines. For example:
        # $ sacct -j 3655032
        #       JobID    JobName  Partition    Account  AllocCPUS      State ExitCode 
        #       ------------ ---------- ---------- ---------- ---------- ---------- -------- 
        #       3655032      test_sbat+       core   a2010002          1  COMPLETED      0:0 
        #       3655032.bat+      batch              a2010002          1  COMPLETED      0:0 
        #
        # In this case I think we want the first one but I'm actually still not
        # totally clear on this point -- the latter may be the return code of the
        # actual sbatch command for the bash interpreter? Unclear.
    except ValueError:
        raise TypeError("SLURM Job ID not an integer: {0}".format(slurm_job_id))
    job_status = subprocess.check_output(shlex.split(check_cl))
    print 'job status for job {0} is "{1}"'.format(slurm_job_id, job_status.strip().split()[0])
    if not job_status:
        raise ValueError("No such slurm job found: {0}".format(slurm_job_id))
    else:
        try:
            return SLURM_EXIT_CODES[job_status.split()[0].strip("+")]
        except (IndexError, KeyError, TypeError) as e:
            print("SLURM job status not understood: {0}".format(job_status))

#this process checks the status of an ongoing job and updates its status in the processFile dictionary
def get_process_status(done,processFile,tools,sample_name):

    if done == 1: 
        print "sample {0} ONGOING".format(sample_name)

    elif done == 2:
        processFile[tools]["analysed"][sample_name] = processFile[tools]["ongoing"][sample_name]
        del processFile[tools]["ongoing"][sample_name]                    
        print "sample {0} DONE".format(sample_name)

    elif done == 3:
        processFile[tools]["cancelled"][sample_name] = processFile[tools]["ongoing"][sample_name]
        del processFile[tools]["ongoing"][sample_name]      
        print "sample {0} CANCELLED".format(sample_name)

    elif done == 4:
        processFile[tools]["timeout"][sample_name] = processFile[tools]["ongoing"][sample_name]
        del processFile[tools]["ongoing"][sample_name]      
        print "sample {0} OUTOFTIME".format(sample_name)

    else:
        processFile[tools]["failed"][sample_name] = processFile[tools]["ongoing"][sample_name]
        del processFile[tools]["ongoing"][sample_name]      
        print "sample {0} FAILED".format(sample_name)

    return(processFile);
    

