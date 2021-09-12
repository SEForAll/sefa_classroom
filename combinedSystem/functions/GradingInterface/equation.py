import re

# keep in mind this is for professors grading stuff, so it shouldn't be too complicated
def calculate_equation(equation):
    """
    takes a string equation and calculates the value

    :param equation: equation to calculate the grade from
    :type equation: str
    :return: float
    """

    whitelistedchars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                        '.', '+', '-', '*', '/', '^', '(', ')', ' ', '\t']
    for letter in equation:
        if letter not in whitelistedchars:
            raise AttributeError(f"equation contains illegal characters: {letter}")

    parenthesis = re.compile(r'\([0-9.+\-*/^\s]+\)')  # regex pattern for parenthesis

    for match in parenthesis.finditer(equation):  # for each parenthesis match in the equation
        replace = match.group(0)[1:-1]  # remove the parenthesis
        equation = equation.replace(match.group(0), str(calculate_equation(replace)))  # reduce using recursion


    exponent = re.compile(r'(-?\d+\.?\d*)+\s*\^\s*(-?\d+\.?\d*)+')  # regex pattern for exponents
    while '^' in equation: # while there is still a ^ in the equation
        for match in exponent.finditer(equation):  # for each exponent match in the equation
            equation = equation.replace(str(match.group(0)), f'{float(match.group(1)) ** float(match.group(2))}')
            #  reduce the exponent to a number

    multdiv = re.compile(r'(-?\d+\.?\d*)+\s*(\*|/)\s*(-?\d+\.?\d*)+')  # regex pattern for multiplication or division

    while '/' in equation or '*' in equation:  # while there is a * or / in the equation
        for match in multdiv.finditer(equation):  # for each multiplication or division match
            if match.group(2) == '*':  # if it's multiplication
                equation = equation.replace(match.group(0), f'{float(match.group(1)) * float(match.group(3))}')
                # reduce the multiplication to a number
            else:  # if it's division
                equation = equation.replace(match.group(0), f'{float(match.group(1)) / float(match.group(3))}')
                # reduce the division to a number

    addsub = re.compile(r'(-?\d+\.?\d*)+\s*(\+|\-)\s*(-?\d+\.?\d*)+')  # regex pattern for addition or subtraction

    for match in addsub.finditer(equation):  # for each multiplication or division match
        if match.group(2) == '+':  # if it's addition
            equation = equation.replace(match.group(0), f'{float(match.group(1)) + float(match.group(3))}')
            # reduce the addition to a number
        else:  # if it's subtraction
            equation = equation.replace(match.group(0), f'{float(match.group(1)) - float(match.group(3))}')
            # reduce the subtraction to a number

    mathchars = ['+', '-']
    negativenumber = re.compile(r'-(\d+\.?\d*)')
    for letter in equation:
        if letter in mathchars:  # if the equation still has addition or subtraction in the equation
            if negativenumber.match(equation) is None:  # if it's not just a negative number
                try:
                    return calculate_equation(equation)  # reduce using recursion
                except RecursionError:  # handle too many recursion calls
                    raise AttributeError("Equation not entered correctly, cannot reduce")
                    # it only happens when the equation is not irreducible
            else:  # if it is a negative number, use the eval equation to reduce
                equation = str(eval(equation))  # handles negative numbers

    return float(equation)  # return a float


def calculate_grade(values, equation="100*(p/t)-m-10*l"):
    """
    calculates the grade from the equation and plugs in the values

    :param equation: equation to calculate the grade from using variables t = num testcases,
                                                                          p = num testcases passed,
                                                                          m = bytes of memory leak,
                                                                          l = days late
    :type equation: str
    :param values: the values of the variables in order: [t, p, m, l]
    :type values: list
    :return: float
    """
    variablelist = ['t', 'p', 'm', 'l']  # list of variables that should be in the equation

    for i in range(len(values)):
        equation = equation.replace(variablelist[i], str(values[i]))  # substitute values for variables

    whitelistedchars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                        '.', '+', '-', '*', '/', '^', '(', ')', ' ', '\t']
    for letter in equation:
        if letter not in whitelistedchars:
            raise AttributeError(f"equation contains an illegal character: {letter}")

    equation = equation.replace('^', '**')

    value = eval(equation)

    if value > 0:
        return value # return the result of the equation if it is negative
    else: 
        return 0



#  testing code
if __name__ == '__main__':
    print(calculate_grade([5, 4, 2, 1], '100*(-p/t+3) - m - l'))



