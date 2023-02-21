from functions.setup import getConfigInputs, isAValidHomework, getHomeworkList
from functions.fetch import fetchLists, fetchRepos, fetchHWInfo, fetchTags
from functions.rmtree import rmtree

import argparse, os, subprocess

#!!--------Set Up Variables From JSON File-----------!! 
#Configname
configJSON = os.getcwd() + "/profFiles/config.json"
#get variables from JSON config file
configInputs = getConfigInputs(configJSON)

#variables
organization =  configInputs["organization"]  #json file
authName = configInputs["authName"] #json file
authKey = configInputs["authKey"] #json file
repoFilter = configInputs.get("repoFilter", None) #json file

tagName = "final_ver"
gradeFileName = "gradeReport.txt"
hwsDir = "/profFiles/hws"
gradeRoot = "/grades"
clonesRoot = "/clones"

#!!----------Set Up Command Line Flag Input--------!!
parser = argparse.ArgumentParser("specify homework assignments to grade")
group = parser.add_mutually_exclusive_group()
group.add_argument("--hw_name", type = str, help= "specify the name of the homework to grade. example: python3 runSystem.py --hw_name hw02sort")
group.add_argument("--hw_range", type = str, nargs = 2, help = "specify a range of homeworks to grade. example: python3 runSystem.py --hw_range hw02sort hw04file")
group.add_argument("--clear_all", action="store_true", help = "specify this option to grade all homeworks. example: python3 runSystem.py --grade_all")
args = parser.parse_args()

homeworkMasterList = getHomeworkList(os.path.join(os.getcwd() + '/profFiles'))

#!!------Checking argument inputs-----!!
if args.hw_range is not None:
    if isAValidHomework(os.getcwd() + hwsDir, args.hw_range[0])[0]: 
        startIndex = isAValidHomework(os.getcwd() + hwsDir, args.hw_range[0])[1]
    else:
        print('Your start range homework name was not valid')
        raise Exception('Invalid Homework Name')

    if isAValidHomework(os.getcwd() + hwsDir, args.hw_range[1])[0]: 
        endIndex = isAValidHomework(os.getcwd() + hwsDir, args.hw_range[1])[1]
    else:
        print('Your end range homework name was not valid')
        raise Exception('Invalid Homework Name')
elif args.clear_all == True:
    startIndex = 0
    endIndex = len(homeworkMasterList) - 1
else: 
    if isAValidHomework(os.getcwd() + hwsDir, args.hw_name)[0]:
        startIndex = isAValidHomework(os.getcwd() + hwsDir, args.hw_name)[1]
    else:
        print('Your homework name was not valid')
        raise Exception('Invalid Homework Name')
    endIndex = startIndex

#!!----Get lists----!!
[students, hws, repos] = fetchLists(fetchRepos(organization, authName, authKey), repoFilter)

for x in range(startIndex, endIndex + 1): #for each homework
    hwName = homeworkMasterList[x]
    hwNum = fetchHWInfo(None, hwName)[1]
    print('\nResetting hw ', hwName, '\n')

    for repo in repos: #for each repository
        if fetchHWInfo(hwNum, repo, False)[0]:
            #!!----Check for local repository and clone if does not exist----!!
            owd = os.getcwd()

            print('Resetting repo', repo)
            
            dirPath = "/clones/" + repo
            repoURL = "https://" + authKey + '@github.com/' + organization + '/' + repo + '.git'

            if not os.path.exists(owd + '/' + clonesRoot): #if cloned repo doesn't exist, clone
                os.mkdir(owd + '/clones')
            
            os.chdir(owd + '/clones')

            tagList = fetchTags(organization, repo, authName, authKey)

            if not os.path.exists(owd + dirPath) and 'final_ver' in tagList and 'graded_ver' in tagList:
                subprocess.run(["git", "clone", "-b", tagName, str(repoURL)]) #clone repo
                os.chdir(owd + dirPath)

            #!!----Delete graded tag-----!!
            tagList = fetchTags(organization, repo, authName, authKey)
            if 'graded_ver' in tagList:
                subprocess.run(["git", "push", "-d", repoURL, "graded_ver"], check=True, stdout=subprocess.PIPE).stdout
            else:
                print('\nNo tag to delete\n')
                
            #!!-----Remove grade report----!!
            if os.path.isfile(owd + dirPath + '/' + gradeFileName):
                os.chdir(owd + dirPath)
                subprocess.run(["git", "rm", gradeFileName], check=True, stdout=subprocess.PIPE).stdout
                subprocess.run(["git", "commit", "-m", "deleted gradeReport.txt"], stdout=subprocess.PIPE).stdout
                subprocess.run(["git", "push", "origin", "HEAD:refs/heads/master", "--force"], check=True, stdout=subprocess.PIPE).stdout
                print('\nDeleted grade file for', repo, '\n')
            
            os.chdir(owd)


if os.path.exists('clones'):
    rmtree('clones') 
    print('Deleted clones')
        #removes all cloned folders
if os.path.exists('grades'):
    rmtree('grades')
    print('Deleted grades')
        #removes folder of grades
if os.path.exists('filteredOutput.txt'):
    os.remove('filteredOutput.txt')
    print('Deleted output file')
