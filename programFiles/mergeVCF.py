import subprocess
import argparse

def main(args,parser):
    header={};
    header["ALT"]={}
    header["INFO"]={}
    header["FILTER"]={}
    header["FORMAT"]={}
    
    print("##fileformat=VCFv4.1")
    print("##source=FindSV")
    for vcf in args.vcf:
        with open(vcf) as text_file:
            for line in text_file:
                if(line[0] == "#"):
                    if("#CHROM\tPOS" in line):
                        break
                    elif "##ALT=" in line  or "##INFO=" in line or "##FILTER=" in line  or "##FORMAT=" in line:
                        field=line.split("=")[2].split(",")[0]
                        if("##ALT=" in line):
                            header["ALT"].update({field:line})
                        elif("##INFO=" in line):
                            header["INFO"].update({field:line})
                        elif("##FILTER=" in line):
                            header["FILTER"].update({field:line})
                        elif("##FORMAT=" in line):
                            header["FORMAT"].update({field:line})
                else:
                    break
    for entry in sorted(header["ALT"]):
        print(header["ALT"][entry].strip())
    for entry in sorted(header["INFO"]):
        print(header["INFO"][entry].strip())
    for entry in sorted(header["FILTER"]):
        print(header["FILTER"][entry].strip())
    for entry in sorted(header["FORMAT"]):
        print(header["FORMAT"][entry].strip())
    if header["FORMAT"]:
        print("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT")
    else:
        print("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO")
    for vcf in args.vcf:
        with open(vcf) as text_file:
            for line in text_file:
                if not (line[0] == "#"):
                    print(line.strip())
if __name__ == '__main__':
    parser = argparse.ArgumentParser("""Accepts multiple vcf files, merges them and prints them to stdout""")
    parser.add_argument('--vcf',nargs='+',type=str,required=True,help="the vcf files")
    args, unknown = parser.parse_known_args()
    main(args,parser)
