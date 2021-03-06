import sys, os, glob, argparse, shutil,fnmatch
sys.path.append(os.path.join(sys.argv[0].replace("FindSV.py",""),"modules"))
import readConfigFile, calling, filter, annotation, database,combine,cleaning,process
import time

def initiateProcessFile(available_tools, processed):
    processFiles = {}

    Files = ["ongoing", "analysed", "failed", "timeout", "cancelled", "excluded"]
    for tool in available_tools:
        processFiles.update({ tool:{} })
        for file in Files:
            processFiles[tool].update({file:{}})

        # Read through the analysed and ongoing samples,
        # or create files if such files are not existing
        pathToVariantFiles = os.path.join(processed, tool, "calling")
        if not (os.path.exists(pathToVariantFiles)):
            os.makedirs(os.path.join(pathToVariantFiles))
            for file in Files:
                open(os.path.join(pathToVariantFiles, file), 'a').close()
        else:
            for file in Files:
                pathToProcessFile = os.path.join(pathToVariantFiles, file)
                if not (os.path.exists(pathToProcessFile)):
                    open(pathToProcessFile, 'a').close()

        for file in processFiles[tool]:
            with open(os.path.join(pathToVariantFiles, file)) as analysed_fd:
                for sample in analysed_fd:

                    row = sample.rstrip().split()
                    sample = row[0]
                    pid = row[1]
                    project = row[2]
                    outpath = row[3]
                    if len(row) == 4:
                        processFiles[tool][file][sample] = {"pid":pid, 
                                                            "project":project,
                                                            "outpath":outpath}
                    else:
                        outputFile = row[4]
                        processFiles[tool][file][sample] = {
                            "pid":pid, "project":project, "outpath":outpath,
                            "outputFile":outputFile }

    return(processFiles)

#this function searches the project folder for bam files and return the names of the files as a list of string
def detect_bam_files(project_path, projectToProcess,path_to_bam,recursive):
    bam_files={};
    for project in project_path:
        path_to_sample = os.path.join(project.strip(),path_to_bam.strip())
        tmp_bam_files=[]    
        if recursive:
            for root, dirnames, filenames in os.walk(path_to_sample):
                for filename in fnmatch.filter(filenames, '*.bam'):
                    tmp_bam_files.append(os.path.join(root, filename))
        else: 
            tmp_bam_files += glob.glob( os.path.join(path_to_sample,"*.bam") )
        for sample in tmp_bam_files:
        	sample_path=sample
                sample_name=sample.split(".")[0]
                sample_name=sample_name.split("/")[-1]
        	bam_files[sample_name]={"folder":path_to_sample,"path":sample_path}
    return(bam_files)
    
