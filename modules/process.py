#this module restart a selected process of a selected pipeline
import sys, os, glob, argparse, shutil
sys.path.append("modules")
import readConfigFile

def restart(programDirectory,step,project,status):
    (working_dir, path_to_bam, available_tools, account, exclude, 
        processed,modules) = readConfigFile.readConfigFile(programDirectory)
    statusFiles = ["timeout", "failed", "cancelled"]
    processes = {"caller":["annotation", "filter", "database","combine","cleaning"],
                 "combine":["annotation", "filter", "database","combine","cleaning"],
                 "db":["annotation", "filter", "database","cleaning"], 
                 "filter":["annotation", "filter","cleaning"], 
                 "annotation":["annotation","cleaning"]}

    print("Restarting:")
    projects = {}
    with open(os.path.join(programDirectory, "project.txt")) as ongoing_fd:
        for line in ongoing_fd:
            if line[0] != "#":
                info = line.split("\t")
                projects[info[0].rstrip()] = info[1].rstrip()     

    #check if any project i selected
    if project:
        projectToProcess  =  project
        tmpProject = {}
        tmpProject[projectToProcess] = projects[projectToProcess]
        projects = tmpProject

    #check if any status file is selected
    restartStatusFiles = []
    if status:
        if status == "all":
            restartStatusFiles = statusFiles
        elif status in statusFiles:
            restartStatusFiles = [status]
        else:
            print("Invalid status file.")
            return(0)

    #check which caller is selected
    callerToBeRestarted = []
    if "caller" in step:
        if step["caller"] == "all":
            print("All callers are being restarted!")
            for tools in available_tools:
                callerToBeRestarted.append(tools)
        else:
            if step["caller"] in available_tools:
                callerToBeRestarted.append(step["caller"])

    #restart the callers by removing the status files
    for project in projects:
        for caller in callerToBeRestarted:
            deletedProcess = os.path.join(processed, project, caller)
            if(os.path.exists(deletedProcess) and not restartStatusFiles):
                shutil.rmtree(deletedProcess)
            #if a certain statusfile is specified, restart only that file
            elif(restartStatusFiles):
                for files in restartStatusFiles:
                    deletedStatusFile = os.path.join(deletedProcess,"calling", files)
                    if(os.path.exists(deletedStatusFile)):
                        os.remove(deletedStatusFile)
        

    # Check which steps will be restarted
    processToBeRestarted = []
    if("caller" in step):
        processToBeRestarted = processes["caller"]
    elif("combine" in step):
        processToBeRestarted = processes["combine"]
    elif("db" in step):
        processToBeRestarted = processes["db"]
    elif("filter" in step):
        processToBeRestarted = processes["filter"]
    elif("annotation" in step):
        processToBeRestarted = processes["annotation"]

    # Iterate through each project
    for project in projects:  
        print(project)
        for process in processToBeRestarted:
            print(process)
            deletedProcess = os.path.join(processed, project, "FindSV", process)
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
