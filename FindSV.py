import sys, os, glob
import subprocess
import shlex
import argparse
import re
import time
import scripts


def main(args):
    analysis = args.analysis
    processed = args.processed
    projectToProcess = args.project    

    analysed = {}
    ongoing   = {}
    with open(os.path.join(processed, "analysed")) as analysed_fd:
        for sample in analysed_fd:
            sample = sample.rstrip()
            analysed[sample] = ""
    with open(os.path.join(processed, "ongoing")) as ongoing_fd:
        for sample in ongoing_fd:
            if(sample[0] != "\n"):
               sample, pid = sample.rstrip().split()
               ongoing[sample] = pid
    
    ##now check all samples
    exclude = {}
    exclude["P1366_fail"]      = ""
    exclude["P1366_new"]       = ""
    exclude["P1366_node"]      = ""
    exclude["P1366_old"]       = ""
    exclude["P1426_previous"]  = ""
    exclude["P1553_old_run"]   = ""
    exclude["P1775_old_plu"]   = ""
    exclude["P1775_test"]      = ""

   # working_dir = "/proj/a2014205/nobackup/vezzi/FindTranslocations"
    working_dir = "/proj/b2014152/nobackup/jesperei/cnvnator"
    for project_name  in os.listdir(analysis):
        if not project_name.startswith('.') and project_name not in exclude.keys() and not os.path.islink(os.path.join(analysis, project_name)):
#            if project_name != "P1553":
#                continue
            if projectToProcess is not None and projectToProcess != project_name:
                continue
            local_project_dir = os.path.join(working_dir, project_name)
            if not os.path.isdir(local_project_dir):
                os.makedirs(local_project_dir)

            path_to_project  = os.path.join(analysis, project_name)
            path_to_analysis = os.path.join(path_to_project, "piper_ngi")

            if os.path.exists(path_to_analysis) and os.path.exists(os.path.join(path_to_analysis, "05_processed_alignments")):
                path_to_bam = os.path.join(path_to_analysis, "05_processed_alignments")
                for file in os.listdir(os.path.join(path_to_analysis, "05_processed_alignments")):
                    print(file);
                    if file.endswith(".bam"):
                        sample_name = file.split(".")[0]
                        print sample_name            
                        if sample_name in analysed.keys():
                            # sample state is ANALYSED
                            print "sample {0} ANALYSED".format(sample_name)
                        elif sample_name in ongoing.keys():
                            # sample state is UNDER_ANALYSIS
                            done = check_if_sample_is_done(sample_name, ongoing[sample_name]) # check if it is still running in that case delete it from ongoing and add to analysed
                            if done == 0:
                                del ongoing[sample_name]
                                analysed[sample_name] = ""
                                print "sample {0} DONE".format(sample_name)
                            else:
                                print "sample {0} RUNNING".format(sample_name)
                        else:
                            # sample state is NEW
                            pid = submit_sample(local_project_dir, sample_name, os.path.join(path_to_bam, file)) # submit this sample, if submission works fine store it in under analysis with the PID 
                            ongoing[sample_name] = pid
                            print "sample {0} LAUNCHED".format(sample_name)
                            #time.sleep(300)

    #write ongoing to file (rewrite it)
    with open(os.path.join(processed, "analysed"), 'w') as analysed_fd:
        for sample, empty in analysed.items():
            analysed_fd.write("{0}\n".format(sample))

    #write analyse to file (rewrite it)
    with open(os.path.join(processed, "ongoing"), 'w') as ongoing_fd:
        for sample, pid in ongoing.items():
            ongoing_fd.write("{0} {1}\n".format(sample, pid))

    return


def check_if_sample_is_done(sample_name, pid):
    return get_slurm_job_status(int(pid))    



SLURM_EXIT_CODES = {"PENDING": 1,
                    "RUNNING": 1,
                    "RESIZING": 1,
                    "SUSPENDED": 1,
                    "COMPLETED": 0,
                    "CANCELLED": 0,
                    "FAILED": 0,
                    "TIMEOUT": 0,
                    "PREEMPTED": 0,
                    "BOOT_FAIL": 0,
                    "NODE_FAIL": 0,
                    }


def get_slurm_job_status(slurm_job_id):
    """Gets the State of a SLURM job and returns it as an integer (or None).
    :param int slurm_job_id: An integer of your choosing
    :returns: The status of the job (None == Queued/Running, 0 == Success, 1 == Failure)
    :rtype: None or int
    :raises TypeError: If the input is not/cannot be converted to an int
    :raises ValueError: If the slurm job ID is not found
    :raises RuntimeError: If the slurm job status is not understood
    """
    try:
        print("sacct -n -j {0} -o STATE".format(slurm_job_id))
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
    print 'Checking slurm job status with cl "{0}"...'.format(check_cl)
    job_status = subprocess.check_output(shlex.split(check_cl))
    print 'job status for job {0} is "{1}"'.format(slurm_job_id, job_status.strip())
    if not job_status:
        raise ValueError("No such slurm job found: {0}".format(slurm_job_id))
    else:
        try:
            return SLURM_EXIT_CODES[job_status.split()[0].strip("+")]
        except (IndexError, KeyError, TypeError) as e:
            raise RuntimeError("SLURM job status not understood: {0}".format(job_status))


if __name__ == '__main__':
    parser = argparse.ArgumentParser("""This scripts checks the analysis folder of the NGI_pipeline
    and for each new BAM file it runs cnvnator
   """)
    parser.add_argument('--analysis', type=str, required=True, help="analysis location")
    parser.add_argument('--processed', type=str, required=True, help="Folder containing two file analysed and ongoing containing samples name of samples analsyed or under analysis")
    parser.add_argument('--project', type=str, required=False, default=None, help="restrict analysis to the specified project")
    args = parser.parse_args()

    main(args)
