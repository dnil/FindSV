import os,subprocess,re,sys


def submit4combination(tools,sample,combinedProcessFile,programDirectory,account,bamFilePath):
    sys.path.append(os.path.join(programDirectory,"modules"))
    import common

    outpath=os.path.join(combinedProcessFile[tools]["outpath"],"FindSV")
    sbatch_dir,out_dir,err_dir=common.createFolder(outpath);
    mergepath=os.path.join(programDirectory,"programFiles","mergeVCF.py")
    contigSort=os.path.join(programDirectory,"programFiles","contigSort.py")

    with open(os.path.join(sbatch_dir, "{}.slurm".format(sample)), 'w') as sbatch:
        sbatch.write("#! /bin/bash -l\n")
        sbatch.write("#SBATCH -A {}\n".format(account))
        sbatch.write("#SBATCH -o {}/combine_{}.out\n".format(out_dir,sample))
        sbatch.write("#SBATCH -e {}/combine_{}.err\n".format(err_dir,sample))
        sbatch.write("#SBATCH -J combine_{}_{}.job\n".format(sample,"FindSV"))
        sbatch.write("#SBATCH -p core\n")
        sbatch.write("#SBATCH -t 5:00:00\n")
        sbatch.write("#SBATCH -n 1 \n")

        sbatch.write("\n");
        sbatch.write("\n");
        sbatch.write("module load bioinfo-tools\n");
        sbatch.write("module load vcftools\n");
        sbatch.write("module load samtools\n");
        vcfPath=[];
        #sort each caller output file
        fileString=''
        for tool in combinedProcessFile:
            files=combinedProcessFile[tool]["outputFile"]
            files=files.strip().split(";")
            for vcf in files:
                vcf=os.path.join(combinedProcessFile[tools]["outpath"],tool,vcf)
                fileString += vcf + " "

        #merge the files          
        output=os.path.join(outpath,sample+".vcf")
        sortedOutput=os.path.join(outpath,sample+".merged.vcf")
        sbatch.write("python {} --vcf {} > {}\n".format(mergepath,fileString,sortedOutput)) 
        sbatch.write( "python {} --vcf {} --bam {} > {}\n".format(contigSort,sortedOutput,bamFilePath,output) )
        sbatch.write( "rm {}\n".format(sortedOutput) )
    pid = int(common.generateSlurmJob(sbatch_dir,sample))
    add2Ongoing={sample:{"pid":pid,"outpath":combinedProcessFile[tools]["outpath"],"project":combinedProcessFile[tools]["project"],"outputFile":sample+".vcf"} };
    
    return (add2Ongoing);
