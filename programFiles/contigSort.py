import subprocess
import argparse

def main(args,parser):
    header=subprocess.check_output("samtools view -H {}".format(args.bam), shell=True)
    header=header.split("\n")
    chromosome_order=[]
    for line in header:
        content=line.split("\t")
        if(content[0] == "@SQ"):
            chromosome=content[1].strip().split(":")[1]
            chromosome_order.append(chromosome)
    vcf_content={};
    with open(args.vcf, "w") as text_file:
        for line in text_file:
            chromosome=line.split("\t")[0];
            if chromosome in vcf_content:
                vcf_content[chromosome].append(line);
            else:
                vcf_content[chromosome]=[line]
    for chromosome in chromosome_order:
        for line in vcf_content[chromosome]:
            print(line)

if __name__ == '__main__':
    parser = argparse.ArgumentParser("""Uses samtools to read the header data of a bam file, accepts a vcf and sorts the contigs of the vcf according to the contig order, the output is printed to stdout""")
    parser.add_argument('--vcf',type=str,required=True,help="the path to the vcf file")
    parser.add_argument('--bam',type=str,required=True,help="the path to the bam file")
    args, unknown = parser.parse_known_args()
    main(args,parser)
