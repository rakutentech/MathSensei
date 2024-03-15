import re
import astor
import ast

# Function to count no of operations in code
def count_operations(node):
    if isinstance(node, ast.BinOp):
        return count_operations(node.left) + count_operations(node.right) + 1
    elif isinstance(node, ast.UnaryOp):
        return count_operations(node.operand) + 1
    elif isinstance(node, ast.Call):
        return len(node.args) + sum(count_operations(arg) for arg in node.args)
    else:
        return 0

# Function to measure complexity of code
def measure_complexity(code):
    parsed = ast.parse(code)
    print("Parse works!")
    num_operations = count_operations(parsed)
    return num_operations

def extract_entities(input_string):
    entities = input_string.split(',')
    entities = [entity.strip() for entity in entities]
    return entities


def extract_unique_elements(input_list):
    unique_elements = list(set(input_list))
    return unique_elements

# Extract mathematical equations
def extract_equations(latex_problem):
    # Find all algebraic equations enclosed in $...$
    equations = re.findall(r'\$([^$]+)\$', latex_problem)
    unique_elements = extract_unique_elements(equations)
    l = []
    for i in range(len(unique_elements)):
        e = extract_entities(unique_elements[i])
        l = l+e
    return l

# Extract mathematical functions
def extract_math_functions(problem_list):
    functions = []
    
    math_functions = [
        "sin", "cos", "tan", "cot", "sec", "csc",
        "log", "ln", "exp", "sqrt", "abs","sinh","cosh","tanh","sech","csch","coth",
        "arccos","deg","arcsin","lg","sup","arctan","det",
        "max","min"
        
        # Add more functions as needed
    ]
    
    for i in range(len(problem_list)):
        problem = problem_list[i]
        functions.append([])
        for func in math_functions:
            if re.search(rf'\b{func}\b', problem, re.IGNORECASE):
                functions[i].append(func)

        
        #print("Done!")        
    
    return functions

# Extract latex symbols 
def extract_latex_symbols(text):
    latex_symbols = re.findall(r'\\[a-zA-Z]+', text)
    return latex_symbols


# Extract latex objects
def extract_latex_objects(problem_list):
    
    latex_objects = []
    
    object_symbols = [
     
        
        # Add more functions as needed
    ]
    
    for i in range(len(problem_list)):
        problem = problem_list[i]
        latex_objects.append([])
        for obj in object_symbols:
            if re.search(rf'\b{func}\b', problem, re.IGNORECASE):
                functions[i].append(func)
        
    return functions


# Count no of mathematical entities in latex problem
def count_math_entities(latex_problem):
    # Count variables, constants, functions, and expressions
    variables = set(re.findall(r'\b([a-zA-Z]+)\b', latex_problem))
    constants = set(re.findall(r'\b([0-9]+(?:\\.[0-9]+)?)\b', latex_problem))
    
    print("*******************************************")
    print("Latex problem:",latex_problem)

    print("Variables",variables)
    print("Constants",constants)


    num_variables = len(variables)
    num_constants = len(constants)
    
    
    return num_variables, num_constants

# Example to extract variables from dataset
def extract_variables(problem_list):
    variable_set = []
    num_variables = []

    for i in range(len(problem_list)):
        problem = problem_list[i]
        variable_set.append([])
        num_variables.append([0])
        equations = re.findall(r'(?<!\\)\$.*?(?<!\\)\$', problem)
        for equation in equations:
            variables = re.findall(r'(?<!\\)\b([a-zA-Z]+)\b', equation)
            variable_set[i]=variable_set[i]+variables
            
        variable_set[i] = list(set(variable_set[i]))
        #print(variable_set[i])
      
   
    return variable_set


# Example LaTeX problems in MATH
problems = [
    "Suppose $x$ is a solution to $x^2 + 1 = 7x$. What is the sum of $x$ and its reciprocal?",
    "If $3a - b + c = -3, a+3b+c = 9, a+b+3c = 19$, then find $abc$.",
    "The two lines $y = 2x - 13$ and $3x+y = 92$ intersect. What is the value of $x$ at the point of intersection?",
    "If $j$ and $k$ are inversely proportional and $j = 16$ when $k = 21$, what is the value of $j$ when $k = 14$?",
    "What is the value of $x$ in the equation $(17^6-17^5)\\div16=17^x$?",
    "Evaluate $\\left(\\frac{i}{4}\\right)^4$.",
    "Let $a$ and $b$ be real numbers. The function $h(x)=ax+b$ satisfies $h(1)=5$ and $h(-1)=1$.  What is $h(6)$?",
    "In triangle $ABC$, medians $\\overline{AD}$ and $\\overline{BE}$ are perpendicular.  If $AC = 22$ and $BC = 31$, then find $AB$.",
    "If\n\\[k = \\sin^6 \\theta + \\cos^6 \\theta = \\sin 2 \\theta,\\]then find $k.$",
    "If $\\tan \\theta = 7,$ then find $\\tan 2 \\theta.$",
    "Suppose that $\\sec x+\\tan x=\\frac{22}7.$  Find $\\csc x+\\cot x.$"
]




