def CNVnator(local_dir, sample_name, bam_file):
    #path to the folder were the reference chromosomes are stored
    chrFolder="/proj/b2014152/nobackup/jesperei/chromosomes"
    sbatch_dir = os.path.join(local_dir, "sbatch")
    out_dir    = os.path.join(local_dir, "sbatch_out")
    err_dir    = os.path.join(local_dir, "sbatch_err")

    if not os.path.isdir(sbatch_dir):
        os.makedirs(sbatch_dir)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    if not os.path.isdir(err_dir):
        os.makedirs(err_dir)
    print(sbatch_dir);   
    output_header = os.path.join(local_dir, sample_name)
    print( "{0}.slurm".format(sample_name));
    print(os.path.join(sbatch_dir, "{0}.slurm".format(sample_name)));
    with open(os.path.join(sbatch_dir, "{0}.slurm".format(sample_name)), 'w') as sbatch:
		
        sbatch.write("#! /bin/bash -l\n")
        sbatch.write("#SBATCH -A b2011162\n")
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
	sbatch.write("cnvnator2VCF.pl {0}.cnvnator.out  >  {1}.cnvnator.vcf \n".format(output_header,output_header));
        sbatch.write("\n")
        sbatch.write("\n")
    process = "sbatch {0}".format(os.path.join(sbatch_dir, "{0}.slurm").format(sample_name))
    p_handle = subprocess.Popen(process, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)    
    p_out, p_err = p_handle.communicate()
    try:
        slurm_job_id = re.match(r'Submitted batch job (\d+)', p_out).groups()[0]
    except AttributeError:
        raise RuntimeError('Could not submit sbatch')

    return int(slurm_job_id)
