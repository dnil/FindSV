import os
import subprocess
import re
import sys
#this module contains all the tools available to the pipeline, scripts may be added or removed as needed. Every tools should be stored in a separate function. the function arguments are the
#local_dir, which is the output folder of the main script, the sample_name, which is the name of the sample, and the bam_file which is the path to the bam file
#Each function must output the slurm_job ID
#The concent of each function is a printer of an sbatch file, the sbatch file is printed to the output folder and started using slurm.

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
def CNVnator(programDirectory,local_dir, sample_name, bam_file,account):
    sys.path.append(os.path.join(programDirectory,"modules"))  
    import common

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

        sbatch.write("module load bioinfo-tools\n")
        sbatch.write("module load bwa\n")
        sbatch.write("module load samtools\n")
        sbatch.write("module load CNVnator\n")

        sbatch.write("\n")
        sbatch.write("\n")
        #now tranfer the bam file   
		

        sbatch.write("mkdir -p $SNIC_TMP/{0}\n".format(sample_name))
        sbatch.write("rsync -rptoDLv {0} $SNIC_TMP/{1}\n".format(bam_file, sample_name))
        #sbatch.write("rsync -rptoDLv {0} $SNIC_TMP/{1}\n".format(bai_file, sample_name))
        
        sbatch.write("cnvnator -root {0}.root -tree $SNIC_TMP/{1}/{2} \n".format(output_header,sample_name, os.path.split(bam_file)[1]) );
        sbatch.write("cnvnator -root {0}.root -his 200 -d {1}\n".format(output_header,chrFolder));
        sbatch.write("cnvnator -root {0}.root -stat 200 >> {1}.cnvnator.log \n".format(output_header,output_header));
        sbatch.write("cnvnator -root {0}.root -partition 200 \n".format(output_header))
        sbatch.write("cnvnator -root {0}.root -call 200 > {1}.cnvnator.out \n".format(output_header,output_header));
        sbatch.write("cnvnator2VCF.pl {0}.cnvnator.out  >  {1}.vcf \n".format(output_header,output_header));
        sbatch.write("\n")
        sbatch.write("\n")

    return ( int(common.generateSlurmJob(sbatch_dir,sample_name)) );

#the function used to run FindTranslocations
def FindTranslocations(programDirectory,local_dir, sample_name, bam_file,account):
    sys.path.append(os.path.join(programDirectory,"modules"))  
    import common
    #build the sbatch file and submit it
    sbatch_dir,out_dir,err_dir=common.createFolder(local_dir);
    output_header = os.path.join(local_dir, sample_name)
    bai_file      = re.sub('m$', 'i', bam_file) # remove the final m and add and i
    if not (os.path.isfile(bai_file)):
        bai_file=bam_file+".bai";

    with open(os.path.join(sbatch_dir, "{}.slurm".format(sample_name)), 'w') as sbatch:
        sbatch.write("#! /bin/bash -l\n")
        sbatch.write("#SBATCH -A {}\n".format(account))
        sbatch.write("#SBATCH -o {}/FT_{}.out\n".format(out_dir,sample_name))
        sbatch.write("#SBATCH -e {}/FT_{}.err\n".format(err_dir,sample_name))
        sbatch.write("#SBATCH -J FT_{}.job\n".format(sample_name))
        sbatch.write("#SBATCH -p core\n")
        sbatch.write("#SBATCH -t 3-00:00:00\n")
        sbatch.write("#SBATCH -n 1 \n")

        sbatch.write("\n");
        sbatch.write("\n");

        sbatch.write("module load bioinfo-tools\n")
        sbatch.write("module load bwa\n")
        sbatch.write("module load samtools\n")
        sbatch.write("FINDTRANS={}/programFiles/FindTranslocations/bin/FindTranslocations\n".format(programDirectory))

        sbatch.write("\n")
        sbatch.write("\n")
        #now tranfer the bam file   
        sbatch.write("mkdir -p $SNIC_TMP/{}\n".format(sample_name))
        sbatch.write("rsync -rptoDLv {} $SNIC_TMP/{}\n".format(bam_file, sample_name))
        sbatch.write("rsync -rptoDLv {} $SNIC_TMP/{}\n".format(bai_file, sample_name))
        
        sbatch.write('$FINDTRANS --sv  --bam $SNIC_TMP/{}/{} --bai $SNIC_TMP/{}/{} --min-insert 100 --max-insert 10000 --minimum-supporting-pairs 6 \
                --orientation innie --output {}\n'.format(sample_name, os.path.split(bam_file)[1], sample_name, os.path.split(bai_file)[1], output_header))
        sbatch.write("\n")
        sbatch.write("\n")

    return ( int(common.generateSlurmJob(sbatch_dir,sample_name)) );

#the function used fermikit
def fermiKit(programDirectory,local_dir, sample_name, bam_file,account):
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

        sbatch.write("module load bioinfo-tools\n")
        sbatch.write("module load bwa\n")
        sbatch.write("module load samtools\n")
        sbatch.write("module load fermikit\n")

        sbatch.write("\n")
        sbatch.write("\n")
        #now tranfer the bam file   
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

    return ( int(common.generateSlurmJob(sbatch_dir,sample_name)) );
