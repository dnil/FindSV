# FindSV
FindSV is a pipeline designed to find structural variations(SVs). It is designed to run on the UPPMAX system but should work well on other servers using slurm to queue the jobs. 

FindSV can simultaneously run FindTranslocations,CNVnator and fermikit on a large number of samples. 
The pipeline also creates a database of the found events and counts the occurance of each event.

FindSV accepts the path to a folder containing multiple project folders. Each project folder should store the bam files that the program uses as input for the various tools and scipts used to analyse structural variants.



Install
=======
Download and build the pipeline using the following commands:
```
git clone https://github.com/J35P312/FindSV.git
cd FindSV/programFiles
bash InstallScript
```

Running
========
First load python 2.7:

```
module load python/2.7
```

The first time a project is run, it neds to be added to the project.txt file. 
This is a tab separated text file containing the path to the folder were the project folders are located, and the name of the project folder.
The project name is assumed to be the same as the folder of the project. 
The first line of the ```project.txt``` file is a header line that starts with #. Thus open the ```project.txt``` and add the following lines:

```
Project1  /home/project/

Project2  /home/project/
```


If these lines are present in the project.txt file, all samples located in the folders ```/home/project/Project1``` and
```/home/project/Project2``` will be analysed by the pipeline


The pipeline is started using the following command:

```
python FindSV --run
```

or run it every nth hour using this command
```
python FindSV --run --cycle n
```

to analyse only one of the projects, run the pipeline using the following arguments:


```
python FindSV --run --project runthisproject
```

where runthisfolder is the project you wish to run.

The available tools of the pipeline may be listed using the ```--list``` option:
```
python FindSV --list
```

At the moment the available variant callers are:
- Fermikit
- FindTranslocations
- CNVnator



The config file
================
The config file (```config.txt```) is located in the FindSV folder. It contains the following fields.

-```working_dir=```
sets the output diretory of the pipeline. The output will be stored in subfolders for project, tool and sample: ```working_dir/project/tool/sample```.

If ```working_dir``` is set to ```default```, a folder named ```output``` will be created in the FindSV directory

-```bamfile_location=```

If the bam files are stored in a sub folder inside each project folder, the subfolder path to the bam files should be given at the ```bamfile_location```. Example:

```
path/to/project/folders/project1/path/to/bam/1.bam
path/to/project/folders/project2/path/to/bam/2.bam
path/to/project/folders/project3/path/to/bam/3.bam

```
Set ```bamfile_location=path/to/bam``` and ```working_dir=path/to/project/folders```.

-```available_tools=```

the tools available for analysing the bam files. Each have a function within the ```script.py``` file found inside the module folder.

-```excluded_tools=```

tools that are not to be used. To exclude CNVnator:

```
excluded_tools=CNVnator
```

If more than one tool is to be excluded, separate the tools with ```;```
```
excluded_tools=CNVnator;FindTranslocations
```

-```account=```

the slurm project account, example:

```
account=b2011162
```

Projects may be excluded by adding them to the excluded projects list

```
excluded_projects=
```

Examples:

```
excluded_projects=project1
```
```
excluded_projects=project1;project2
```

The pipeline uses two files to keep track of the analysis of the bam files, the folder of these files is set in the processed line of the config file
```
processed=
```
Example:
```
processed=/home/jesper/files
```
now the logs will be kept inside the ```/home/jesper/files``` directory. Processed may also be set to ```default```. Then the logs
will be stored in the ```FindSV/analysis``` folder.



The reference file
===================
The reference file contains paths leading to the references used by fermikit and CNVnator, the file(references.txt) is found in the FindSV directory and contains the following:

```
chromosomes=/proj/b2014152/nobackup/jesperei/references/chromosomes
bwa-indexed-ref=/sw/data/uppnex/reference/Homo_sapiens/hg19/program_files/bwa/concat.fa
```

```chromosomes``` is used by cnvnator and should contain a refererence fasta file for each chromosome. Files should be named in the following manner:
```
chr1.fa
chr2.fa
...
chrN.fa
```

```bwa-indexed-ref``` is used by fermikit, it should contain the path to a bwa inexed reference file.
