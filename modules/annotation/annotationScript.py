import os,subprocess,re,sys

#generates a database from the vcf of a sample analysed with a specified tool
def submit2Annotation(tools,sample,analysed,programDirectory,account):
    sys.path.append(os.path.join(programDirectory,"modules"))  
    import common

    samplePath=os.path.join(analysed[tools][sample]["outpath"],tools)
    path2snpEFF = os.path.join(programDirectory,"programFiles","snpEff","snpEff.jar");
    path2snpEFFconfig=os.path.join(programDirectory,"programFiles","snpEff","snpEff.config")
    reference="GRCh37.75";
    

    outpath=os.path.join(samplePath,"annotation");
    sbatch_dir,out_dir,err_dir=common.createFolder(outpath);

    with open(os.path.join(sbatch_dir, "{}.slurm".format(sample)), 'w') as sbatch:
        sbatch.write("#! /bin/bash -l\n")
        sbatch.write("#SBATCH -A {}\n".format(account))
        sbatch.write("#SBATCH -o {}/annotation_{}.out\n".format(out_dir,sample))
        sbatch.write("#SBATCH -e {}/annotation_{}.err\n".format(err_dir,sample))
        sbatch.write("#SBATCH -J annotation_{}_{}.job\n".format(sample,tools))
        sbatch.write("#SBATCH -p core\n")
        sbatch.write("#SBATCH -t 3:00:00\n")
        sbatch.write("#SBATCH -n 1 \n")

        sbatch.write("\n");
        sbatch.write("\n");

        files=analysed[tools][sample]["outputFile"]
        files=files.strip().split("\t")
        path2Input=os.path.join(samplePath,"filtered")
        FileName=[];
        for file in files:
            prefix,sufix=file.split(";");
            outsufix=".annotated.vcf"

            outfile=prefix+outsufix;
            infile=prefix+sufix;

            FileName.append(";".join([prefix,outsufix]))
            sbatch.write("java -Xmx4g -jar {0} -c {1} {2} {3} > {4}\n".format(path2snpEFF,path2snpEFFconfig,reference,os.path.join(path2Input,infile),os.path.join(outpath,outfile)) );
        
        sbatch.write("\n")
        sbatch.write("\n")


    analysed[tools][sample]["outputFile"]="\t".join(FileName)
    analysed[tools][sample]["pid"]=int(common.generateSlurmJob(sbatch_dir,sample))
    return ( {sample:analysed[tools][sample]} );