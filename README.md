# FindSV
FindSV is a pipeline designed to find structural variations(SVs). It is designed to run on the uppmax system but should work well on other servers using slurm to queue the jobs. 

FindSV accepts the path to a folder containing multiple project folders. Each project folder should store the bam files that the program uses as input for the various tools and scipts used to analyse structural variants.

The pipeline is under construction but may be used to simultaneously run FindTranslocations,CNVnator and fermikit on a large number of samples, the pipeline also creates a database of the found events and counts the occurance of each event from the output of cnvnator and Findtranslocations.


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


The first time a project is run, it neds to be added to the project.txt file. This is a tab separated text file containing the path to the folder were the project folder is located, and the name of the project folder. The project name is assumed to be the same as the folder of the project. The first line of the project.txt file is a header line that starts with #. Thus open the project.txt and add the following lines:


Project1  /home/project/

Project2  /home/project/



if these lines are present in the project.txt file, all samples located in the folders /home/project/Project1 and
/home/project/Project2 will be analysed by the pipeline


The pipeline is started using the following command:

- python FindSV


to analyse only one of the projects, run the pipeline using the following arguments:


- python FindSV --project runthisproject


where runthisfolder is the project you wish to run.

The available tools of the pipeline may be listed using the following command
- python FindSV --list

At the moment the available tools are:
- Fermikit
- FindTranslocations
- CNVnator



The config file
================
The config file (config.txt) is located in the FindSV folder. it contains the following fields:

- working_dir=
the output diretory of the pipeline, the output will be stored in the following fashion:
working_dir/project/tool/sample
if the working_dir is set to default, a folder named output will be created in the FindSV directory
bamfile_location=
If the bam files are stored in a sub folder inside each project folder, the subfolder path to the bam files are given at the bamfile_location, example:

path/to/project/folders:
project1/path/to/bam
project2/path/to/bam
ptoject3/path/to/bam

then the bamfile_location is set to path/to/bam

available_tools=

the tools available for analysing the bam files. Each have a function with in the script.py file foun inside the module folder.

- excluded_tools=

tools that are not to be used. To exclude CNVnator:

- excluded_tools=CNVnator

if more than one tool is to be excluded, separate the tools with ;

- excluded_tools=CNVnator;FindTranslocations

-account=

the slurm project account, example:

-account=b2011162

Projects may be excluded by adding them to the excluded projects list

excluded_projects=

example

excluded_projects=project1

excluded_projects=project1;project2

The pipeline uses two files to keep track of the analysis of the bam files, the folder of these files is set in the processed line of the config file

processed=

example:

processed=/home/jesper/files

now the logs will be kept inside the /home/jesper/files directory. Processed may also be set to default, then the logs
will be stored in the FindSV/analysis folder.





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


