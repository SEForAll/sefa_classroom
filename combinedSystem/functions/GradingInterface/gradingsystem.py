import os
from distutils.ccompiler import new_compiler
import filecmp
import re
import multiprocessing
import time

# Important!!!!!! If you want to use grade function, to go interface.py <-- line 132 of interface.py
def grade(path, weights):
    """
    :param path: path to the project. ex) /users/alex/myfiles/project
    :type path: str
    :param weights: a dictionary that contains the weights of each testcase and the memoryleak (ex: {'test1': 40, 'test2' 60, 'mem_coef': 2})
    :type weights: dict

    :return points: Final grade of the input homework
    :type points: float
    :return list_final: Feedback of the input homework
    :type list_final: list of string
    """

    weights = dict(weights)  # have to make a copy because it's using the changed values from the previous function call for some reason

    testcases_dict = dict()

    list_final = []  # list of feedback for the submission

    debugging = False  # set to True to enable debugging print statements

    os.chdir(path)  # change the directory to the path of the project
    os.system('make clean >/dev/null 2>&1')  # get rid of files not needed

    if debugging:
        print('starting compile')

    # ---------------------------------
    # check that everything can compile

    if len(os.listdir(path)) == 0:  # if there are no files in the directory
        list_final.append('no files submitted')
        return None, list_final, None

    result = os.system("make >/dev/null 2>&1")  # Run make to see if files compile

    filename = "hw"
    if result == 0:
        list_final.append(f'{filename} compiled correctly! going to next step...')
    else:
        list_final.append(f'{filename} did not compile correctly, please check your files')
        return None, list_final, None
        exit
    if debugging:
        print('compile finished\nstarting diff')

    # this is the setup for the next few parts

    with open("Makefile", 'r') as f:  # open the Makefile
        text = f.read()  # read the contents of the Makefile

        # ------------------------
        # get the number of test cases to run

        num = re.compile(r'test(\d+):')  # pattern to find how many testcases there are
        match = num.findall(text)
        if len(match) != 0:  # if there is at least one match
            numberoftestcases = int(len(match))
        else:  # if there are no matches, stop grading
            list_final.append('error when executing Makefile... contact your '
                              'professor about this issue (number of test cases could not be found)')
            return None, list_final, None

        if numberoftestcases == 0:  # if there are no testcases, stop grading
            list_final.append('error when executing Makefile... contact your '
                              'professor about this issue (number of test cases is not correct)')
            return None, list_final, None
        
        testcases_dict = {f'test{i}': dict() for i in range(1, numberoftestcases + 1)}  # initialize dict of dicts
        testcases_dict['num_testcases'] = numberoftestcases  # add the number of test cases to the dict

        # ------------------------
        # get the valgrind statements to run

        valgrindstatements = []  # statements to run valgrind on (./hw14 inputs/input1)
        val = re.compile(r'(\./.+)')  # pattern to find statements to run valgrind on
        reglist = val.findall(text)  # all matches
        for elem in reglist:
            temp = elem.split('>')[0]  # get rid of these characters bc they write / append to a different file and we don't want that
            temp = elem.split('>>')[0]
            temp = elem.split('|')[0]
            valgrindstatements.append(temp)
        
        # removes valgrind statement for the 'testall' case in the makefile, assuming it is at the bottom
        while len(valgrindstatements) > numberoftestcases:
            valgrindstatements.pop()  # get rid of extra statements that may have been picked up

    # -------------------------
    # Check diff

    passed = 0  # number of test cases that have passed
    os.chdir(path)  # change the directory to the path with the submission files
    with open('empty.txt', 'w+') as f:  # make an empty file for comparison
        f.write('')

    with open('grade.txt', 'w+') as f:  # make a grading file
        f.write('')

    total_weight = 0  # the total weight given by the professor (incase it does not add up to 100%)

    for i in range(1, numberoftestcases + 1):  # run the loop for each testcase
        total_weight += weights[f'test{i}']  # add up the total weight of all the testcases so we can divide later
        testcases_dict[f'test{i}']['weight'] = weights[f'test{i}']  # set the weight field for the ith test in the testcase dict

        os.system('make clean >/dev/null 2>&1')  # get rid of unwanted
        os.system('make >/dev/null 2>&1')  # run 'make' in the console
        #os.system(f'make testcase{i} >/dev/null 2>&1')  # PROF MUST SEND THE OUTPUT OF THE DIFF COMMAND TO grade.txt !!
        # i can't route the output of the diff command, only the output of the testcase command
        # this must be done by the professor
        # ex) diff output1.txt expected1.txt > grade.txt
        try:
            checkfortimeout(os.system, args=[f'make test{i} >/dev/null 2>&1'])  # try to run a test
        except TimeoutError:  # if it times out, end the process and go to the next testcase
            list_final.append(f'Test case {i} timed out')
            testcases_dict[f'test{i}']['error_log'] = f'Test case {i} timed out'  # set error_log field for the test[i] dict
            testcases_dict[f'test{i}']['passed'] = False  # set passed field for the test[i] dict
            weights[f'test{i}'] = 0  # change the points earned to 0   

            continue

        comp = filecmp.cmp('grade.txt', 'empty.txt', shallow=False)  # compare the files
        if comp is True:  # if the files match
            list_final.append(f"Test case {i} is correct!")
            testcases_dict[f'test{i}']['error_log'] = f"Test case {i} is correct!"
            testcases_dict[f'test{i}']['passed'] = True

            passed += 1
        else:  # if the files don't mach
            list_final.append(f"Test case {i} is wrong...")
            testcases_dict[f'test{i}']['error_log'] = "Test case {i} is wrong..."
            testcases_dict[f'test{i}']['passed'] = False

            weights[f'test{i}'] = 0  # change the points earned to 0

    list_final.append(f'{passed}/{numberoftestcases} test cases passed!')

    for key in weights.keys():  # divide each testcase by the total weight and multiply by 100 to make each testcase worth a percentage
        if key.startswith('test'):
            weights[key] *= 100 / total_weight 
        

    if debugging:
        print('diff finished\nstarting memcheck')

    # ----------------------------
    # Check memory
    bytesLeaked, blocksLeaked = memcheck(path, valgrindstatements)  # check leaked memory for each testcase

    # print(bytesLeaked)
    if bytesLeaked == -1:  # if bytes leaked is negative that means there was something wrong
        list_final.append('error when executing Makefile... contact your professor about this issue (valgrind not called correctly, make sure it is installed on the server)')
        return None, list_final, None
    # else:
    #     list_final.append('makefile executed correctly!')

    for i in range(len(bytesLeaked)):  # go through each testcase and say how many bytes were leaked
        if bytesLeaked[i] > 0:  # if there was memory leak
            list_final.append(f'{bytesLeaked[i]} byte(s) of memory leak present in test case {i+1}')
        if bytesLeaked[i] == 0:  # if there was no memory leak
            list_final.append(f'No memory leak in test case {i+1}')

    for i in range(numberoftestcases):  # subtract points for memory leak
        weights[f'test{i + 1}'] -= weights['mem_coef'] * bytesLeaked[i]
        if weights[f'test{i + 1}'] < 0:
            weights[f'test{i + 1}'] = 0

    if debugging:
        print('memcheck finished')

    os.system('make clean >/dev/null 2>&1')  # get rid of unwanted files
    os.remove('grade.txt')  # get rid of file now that grading is complete
    os.remove('empty.txt')  # get rid of file now that grading is complete

    # calculate the total grade
    points = 0
    for key in weights.keys():
        if key.startswith('test'):
            points += weights[key]  # sum up all the points from 

    return points, list_final, testcases_dict


