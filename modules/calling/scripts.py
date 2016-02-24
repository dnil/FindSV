import os
import subprocess
import re
import sys

#This module contains all the variant calling tools available to the
#pipeline, scripts may be added or removed as needed. Every tool
#should be stored in a separate function. The function arguments are
#the programDirectory, which is the path to FindSV. local_dir, which
#is the output folder of the main script, the sample_name, which is
#the name of the sample, and the bam_file which is the path to the bam
#file and lastly account, which is the slurm account as well as
#modules, a boolean indicating if the SNIC module system and SNIC_TMP
#should be used. Each function must output a list containing the
#slurm_job ID and the name of the output vcf The concent of each
#function is a printer of an sbatch file, the sbatch file is printed
#to the output folder and started using slurm.

#This function is used to search the reference file for the path of the references.
def references(programDirectory,reference):
	#open the config file to read through the settings
	with open(os.path.join(programDirectory,"references.txt")) as ongoing_fd:
		for line in ongoing_fd:
			reference_type = line.rstrip().split()[0];
			reference_type=reference_type.split("=");
			if(reference_type[0] == reference):
				referencePath=reference_type[1];

	return(referencePath);

#the function used to run CNVnator
def CNVnator(programDirectory,local_dir, sample_name, bam_file,account,modules):
    sys.path.append(os.path.join(programDirectory,"modules"))  
    import common

    #samplePath=os.path.join(analysed[tools]["analysed"][sample]["outpath"],tools)
    path_dict={}
    with open(os.path.join(programDirectory,"path.txt")) as path_file:
        for line in path_file:
            if not line.startswith("#") and not line == "\n":
                content=line.strip().split("=")
                path_dict[content[0]]=content[1]
    cnvnator_path="cnvnator"
    cnvnator2vcf_path="cnvnator2VCF.pl"
    if path_dict["CNVnator"]:
        cnvnator_path=path_dict["CNVnator"]
    if path_dict["cnvnator2VCF"]:
        cnvnator2vcf_path=path_dict["cnvnator2VCF"]
    

    #path to the folder were the reference chromosomes are stored
    sbatch_dir,out_dir,err_dir=common.createFolder(local_dir);
    chrFolder=references(programDirectory,"chromosomes");

    output_header = os.path.join(local_dir, sample_name)
    print( "{0}.slurm".format(sample_name));
    print(os.path.join(sbatch_dir, "{0}.slurm".format(sample_name)));
    with open(os.path.join(sbatch_dir, "{0}.slurm".format(sample_name)), 'w') as sbatch:
		
        sbatch.write("#! /bin/bash -l\n")
        sbatch.write("#SBATCH -A {}\n".format(account))
        sbatch.write("#SBATCH -o {0}/CNVnator_{1}.out\n".format(out_dir,sample_name))
        sbatch.write("#SBATCH -e {0}/CNVnator_{1}.err\n".format(err_dir,sample_name))
        sbatch.write("#SBATCH -J CNVnator_{0}.job\n".format(sample_name))
        sbatch.write("#SBATCH -p core\n")
        sbatch.write("#SBATCH -t 2-00:00:00\n")
        sbatch.write("#SBATCH -n 1 \n")

        sbatch.write("\n");
        sbatch.write("\n");

        # If we are on a machine with the SNIC modules installed
        if(modules == "True"):
            sbatch.write("module load bioinfo-tools\n")
            sbatch.write("module load bwa\n")
            sbatch.write("module load samtools\n")
            sbatch.write("module load CNVnator\n")

        sbatch.write("\n")
        sbatch.write("\n")
        if (path_dict["ROOTSYS"]):
            sbatch.write("export ROOTSYS= {}\n".format(path_dict["ROOTSYS"]))
            sbatch.write("export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ROOTSYS/lib\n")
               
	    # If we are on a non-SNIC system, chances are there is no 
        # SNIC_TMP var set. TMP_DIR is more universal, or fall back
        # to /tmp. 
        sbatch.write("if [[ -z $SNIC_TMP ]] ; then if [[ -z $TMPDIR ]] ; then SNIC_TMP=/tmp ; else SNIC_TMP=$TMPDIR ; fi ; fi\n")

        # now transfer the bam file

        sbatch.write("mkdir -p $SNIC_TMP/{0}\n".format(sample_name))
        sbatch.write("rsync -rptoDLv {0} $SNIC_TMP/{1}\n".format(bam_file, sample_name))
        #sbatch.write("rsync -rptoDLv {0} $SNIC_TMP/{1}\n".format(bai_file, sample_name))
       	
        sbatch.write("{0} -root {1}.root -tree $SNIC_TMP/{2}/{3} \n".format(cnvnator_path,output_header,sample_name, os.path.split(bam_file)[1]) );
        sbatch.write("{0} -root {1}.root -his 1000 -d {2}\n".format(cnvnator_path,output_header,chrFolder));
        sbatch.write("{0} -root {1}.root -stat 1000 >> {2}.cnvnator.log \n".format(cnvnator_path,output_header,output_header));
        sbatch.write("{0} -root {1}.root -partition 1000 \n".format(cnvnator_path,output_header))
        sbatch.write("{0} -root {1}.root -call 1000 > {2}.cnvnator.out \n".format(cnvnator_path,output_header,output_header));
        sbatch.write("{0} {1}.cnvnator.out  >  {2}.vcf \n".format(cnvnator2vcf_path,output_header,output_header));
        sbatch.write("rm {0}.root\n".format(output_header));
        sbatch.write("rm $SNIC_TMP/{0}/*".format(sample_name));
        sbatch.write("\n")
        sbatch.write("\n")

    return ([ int(common.generateSlurmJob(sbatch_dir,sample_name)), "{}.vcf".format(sample_name) ] );

