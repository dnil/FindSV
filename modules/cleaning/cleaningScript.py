import os,subprocess,re,sys

#generates a database from the vcf of a sample analysed with a specified tool
def submit2Cleaning(tools,sample,analysed,programDirectory,account):
    sys.path.append(os.path.join(programDirectory,"modules"))  
    import common
    samplePath=os.path.join(analysed[tools]["analysed"][sample]["outpath"],tools)

    outpath=os.path.join(samplePath,"cleaning");
    sbatch_dir,out_dir,err_dir=common.createFolder(outpath);

    with open(os.path.join(sbatch_dir, "{}.slurm".format(sample)), 'w') as sbatch:
        sbatch.write("#! /bin/bash -l\n")
        sbatch.write("#SBATCH -A {}\n".format(account))
        sbatch.write("#SBATCH -o {}/cleaning_{}.out\n".format(out_dir,sample))
        sbatch.write("#SBATCH -e {}/cleaning_{}.err\n".format(err_dir,sample))
        sbatch.write("#SBATCH -J cleaning_{}_{}.job\n".format(sample,tools))
        sbatch.write("#SBATCH -p core\n")
        sbatch.write("#SBATCH -t 1:00:00\n")
        sbatch.write("#SBATCH -n 1 \n")

        sbatch.write("\n");
        sbatch.write("\n");
        sbatch.write("module load bioinfo-tools\n")
        sbatch.write("module load vcftools\n")

        files=analysed[tools]["analysed"][sample]["outputFile"]
        files=files.strip().split(";")
        path2Input=os.path.join(samplePath,"annotation")
        FileName=[];

        for file in files:
            infile=file;
            outsufix=".cleaned.vcf"
            prefix=file.rsplit(".",1)[0]
            outfile=prefix+outsufix;

            FileName.append(outfile)
            sbatch.write("vcftools --recode --recode-INFO-all --remove-filtered-all --vcf {0} --stdout > {1} \n".format(infile,outfile))

        sbatch.write("\n")
        sbatch.write("\n")


    analysed[tools]["analysed"][sample]["outputFile"]=";".join(FileName)
    analysed[tools]["analysed"][sample]["pid"]=int(common.generateSlurmJob(sbatch_dir,sample))
    return ( {sample:analysed[tools]["analysed"][sample]} );