def memcheck(makefile_dir, valgrindstatements):
    """
    :param makefile_dir: full directory to the makefile (starts with a '/' and does not include the makfile)
    :type makefile_dir: str
        example: /users/alex/desktop/project14

    :param valgrindstatements: list containing the statements to run valgrind on
    :type valgrindstatements: list
        example: ['./hw14 inputs/input1', ./hw14 inputs/input2]
    :return bytes: bytes of code leaked in the program
    :return blocks: blocks of code that leaked memory
    if the output is -1, -1: valgrind was not run correctly (make sure it's installed and working on your computer first)
    """

    os.chdir(makefile_dir)  # go to the folder where the makefile and other files are (essentially the project folder)
    # os.system("make") # >/dev/null 2>&1")  # compiles the code according to the makefile

    tempfile = "tempfile.txt"  # name of the tempfile which will store the valgrind output

    bytesInUse = []  # bytes that are in use at the end of the program. each entry is a valgrindstatement
    blocks = []  # how many blocks leak memory. each entry is a valgrindstatement

    for statement in valgrindstatements:  # run through the valgrind statements
        #os.system(f'valgrind {statement} > {tempfile} 2>&1')
        try:
            checkfortimeout(os.system, args=[f'valgrind --tool=memcheck --log-file={tempfile} --leak-check=full --verbose {statement} >/dev/null 2>&1'], timeout=10)
            # previous statement executes valgrind on the executable and writes the output to the tempfile
            # also gets checked for a timeout obviously lmao
        except TimeoutError:
            bytesInUse.append(0)
            blocks.append(0)
            continue
        
        p = re.compile(r': ((\d*\,)*\d+) bytes in (\d+) blocks')  # regex for getting values from valgrind output

        with open(tempfile, 'r') as f:
            text = f.read()
            match = p.search(text)  # use regex to get number of bytes leaked and in how many blocks
            if match is None:
                return -1, -1  # return this if valgrind is not called properly (might happen bc i wrote this on mac)
            bytesInUse.append(int(match.group(1).replace(',', '')))  # put regex groups from the match into variables and cast to integers
            blocks.append(int(match.group(3)))

        os.remove(tempfile)  # remove the files we created as they only pertain to this function

    return bytesInUse, blocks


def checkfortimeout(func, args=None, timeout=5):
    """
    runs a function and raises TimeoutError if the specified time limit is reached
    :param func: funciton that could timeout
    :type func: function
    :param args: arguments to pass to the function (defaults to None)
    :type args: list
    :param timeout: number of seconds to trigger a timeout (defaults to 5)
    :type timeout: int
    :return:
    """

    process1 = multiprocessing.Process(target=time.sleep, args=[timeout])  # sets timeout process
    if args is None:  # sets process that might timeout
        process2 = multiprocessing.Process(target=func)
    else:
        process2 = multiprocessing.Process(target=func, args=args)

    process1.start()  # start both processes
    process2.start()
    while process1.is_alive():  # while the timeout process is still running
        if process2.is_alive() is False:  # if the function is done running, return the function
            return
    process2.terminate()  # if the timeout process is finished and the function is not, raise an error
    raise TimeoutError("the program timed out")
