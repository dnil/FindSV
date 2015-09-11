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

    VCFdictionary={};    
    for sample in analysedProject:
        VCFdictionary[sample]=[];
        path=analysed[analysisTool]["analysed"][sample]["outpath"];
        project=analysed[analysisTool]["analysed"][sample]["project"];
        # _ needs to be split from the FindTranslocation vcf name, thus the number of _ present in teh sample must be known
        N=sample.count('_')

    pathToTool=os.path.join(path, analysisTool);
    #find every vcf beloning to an analysed sample
    for file in os.listdir(pathToTool):
        if file.endswith(".vcf"):
            filename=file.split(".")[0];
            sample=filename       
            #join the _ belonging to the file name
            sample=sample.split("_")
            sample='_'.join(sample[0:N+1])
            
            if(sample in analysedProject):
                if(analysisTool != "fermiKit" or ( analysisTool == "fermiKit" and "sv" in file.split(".") )):
                    print("sample in analysed:" + sample);
                    VCFdictionary[sample].append([os.path.join(pathToTool,file) ,filename])

    #find all the features in the feature folder
    path2FeatureFolder=os.path.join(programDirectory,"feature");
    featureList="";
    for file in os.listdir(path2FeatureFolder):
        if file.endswith(".tab") or file.endswith(".bed") or file.endswith(".txt"):    
            featureList += " " + os.path.join(path2FeatureFolder,file);
    
    outpath=os.path.join(path,analysisTool,"filtered");
    sbatch_dir,out_dir,err_dir=common.createFolder(outpath);

    
    path2Query = os.path.join(programDirectory,"programFiles","FindTranslocations","scipts","query_db.py")
    path2Features = os.path.join(programDirectory,"programFiles","FindTranslocations","scipts","screen_results.py")
    with open(os.path.join(sbatch_dir, "{0}.slurm".format(project)), 'w') as sbatch:
		
        sbatch.write("#! /bin/bash -l\n")
        sbatch.write("#SBATCH -A {}\n".format(account))
        sbatch.write("#SBATCH -o {0}/filter_{1}.out\n".format(out_dir,project))
        sbatch.write("#SBATCH -e {0}/filter_{1}.err\n".format(err_dir,project))
        sbatch.write("#SBATCH -J filter_{0}_{1}.job\n".format(project,analysisTool))
        sbatch.write("#SBATCH -p core\n")
        sbatch.write("#SBATCH -t 2-00:00:00\n")
        sbatch.write("#SBATCH -n 1 \n")
        sbatch.write("\n")
        sbatch.write("\n")
        #iterate through every analysed sample, query every vcf of the sample against every db
        for sample in analysedProject:
            FileName=[]
            i=0;
            for vcf in VCFdictionary[sample]:
                FileName.append("");
                filePath=os.path.join(outpath,"{0}.Query.vcf".format(vcf[1]))
                sbatch.write("python {0} --variations {1} --db {2} > {3}\n".format(path2Query,vcf[0] , os.path.join(pathToTool,"database") ,filePath) );
                FileName[i]="{0};.Query.vcf".format(vcf[1])
                #add features
                sbatch.write("\n")
                if featureList != "":
                    feature_vcf=os.path.join(outpath,"{0}.Feature.vcf".format(vcf[1]));
                    sbatch.write("python {0} --variations {1} --bed-files {2} > {3}\n".format(path2Features, filePath , featureList ,feature_vcf) );
                    sbatch.write("\n")
                    FileName[i]="{0};.Feature.vcf".format(vcf[1])
                i=i+1
            analysed[analysisTool]["analysed"][sample]["outputFile"]="\t".join(FileName);
        sbatch.write("\n")
        sbatch.write("\n")


    add2Ongoing={};
    pid = int(common.generateSlurmJob(sbatch_dir,project))
    for sample in analysedProject:
        add2Ongoing.update({sample:{"pid":pid,"outpath":analysed[analysisTool]["analysed"][sample]["outpath"],"project":analysed[analysisTool]["analysed"][sample]["project"],"outputFile":analysed[analysisTool]["analysed"][sample]["outputFile"]}});
    
    return (add2Ongoing);

