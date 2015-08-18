import os,subprocess,re

#this function submits the slurmjob generated by one of the tool scripts
def generateSlurmJob(sbatch_dir,sample_name):
    process = "sbatch {0}".format(os.path.join(sbatch_dir, "DB_{0}.slurm").format(sample_name))
    p_handle = subprocess.Popen(process, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)    
    p_out, p_err = p_handle.communicate()
    try:
        return( re.match(r'Submitted batch job (\d+)', p_out).groups()[0] );
    except AttributeError:
        raise RuntimeError('Could not submit sbatch')



#generates a database from the vcf of a sample analysed with a specified tool
def submit2DB(newsamples,tools,sample,programDirectory,processed,account):
    fileExtensions={"fermiKit":[".sv.vcf"],"CNVnator":[".vcf"],"FindTranslocations":["_inter_chr_events.vcf","_intra_chr_events.vcf"]}

    samplePath=os.path.join(newsamples[tools][sample]["outpath"],tools)
    path2Build = os.path.join(programDirectory,"programFiles","FindTranslocations","scipts","build_db.py");

    sbatch_dir = os.path.join(samplePath, "sbatch")
    out_dir    = os.path.join(samplePath, "sbatch_out")
    err_dir    = os.path.join(samplePath, "sbatch_err")

    fileString=""
    for file in fileExtensions[tools]:
        fileString += " " + os.path.join(samplePath,sample+file)

    with open(os.path.join(sbatch_dir, "DB_{}.slurm".format(sample)), 'w') as sbatch:
        sbatch.write("#! /bin/bash -l\n")
        sbatch.write("#SBATCH -A {}\n".format(account))
        sbatch.write("#SBATCH -o {}/DB_{}.out\n".format(out_dir,sample))
        sbatch.write("#SBATCH -e {}/DB_{}.err\n".format(err_dir,sample))
        sbatch.write("#SBATCH -J DB_{}_{}.job\n".format(sample,tools))
        sbatch.write("#SBATCH -p core\n")
        sbatch.write("#SBATCH -t 1:00:00\n")
        sbatch.write("#SBATCH -n 1 \n")

        sbatch.write("\n");
        sbatch.write("\n");
        DBpath=os.path.join(samplePath,sample+".db")
        sbatch.write("python {0} --variations {1} --tollerance  1000 > {2}\n".format(path2Build,fileString,DBpath) );

        sbatch.write("\n")
        sbatch.write("\n")

    return ( int(generateSlurmJob(sbatch_dir,sample)) );

