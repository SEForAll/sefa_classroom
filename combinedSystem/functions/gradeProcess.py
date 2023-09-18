import os, subprocess, shutil, re, sys, traceback
from datetime import datetime
from functions.fetch import fetchHWInfo, fetchTags, fetchHoursLate, fetchDueDate
from functions.GradingInterface import interface
from functions.dataFrameHelper import loadCSV, writeCSV, editEntry

#THIS FILE CONTAINS
#cloneFromRepos, startGradingProcess, putGradesInRepos, putGradesInCSV, pushChangeToRepos

GRADE_KEY = "Grade: "

def cloneFromRepos(org, repo, hwNum, tagName, authName, authKey, profPath, clonePath, outputFile): 
    newProfPath = os.getcwd() + profPath #must set before looping through repos
    owd = os.getcwd()

    subprocess.run(["git", "config", "--global", "advice.detachedHead", "false"], check=True) #Hide detatched head error
    if fetchHWInfo(hwNum, repo, True)[0]: # but why TRUE?
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

        if 'graded_ver' in tagList:
            outputFile.write("Already Graded this homework. graded_ver tag already present. Skipping\n")

        if ('graded_ver' not in tagList): #If the repo is marked to be graded and hasn't already been graded
            repoURL = "https://" + authKey + "@github.com/" + org + "/" + repo + ".git"
            
            if os.path.isdir(os.getcwd() + clonePath) == False: #create clones folder if it doesn't exist
                os.mkdir(os.getcwd() + clonePath)
            
            os.chdir(os.getcwd() + clonePath)

            subprocess.run(["git", "clone", str(repoURL)])

            os.chdir(os.getcwd() + "/" + repo) #navigate to cloned repo

            tagStr = 'git log -1 --format=%ai '
            info = subprocess.check_output(tagStr.split()).decode()
            subDate = info.split(' ')[0] + ' ' + info.split(' ')[1]
            hoursLate = fetchHoursLate(subDate, fetchDueDate(newProfPath, hwNum))

            os.chdir(owd)
            
            outputFile.write('  * Cloned ' + repo)
            return True, hoursLate
    return False, 0

def startGradingProcess(repo, hoursLate, hwName, outputFile, gradeDir, cloneDir, profDir, gradeFile, failedTestsDir, dryrun):
    owd = os.getcwd()

    gradePath = owd + gradeDir + '/' + repo #path to grade directory
    clonePath = owd + cloneDir + '/' + repo
    profPath = owd + profDir + '/' + hwName #path to professor directory
    failedPath = owd + cloneDir + '/' + repo + failedTestsDir #path to failed tests directory

    if not os.path.exists(gradePath):
        os.makedirs(gradePath) #creates repository folder in grades folder
	
    gradePath = gradePath + '/' + gradeFile
    
    outputFile.write("\n  --Calling grade_submission.py")
    
    try:
        obj = interface.grade_submission(clonePath, profPath, int(hoursLate))
        grade = obj.get_grade() #returns a float that is rounded to two decimals
        feedback = obj.get_error_list() #returns a list
    except:
        grade = 'N/A'
        feedback = ['An error occured while grading your homework.', traceback.format_exc()]
        outputFile.write("\n    **An error occured while grading")

    outputFile.write("\n    --Grade is " + str(grade) + "\n")
    
    os.chdir(owd)
    
    gradefile = open(gradePath, "w") #creates grade report file
    if dryrun:
        gradefile.write("******\nTHIS IS A DRY RUN, NOT THE OFFICIAL GRADE REPORT.\n******\n\n")
    gradefile.write("Graded on " + datetime.now().strftime("%m-%d %H:%M:%S"))
    gradefile.write("\n" + GRADE_KEY + str(grade))
    gradefile.write("%\nSubmission was " + str(hoursLate) + ' hours late.')
    gradefile.write('\nFeedback: ')
    for line in feedback:
        gradefile.write(line)
        gradefile.write(". ")
    gradefile.close()
    
    outputFile.write('\n    --gradeReport.txt created')

    # Copy failed test cases to failedTests folder
    os.makedirs(failedPath, exist_ok=True)
    for test_name, test_case in (obj.dict or {}).items():
        if (isinstance(test_case, dict) and test_case.get('passed') == False):
            if (test_case.get('stdout') == None):
                file = open("CompileAndRunFailed.txt", "w")
                # Write some text to the file
                file.write(str(test_case))
                file.write("Test Name: " + str(test_name))
                file.write("Test Case: " + str(test_case))
                # Close the file
                file.close()
                shutil.copy(f"CompileAndRunFailed.txt", failedPath)
            else:
                files = re.findall(r'\.\/.* (inputs/.*) >', test_case.get('stdout'))
                for file in files:
                    if os.path.exists(f"{profPath}/{file}"):
                        shutil.copy(f"{profPath}/{file}", failedPath)
    
    outputFile.write(f'\n    --Failed test cases copied to {failedPath}')
            
def getGradeFromReport(reportFile):
    grade = "N/A"

    if os.path.exists(reportFile):
        fp = open(reportFile, "r")
        for cl in fp.readlines():
            cl = cl.strip()
            if GRADE_KEY in cl:
                perc = cl.split(GRADE_KEY)[1]
                grade = perc.split("%")[0]
                break
        fp.close()
    print(grade)
    return grade
    
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
        template = re.compile('.*(hw[a-zA-Z0-9]+[-][a-zA-Z0-9]+)[-]([a-zA-Z0-9-]+)$') # regex template for getting hw and student from repo name
        srcPath = str(owd + gradesDir + "/" + repo + "/" + fileName)
        match = re.fullmatch(template, repo) # match template with repository name
        print(match[1])
        print(match[2])
        if os.path.exists(str(srcPath)):
            grade = getGradeFromReport(str(srcPath))
            if grade == 'N/A':
                df = editEntry(0, match[2], match[1], df)
            else:
                df = editEntry(float(grade), match[2], match[1], df) # add grade to respective hw and student
        else:
            print("Grade does not exist: " +  str(srcPath))
        
        writeCSV(owd + profDir + "/masterGrades.csv", df)
    else:
        print("Path Missing: " + str(gradesDir) + " or " + str(profDir))

def pushChangeToRepos(clonesDir, gradeFile, failedTestsDir, repo):
    srcPath = os.getcwd() + clonesDir + '/' + repo

    if os.path.exists(srcPath):
        owd = os.getcwd()
        os.chdir(str(srcPath))
        subprocess.run(["git", "add", gradeFile], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["git", "add", f'.{failedTestsDir}'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        message = "Grades updated for your homework."
        subprocess.run(["git", "commit", "-m", message], stdout=subprocess.PIPE).stdout
        subprocess.run(["git", "push", "origin", "HEAD:refs/heads/main", "--force"], check=True, stdout=subprocess.PIPE).stdout
        subprocess.run(["git", "tag", "graded_ver"], check=True, stdout=subprocess.PIPE).stdout #adds graded version tag
        subprocess.run(["git", "push", "origin", "graded_ver"], check=True, stdout=subprocess.PIPE).stdout #need to push the tag specifically, will not update tag with just a general push command
        os.chdir(owd)
    else:
        print("The directory " + srcPath + " does not exist.")
