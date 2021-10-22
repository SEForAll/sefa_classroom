import os, sys, argparse, shutil, subprocess
from datetime import datetime
from functions.setup import getConfigInputs, argParse
from functions.fetch import fetchLists, fetchRepos

#File Structure
#moss.py                -> this file
#/MossDirectory         -> a folder in this directory
#   moss.pl             -> the moss script, paste directly from email
#   student_files.c     -> the c files from the students, automatically put into the directory

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
group.add_argument("--hw_range", type = str, nargs = 2, help = "specify a range of homeworks to grade. example: python3 runSystem.py --hw_range hw02sort hw04file")
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
os.mkdir("TempMossDirectory")
os.chdir("TempMossDirectory")
print(students)
for student in students:
    cloneCmd = "git clone git@github.com:{}/{}-{}".format(organization, hw_number, student)
    os.system(cloneCmd)


for root, dir, files in os.walk("TempMossDirectory"):
    for file in files :
        if ".c" in file : #change this
            for student in students:
                if student in root :
                    shutil.copy(os.path.join(root, file), os.path.join("MossDirectory", hw_number + "_" + student))


runMoss = "perl moss.pl -l c *.c"
subprocess.call(runMoss, shell = True)