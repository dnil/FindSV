import os,subprocess,re,sys


def submit4combination(tools,sample,combinedProcessFile,programDirectory,account,bamFilePath):
    sys.path.append(os.path.join(programDirectory,"modules"))
    import common

    outpath=os.path.join(combinedProcessFile[tools]["outpath"],"FindSV")
    sbatch_dir,out_dir,err_dir=common.createFolder(outpath);
    RTGpath=os.path.join(programDirectory,"programFiles","RTG","rtg")
    contigSort=os.path.join(programDirectory,"programFiles","ContigSort.py")

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
        vcfPath=[];
        #sort each caller output file
        for tool in combinedProcessFile:
            files=combinedProcessFile[tool]["outputFile"]
            files=files.strip().split(";")
            
            for vcf in files:
                sortedvcf=os.path.join(combinedProcessFile[tools]["outpath"],tool,"sorted_"+vcf)
                vcf=os.path.join(combinedProcessFile[tools]["outpath"],tool,vcf)
                vcfPath.append(sortedvcf)
                sbatch.write( "vcf-sort {} > {}\n".format(vcf,sortedvcf) ) 
        #index and compress the files
        fileString=''
        for files in vcfPath:
            #clear up from previous runs
            sbatch.write( "rm {}.gz\n".format(files) )

            sbatch.write( "{} bgzip {}\n".format(RTGpath,files) )
            sbatch.write( "{} index -f vcf {}.gz\n".format(RTGpath,files) )
            fileString += files+".gz "

        #merge the files          
        output=os.path.join(outpath,sample+".vcf")
        sortedOutput=os.path.join(outpath,sample+".sorted.vcf")
        sbatch.write("{} vcfmerge -o - -F {} > {}\n".format(RTGpath,fileString,output)) 
        sbatch.write( "vcf-sort {} > {}\n".format(output,sortedOutput) )
        sbatch.write( "python {} --vcf {} --bam {} > {}\n".format(contigSort,sortedOutput,bamFilePath,sortedOutput) )
        sbatch.write( "rm {}\n".format(output) )

    pid = int(common.generateSlurmJob(sbatch_dir,sample))
    add2Ongoing={sample:{"pid":pid,"outpath":combinedProcessFile[tools]["outpath"],"project":combinedProcessFile[tools]["project"],"outputFile":sample+".sorted.vcf"} };
    
    return (add2Ongoing);
