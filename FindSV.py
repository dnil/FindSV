import sys, os, glob, argparse, shutil
sys.path.append("modules")
import readConfigFile, calling, filter, annotation, database
import time

#this module restart a selected process of a selected pipeline
def restart(args):
    programDirectory = os.path.dirname(os.path.abspath(__file__))
    (working_dir, path_to_bam, available_tools, account, exclude, 
        processed) = readConfigFile.readConfigFile(programDirectory)
    statusFiles = ["timeout", "failed", "cancelled"]
    processes = {"vc":["annotation", "filter", "database", "calling"],
                 "db":["annotation", "filter", "database"], 
                 "filter":["annotation", "filter"], 
                 "annotation":["annotation"]}

    print("Restarting:")
    projects = {}
    with open(os.path.join(programDirectory, "project.txt")) as ongoing_fd:
        for line in ongoing_fd:
            if line[0] != "#":
                info = line.split("\t")
                projects[info[0].rstrip()] = info[1].rstrip()     

    #check if any project i selected
    if args.project:
        projectToProcess  =  args.project
        tmpProject = {}
        tmpProject[projectToProcess] = projects[projectToProcess]
        projects = tmpProject

    #check if any status file is selected
    restartStatusFiles = []
    if args.status:
        if args.status == "all":
            restartStatusFiles = statusFiles
        elif args.status in statusFiles:
            restartStatusFiles = [args.status]
        else:
            print("Invalid status file.")
            return(0)

    #check which caller is selected
    callerToBeRestarted = []
    if args.caller == "all":
        print("All callers are being restarted!")
        for tools in available_tools:
            callerToBeRestarted.append(tools)
    else:
        if args.caller in available_tools:
            callerToBeRestarted.append(args.caller)
        else:
            print("Error, the caller is not available.")
            return(0)

    # Check which steps will be restarted
    processToBeRestarted = []
    if(args.vc):
        processToBeRestarted = processes["vc"]
    elif(args.db):
        processToBeRestarted = processes["db"]
    elif(args.filter):
        processToBeRestarted = processes["filter"]
    elif(args.annotation):
        processToBeRestarted = processes["annotation"]

    # Iterate through each project
    for project in projects:  
        print(project)
        for tools in callerToBeRestarted:
            for process in processToBeRestarted:
                print(process)
                deletedProcess = os.path.join(processed, project, tools, process)
                # If the entire step is to be restarted, 
                # delete the folder containing the status files.
                if(os.path.exists(deletedProcess) and not restartStatusFiles):
                    shutil.rmtree(deletedProcess)
                #if a certain statusfile is specified, restart only that file
                elif(restartStatusFiles):
                    for files in restartStatusFiles:
                        deletedStatusFile = os.path.join(deletedProcess, files)
                        if(os.path.exists(deletedStatusFile)):
                            os.remove(deletedStatusFile)

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


def main(args):
    programDirectory = os.path.dirname(os.path.abspath(__file__))
    #read the project file
    projects = {}
    with open(os.path.join(programDirectory, "project.txt")) as ongoing_fd:
        for line in ongoing_fd:
            if line[0] != "#":
                info = line.split("\t")
                projects[info[0].rstrip()] = info[1].rstrip()     

    if args.project:
        projectToProcess = args.project
        tmpProject = {}
        tmpProject[projectToProcess] = projects[projectToProcess]
        projects = tmpProject  
    
    # Read the config file
    (working_dir, path_to_bam, available_tools, account, exclude, 
        processed) = readConfigFile.readConfigFile(programDirectory)

    for project in projects:
        analysis = projects[project]
        projectToProcess = project
        processFilesPath = os.path.join(processed, project)
        #create a directory to keep track of the analysed files
        if not (os.path.exists(processFilesPath)):
            os.makedirs(processFilesPath)

        #initate the processFiles
        processFiles = initiateProcessFile(available_tools, processFilesPath)

        #function used to find variants
        processFiles = calling.variantCalling(
            programDirectory, analysis, projectToProcess, working_dir, 
            path_to_bam, available_tools, account, exclude, processFiles,
            processFilesPath)

        #a function used to build databases from vcf files
        processFiles = database.buildDatabase(programDirectory, processFiles,
                                              processFilesPath, account)
        

        # Function that filters the variant files and finds genomic features of 
        # the variants
        processFiles = filter.applyFilter(programDirectory, processFiles, 
                                          processFilesPath, account)

        #function used to annotate the samples
        processFiles = annotation.annotation(programDirectory, processFiles, 
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
        parser.add_argument('--caller', type=str, required=True, 
                            help=("The variant caller that is to be restarted, "
                                  "use the list command to get the available "
                                  "callers, type all to reset all."))
        parser.add_argument('--vc', action="store_true", required=False, 
                            help="Restart the selected caller.")
        parser.add_argument('--db', action="store_true", required=False, 
                            help="Restart the database creation step of the selected caller.")
        parser.add_argument('--filter', action="store_true", required=False,
                            help="Restart the database query step of the selected caller.")
        parser.add_argument('--annotation', action="store_true", required=False,
                            help="Restart the annotation step of the selected caller.")
        parser.add_argument('--status', type=str, default=None,
                            help="Restart one of the status files (failed, timeout, cancelled, all).")
        args = parser.parse_args()
        restart(args)
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
