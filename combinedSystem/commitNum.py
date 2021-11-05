# Uses the GitHub REST API to write the number of commits for each student
# for a given homework to a csv file.
# Input csv file should have the columns:
# Timestamp, First Name, Last Name, University username, Github username
# Run command with following format:
# python commitNum.py pathToInputCSV hwToCheck

# Import packages
import sys, os, json, re, requests
import pandas as pd
from functions.fetch import fetchRepos
from functions.setup import getConfigInputs
from functions.dataFrameHelper import updateDF, loadCSV, writeCSV


def commit_num(hwName, githubUser, colNameGH):
    """Description: Finds the number of commits by each student for a given homework

    Parameters:
    hwName (str): name of homework to be checked
    githubUser (list of str): list of students' GitHub usernames
    colNameGH (str): name of column containing GitHub usernames

    Returns:
    commitDict: dictionary of student usernames and number of commits
    """

    # Get authentication details
    parentDir = os.getcwd()
    configJSON = parentDir + "/profFiles/config.json"
    #get variables from JSON config file
    configInputs = getConfigInputs(configJSON)

    orgName =  configInputs["organization"]  #json file
    authName = configInputs["authName"] #json file
    authKey = configInputs["authKey"] #json file

    commitDict = {colNameGH: githubUser, 'Commits': []}
    
    params = {
        'sha': 'master',
        'per_page': 1,
    }
    headers = {
        'Accept': 'application/vnd.github.v3+json',
    }

    # loop through repositories for given hw
    for s in commitDict.get(colNameGH):
        r = orgName+ '/' + hwName + '-' + s
        # try to find the url and request
        try:
            url = f'https://api.github.com/repos/{r}/commits'
            resp = requests.get(url, params=params, headers=headers, auth=(authName, authKey))
            # find count
            count = re.search('\d+$', resp.links['last']['url']).group()
            commitDict['Commits'].append(count)
        except KeyError:
            commitDict['Commits'].append('No repository created')

    return commitDict

if __name__ == '__main__':
    # check command line arguments
    if len(sys.argv) != 3:
        print('Include class CSV file path and homework name')
        sys.exit(0)

    # create dataframe
    df = pd.read_csv(sys.argv[1], delimiter= ",", engine= "python")
    try:
        df = df.drop(labels= "Unnamed: 0", axis= 1)
    except:
        pass
    colNameGH = df.columns[4]
    githubUser = df[colNameGH].tolist()
    hwName = sys.argv[2]
    # remove the timestamp column
    df = df.iloc[: , 1:]

    # call function
    commitDict = commit_num(hwName, githubUser, colNameGH)

    # outpur csv file with commit information
    commitDF = pd.DataFrame.from_dict(commitDict)
    outputDF = df.merge(commitDF, on=colNameGH, how = 'inner')
    writeCSV(hwName + 'CommitInfo.csv', outputDF)