#the function used to run FindTranslocations
def FindTranslocations(programDirectory,local_dir, sample_name, bam_file,account,modules):
    sys.path.append(os.path.join(programDirectory,"modules"))  
    import common
    #build the sbatch file and submit it
    sbatch_dir,out_dir,err_dir=common.createFolder(local_dir);
    output_header = os.path.join(local_dir, sample_name)
    bai_file      = re.sub('m$', 'i', bam_file) # remove the final m and add and i
    if not (os.path.isfile(bai_file)):
        bai_file=bam_file+".bai";

    path_dict={}
    with open(os.path.join(programDirectory,"path.txt")) as path_file:
        for line in path_file:
            if not line.startswith("#") and not line == "\n":
                content=line.strip().split("=")
                print content
                path_dict[content[0]]=content[1]
    FT_path="{0}/programFiles/FindTranslocations/bin/FindTranslocations".format(programDirectory)
    if path_dict["FindTranslocations"]:
        FT_path=path_dict["FindTranslocations"]



    with open(os.path.join(sbatch_dir, "{}.slurm".format(sample_name)), 'w') as sbatch:
        sbatch.write("#! /bin/bash -l\n")
        sbatch.write("#SBATCH -A {}\n".format(account))
        sbatch.write("#SBATCH -o {}/FT_{}.out\n".format(out_dir,sample_name))
        sbatch.write("#SBATCH -e {}/FT_{}.err\n".format(err_dir,sample_name))
        sbatch.write("#SBATCH -J FT_{}.job\n".format(sample_name))
        sbatch.write("#SBATCH -p core\n")
        sbatch.write("#SBATCH -t 2-00:00:00\n")
        sbatch.write("#SBATCH -n 1 \n")

        sbatch.write("\n");
        sbatch.write("\n");
        
        sbatch.write("FINDTRANS={0}".format(FT_path))
        sbatch.write("\n")
        sbatch.write("\n")

    	# If we are on a non-SNIC system, chances are there is no 
    	# SNIC_TMP var set. TMP_DIR is more universal, or fall back
    	# to /tmp. 
        sbatch.write("if [[ -z $SNIC_TMP ]] ; then if [[ -z $TMPDIR ]] ; then SNIC_TMP=/tmp ; else SNIC_TMP=$TMPDIR ; fi ; fi\n")


        #now tranfer the bam file   
        sbatch.write("mkdir -p $SNIC_TMP/{}\n".format(sample_name))
        sbatch.write("rsync -rptoDLv {} $SNIC_TMP/{}\n".format(bam_file, sample_name))
        sbatch.write("if [[ -z {} ]] ; then samtools index {} ; fi\n".format(bai_file, bam_file))
        sbatch.write("rsync -rptoDLv {} $SNIC_TMP/{}\n".format(bai_file, sample_name))

        sbatch.write('$FINDTRANS --sv  --bam $SNIC_TMP/{}/{} --bai $SNIC_TMP/{}/{} --auto --minimum-supporting-pairs 4 --output {}\n'.format(sample_name, os.path.split(bam_file)[1], sample_name, os.path.split(bai_file)[1], output_header))
        sbatch.write("rm {0}.tab\n".format(output_header))
        sbatch.write("rm $SNIC_TMP/{0}/*".format(sample_name));
        sbatch.write("\n")
        sbatch.write("\n")

    return ( [int(common.generateSlurmJob(sbatch_dir,sample_name)),"{0}_inter_chr_events.vcf;{0}_intra_chr_events.vcf".format(sample_name)] );

