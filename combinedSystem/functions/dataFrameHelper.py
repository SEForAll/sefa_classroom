import numpy as np, pandas as pd, os

#THIS FILE CONTAINS
#updateDF, loadCSV, writeCSV, editEntry, updateRoster, getSurveyDataFrame

def updateDF(hws, students, df):

    #Takes in existing dataframe and returns the same dataframe with empty columns added
    #for each new entry in the student or homework list provided

    if (df.empty): #If data is not provided create datafram with correct fields
        df= pd.DataFrame(np.zeros((len(students), len(hws))), columns= hws, dtype= float)
        df.insert(0, "GitHub Username", students)

    else:
        for student1 in students: #loop though students who's homework was graded
            presentFlag = False #assume student is not in csv already
            for student2 in list(df["GitHub Username"]): #students already in csv
                if (student1 == student2):
                    presentFlag = True 
            if (presentFlag == False): #student is not found in csv
                newStudent= [{"GitHub Username":student1}] #add student to username col
                for i in range(1, len(df.columns)): #fill grades with zeros
                    newStudent[0][df.columns[i]]= 0
                df= df.append(newStudent, ignore_index= True, sort= True)

        oldHws = list(df.columns) 
        oldHws.remove("GitHub Username") #clean hw list from dataframe
        for hw1 in hws: #hws provided
            presentFlag = False #assume not in csv
            for hw2 in oldHws:
                if (hw1 == hw2):
                    presentFlag = True
            if (presentFlag == False): #If hw is not in csv add with appropriate zero grades for all students
                newHw= [0.0] * len(df.index)
                df[hw1]= newHw

    return df

def loadCSV(path):

    #Takes in the file location of a csv and returns a the data in a dataframe 

    if (os.path.exists(path)):
        df= pd.read_csv(path, delimiter= ",", engine= "python").drop(labels= "Unnamed: 0", axis= 1)
    else:
        df= pd.DataFrame({"GitHub Username":[]})
    return df

def writeCSV(path, df):

    #Takes in a dataframe and writes data to an csv

    df.to_csv(path)
    return

def editEntry(data, student, hw, df):

    #Takes a student and a homework assignment and assigns data to cooresponding data point
    #Returns updated data frame

    if hw not in df.columns: #hw isn't in dataframe
        print("Homework not present in dataframe.")
    else:
        condition = df["GitHub Username"] == student
        index = df.index
        studIndex = index[condition]
        if (len(studIndex) != 1): #student isn't in dataframe
            print("Student not present in dataframe.")
        else:
            df.loc[studIndex,hw] = data #edit homework assignment grade for student

    return df

def updateRoster(dfSurvey, df, path):
    dfSurvey.merge(df, how='left', on='GitHub Username')
    df = dfSurvey
    writeCSV(path, df)
    return df

def getSurveyDataFrame(surveyPath):
    df = loadCSV(surveyPath)
    timeStampColumn = df.columns[0]
    df = df.drop([timeStampColumn], axis=1)
    df.columns = ['Real Name','GitHub Username']
    return df
