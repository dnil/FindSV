import sys, os, glob, argparse
sys.path.append("modules")
import readConfigFile, calling, filter, annotation,database


def initiateProcessFile(available_tools,processed):
	
    analysed={}
    ongoing={};
    #read through the analysed and ongoing samples, or create files if such files are not existing
    for tools in available_tools:
        analysed[tools]={};
        ongoing[tools]={};
        pathToVariantFiles=os.path.join(processed,tools,"calling");
        if not (os.path.exists(pathToVariantFiles)):
            os.makedirs(os.path.join(pathToVariantFiles))
            open(os.path.join(pathToVariantFiles,"ongoing"), 'a').close()
            open(os.path.join(pathToVariantFiles,"analysed"), 'a').close()
        else:
            with open(os.path.join(pathToVariantFiles,"analysed")) as analysed_fd:
                for sample in analysed_fd:
                    sample , pid ,project, outpath = sample.rstrip().split()
                    analysed[tools][sample] = {"pid":pid,"project":project,"outpath":outpath}
            with open(os.path.join(pathToVariantFiles,"ongoing")) as ongoing_fd:
                for sample in ongoing_fd:
                    if(sample[0] != "\n"):
                        sample , pid ,project, outpath = sample.rstrip().split()
                        ongoing[tools][sample] = {"pid":pid,"project":project,"outpath":outpath}

    return(analysed,ongoing);


def main(args):
    programDirectory=os.path.dirname(os.path.abspath(__file__));
    #read the project file
    projects={};
    with open(os.path.join(programDirectory,"project.txt")) as ongoing_fd:
        for line in ongoing_fd:
            if line[0] != "#":
                info=line.split("\t");
                projects[info[0].rstrip()]=info[1].rstrip();     

    if args.project:
        projectToProcess = args.project;
        tmpProject={};
        tmpProject[projectToProcess]=projects[projectToProcess];
        projects=tmpProject;  
    
	#read the config file
    working_dir,path_to_bam,available_tools,account,exclude,processed=readConfigFile.readConfigFile(programDirectory)



    for project in projects:
        analysis=projects[project];
        projectToProcess=project;
        processFilesPath=os.path.join(processed,project)
        #create a directory to keep track of the analysed files
        if not (os.path.exists(processFilesPath)):
            os.makedirs(processFilesPath)

        #initate the analysed and ongoing dictionaries
        analysed,ongoing=initiateProcessFile(available_tools,processFilesPath);

        #function used to find variants
        analysed,ongoing=calling.variantCalling(programDirectory,analysis,projectToProcess,working_dir,path_to_bam,available_tools,account,exclude,analysed,ongoing,processFilesPath);

        #a function used to build databases from vcf files
        analysed=database.buildDatabase(programDirectory,analysed,processFilesPath,account);
        

        #function that filters the variant files and finds genomic features of the variants
        analysed=filter.applyFilter(programDirectory,analysed,processFilesPath,account);

        #function used to annotate the samples
        analysed=annotation.annotation(programDirectory,analysed,processFilesPath);

    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser("""This scripts checks the projects given in the project.txt file, every found file is analysed with the selected tools and the results are stored in the the working_dir folder given in the config file\nTo exclude a tool, copy it to the excluded_tools line of the config file. multiple tools should be separated using ;
   """)
    parser.add_argument('--project', type=str, required=False, default=None, help="restrict analysis to the specified project\n")
    parser.add_argument('--list', required=False, action='store_true', help="print the available tools, unless tools are excluded, they will all be used\n")
    args = parser.parse_args()
    if(args.list):
        i=0;
        #list the available tools
        print("available tools");
        programDirectory=os.path.dirname(os.path.abspath(__file__));
        with open(os.path.join(programDirectory, "config.txt")) as ongoing_fd:
            for line in ongoing_fd:
                i=i+1
                if(i == 3):
                    available_tools=line.rstrip().split()[0];
                    available_tools = available_tools.split("=")[1]
                    available_tools=available_tools.split(";");
            for tools in available_tools:
                print(tools);
    else:
        main(args)