#the function used fermikit
def fermiKit(programDirectory,local_dir, sample_name, bam_file,account,modules):
    #build the sbatch file and submit it
    sys.path.append(os.path.join(programDirectory,"modules"))  
    import common
    sbatch_dir,out_dir,err_dir=common.createFolder(local_dir);
    output_header = os.path.join(local_dir, sample_name)
    reference=references(programDirectory,"bwa-indexed-ref");

    with open(os.path.join(sbatch_dir, "{}.slurm".format(sample_name)), 'w') as sbatch:
        sbatch.write("#! /bin/bash -l\n")
        sbatch.write("#SBATCH -A {}\n".format(account))
        sbatch.write("#SBATCH -o {}/fermiKit_{}.out\n".format(out_dir,sample_name))
        sbatch.write("#SBATCH -e {}/fermiKit_{}.err\n".format(err_dir,sample_name))
        sbatch.write("#SBATCH -J FermiKit_{}.job\n".format(sample_name))
        sbatch.write("#SBATCH -p node\n")
        sbatch.write("#SBATCH -t 4-00:00:00\n")

        sbatch.write("\n");
        sbatch.write("\n");

	if(modules == "True"):
		sbatch.write("module load bioinfo-tools\n")
		sbatch.write("module load bwa\n")
		sbatch.write("module load samtools\n")
		sbatch.write("module load fermikit\n")

		sbatch.write("\n")
		sbatch.write("\n")

        #now transfer the bam file   

        # If we are on a non-SNIC system, chances are there is no 
	    # SNIC_TMP var set. TMP_DIR is more universal, or fall back
        # to /tmp. 
        sbatch.write("if [[ -z $SNIC_TMP ]] ; then if [[ -z $TMPDIR ]] ; then SNIC_TMP=/tmp ; else SNIC_TMP=$TMPDIR ; fi ; fi\n")

        sbatch.write("mkdir -p $SNIC_TMP/{}\n".format(sample_name))
        sbatch.write("rsync -rptoDLv {} $SNIC_TMP/{}\n".format(bam_file, sample_name))
        sbatch.write("samtools bam2fq $SNIC_TMP/{0}/{1} > $SNIC_TMP/{0}/output.fastq\n".format(sample_name,os.path.split(bam_file)[1]))
        sbatch.write("fermi2.pl unitig -s3g -t16 -p $SNIC_TMP/{0}/{0} $SNIC_TMP/{0}/output.fastq > $SNIC_TMP/{0}/{0}.mak\n".format(sample_name));
        sbatch.write("make -f $SNIC_TMP/{0}/{0}.mak\n".format(sample_name));
        sbatch.write("echo run_calling\n");
        sbatch.write("run-calling -t16 {0} $SNIC_TMP/{1}/{1}.mag.gz | sh\n".format(reference,sample_name));
        sbatch.write("cd $SNIC_TMP/{}\n".format(sample_name));
        sbatch.write("cp *vcf* {}\n".format(local_dir));
        sbatch.write("cd {}\n".format(local_dir));
        sbatch.write("gunzip *vcf.gz\n");
        sbatch.write("echo finished!\n");
        sbatch.write("\n")
        sbatch.write("\n")

    return ( [int(common.generateSlurmJob(sbatch_dir,sample_name)), "{}.sv.vcf".format(sample_name)] );

#the function used fermikit
def Delly(programDirectory,local_dir, sample_name, bam_file,account,modules):
    #build the sbatch file and submit it
    sys.path.append(os.path.join(programDirectory,"modules"))  
    import common
    sbatch_dir,out_dir,err_dir=common.createFolder(local_dir);
    output_header = os.path.join(local_dir, sample_name)
    reference=references(programDirectory,"bwa-indexed-ref");

    with open(os.path.join(sbatch_dir, "{}.slurm".format(sample_name)), 'w') as sbatch:
        sbatch.write("#! /bin/bash -l\n")
        sbatch.write("#SBATCH -A {}\n".format(account))
        sbatch.write("#SBATCH -o {}/DellyTra_{}.out\n".format(out_dir,sample_name))
        sbatch.write("#SBATCH -e {}/DellyTra_{}.err\n".format(err_dir,sample_name))
        sbatch.write("#SBATCH -J DellyTra_{}.job\n".format(sample_name))
        sbatch.write("#SBATCH -p core\n")
        sbatch.write("#SBATCH -t 3-00:00:00\n")

        sbatch.write("\n");
        sbatch.write("\n");

        if(modules == "True"):
    	    sbatch.write("module load bioinfo-tools\n")
    	    sbatch.write("module load delly\n")

        sbatch.write("\n")
        sbatch.write("\n")

        # now transfer the bam file   


        sbatch.write("delly -t TRA -o {}.tra.vcf -g {} {}\n".format(output_header,reference,bam_file))
        sbatch.write("delly -t DEL -o {}.del.vcf -g {} {}\n".format(output_header,reference,bam_file))
        sbatch.write("delly -t DUP -o {}.dup.vcf -g {} {}\n".format(output_header,reference,bam_file))
        sbatch.write("delly -t INV -o {}.inv.vcf -g {} {}\n".format(output_header,reference,bam_file))
        sbatch.write("\n")

    return ( [int(common.generateSlurmJob(sbatch_dir,sample_name)), "{0}.tra.vcf;{0}.del.vcf;{0}.dup.vcf;{0}.inv.vcf".format(sample_name)] );
