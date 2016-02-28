#this module restart a selected process of a selected pipeline
import sys, os, glob, argparse, shutil
sys.path.append("modules")
import readConfigFile

def restart(programDirectory,step,project,status):
    (working_dir,available_tools, account, exclude, modules,recursive)  = readConfigFile.readConfigFile(programDirectory)
    statusFiles = ["timeout", "failed", "cancelled"]
    processes = {"caller":["annotation", "filter", "database","combine","cleaning"],
                 "combine":["annotation", "filter", "database","combine","cleaning"],
                 "db":["annotation", "filter", "database","cleaning"], 
                 "filter":["annotation", "filter","cleaning"], 
                 "annotation":["annotation","cleaning"]}
    default_working_dir=working_dir
    print("Restarting:")
    projects = {}
    if project:
        #the user has selected a project manually
        with open(args.project) as ongoing_fd:
            projectID=file.split("/")[-1]
            projectID=file.replace(".txt","")
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
    else:  
        #all projects found in the project dictionary are being analysed
        for file in os.listdir(os.path.join(programDirectory,"projects")):
            if file.endswith(".txt") and not file.endswith("example.txt"):
                with open(os.path.join(programDirectory,"projects" ,file)) as ongoing_fd:
                    projectID=file.split("/")[-1]
                    projectID=file.replace(".txt","")
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
        if not projects[project]["output"]:
            working_dir = default_working_dir
        else:
            working_dir= projects[project]["output"][0]
            
        for caller in callerToBeRestarted:
            deletedProcess = os.path.join(working_dir, project,"process", caller)
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
        if not projects[project]["output"]:
            working_dir = default_working_dir
        else:
            working_dir= projects[project]["output"][0] 
        print(project)
        for process in processToBeRestarted:
            print(process)
            deletedProcess = os.path.join(working_dir, project,"process", "FindSV", process)
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
