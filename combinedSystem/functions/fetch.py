import os, json, re, requests
from datetime import datetime, timedelta
from math import ceil

#THIS FILE CONTAINS:
#fetchLists, fetchRepos, fetchTags, fetchDueDate, fetchHoursLate, fetchHWInfo

def fetchLists(jsonFile):
    """Description: Obtains list of students and homeworks when given a JSON file of repositories
    
    Parameters: 
    jsonFile (file): JSON file of repository names
    
    Returns:
    students (list of str): list of students in organization
    hws (list of str): list of homeworks in organization
    repos (list of str): list of repository names in organization
    """

    repoList = []
    for entry in jsonFile:
        repoList.append(entry["name"])
    
    template = re.compile('^(hw[a-zA-Z0-9]+)[-]([a-zA-Z0-9-]+)$') #template for student's repo name
    studentSet = set()
    hwSet = set()
    repos = []
    
    for repo in repoList:
        match = re.fullmatch(template, repo)
        if match != None: #does not match any of the valid templates
            repos.append(match[0]) #full match
            hwSet.add(match[1]) #hw num
            studentSet.add(match[2])#student name
    
    students = list(studentSet)
    hws = list(hwSet)
    students.sort()
    hws.sort()
    return students, hws, repos

def fetchRepoPage(orgName, authName, authKey, pageNum):
    """Description: Obtains JSON file of repository names for specified organization page using GitHub
    
    Parameters: 
    orgName (str): name of classroom
    authName (str): name of authorized user
    authKey(str): GPG key
    page (num): page number to fetch
    
    Returns:
    JSONfile: JSON file of repository names"""

    url = "https://api.github.com/orgs/" + orgName + "/repos?per_page=100&page=" + str(pageNum) #specifies page num to fetch
    headers = {
        'Accept': 'application/vnd.github.v3+json',
    }
    response = requests.get(url, headers=headers, auth=(authName, authKey))

    return response.json()

def fetchRepos(orgName, authName, authKey):
    """Description: Obtains JSON file of all repository names for specified organization using GitHub
    
    Parameters: 
    orgName (str): name of classroom
    authName (str): name of authorized user
    authKey(str): GPG key
    
    Returns:
    JSONfile: JSON file of repository names"""

    pageNum = 1
    fullJson = fetchRepoPage(orgName, authName, authKey, pageNum) #fetch list for page 1
    pageJson = fullJson
    while (pageJson != []): #the page contains repo info
        pageNum += 1
        pageJson = fetchRepoPage(orgName, authName, authKey, pageNum)
        for entry in pageJson:
            fullJson.append(entry) #compile page into master json
    return fullJson

def fetchLimit(authName, authKey):
    """Description: Provides data on authenticated request limit
    
    Parameters: 
    authName (str): name of authorized user
    authKey(str): GPG key
    
    Returns:
    used (int): num of requests used this hour
    remaining (int): num of requests left this hour
    """
    headers = {
        'Accept': 'application/vnd.github.v3+json',
    }

    response = requests.get('https://api.github.com/rate_limit', headers=headers, auth=(authName, authKey))
    return response.json()["rate"]["used"], response.json()["rate"]["remaining"]

def fetchTags(orgName, repoName, authName, authKey):
    """Description: Provides list of tags that exist for specified repository
    
    Parameters: 
    orgName (str): name of classroom
    repoName (str): name of repository
    authName (str): name of authorized user
    authKey(str): GPG key
    
    Returns:
    tagList (list of str): list of tag names for that repository
    """
    repoURL = "https://" + authKey + "@github.com/" + orgName + "/" + repoName + ".git"

    command = "git -c 'versionsort.suffix=-' ls-remote --tags --sort='v:refname' " + repoURL
    tags = os.popen(command).read()

    tagList = []
    tags = tags.split("refs/tags/")
    for x in range(1, len(tags)):
        tagList.append(tags[x].split('\n')[0])

    return tagList

def fetchDueDate(profDir, hwNum):
    """Description: Obtains JSON file of repository names for specified organization using GitHub
    
    Parameters: 
    profDir (str): path of root folder of professor files
    hwNum (int): number of homework that is being graded

    Returns:
    (str) or None: due date of homework
    """

    if os.path.exists(profDir):
        files = os.listdir(profDir)
        hws = [file for file in files if (os.path.isdir(profDir + "/" + file) and fetchHWInfo(None, file)[1] == hwNum)]
        if (len(hws) == 1):
            jsonFile = json.load(open(profDir + "/" + hws[0] + "/weights.json")) #open Json
            return(jsonFile["due"]) #look for "due" field
        else:
            return None
    else:
        print("HW not present or profFiles doesn't exist: " + str(profDir))
    return None

def fetchDaysLate(subDate, dueDate):
    """Description: Calculates the number of days between the submission date and due date
    
    Parameters: 
    subDate (str): date associated with the final_ver tag
    dueDate (str): due date of homework from JSON file

    Returns:
    timeDiff: difference in days between dates
    """

    #date format: year, month, day, hour, minute, second
    #24 hour clock, must be padded with zeroes. example: "2021-07-02 23:59:59"
    FMT = '%Y-%m-%d %H:%M:%S'
    timeDiff = datetime.strptime(dueDate, FMT) - datetime.strptime(subDate, FMT) #calculate time difference
    timeDiff = timedelta.total_seconds(timeDiff) #convert difference to seconds
    timeDiff = timeDiff / 3600 #convert difference to hours
    timeDiff = timeDiff / 24 #convert difference to days
    
    #timeDiff is positive if submitted before deadline and negative if after deadline
    if (timeDiff >= 0):
        #not late
        return 0
    else:
        return ceil(timeDiff * -1)

def fetchHWInfo(num, hwName):
    """Description: Confirms whether or not the submitted number matches the string provided, and returns number associated with provided string
    
    Parameters: 
    num (int): number of homework that is being graded
    hwName (str): string to check number against

    Returns:
    (boolean): whether or not the number and string provided match numbers
    (int): homework number found in string 
    """

    template = re.compile('^([a-zA-Z]*)([0-9]+)(.*)') #accepted temlates for hw name
    match = re.fullmatch(template, hwName)
    if match != None: #there was a match
        if (num == None):
            return True, int(match[2]) #return extracted number
        elif (num == int(match[2])):
            return True, None  #the hw num matches the extracted num
        else:
            return False, None #the hw num does not match that of the hwname
    else:
        #print("Invalid hw name format:")
        return False, None
