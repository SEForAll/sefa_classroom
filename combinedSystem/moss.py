import os, sys, argparse, shutil, subprocess
from datetime import datetime
from functions.setup import getConfigInputs, argParse
from functions.fetch import fetchLists, fetchRepos

#How to run: 
#   $python3 moss.py --grade_all --config [Path to config.json]

#File Structure
#moss.py                    -> this file
#
#config.json                -> in profFiles directory, must change all arguments
#
#/MossDirectory             -> a folder in this directory
#   moss.pl                 -> the moss script, paste directly from email
#   student_files.c         -> the c files from the students, automatically put into and deleted from the directory
#
#/TempMossDirectory         -> automatically created and deleted 
#   cloned_student_repos    -> the student repos from GitHub Classrooms


#!!----------Static Variables------!!
profDir = "/profFiles"
hwsDir = "/hws"

#!!----------Set Up File For Collecting Output------!!
outputFile = open('filteredOutput.txt', 'w')
outputFile.write("Ran on ")
outputFile.write(datetime.now().strftime("%m-%d %H:%M:%S") + "\n")

#!!----------Set Up Command Line Flag Input--------!!
parser = argparse.ArgumentParser("specify run options")
group = parser.add_mutually_exclusive_group()
group.add_argument("--grade_all", action="store_true", help = "specify this option to grade all homeworks. example: python3 runSystem.py --grade_all")
parser.add_argument("--config", type = str, nargs = 1, help = "specify the absolute path of a config.json file")
parser.add_argument("--git_username", type = str, nargs = 1, help = "grade only a specific student's homework")
args = parser.parse_args()
    
[startIndex, endIndex, homeworkMasterList, configJSON, gitUser] = argParse(args, profDir + hwsDir, profDir, outputFile)

#!!--------Set Up Variables From JSON File-----------!! 
configInputs = getConfigInputs(configJSON)   

#variables
organization =  configInputs["organization"]  #json file 
hw_number = configInputs["hw_number"] #json file
authName = configInputs["authName"] #json file
authKey = configInputs["authKey"] #json file

#!!----------Run Actual System--------!!
[students, hws, repos] = fetchLists(fetchRepos(organization, authName, authKey), gitUser)  #fetchRepos returns json file of repos, then fetchLists returns list of students in class and lists of homeworks that exist

#!!----------Clone Repos in TempMossDirectory----------!!
os.mkdir("TempMossDirectory")
os.chdir("TempMossDirectory")
print(students)
for student in students:
    cloneCmd = "git clone git@github.com:{}/{}-{}".format(organization, hw_number, student)
    os.system(cloneCmd)

#!!----------Directory Work----------!!
path = os.getcwd()
temppath = os.getcwd() # to get into the Moss Directory
baseDirectory = path.replace("/TempMossDirectory", "")
os.chdir(baseDirectory)

#!!----------Move Specific Files to MossDirectory----------!!
for root, dir, files in os.walk("TempMossDirectory"):
    for file in files:
        if ".c" in file: # CHANGE THIS if you want to run different types of files
            for student in students:
                if student in root:
                    shutil.copy(os.path.join(root, file), os.path.join("MossDirectory", hw_number + "_" + student + ".c"))

#!!----------Run Moss Script----------!!
toMossDirectory = temppath.replace("/TempMossDirectory", "/MossDirectory")
os.chdir(toMossDirectory)
runMoss = "perl moss.pl -l c *.c" # CHANGE THIS if you want to change the paramaters of the script, 
subprocess.call(runMoss, shell = True) # ^ look at the script email for more details

#!!----------Delete TempMossDirectory----------!!
os.chdir(baseDirectory)
deleteTempMossDirectory = "rm -rf ./TempMossDirectory"
os.system(deleteTempMossDirectory)

#!!----------Delete Other Files in MossDirectory----------!!
dirs = os.listdir(toMossDirectory)
os.chdir(toMossDirectory)
for file in dirs: 
    if ".c" in file: 
        os.remove(file)
