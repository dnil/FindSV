import sys, os, glob,subprocess,re


#this function is used to create a folder to keep the output of each tool
def createFolder(local_dir):
    sbatch_dir = os.path.join(local_dir, "sbatch")
    out_dir    = os.path.join(local_dir, "sbatch_out")
    err_dir    = os.path.join(local_dir, "sbatch_err")

    if not os.path.isdir(sbatch_dir):
        os.makedirs(sbatch_dir)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    if not os.path.isdir(err_dir):
        os.makedirs(err_dir)
    return(sbatch_dir,out_dir,err_dir);
#this function submits the slurmjob generated by one of the tool scripts
def generateSlurmJob(sbatch_dir,sample_name):
    process = "sbatch {0}".format(os.path.join(sbatch_dir, "{0}.slurm").format(sample_name))
    p_handle = subprocess.Popen(process, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)    
    p_out, p_err = p_handle.communicate()
    try:
        return( re.match(r'Submitted batch job (\d+)', p_out).groups()[0] );
    except AttributeError:
        raise RuntimeError('Could not submit sbatch')


#module used to filter the cariant call files
def runScripts(analysisTool,tool,analysedProject,analysed,programDirectory,account):  
        add2Ongoing={};

        call=tool+"(analysisTool,tool,analysedProject,analysed,programDirectory,account)"
        pid=eval(call);      

        for sample in analysedProject:
                        add2Ongoing.update({sample:{"pid":pid,"outpath":analysed[analysisTool][sample]["outpath"],"project":analysed[analysisTool][sample]["project"]}});
	return add2Ongoing;

#tool used to build a database over all the events found by a variant call software within one project
def build_DB(analysisTool,tool,analysedProject,analysed,programDirectory,account):
     #get the project path  

    VCFdictionary={};    
    for sample in analysedProject:
        VCFdictionary[sample]=[];
        path=analysed[analysisTool][sample]["outpath"];
        project=analysed[analysisTool][sample]["project"];
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
                print("sample in analysed:" + sample);
                VCFdictionary[sample].append([os.path.join(pathToTool,file) ,filename])

    #find all the features in the feature folder
    path2FeatureFolder=os.path.join(programDirectory,"feature");
    featureList="";
    for file in os.listdir(path2FeatureFolder):
        if file.endswith(".tab") or file.endswith(".bed") or file.endswith(".txt"):    
            featureList += " " + os.path.join(path2FeatureFolder,file);
    
    outpath=os.path.join(path,analysisTool,"filtered");
    sbatch_dir,out_dir,err_dir=createFolder(outpath);

    
    path2Query = os.path.join(programDirectory,"programFiles","FindTranslocations","scipts","query_db.py")
    path2Features = os.path.join(programDirectory,"programFiles","FindTranslocations","scipts","screen_results.py")
    with open(os.path.join(sbatch_dir, "{0}.slurm".format(project)), 'w') as sbatch:
		
        sbatch.write("#! /bin/bash -l\n")
        sbatch.write("#SBATCH -A {}\n".format(account))
        sbatch.write("#SBATCH -o {0}/buildDB_{1}.out\n".format(out_dir,project))
        sbatch.write("#SBATCH -e {0}/buildDB_{1}.err\n".format(err_dir,project))
        sbatch.write("#SBATCH -J buildDB_{0}_{1}.job\n".format(project,analysisTool))
        sbatch.write("#SBATCH -p core\n")
        sbatch.write("#SBATCH -t 5:00:00\n")
        sbatch.write("#SBATCH -n 1 \n")
        sbatch.write("\n")
        sbatch.write("\n")
        #iterate through every analysed sample, query every vcf of the sample against every db
        for sample in analysedProject:
            for vcf in VCFdictionary[sample]:
                filePath=os.path.join(outpath,"{0}.Query.vcf".format(vcf[1]))
                sbatch.write("python {0} --variations {1} --db {2} > {3}\n".format(path2Query,vcf[0] , pathToTool ,filePath) );
                #add features
                sbatch.write("\n")
                feature_vcf=os.path.join(outpath,"{0}.Feature.vcf".format(vcf[1]));
                sbatch.write("python {0} --variations {1} --bed-files {2} > {3}\n".format(path2Features, filePath , featureList ,feature_vcf) );
                sbatch.write("\n")
        sbatch.write("\n")
        sbatch.write("\n")


            


    return ( int(generateSlurmJob(sbatch_dir,project)) );

