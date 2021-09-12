import os, subprocess, shutil, re, sys, traceback
from datetime import datetime
from functions.fetch import fetchHWInfo, fetchTags, fetchDaysLate, fetchDueDate
from functions.GradingInterface import interface
from functions.dataFrameHelper import loadCSV, writeCSV, editEntry

#THIS FILE CONTAINS
#cloneFromRepos, startGradingProcess, putGradesInRepos, putGradesInCSV, pushChangeToRepos

def cloneFromRepos(org, repo, hwNum, tagName, authName, authKey, profPath, clonePath, outputFile): 
    newProfPath = os.getcwd() + profPath #must set before looping through repos
    owd = os.getcwd()

    subprocess.run(["git", "config", "--global", "advice.detachedHead", "false"], check=True) #Hide detatched head error
    if fetchHWInfo(hwNum, repo)[0]:
        outputFile.write('\n[Evaluating repo: ' + repo + ']\n')
        tagList = fetchTags(org, repo, authName, authKey) #Get the tags for a specific repository
        
        outputFile.write('  --Tags for this repo: ')
        if len(tagList) == 0:
            outputFile.write('None\n')
        else: 
            outputFile.write(tagList[0])
            for x in range(1, len(tagList)):
                outputFile.write(', ' + tagList[x])
            outputFile.write('\n')

        if (tagName in tagList): #If tagName is in the list
            repoURL = "https://" + authKey + "@github.com/" + org + "/" + repo + ".git"
            
            if os.path.isdir(os.getcwd() + clonePath) == False: #create clones folder if it doesn't exist
                os.mkdir(os.getcwd() + clonePath)
            
            os.chdir(os.getcwd() + clonePath)

            subprocess.run(["git", "clone", "-b", tagName, str(repoURL)])

            os.chdir(os.getcwd() + "/" + repo) #navigate to cloned repo

            tagStr = 'git log -1 --format=%ai ' + tagName
            info = subprocess.check_output(tagStr.split()).decode()
            subDate = info.split(' ')[0] + ' ' + info.split(' ')[1]
            daysLate = fetchDaysLate(subDate, fetchDueDate(newProfPath, hwNum))

            commitStr = 'git log -1 --format=%H ' + tagName
            commitHash = subprocess.check_output(commitStr.split()).decode()
            os.chdir(owd)
            
            outputFile.write('  * Cloned ' + repo)
            return True, commitHash, daysLate
    return False, 0, 0

def startGradingProcess(repo,commitHash, daysLate, hwName, outputFile, gradeDir, cloneDir, profDir):
    owd = os.getcwd()

    gradePath = owd + gradeDir + '/' + repo #path to grade directory
    clonePath = owd + cloneDir + '/' + repo
    profPath = owd + profDir + '/' + hwName #path to professor directory
    
    os.makedirs(gradePath) #creates repository folder in grades folder
	
    gradePath = gradePath + '/gradeReport.txt'
    
    outputFile.write("\n  --Calling grade_submission.py")
    
    try:
        obj = interface.grade_submission(clonePath, profPath, int(daysLate))
        grade = obj.get_grade() #returns a float that is rounded to two decimals
        feedback = obj.get_error_list() #returns a list
    except:
        grade = 'N/A'
        feedback = ['An error occured while grading your homework.', traceback.format_exc()]
        outputFile.write("\n    **An error occured while grading")

    outputFile.write("\n    --Grade is " + str(grade))
    
    os.chdir(owd)
    
    gradefile = open(gradePath, "w") #creates grade report file
    gradefile.write("Graded on " + datetime.now().strftime("%m-%d %H:%M:%S"))
    gradefile.write("\nGraded on Commit ID: " + str(commitHash))
    gradefile.write("\nGrade: " + str(grade))
    gradefile.write("%\nSubmission was " + str(daysLate) + ' Days late.')
    gradefile.write('\nFeedback:\n')
    for line in feedback:
        gradefile.write(line)
        gradefile.write("- ")
    gradefile.close()
    
    outputFile.write('\n    --gradeReport.txt created')
    
def putGradesInRepos(gradesDir, clonesDir, fileName, repo):
	owd = os.getcwd()
	srcPath = str(owd + gradesDir + '/' + repo + '/' + fileName)
	dstPath = str(owd + clonesDir + '/' + repo)
	if os.path.exists(str(srcPath)) and os.path.exists(str(dstPath)):
		shutil.copy(srcPath, dstPath)
	else:
		print("One of these directories does not exist: " +  str(srcPath) + " or " + str(dstPath))

def putGradesInCSV(profDir, gradesDir, fileName, repo):
    owd = os.getcwd() # get working directory

    if (os.path.exists(owd + profDir) and os.path.exists(owd + gradesDir)):
        df = loadCSV(owd + profDir + "/masterGrades.csv") 
        template = re.compile('^(hw[a-zA-Z0-9]+)[-]([a-zA-Z0-9-]+)$') # regex template for getting hw and student from repo name
        srcPath = str(owd + gradesDir + "/" + repo + "/" + fileName)
        match = re.fullmatch(template, repo) # match template with repository name
        
        if os.path.exists(str(srcPath)):
            grade = open(srcPath, "r").readlines()[3] # open grade file, get the first line
            grade = grade.split(" ")[1].split("%")[0] #retrives just the number from the text file
            if grade == 'N/A':
                df = editEntry(0, match[2], match[1], df)
            else:
                print(grade)
                df = editEntry(float(grade), match[2], match[1], df) # add grade to respective hw and student
        else:
            print("Grade does not exist: " +  str(srcPath))
        
        writeCSV(owd + profDir + "/masterGrades.csv", df)
    else:
        print("Path Missing: " + str(gradesDir) + " or " + str(profDir))

def pushChangeToRepos(clonesDir, fileName, repo):
    srcPath = os.getcwd() + clonesDir + '/' + repo

    if os.path.exists(srcPath):
        owd = os.getcwd()
        os.chdir(str(srcPath))
        subprocess.run(["git", "add", fileName], check=True, stdout=subprocess.PIPE).stdout
        message = "Grades updated for your homework."
        subprocess.run(["git", "commit", "-m", message], stdout=subprocess.PIPE).stdout
        subprocess.run(["git", "push", "origin", "HEAD:refs/heads/main", "--force"], check=True, stdout=subprocess.PIPE).stdout
        subprocess.run(["git", "tag", "graded_ver","-f"], check=True, stdout=subprocess.PIPE).stdout #adds graded version tag
        subprocess.run(["git", "push", "origin", "graded_ver","-f"], check=True, stdout=subprocess.PIPE).stdout #need to push the tag specifically, will not update tag with just a general push command
        os.chdir(owd)
    else:
        print("The directory " + srcPath + " does not exist.")
