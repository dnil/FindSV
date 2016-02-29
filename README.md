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

Before a project can be analysed, a project file must be created. An example file is found within the projects folder within the FindSV folder. the extension of the project files must be txt. if no project is specified by the --project option, all projects that have a project file within the projects folder till be analysed.
By copying the example.txt file and changing the various fields, the user can customise the analysis of different projects.

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

where runthisproject is the path to a project file.

The available tools of the pipeline may be listed using the ```--list``` option:
```
python FindSV --list
```

At the moment the available variant callers are:
- Fermikit
- FindTranslocations
- CNVnator
- delly


The config file
================
The config file (```config.txt```) is located in the FindSV folder. It contains the following fields.

-```working_dir=```
sets the output diretory of the pipeline. The output will be stored in subfolders for project, tool and sample: ```working_dir/project/tool/sample```.

If ```working_dir``` is set to ```default```, a folder named ```output``` will be created in the FindSV directory

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

-```uppmax=```
Used to enable the uppmax module system(default)

-```recursive=```
If recursive is set to yes, FindSV will perform a recursive searh for bam files within the project folders(default)
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
The path file
===================
The path file contains the path to cnvnator, FindTranslocations and vep. If no path is added, FindSV will try the default uppmax configuration. Example:

```
FindTranslocations=/home/jesperei/FindTranslocations/bin/FindTranslocations
CNVnator=
cnvnator2VCF=
vep=/home/jesperei/FindSV/programFiles/ensembl-tools-release-81/scripts/variant_effect_predictor/variant_effect_predictor.pl
```
