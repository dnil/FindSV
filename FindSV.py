import sys, os, glob, argparse
sys.path.append("modules")
import readConfigFile, calling, filter, annotation,database

#this module restart a selected process of a selected pipeline
def restart(args):

    processes={"vc":["annotation","filter","database","calling"],"db":["annotation","filter","database"],"filter":["annotation","filter"],"annotation":["annotation"]}

    print("restarting");
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

    toBeRestarted=[];
    if args.caller == "all":
        print("all callers are being restarted!")    
    
	#read the config file
    working_dir,path_to_bam,available_tools,account,exclude,processed=readConfigFile.readConfigFile(programDirectory)
    for project in projects:  
        
        if(args.vc):
            print("restarting project:" + project);
        elif(args.db):
            print("restarting project:" + project);
        elif(args.filter):
            print("restarting project:" + project);
        elif(args.annotation):
            print("restarting project:" + project);
    



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
        analysed=annotation.annotation(programDirectory,analysed,processFilesPath,account);

    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser("""This scripts checks the projects given in the project.txt file, every found file is analysed with the selected tools and the results are stored in the the working_dir folder given in the config file\nTo exclude a tool, copy it to the excluded_tools line of the config file. multiple tools should be separated using ;
   """,add_help=False)
    parser.add_argument('--help',action="store_true",help="generate a help message")
    parser.add_argument('--run',action="store_true",help="run the pipeline")
    parser.add_argument('--manage',action="store_true",help="manage the included projects")
    parser.add_argument('--list', required=False, action='store_true', help="print the available callers, unless tools are excluded, they will all be used\n")
    parser.add_argument('--restart',action='store_true', help="restart the analysis of a variant caller from a chosen pipeline step\n")
    args ,unknown= parser.parse_known_args()

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
    elif(args.restart):
        parser= argparse.ArgumentParser("the restart module: select a caller and a proccess of the pipeline, restart the analysis of that process and all downstream processes")
        parser.add_argument('--restart',action='store_true', help="restart the analysis of a variant caller from a chosen pipeline step\n")
        parser.add_argument('--project', type=str, required=False, default=None, help="restrict analysis to the specified project\n")
        parser.add_argument('--caller',type = str,required=True,help="The variant caller that is to be restarted, use the list command to get the available callers, type all to reset all")
        parser.add_argument('--vc',action="store_true",required=False,help="restart the selected caller ")
        parser.add_argument('--db',action="store_true",required=False,help="restart the database creation step of the selected caller")
        parser.add_argument('--filter',action="store_true",required=False,help="restart the database query step of the selected caller")
        parser.add_argument('--annotation',action="store_true",required=False,help="restart teh annotation step of the selected caller")
        args = parser.parse_args()
        restart(args);
    elif(args.manage):
        parser= argparse.ArgumentParser("the manage module: manage the samples and projects of the pipeline")
    elif(args.run):
        parser = argparse.ArgumentParser("the run module: use this module to run the pipeline")
        parser.add_argument('--run',action="store_true",required=True,help="run the pipeline")
        parser.add_argument('--project', type=str, required=False, default=None, help="restrict analysis to the specified project\n")
        args = parser.parse_args()
        main(args)
    elif(args.help):
        parser.print_help()
    else:
        print("Error: uncrecognised option, to generate a help message, type: FindSV.py --help")
