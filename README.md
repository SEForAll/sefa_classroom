# Automated Grading using GitHub Classroom
Scripts to handle Github class room based grading!

## GitHub Classroom
This section will go through everything needed to work with GitHub Classroom

### Setting up GitHub Classroom
1. Go to <https://classroom.github.com>
2. Login and click "New Classroom"
3. Click "Create an Organization"
4. Go through organization setup
    * This organization belongs to:
      * [x] My Personal Account
      * [ ] A business or institution
5. Select the new organization
6. Follow listed steps to add TAs if desired

GitHub also has extensive [documentation](https://github.blog/2020-03-18-set-up-your-digital-classroom-with-github-classroom/) to look at.

### Setting up an Assignment in Github Classroom
There are 2 ways to go about this using our system: 
* set up a batch of assignments.
* add a single assignment.

These methods are outlined below. Additionally, the following [video](https://www.youtube.com/watch?v=6QzKZ63KLss) can also be used for reference.

#### Batch of Assignments
Note: Please refer to [Variable Configuration](#variable-configuration) before hand.

If you have an existing repository of homeworks that you would like to use you can automatically create the template repositories by running: 
```
python3 functions/splitRepo.py
``` 
If no repo is specified, it will use [https://github.com/PurdueECE264/2020FallProblems-Lu](https://github.com/PurdueECE264/2020FallProblems-Lu)


#### Single Assignment
Go to class organization page
  1. Create a new repository
  2. Add homework files you wish the student to have to repository (makefile, test cases, c files etc.)
  3. Change setting of repository:
      * [x] Template Repository
  4. Add Autograding tests:
     Add test run -> Run Command: ```make testall```

Please make sure that **the assignment should be private and the student should __not__ have admin access**.

For more details, refer [official documentation](https://docs.github.com/en/education/manage-coursework-with-github-classroom/teach-with-github-classroom/create-an-individual-assignment).

#### Sending the Assignment Link to Students
Go to your [classroom](https://classroom.github.com/classrooms)

1. Select the assignment you want to share with the students.
2. Click on **Edit Assignment** (Pencil icon)
3. Copy the invite link and share it with students. (Use BrightSpace to send this link as an email.)


## Deploying the System
This section will cover how to set up our auto-grading system and grade assignments.

### Downloading/Set-Up
First, install necessary packages on the server or computer you are using. This can be done using :

```bash
sudo apt-get update
sudo apt-get install valgrind \
  make \
  gcc \
  python3 \
  python3-pip \
  git
```

To use the grading system, this repository needs to be cloned to a server (or computer), which can be done using the following terminal command:
```git clone https://github.com/PurdueCAM2Project/pas_githubclassroom```

Then, install all packages needed to run the grading system by running ```sudo pip3 install -r requirements.txt``` in the terminal.

### Variable Configuration
Certain variables need to be specified by the professor in the `config.json` file. A template for this file can be found in `combinedSystem/profFiles/config.json`. This file will be used if another is not specified (see: _Running the System_).
- _Organization name_: name of the classroom.
- _Authentication username_: The name of the GitHub account with access to the classroom.
- _Authentication key_: A token tied to this account that allows for automation of important GitHub API features.
  - Setting up your GPG token:
  - Go to <https://github.com/settings/tokens>
  - Click '''Generate new token'''
  - Add a Note and check the following scopes:
    * [x] repo
    * [x] admin:org
  - Generate and copy the token
  - Paste token into `config.json`

Other parameters are set by the system. These are the name of the tag that references submitted homeworks _(final_ver)_, the name of the file to which the grade and feedback are written _(gradeReport.txt)_, the location of the master list of homework directories as well as the location of the assignment data JSON file, configuration JSON file, and grade CSV file _(/profFiles)_, the directory in which repositories are cloned _(/clones)_, and the directory in which grade reports are intially created _(/grades)_. You do not need to change these unless desired.

### Running the System
As a user, everything is ran from runSystem.py. This is the core script of the system as it integrates all functions into one process. 

This file should be run from a command line in a Linux based system. It will not work on Windows. There are a few options that can be specified when running. At least one option of the three grade options _must_ be specified for the program to run.

- Grade a single homework: Call the file with the tag `--hw_name` and the name of the homework. The name of the homework can be the full name or even just the number.  
`python3 runSystem.py --hw_name HW02Sort`  
`python3 runSystem.py --hw_name hw02sort`  
`python3 runSystem.py --hw_name 2`  

- Grade a range of homeworks: Call the file with the tag `--hw_range` and two homework names/numbers to specify the start and end of the range. The start and end indexes are inclusive.  
`python3 runSystem.py --hw_range hw02sort hw10cake2`  
`python3 runSystem.py --hw_range 4 15`  
`python3 runSystem.py --hw_range hw03cake 20`

- Grade all homeworks: Call the file with the tag `--grade_all`. This will grade all homeworks for which a professor-created example folder exists in the professor directory.   
`python3 runSystem.py --grade_all`

- Specify a custom config file with the tag `--config`. The input must be the **absolute** path. If this flag is not included, the default config file location will be used: `combinedSystem/profFiles/config.json`

Throughout this process, feedback messages are written to a text file in filteredOutput.txt and grades are added to _profFiles\mastergrades.csv_ for easy reference.

### Grading Process
The system works in two loops. The top-level loop grades each homework at a time - all student repositories are graded for one homework before moving on to the next homework. The bottom level loop grades each student's repository at a time - all steps are completed for one student's repository before moving on to the next. 

_Example:_
A classroom with 3 students. Two homeworks (HW1 and HW2) are specified to be graded. The order of grading will be:

HW1-Student1 -> HW1-Student2 -> HW1-Student3 -> HW2-Student1 -> HW2-Student2 -> HW2-Student3

Grading Steps:
1. The first step of the system is cloning the student's repository. The student repository will be cloned if it has the specified submission tag and _doesn't_ have the graded tag. In this step, the submission date of the homework is also collected and the number of hours late that it was submitted is calculated. 
2. Next, the homework is graded. Using the GradingInterface, test cases are ran and memory checks are performed to calculate a grade for the homework. The grade and feedback are written to a text file that is placed in the grades directory.
3. The grade report text file is copied from the grades directory to the cloned repositories.
4. The grade, without any feedback, is added to a CSV file for easy reference of the professor.
5. Changes are pushed to the student repository. The first change is the addition of the grade report text file. The second change is the addition of a new tag that specifies that the repository has been graded. 
6. The cloned repository is deleted from the local computer.
Once all homeworks have been graded, the grades directory is also deleted.

### Assignment Customization

#### Test Case Weights
_weights.json_ contains information that is used during the grading process. It contains:
- Weights of each test case
- Coefficient for deduction for memory leaks
- Coefficient for deduction for late submissions
- Whether to grade late work or not

This file can easily be generated using _jsonfile_generator.py_. The user will specify the weight values in the command line call, and the file will be created with the correct format. 

The details of this file are completely up to the professor. The professor can choose to use the same _weights.json_ for every assignment, or can create different ones for different assignments. This file must be located in the respective homework folder in profFiles. Example: HW03Cake -> _profFiles/hws/HW03Cake/weights.json_

The grading script will correctly assign test case weights regardless of their sum.

### Setting due dates
The grading system makes use of Linux Cron in order to run the system at the appropiate time. Put the appropiate due dates in duedates.json. The JSON format and a precreated format must be followed to insert due dates. The duedates.json is a dictionary. The keys are the homework name, and the values are the date on which to execute the code. The arbitrary format for the values is as follows: "MM-DD-YEAR,HR:MN". The keys can be written in the same format as running the program manually. To remove a due date, simply exclude it from the JSON file. In order to set the new due dates, run cronManager.py to set them into the crontab file. cronManager.py also needs to be modified to contain the correct username of the operating system (this needs to be done by an administrator). This is subject to change, as cronManager.py is not directly integrated into the full system yet and operates as an independent unit. 


#### Makefiles
A new makefile is needed for each homework assignment. User need to manually write these Makefiles, but we have a Makefile template setted up to help the user write Makefiles. User only need to download the template and modify the template according to the guidance. User must follow the gridance, otherwise, our grading system will output unexpected result. Please go to the [Makefile_template](documentation/Makefile) for detail guidance.  

## Student Side
This section will go over how students will access and submit assignments.

### Accessing an Assignment
To access an assignment, the student must click the assignment link given by the professor. From there, the student will
be prompted to clone the repository and have a copy they can edit and submit from.

### Submitting an Assignment
In order to submit an assignment, the student must push their completed code to their assignment repository. Then, they 
must tag their submission as 'final_ver', which tells the grading system it is ready to be graded. Without the 'final_ver' 
tag, the submission will not be graded.
 
### Tagging an Assignment
A tag points to a specific version of your repository. Creating a tag preserves a specific version of your files, so any changes made after the tag will not be reflected in the tagged version. When we pull the "final_ver" of your repository, it will pull whatever the files looked like at the most recent commit before the tag. More info can be found [here](https://docs.github.com/en/github/administering-a-repository/releasing-projects-on-github/about-releases).

We also collect the date of your submission to calculate how late it has been submitted. The date of the submission will be the date and time of whatever commit the "final_ver" tag refers to. 

You can check the date and time for yourself by typing ```git log -1 --format=%ai [tag name]```.

#### On GitHub.com
To create a tag, you can click on "create a new release" on the right side bar. The only thing that needs to be specified on this page is "Tag Version", which must be "final_ver". Click "Publish Release" and the tag will be created.

If you want to update your submission, delete and re-add the tag. Click on the tags icon next to the branch selector. Click on the name of the tag, and there should be an option to delete the tag in the top right. Deleting the release is the same thing as deleting the tag. 
#### From the Command Line
To create a tag from the command line, type ```git tag [tag name]```. To show all tags that exist for a repository, ```git show```. Once your tag is created, you must ```git push origin [tag name]```. A normal repository push will not include any tag updates.

To update your submission, there are two options. You can either ```git tag [tag name] -f ```, which forces the tag to update, and ```git push origin [tag name] -f```. Or, you can ```git push -d origin [tag name]``` to delete the tag, and then re-add the tag. 

### Viewing the Grade Report
If students want to see their grade and feedback, they can simply navigate to their assignment repository and view gradeReport.txt.
In gradeReport.txt the student can see their overall grade and the feedback for their submission, which lists where they 
may have lost points and why. 

