import sys, os, glob,subprocess,re

#module used to filter the cariant call files
def runScripts(analysisTool,analysedProject,analysed,programDirectory,account):
    add2Ongoing=build_DB(analysisTool,analysedProject,analysed,programDirectory,account)
    return add2Ongoing;

#tool used to build a database over all the events found by a variant call software within one project
def build_DB(analysisTool,analysedProject,analysed,programDirectory,account):
    sys.path.append(os.path.join(programDirectory,"modules"))  
    import common

    #get the project path    
    for sample in analysedProject:
        path=analysed[analysisTool]["analysed"][sample]["outpath"];
    pathToTool=os.path.join(path, analysisTool);

    #find all the features in the feature folder
    path2FeatureFolder=os.path.join(programDirectory,"feature");
    featureList="";
    for file in os.listdir(path2FeatureFolder):
        if file.endswith(".tab") or file.endswith(".bed") or file.endswith(".txt"):    
            featureList += " " + os.path.join(path2FeatureFolder,file);
    inpath=os.path.join(path,analysisTool);
    outpath=os.path.join(path,analysisTool,"filtered");
    sbatch_dir,out_dir,err_dir=common.createFolder(outpath);

    
    path2Query = os.path.join(programDirectory,"programFiles","FindTranslocations","scipts","query_db.py")
    path2Features = os.path.join(programDirectory,"programFiles","FindTranslocations","scipts","screen_results.py")
    add2Ongoing={};
    for sample in analysedProject:
        with open(os.path.join(sbatch_dir, "{0}.slurm".format(sample)), 'w') as sbatch:
            sbatch.write("#! /bin/bash -l\n")
            sbatch.write("#SBATCH -A {}\n".format(account))
            sbatch.write("#SBATCH -o {0}/filter_{1}.out\n".format(out_dir,sample))
            sbatch.write("#SBATCH -e {0}/filter_{1}.err\n".format(err_dir,sample))
            sbatch.write("#SBATCH -J filter_{0}_{1}.job\n".format(sample,analysisTool))
            sbatch.write("#SBATCH -p core\n")
            sbatch.write("#SBATCH -t 10:00:00\n")
            sbatch.write("#SBATCH -n 1 \n")
            sbatch.write("\n")
            sbatch.write("\n")
            #iterate through every analysed sample, query every vcf of the sample against every db
            filePath=os.path.join(outpath,"{0}.Query.vcf".format(sample))
            input_vcf=os.path.join(inpath,sample+".vcf")
            sbatch.write("python {0} --variations {1} --db {2} > {3}\n".format(path2Query,input_vcf, os.path.join(pathToTool,"database") ,filePath) );
            FileName="{0}.Query.vcf".format(sample)
            #add features
            sbatch.write("\n")
            if featureList != "":
                feature_vcf=os.path.join(outpath,"{0}.Feature.vcf".format(sample));
                sbatch.write("python {0} --variations {1} --bed-files {2} > {3}\n".format(path2Features, filePath , featureList ,feature_vcf) );
                sbatch.write("\n")
                FileName="{0}.Feature.vcf".format(sample)
            analysed[analysisTool]["analysed"][sample]["outputFile"]=FileName;
            sbatch.write("\n")
            sbatch.write("\n")
        
        pid = int(common.generateSlurmJob(sbatch_dir,sample))
        add2Ongoing.update({sample:{"pid":pid,"outpath":analysed[analysisTool]["analysed"][sample]["outpath"],"project":analysed[analysisTool]["analysed"][sample]["project"],"outputFile":FileName}});
    
    return (add2Ongoing);

