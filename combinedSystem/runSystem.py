#this file will run all the functions
from functions.fetchLists import fetchLists
from functions.fetchRepos import fetchRepos
from functions.cloneFromRepos import cloneFromRepos
from functions.putGradesInRepos import putGradesInRepos
from functions.pushChangeToRepos import pushChangeToRepos
from functions.startGradingProcess import startGradingProcess
from functions.putGradesInCSV import putGradesInCSV

import os

#variables
hwName = "hw02sort" #input from python script

organization = "cam2testclass" #json file
authName = "myers395" #json file
authKey = "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" #json file

tagName = "final_ver" #not changed by professor
gradeFileName = "gradeReport.txt" #not changed by professor
profFiles = "/profFiles"
gradeRoot = "/grades"
clonesRoot = "/clones"

#running functions
[students, hws, repos] = fetchLists(fetchRepos(organization, authName, authKey)) 
print(students)
    #fetchRepos returns json file of repos, then fetchLists returns list of students in class and lists of homeworks that exist
[clonedRepos, hoursLateArr] = cloneFromRepos(organization, repos, hwName, tagName, authName, authKey, profFiles)
    #[repos cloned to the server at this step, each repo and its hours late]
    #clones all repositories of students with the specified homework name and tag

startGradingProcess(clonedRepos, hoursLateArr)
    #fake grading function that just creates grade.txt file in the a grades folder
print('\nran startGradingProcess\n')

putGradesInRepos(gradeRoot, gradeFileName, clonedRepos)
    #puts grade.txt file into the cloned repositories
print('\nran putGradesInRepos\n')

putGradesInCSV(profFiles, gradeRoot, gradeFileName, clonedRepos, hws, students)
    #adds new hws and students to a csv
    #uses the grade directory to modify data points
print('\nran putGradesInCSV\n')

pushChangeToRepos(clonesRoot, gradeFileName, clonedRepos, hwName, organization)
    #pushes the grade.txt file to remote repositories
print('\nran pushChangeToRepos\n')
