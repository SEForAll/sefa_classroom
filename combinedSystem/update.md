# ADDONS
## Commit Tracker:
* Uses the GitHub REST API to write the number of commits for each student
for a given homework to a csv file.

* Input csv file example can be found `combinedSystem/example.csv`

* Run command with following format:

    ```$python commitNum.py pathToInputCSV hwToCheck```
## Moss:
### How to run: 
```$python3 moss.py --grade_all --config [Path to config.json]```

### File Structure
* moss.py
* config.json                -> in profFiles directory, must change all arguments
* /MossDirectory             -> a folder in this directory
* moss.pl                 -> the moss script, paste directly from email
* student_files.c         -> the c files from the students, automatically put into and deleted from the directory
* /TempMossDirectory         -> automatically created and deleted 
* cloned_student_repos    -> the student repos from GitHub Classrooms