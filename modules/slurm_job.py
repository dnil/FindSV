import subprocess
import shlex

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

