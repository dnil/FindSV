import os,subprocess,re,sys

#generates a database from the vcf of a sample analysed with a specified tool
def submit2Annotation(tools,sample,analysed,programDirectory,account):
    sys.path.append(os.path.join(programDirectory,"modules"))  
    import common
    samplePath=os.path.join(analysed[tools]["analysed"][sample]["outpath"],tools)
    path2snpEFF = os.path.join(programDirectory,"programFiles","ensembl-tools-release-81","scripts","variant_effect_predictor","variant_effect_predictor.pl");
    reference="GRCh37.75";

    outpath=os.path.join(samplePath,"annotation");
    sbatch_dir,out_dir,err_dir=common.createFolder(outpath);


    #check for a genmod file in the genmod folder
    path2GenmodFolder=os.path.join(programDirectory,"genmod");
    genmod="";
    for file in os.listdir(path2GenmodFolder):
        if file.endswith(".ini") or file.endswith(".txt"):    
            genmod = os.path.join(path2GenmodFolder,file)



    with open(os.path.join(sbatch_dir, "{}.slurm".format(sample)), 'w') as sbatch:
        sbatch.write("#! /bin/bash -l\n")
        sbatch.write("#SBATCH -A {}\n".format(account))
        sbatch.write("#SBATCH -o {}/annotation_{}.out\n".format(out_dir,sample))
        sbatch.write("#SBATCH -e {}/annotation_{}.err\n".format(err_dir,sample))
        sbatch.write("#SBATCH -J annotation_{}_{}.job\n".format(sample,tools))
        sbatch.write("#SBATCH -p core\n")
        sbatch.write("#SBATCH -t 10:00:00\n")
        sbatch.write("#SBATCH -n 1 \n")

        sbatch.write("\n");
        sbatch.write("\n");

        files=analysed[tools]["analysed"][sample]["outputFile"]
        files=files.strip().split(";")
        path2Input=os.path.join(samplePath,"filtered")
        FileName=[];

        for file in files:
            infile=file;
            outsufix=".annotated.vcf"
            prefix=file.rsplit(".",1)[0]
            outfile=prefix+outsufix;

            FileName.append(outfile)
            sbatch.write("perl {0} --cache --force_overwrite --poly b -i {1} -o {2} --buffer_size 5 --port 3337 --vcf --whole_genome  --format vcf -q\n"
            .format( path2snpEFF , os.path.join(path2Input,infile) , os.path.join(outpath,outfile )))

            #generate genmod
            if genmod != "":
                sbatch.write("genmod score -c {0} {1} > {1}.tmp\n".format(genmod, os.path.join(outpath,outfile ) ) );
                sbatch.write("mv {0}.tmp {0}\n".format( os.path.join(outpath,outfile ) ) );

        sbatch.write("\n")
        sbatch.write("\n")


    analysed[tools]["analysed"][sample]["outputFile"]=";".join(FileName)
    analysed[tools]["analysed"][sample]["pid"]=int(common.generateSlurmJob(sbatch_dir,sample))
    return ( {sample:analysed[tools]["analysed"][sample]} );