def main(args):
    programDirectory = os.path.dirname(os.path.abspath(__file__))
    #read the project file
    projects = {}

    for file in os.listdir(os.path.join(programDirectory,"projects")):
        if file.endswith(".txt") and not file.endswith("example.txt"):
            with open(os.path.join(programDirectory,"projects" ,file)) as ongoing_fd:
                projectID=file.split("/")[-1]
                projectID=file.replace(".txt","")
                #the user has selected a project manually, and it is not this one
                #then there is really nothing to do.

                if not (args.project and (args.project != projectID)):
                    projects[projectID]={};
                    for line in ongoing_fd:
                        try:
                            if line[0] != "#":
                                info=line.strip();
                                info = info.split("\t")
                                projects[projectID][info[0]]=info[1:]
                        except:
                        #the pipeline should not crash if the user adds some newlines etc to the project file
                            pass

    # Read the config file
    (working_dir, available_tools, account, exclude,modules,recursive) = readConfigFile.readConfigFile(programDirectory)
    path_to_bam=""
    default_working_dir=working_dir
    for project in projects:
        #initiate the project parameters based on the project dictionary
        project_path = projects[project]["bam"]
        projectName = project
        #set the output,genmod and frequency db path
        if not projects[project]["output"]:
            working_dir = default_working_dir
        else:
            working_dir= projects[project]["output"][0]
            
        if not projects[project]["genmod"]:
            genmod_file = os.path.join(programDirectory,"genmod")
        else:
            genmod_file=projects[project]["genmod"][0]
        if not projects[project]["db"]:
            frequency_db=os.path.join(working_dir, project,"FindSV","database")
        else:
            frequency_db=projects[project]["db"][0]
        processFilesPath = os.path.join(working_dir, project,"process")
        
        #create a directory to keep track of the analysed files
        if not (os.path.exists(processFilesPath)):
            os.makedirs(processFilesPath)

        #initate the processFiles
        processFiles = initiateProcessFile(available_tools, processFilesPath)

        #search for the projects bam files
        bamfiles=detect_bam_files(project_path, projectName,path_to_bam,recursive)
        #function used to find variants
        processFiles= calling.variantCalling(
            programDirectory, project_path, projectName, working_dir, 
            path_to_bam, available_tools, account, modules,bamfiles, exclude, processFiles,
            processFilesPath)

        #combine the results o the variant calling
        processFiles = combine.combine(programDirectory, processFiles, 
                                             processFilesPath, account,bamfiles)

        #a function used to build databases from vcf files
        processFiles = database.buildDatabase(programDirectory, processFiles,
                                              processFilesPath, account)
        

        # Function that filters the variant files and finds genomic features of 
        # the variants
        processFiles = filter.applyFilter(programDirectory, processFiles, 
                                          processFilesPath, account,frequency_db)

        #function used to annotate the samples
        processFiles = annotation.annotation(programDirectory, processFiles, 
                                             processFilesPath, account,genmod_file)

        #the funciton used for cleaning the vcf file, this is the final step of the pipeline
        processFiles = cleaning.cleaning(programDirectory, processFiles, 
                                             processFilesPath, account)
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        ("This scripts checks the projects given in the project.txt file.\n"
         "Every file found in projects is analysed with the selected tools,\n"
         "and the results are stored in the the working_dir"
         "folder given in the config file.\nTo exclude a tool, copy it to the"
         "excluded_tools line of the config file.\nMultiple tools should be "
         "separated using \';\'.\n"), add_help=False)
    parser.add_argument('--help', action="store_true", 
                        help="generate a help message")
    parser.add_argument('--run', action="store_true", 
                        help="run the pipeline")
    parser.add_argument('--manage', action="store_true", 
                        help="manage the included projects")
    parser.add_argument('--list',  required=False,  action='store_true',  
                        help=("print the available callers, unless tools are "
                              "excluded, they will all be used\n"))
    parser.add_argument('--restart', action='store_true',  
                        help=("restart the analysis of a variant caller from a "
                              "chosen pipeline step\n"))
    args, unknown = parser.parse_known_args()

    if(args.list):
        i = 0
        #list the available tools
        print("available tools")
        programDirectory = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(programDirectory, "config.txt")) as ongoing_fd:
            for line in ongoing_fd:
                i = i+1
                if(i == 3):
                    available_tools = line.rstrip().split()[0]
                    available_tools = available_tools.split("=")[1]
                    available_tools = available_tools.split(";")
            for tools in available_tools:
                print(tools)
    elif(args.restart):
        parser = argparse.ArgumentParser(
            "The restart module: select a caller and a proccess of "
            "the pipeline, restart the analysis of that process and "
            "all downstream processes.")
        parser.add_argument('--restart', action='store_true', 
                            help="Restart the analysis of a variant caller from a chosen pipeline step.\n")
        parser.add_argument('--project', type=str, required=False, default=None,
                            help="Restrict analysis to the specified project.\n")
        parser.add_argument('--caller', type=str, required=False, 
                            help=("Restarts a selected variant caller (or all)"))
        parser.add_argument('--combine', action="store_true", required=False,
                            help="Restart the combination of the caller output")
        parser.add_argument('--db', action="store_true", required=False, 
                            help="Restart the database creation step")
        parser.add_argument('--filter', action="store_true", required=False,
                            help="Restart the database query and database annotation step")
        parser.add_argument('--annotation', action="store_true", required=False,
                            help="Restart the annotation step of the selected caller.")
        parser.add_argument('--status', type=str, default=None,
                            help="Restart one of the status files (failed, timeout, cancelled, all).")
        args = parser.parse_args()

        step={}
        if args.caller:
            step["caller"]=args.caller
        elif args.combine:
            step["combine"]=True
        elif args.db:
            step["db"]=True
        elif args.filter:
            step["filter"]=True
        elif args.annotation:
            step["annotation"]=True

        programDirectory = os.path.dirname(os.path.abspath(__file__))
        process.restart(programDirectory,step,args.project,args.status)
    elif(args.manage):
        parser = argparse.ArgumentParser(
            "the manage module: manage the samples and projects of the pipeline")
    elif(args.run):
        parser = argparse.ArgumentParser(
            "the run module: use this module to run the pipeline")
        parser.add_argument('--run', action="store_true", required=True, 
                            help="run the pipeline")
        parser.add_argument('--project', type=str, required=False, default=None,
                            help="restrict analysis to the specified project\n")
        parser.add_argument('--cycle', type=float , default = None, 
                            help="rerun the pipeline automatically once every nth hour")
        args = parser.parse_args()

        while True:
            main(args)
            if(args.cycle):
                timeToSleep=round(args.cycle*3600)
                print("next itteration in " + str(timeToSleep) + " seconds")
                time.sleep(timeToSleep)
            else:
                break


    elif(args.help):
        parser.print_help()
    else:
        print("Error: uncrecognised option. "
              "To generate a help message, type: FindSV.py --help")
