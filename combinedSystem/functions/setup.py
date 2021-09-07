import os, json, re
from functions.rmtree import rmtree

#THIS FILE CONTAINS
#getConfigInputs, argParse, getHomeworkList, isAValidHomework

def getConfigInputs(JSONFile):
	dictJSON = {} 
	with open(JSONFile, "r") as JFile:
		dictJSON = json.load(JFile)
	return dictJSON

def argParse(args, hwDir, profFiles, outputFile):
    homeworkMasterList = getHomeworkList(os.path.join(os.getcwd() + hwDir)) #list of all homework directories

    if args.config is not None: #user specified location for config json
        if os.path.exists(args.config[0]) and os.path.isfile(args.config[0]): #is not a directory and exists
            configJSON = args.config[0]
            outputFile.write('\nUsing Custom Config File:\n' + configJSON + '\n')
        else:
            raise Exception('Custom Config Path Error')
    else:
        configJSON = os.getcwd() + profFiles + "/config.json" #default location of config file
        outputFile.write('\nUsing Default Config File:\n' + configJSON + '\n')

    if args.grade_all == True: 
        startIndex = 0
        endIndex = len(homeworkMasterList) - 1
        outputFile.write('\nGrading all homeworks!')

    elif args.hw_range is not None:
        outputFile.write('\nGrading a range of homeworks: ')

        if isAValidHomework(os.getcwd() + hwDir, args.hw_range[0])[0]: 
            startIndex = isAValidHomework(os.getcwd() + hwDir, args.hw_range[0])[1]
            outputFile.write(homeworkMasterList[startIndex] + ' to ')
        else:
            print('Your start range homework name was not valid')
            raise Exception('Invalid Homework Name')

        if isAValidHomework(os.getcwd() + hwDir, args.hw_range[1])[0]: 
            endIndex = isAValidHomework(os.getcwd() + hwDir, args.hw_range[1])[1]
            outputFile.write(homeworkMasterList[endIndex])
        else:
            print('Your end range homework name was not valid')
            raise Exception('Invalid Homework Name')
    
    else:
        if isAValidHomework(os.getcwd() + hwDir, args.hw_name)[0]:
            startIndex = isAValidHomework(os.getcwd() + hwDir, args.hw_name)[1]
            outputFile.write('\nGrading ' + homeworkMasterList[startIndex])
        else:
            print('Your homework name was not valid')
            raise Exception('Invalid Homework Name')
        endIndex = startIndex

    outputFile.write('\n')
    return startIndex, endIndex, homeworkMasterList, configJSON

def getHomeworkList(HWDirectory):
	dirNames = []
	for roots, dirs, files in os.walk(HWDirectory, topdown = False): #Find all directories
		for dir in dirs:
			dirNames.append(dir)
	directoryFileFormat = re.compile(r"((hw)|(HW)).*")
	HWDirNames = []
	for dir in dirNames: #Narrow directories down just to HW Names
		doesMatch = directoryFileFormat.match(dir)
		if(doesMatch != None):
			HWDirNames.append(doesMatch.group())
	return HWDirNames

def isAValidHomework(HWDirectory, inputHW):
	HWList = getHomeworkList(HWDirectory)
	isAHomework = False
	index = -1

	catchDigit = re.compile(r"(\d)+")
	getRegexMatchInput = catchDigit.search(inputHW)
	if(getRegexMatchInput != None):	
		HWDigit = int(getRegexMatchInput.group())
	else:
		print("Something's wrong with your HW input! We couldn't find a number in your input.")
		return isAHomework, -1
	for x in range(0, len(HWList)):
		getRegexMatchDir = catchDigit.search(HWList[x])
		if(getRegexMatchDir != None):
			HWDirDigit = int(getRegexMatchDir.group())
			#print(str(HWDirDigit))
			if(HWDirDigit == HWDigit): 
				isAHomework = True
				index = x
		else:
			print("One of the homeworks in the directory does not have a number!")
	return isAHomework, index

def cleanDirs(clonesDir, gradesDir, outputFile):
    if os.path.exists(os.getcwd() + clonesDir):
        rmtree('clones') 
        outputFile.write('\n\nRemoved clones')
        #removes all cloned folders
    if os.path.exists(os.getcwd() + gradesDir):
        rmtree('grades')
        outputFile.write('\nRemoved grades')
            #removes folder of grades