'''
for idx, problem in enumerate(problems, start=1):
    equations = extract_equations(problem)
    #print(type(equations))
    print(f"Problem {idx}:")
    for eq_idx, equation in enumerate(equations, start=1):
        print(f"Latex entity : {eq_idx}: {equation}")
    print()
'''



'''
# Example text containing LaTeX symbols
for idx, text in enumerate(problems, start=1):
  #text = "Consider the matrix \\matrix{1 & 2 \\\\ 3 & 4} and the vector \\vec{x}."
    
    symbols = extract_latex_symbols(text)
    print("Extracted LaTeX Symbols:", symbols)

'''    




'''
extracted_functions = extract_math_functions(problems)
print("Extracted Mathematical Functions:", extracted_functions)
'''


def remove_long_strings(input_list):
    return [item for item in input_list if len(item) <= 1]


'''

big_var_set = extract_variables(problems)

# Also include unknown functions like f,g,h
var_set = [remove_long_strings(i) for i in big_var_set]
num_variables = [len(i) for i in var_set]
print("Number of Variables:", num_variables)
print("Var set",var_set)
print(big_var_set)

'''

# Function to display AST
def display_ast(code):
    parsed = ast.parse(code)
    print(type(parsed))
    tree = ast.dump(parsed)
    print(type(tree))
    print(tree)
    #print("\nFormatted Tree:\n")
    formatted_tree = astor.to_source(parsed)
    #print(formatted_tree)


# Function to analyze code complexity
def analyze_code_complexity(code):
    # Parse the code into an AST
    parsed_code = ast.parse(code)
    
    # Initialize complexity counters
    num_operations = 0
    num_intermediate_steps = 0
    
    # Traverse the AST to analyze complexity
    for node in ast.walk(parsed_code):
        if isinstance(node, ast.BinOp):
            num_operations += 1
        elif isinstance(node, ast.Assign):
            num_intermediate_steps += 1
    
    # Calculate a complexity score based on the counters
    complexity_score = num_operations + num_intermediate_steps
    
    return complexity_score

# Function to count no of variables in AST
def count_variables(code):
    parsed_code = ast.parse(code)
    variable_names = set()
    
    for node in ast.walk(parsed_code):
        if isinstance(node, ast.Name):
            variable_names.add(node.id)
    
    num_variables = len(variable_names)
    return num_variables, variable_names



code = """
from sympy import *
# Define the variables
x, c = symbols('x c')
# Define the equation
eq = (x**2 - 4*x + 3)*(x + 5) - (x**2 + 4*x - 5)*(x - c)
# Simplify the equation
simplified_eq = simplify(eq)
print(\\\"Simplified equation:\\\", simplified_eq)
# Since the equation must hold for all x, the coefficient of x must be zero.
# Therefore, we solve the equation simplified_eq = 0 for c.
solution = solve(simplified_eq, c)
print(\\\"Solution:\\\",solution)
# Print the solution
print('c =', solution[0])
"""

import codecs

#print(len(codecs.decode(code_string5, 'unicode_escape')))
#print(len(code_string4))
'''
print("Abstract syntax tree of the code:")
display_ast(codecs.decode(code, 'unicode_escape'))
print("***************************")
'''

'''
# Print a simple complexity 
complexity = measure_complexity(codecs.decode(code, 'unicode_escape'))
print("Code Complexity:", complexity)
'''


# Calculate and print complexity measure (use Abstract Syntax Tree to add intermediate steps(Assignments) and No of binOP)
complexity = analyze_code_complexity(codecs.decode(code, 'unicode_escape'))
print("Code Complexity:", complexity)

# Count variables and print the result
num_variables, variable_names = count_variables(codecs.decode(code, 'unicode_escape'))
print("Number of Variables:", num_variables)
print("Variable Names:", variable_names)

