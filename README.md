# FindSV
Install
=======
Download the pipeline using the following command:
git clone https://github.com/J35P312/FindSV.git

enter the FindSV/programFiles folder and run the downloadFindTranslocations script:

- cd FindSV/programFiles

- chmod +x downloadFindTranslocations

- ./downloadFindTranslocations

enter the FindTranslocations folder and compile:

- cd FindTranslocations

- mkdir build

- cd build

- cmake .. -DBoost_NO_BOOST_CMAKE=ON

- make

make FindTranslocations executable:

- cd ..

- cd bin

- chmod +x FindTranslocations


Running
========
First load python 2.7:

- module load python/2.7


thereafer FindSV is started:

- python FindSV --analysis projectfolders


where projectfolders is the path to a folder containing folders that contains the bam files.

to analyse only one of the folders, run the pipeline using the following arguments:


- python FindSV --analysis projectfolders --project runthisproject


where runthisfolder is the project folder you wish to run.

The available tools of the pipeline may be listed using the following command
- python FindSV --list

At the moment the available tools are:
- Fermikit
- FindTranslocations
- CNVnator



The config file
================


The reference file
===================
The reference file contains paths leading to the references used by fermikit and CNVnator, the file(references.txt) is found in the FindSV directory and contains the following:

- chromosomes=/proj/b2014152/nobackup/jesperei/references/chromosomes
- bwa-indexed-ref=/proj/b2014152/nobackup/jesperei/references/concat.fa

chromosomes is used by cnvnator and should contain a refererence file for each chromosome, files should be named in the following manner:
-chr1
-chr2
-chrN

bwa-indexed-ref is used by fermikit, it should contain the path to a bwa inexed reference file


